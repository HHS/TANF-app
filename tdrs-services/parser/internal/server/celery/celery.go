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

const statusUpdateTimeout = 5 * time.Second

// Server owns the full lifecycle for celery worker mode.
// It maintains long-lived connections (DB pool, S3 client) and processes
// tasks as they arrive from the celery broker.
type Server struct {
	server.Base
	dbPool    *pgxpool.Pool
	s3Storage *storage.S3Storage
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
		queueName = "go-parser"
	}
	broker := gocelery.NewRedisBroker(redisPool)
	broker.QueueName = queueName

	celeryClient, err := gocelery.NewCeleryClient(
		broker,
		newRedisCeleryBackend(redisPool),
		numWorkers,
	)
	if err != nil {
		return fmt.Errorf("failed to create celery client: %w", err)
	}

	// Register the parse task handler. Django sends data_file_id as a
	// positional arg which arrives as float64 after JSON deserialization.
	// The closure includes panic recovery so a single bad task cannot kill
	// the worker goroutine.
	taskCtx := context.WithoutCancel(parentCtx)
	celeryClient.Register(taskName, func(dataFileID float64) (result string) {
		id := int32(dataFileID)

		defer func() {
			if r := recover(); r != nil {
				log.Printf("PANIC in task for data_file_id=%d: %v", id, r)
				result = fmt.Sprintf("panic: %v", r)
				if err := s.updateDataFileSummaryStatus(taskCtx, id, "Rejected"); err != nil {
					log.Printf("Failed to update DataFileSummary status for data_file_id=%d during worker panic: %v", id, err)
				}
			}
		}()

		log.Printf("Received parse task for data_file_id=%d", id)

		if err := s.processTask(taskCtx, id); err != nil {
			log.Printf("Task failed for data_file_id=%d: %v", id, err)
			return fmt.Sprintf("error: %v", err)
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

func (s *Server) updateDataFileSummaryStatus(parentCtx context.Context, dataFileID int32, status string) error {
	statusCtx, cancel := context.WithTimeout(context.WithoutCancel(parentCtx), statusUpdateTimeout)
	defer cancel()

	return db.UpdateDataFileSummaryStatus(statusCtx, s.dbPool, dataFileID, status)
}

// processTask handles a single parse task end-to-end:
// DB lookup → S3 download → decode → pipeline → status update.
func (s *Server) processTask(taskCtx context.Context, dataFileID int32) error {
	// 1. Look up datafile metadata from the database.
	df, err := db.GetDataFile(taskCtx, s.dbPool, dataFileID)
	if err != nil {
		return fmt.Errorf("failed to get datafile: %w", err)
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
		if updateErr := s.updateDataFileSummaryStatus(taskCtx, dataFileID, "Rejected"); updateErr != nil {
			log.Printf("Failed to update DataFileSummary status for data_file_id=%d: %v", dataFileID, updateErr)
		}
		return fmt.Errorf("pipeline processing failed: %w", err)
	}

	// 6. Log results.
	log.Printf("data_file_id=%d processed in %s", dataFileID, result.Duration)
	for table, count := range result.RecordCounts {
		log.Printf("  %s: %d records", table, count)
	}

	return nil
}

// sectionNumber maps a DataFile section name to the section number
// used by the pipeline and file spec registry.
func sectionNumber(section string) int {
	switch section {
	case "Active Case Data":
		return 1
	case "Closed Case Data":
		return 2
	case "Aggregate Data":
		return 3
	case "Stratum Data":
		return 4
	default:
		return 0
	}
}
