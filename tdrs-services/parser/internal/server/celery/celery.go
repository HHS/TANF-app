package celery

import (
	"context"
	"fmt"
	"log"
	"os/signal"
	"syscall"
	"time"

	"github.com/gocelery/gocelery"
	"github.com/gomodule/redigo/redis"
	"github.com/jackc/pgx/v5/pgxpool"

	"go-parser/internal/config"
	"go-parser/internal/db"
	"go-parser/internal/pipeline"
	"go-parser/internal/server"
	"go-parser/internal/storage"
	"go-parser/internal/storage/reader"
	"go-parser/internal/storage/writer"
	"go-parser/internal/validation"
)

// taskName is the fully-qualified Celery task name that Django dispatches.
// We use a different task name to not collide with the python parser while developing.
const taskName = "tdpservice.scheduling.parser_task.go_parse"
const postParseTaskName = "tdpservice.scheduling.parser_task.post_parse"
const defaultQueueName = "go-parser"
const defaultPostParseQueueName = "celery"

const statusUpdateTimeout = 5 * time.Second

const (
	dataFileStateParseStarted   = "parse_started"
	dataFileStateParseFailed    = "parse_failed"
	dataFileStateParseCompleted = "parse_completed"

	summaryStatusRejected = "Rejected"
)

// Server owns the full lifecycle for celery worker mode.
// It maintains long-lived connections (DB pool, S3 client) and processes
// tasks as they arrive from the celery broker.
type Server struct {
	server.Base
	dbPool    *pgxpool.Pool
	s3Storage *storage.S3Storage
}

type celeryTaskSender interface {
	Delay(task string, args ...interface{}) (*gocelery.AsyncResult, error)
}

// New creates a celery mode runner. It connects to the database,
// loads content types, and initializes the S3 client.
func New(cfg *config.Config, reg *config.Registry, validators *validation.ValidatorRegistry) (*Server, error) {
	ctx := context.Background()
	base := server.NewBase(cfg, reg, validators)

	dbPool, err := base.ConnectDB(ctx)
	if err != nil {
		return nil, err
	}

	s3Storage, err := storage.NewS3Storage(storage.S3StorageConfig{
		Region:   cfg.Storage.S3.Region,
		Endpoint: cfg.Storage.S3.Endpoint,
	})
	if err != nil {
		dbPool.Close()
		return nil, fmt.Errorf("failed to initialize S3 storage: %w", err)
	}

	return &Server{
		Base:      base,
		dbPool:    dbPool,
		s3Storage: s3Storage,
	}, nil
}

// Run starts the celery worker loop. It blocks until the context is cancelled
// or the process receives SIGINT/SIGTERM.
func (s *Server) Run(parentCtx context.Context) error {
	if s.dbPool != nil {
		defer s.dbPool.Close()
	}

	if s.Config.Server.Celery.RedisURL == "" {
		return fmt.Errorf("server.celery.redis_url is required in celery mode")
	}

	// Create Redis connection pool for the celery broker and result backend.
	redisPool := &redis.Pool{
		MaxIdle:     3,
		IdleTimeout: 240 * time.Second,
		Dial: func() (redis.Conn, error) {
			return redis.DialURL(s.Config.Server.Celery.RedisURL)
		},
	}
	defer redisPool.Close()

	numWorkers := s.Config.Server.Celery.NumWorkers
	if numWorkers < 1 {
		numWorkers = 1
	}
	queueName := s.Config.Server.Celery.Queue
	if queueName == "" {
		queueName = defaultQueueName
	}

	broker := gocelery.NewRedisBroker(redisPool)
	broker.QueueName = queueName
	postParseQueueName := s.Config.Server.Celery.PostParseQueue
	if postParseQueueName == "" {
		postParseQueueName = defaultPostParseQueueName
	}
	postParseBroker := gocelery.NewRedisBroker(redisPool)
	postParseBroker.QueueName = postParseQueueName

	celeryClient, err := gocelery.NewCeleryClient(
		broker,
		newRedisCeleryBackend(redisPool),
		numWorkers,
	)
	if err != nil {
		return fmt.Errorf("failed to create celery client: %w", err)
	}
	postParseClient, err := gocelery.NewCeleryClient(
		postParseBroker,
		newRedisCeleryBackend(redisPool),
		1,
	)
	if err != nil {
		return fmt.Errorf("failed to create post-parse celery client: %w", err)
	}

	// Register the parse task handler. Django sends data_file_id as a
	// positional arg which arrives as float64 after JSON deserialization.
	// The closure includes panic recovery so a single bad task cannot kill
	// the worker goroutine.
	taskCtx := context.WithoutCancel(parentCtx)
	celeryClient.Register(taskName, func(dataFileID float64, reparseID float64) (result string) {
		id := int32(dataFileID)
		reparse := int32(reparseID)
		parseError := ""

		defer func() {
			if r := recover(); r != nil {
				parseError = fmt.Sprintf("panic: %v", r)
				log.Printf("PANIC in task for data_file_id=%d: %v", id, r)
				result = parseError
				if err := s.updateDataFileSummaryStatus(taskCtx, id, summaryStatusRejected); err != nil {
					log.Printf("Failed to update DataFileSummary status for data_file_id=%d during worker panic: %v", id, err)
				}
				if err := s.updateDataFileState(taskCtx, id, dataFileStateParseFailed); err != nil {
					log.Printf("Failed to update shadow DataFile state for data_file_id=%d during worker panic: %v", id, err)
				}
			}
			if err := s.enqueuePostParseTask(postParseClient, id, reparse, parseError); err != nil {
				log.Printf("Failed to enqueue post-parse task for data_file_id=%d: %v", id, err)
				if updateErr := s.updateDataFileSummaryStatus(taskCtx, id, summaryStatusRejected); updateErr != nil {
					log.Printf("Failed to update DataFileSummary status for data_file_id=%d after post-parse enqueue failure: %v", id, updateErr)
				}
				if updateErr := s.updateDataFileState(taskCtx, id, dataFileStateParseFailed); updateErr != nil {
					log.Printf("Failed to update shadow DataFile state for data_file_id=%d after post-parse enqueue failure: %v", id, updateErr)
				}
				result = fmt.Sprintf("post-parse enqueue error: %v", err)
			}
		}()

		log.Printf("Received parse task for data_file_id=%d reparse_id=%d", id, reparse)

		if err := s.processTask(taskCtx, id); err != nil {
			parseError = fmt.Sprintf("error: %v", err)
			log.Printf("Task failed for data_file_id=%d: %v", id, err)
			return parseError
		}

		log.Printf("Task completed successfully for data_file_id=%d", id)
		return "success"
	})

	// Derive a context that cancels on OS signals for graceful shutdown.
	workerCtx, stop := signal.NotifyContext(parentCtx, syscall.SIGINT, syscall.SIGTERM)
	defer stop()

	log.Printf(
		"Starting celery worker (%d goroutines), listening for '%s' tasks on queue %q via %s",
		numWorkers,
		taskName,
		queueName,
		s.Config.Server.Celery.RedisURL,
	)
	celeryClient.StartWorkerWithContext(workerCtx)

	// Block until the context is cancelled (signal received).
	<-workerCtx.Done()
	log.Println("Shutting down celery worker...")

	// Wait for any in-flight task to complete.
	celeryClient.StopWorker()
	log.Println("Celery worker stopped")

	return nil
}

func (s *Server) enqueuePostParseTask(client celeryTaskSender, dataFileID int32, reparseID int32, parseError string) error {
	task := s.Config.Server.Celery.PostParseTaskName
	if task == "" {
		task = postParseTaskName
	}

	var parseErrorArg any
	if parseError != "" {
		parseErrorArg = parseError
	}

	_, err := client.Delay(task, dataFileID, reparseID, parseErrorArg)
	return err
}

func (s *Server) updateDataFileSummaryStatus(parentCtx context.Context, dataFileID int32, status string) error {
	statusCtx, cancel := context.WithTimeout(context.WithoutCancel(parentCtx), statusUpdateTimeout)
	defer cancel()

	summaryTable := config.DataFileSummaryTableName(s.Config.Database.EffectiveTablePrefix())
	return db.UpdateDataFileSummaryStatus(statusCtx, s.dbPool, summaryTable, dataFileID, status)
}

func (s *Server) updateDataFileState(parentCtx context.Context, dataFileID int32, state string) error {
	statusCtx, cancel := context.WithTimeout(context.WithoutCancel(parentCtx), statusUpdateTimeout)
	defer cancel()

	dataFileTable := config.DataFileTableName(s.Config.Database.EffectiveTablePrefix())
	return db.UpdateDataFileState(statusCtx, s.dbPool, dataFileTable, dataFileID, state)
}

// processTask handles a single parse task end-to-end:
// DB lookup → S3 download → decode → pipeline → status update.
func (s *Server) processTask(taskCtx context.Context, dataFileID int32) error {
	dataFileTable := config.DataFileTableName(s.Config.Database.EffectiveTablePrefix())

	// 1. Look up datafile metadata from the database.
	df, err := db.GetDataFile(taskCtx, s.dbPool, dataFileTable, dataFileID)
	if err != nil {
		return fmt.Errorf("failed to get datafile: %w", err)
	}

	if err := db.EnsureShadowDataFile(taskCtx, s.dbPool, dataFileTable, df); err != nil {
		return fmt.Errorf("failed to prepare shadow datafile: %w", err)
	}

	summaryTable := config.DataFileSummaryTableName(s.Config.Database.EffectiveTablePrefix())
	if err := db.EnsureDataFileSummary(taskCtx, s.dbPool, summaryTable, dataFileID); err != nil {
		return fmt.Errorf("failed to prepare shadow datafile summary: %w", err)
	}
	if err := db.UpdateDataFileState(taskCtx, s.dbPool, dataFileTable, dataFileID, dataFileStateParseStarted); err != nil {
		return fmt.Errorf("failed to mark shadow datafile parse started: %w", err)
	}

	// 2. Build the pipeline's DataFileContext from the DB record.
	section := sectionNumber(df.Section)
	if section == 0 {
		return fmt.Errorf("unknown section name %q for datafile %d", df.Section, dataFileID)
	}

	dfCtx := pipeline.DataFileContext{
		Program:       df.ProgramType,
		Section:       section,
		DatafileID:    df.ID,
		FiscalYear:    int(df.Year),
		FiscalQuarter: df.Quarter,
		SectionName:   df.Section,
	}

	// 3. Build the S3 file key.
	// Django's storage backend prepends APP_NAME (e.g. "dev") to the DB file path,
	// so we must do the same via the configured key_prefix.
	if !df.File.Valid || df.File.String == "" {
		return fmt.Errorf("datafile %d has no S3 file key", dataFileID)
	}

	s3Key := df.File.String
	if prefix := s.Config.Storage.S3.KeyPrefix; prefix != "" {
		s3Key = prefix + "/" + s3Key
	}

	// 4. Create the database sink using the shared connection pool.
	sink, err := writer.CreateSink("database", "", "", s.dbPool)
	if err != nil {
		return fmt.Errorf("failed to create database sink: %w", err)
	}
	defer sink.Close()

	// 5. Open file, decode, and run the parsing pipeline.
	source := reader.NewS3Source(s.s3Storage, s.Config.Storage.S3.Bucket, s3Key)
	result, err := s.RunPipeline(taskCtx, source, sink, dfCtx)
	if err != nil {
		// Update status to indicate failure before returning.
		if updateErr := s.updateDataFileSummaryStatus(taskCtx, dataFileID, summaryStatusRejected); updateErr != nil {
			log.Printf("Failed to update DataFileSummary status for data_file_id=%d: %v", dataFileID, updateErr)
		}
		if updateErr := s.updateDataFileState(taskCtx, dataFileID, dataFileStateParseFailed); updateErr != nil {
			log.Printf("Failed to update shadow DataFile state for data_file_id=%d: %v", dataFileID, updateErr)
		}
		return fmt.Errorf("pipeline processing failed: %w", err)
	}

	totalCreated, totalInFile := recordTotalsForResult(result)
	if err := db.UpdateDataFileSummaryResult(taskCtx, s.dbPool, summaryTable, dataFileID, totalInFile, totalCreated); err != nil {
		return fmt.Errorf("failed to update shadow datafile summary result: %w", err)
	}
	if err := db.UpdateDataFileState(taskCtx, s.dbPool, dataFileTable, dataFileID, dataFileStateParseCompleted); err != nil {
		return fmt.Errorf("failed to update shadow datafile state: %w", err)
	}

	// 6. Log results.
	log.Printf("data_file_id=%d processed in %s", dataFileID, result.Duration)
	for table, count := range result.RecordCounts {
		log.Printf("  %s: %d records", table, count)
	}

	return nil
}

func recordTotalsForResult(result *pipeline.ParsingResult) (created int64, total int64) {
	if result == nil {
		return 0, 0
	}
	for table, count := range result.RecordCounts {
		if table == "parser_error" {
			continue
		}
		created += count
	}
	total = created
	return created, total
}

// sectionNumber maps a DataFile section name to the section number
// used by the pipeline and file spec registry.
func sectionNumber(section string) int {
	switch section {
	case "Active Case Data":
		return 1
	// TODO: We should probably move off of the number system for sections.
	case "Work Outcomes of TANF Exiters":
		return 1
	case "Closed Case Data":
		return 2
	case "Secondary School Attainment":
		return 2
	case "Aggregate Data":
		return 3
	case "Supplemental Work Outcomes":
		return 3
	case "Stratum Data":
		return 4
	default:
		return 0
	}
}
