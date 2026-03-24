package pipeline

import (
	"context"
	"fmt"
	"log"
	"time"

	"github.com/jackc/pgx/v5/pgxpool"

	"go-parser/internal/config"
	"go-parser/internal/decoder"
	"go-parser/internal/parser"
	"go-parser/internal/storage"
	"go-parser/internal/storage/reader"
	"go-parser/internal/storage/writer"
	"go-parser/internal/validation"
)

// Pipeline orchestrates the full file parsing process.
type Pipeline struct {
	dbPool     *pgxpool.Pool
	registry   *config.Registry
	validators *validation.ValidatorRegistry
	config     PipelineConfig
	s3Storage  *storage.S3Storage // nil when reader source is "local"
}

// DataFileParams contains the inputs for processing a file.
type DataFileParams struct {
	Program    string
	Section    int
	FilePath   string // Used when source is "local"
	ObjectKey  string // Used when source is "s3"
	DatafileID int32
}

// ParsingResult contains statistics from the processing run.
type ParsingResult struct {
	RecordCounts map[string]int64
	ErrorCount   int64
	ErrorStats   *ErrorStats // Validation error counts by category
	BatchCount   int64       // Number of batches processed
	GroupCount   int64       // Number of groups processed
	Duration     time.Duration
}

// NewPipline creates a Pipeline with the given configuration.
func NewPipline(dbPool *pgxpool.Pool, reg *config.Registry, validators *validation.ValidatorRegistry, config PipelineConfig, s3Storage *storage.S3Storage) *Pipeline {
	return &Pipeline{
		dbPool:     dbPool,
		registry:   reg,
		validators: validators,
		config:     config,
		s3Storage:  s3Storage,
	}
}

// ProcessFile parses a file and writes records to the database.
// This is the main entry point for file processing.
func (p *Pipeline) ProcessFile(ctx context.Context, params DataFileParams) (*ParsingResult, error) {
	// Step 1: Get the file specification
	spec := p.registry.GetFileSpec(params.Program, params.Section)
	if spec == nil {
		return nil, fmt.Errorf("no file spec for %s section %d", params.Program, params.Section)
	}

	log.Printf("Processing %s Section %d file: %s", params.Program, params.Section, params.FilePath)
	log.Printf("Format: %s, KeyFields: %v, BatchSize: %d",
		spec.Format, spec.Accumulator.HasKeyFields(), spec.Accumulator.EffectiveBatchSize())

	// Step 2: Acquire file via configured source
	var source reader.FileSource
	switch p.config.ReaderSource {
	case "s3":
		source = reader.NewS3Source(p.s3Storage, p.config.S3.Bucket, params.ObjectKey)
	default:
		source = reader.NewLocalSource(params.FilePath)
	}
	file, err := source.Open(ctx)
	if err != nil {
		return nil, fmt.Errorf("failed to acquire file: %w", err)
	}
	defer file.Close()
	defer source.Cleanup()

	dec, err := CreateDecoder(file, spec)
	if err != nil {
		return nil, fmt.Errorf("failed to create decoder: %w", err)
	}
	defer dec.Close()

	// Start timing for performance measurement
	startTime := time.Now()

	// Step 3: Create database router/initialize object pools
	// TODO: I hate that we have to initialize the object pools on the schemas in NewRouter.
	router := writer.NewRouter(p.dbPool, params.DatafileID, spec, p.registry, writer.RouterConfig{
		PoolPrewarmSize:     p.config.PoolPrewarmSize,
		FlushThreshold:      p.config.FlushThreshold,
		ErrorFlushThreshold: p.config.ErrorFlushThreshold,
	})
	router.Start(ctx)

	// Step 4: Read and parse header (for positional files)
	// TODO: we will need to do header validation here
	headerRow, err := dec.ReadFirst()
	if err != nil {
		return nil, fmt.Errorf("failed to read header: %w", err)
	}

	headerSchema := p.registry.GetSchema(parser.HeaderSchemaPath)
	parseCtx, err := parser.ParseHeader(headerRow, headerSchema)
	parseCtx.DatafileID = params.DatafileID
	if err != nil {
		return nil, fmt.Errorf("failed to parse header: %w", err)
	}

	if parseCtx != nil {
		log.Printf("Header: Year=%d, Quarter=%s, Encrypted=%v",
			parseCtx.Year, parseCtx.Quarter, parseCtx.IsEncrypted)
		log.Printf("Header fields: %v", parseCtx.Header.Fields)
	}

	// Step 5: Create record type detector
	detector := decoder.NewRecordTypeDetector(spec, p.registry)

	// Step 5b: Sort the file if presort is enabled
	if spec.Accumulator.Presort && spec.Accumulator.HasKeyFields() {
		if err := dec.Sort(detector, decoder.NewKeyExtractor(spec), spec.Accumulator.GroupedSchemas); err != nil {
			return nil, fmt.Errorf("presort failed: %w", err)
		}
	}

	// Step 6: Create parsing orchestrator
	parsingOrchestrator := parser.NewParsingOrchestrator(spec.Format, parseCtx)

	// Step 7: Create validation orchestrator
	filespecKey := fmt.Sprintf("%s:%d", params.Program, params.Section)
	validationOrchestrator := validation.NewValidationOrchestrator(p.validators, p.config.ShortCircuit)

	// Step 8: Create pipeline worker pool (workers parse, validate, and route)
	workers := NewWorkerPool(parsingOrchestrator, validationOrchestrator, filespecKey, router, params.DatafileID, WorkerPoolConfig{
		NumWorkers:     p.config.NumWorkers,
		WorkBufferSize: p.config.WorkBufferSize,
	})
	workers.Start(ctx)

	// Step 10: Process rows through the accumulator
	// TODO: I feel like step 8 and this step should be apart of the worker pool
	acc := parser.NewAccumulator(spec, detector)
	err = processRowsStreaming(dec, acc, workers)
	if err != nil {
		workers.CloseInputs()
		workers.Wait()
		return nil, err
	}

	// Step 9: Wait for everything to complete
	workers.CloseInputs()
	workers.Wait()

	if err := workers.Err(); err != nil {
		return nil, err
	}

	// Flush remaining rows in all writers
	if err := router.Stop(); err != nil {
		return nil, err
	}

	// Calculate duration
	duration := time.Since(startTime)
	log.Printf("Time to parse: %s", duration)

	// Collect stats
	routeStats := workers.AggregateStats()
	recordCounts, errorCount := router.Stats()
	recordCounts["parser_error"] = errorCount

	log.Printf("Validation errors: RecordPreCheck=%d, FieldValue=%d, ValueConsistency=%d, CaseConsistency=%d, Total=%d",
		routeStats.RecordPreCheck, routeStats.FieldValue, routeStats.ValueConsistency, routeStats.CaseConsistency, routeStats.Total())
	log.Printf("Batches: %d, Groups: %d", routeStats.BatchCount, routeStats.GroupCount)

	return &ParsingResult{
		RecordCounts: recordCounts,
		ErrorCount:   errorCount,
		ErrorStats:   &routeStats.ErrorStats,
		BatchCount:   routeStats.BatchCount,
		GroupCount:   routeStats.GroupCount,
		Duration:     duration,
	}, nil
}

// processRowsStreaming processes rows in file order.
func processRowsStreaming(
	dec decoder.Decoder,
	acc *parser.Accumulator,
	workers *WorkerPool,
) error {
	for row, err := range dec.Rows() {
		if err != nil {
			return err
		}

		batch, sch, isAccumulated, err := acc.Add(row)
		if err != nil {
			log.Printf("Line %d: %v", row.LineNum(), err)
			continue
		}

		// Non-accumulated rows (HEADER, TRAILER) could be processed here
		if !isAccumulated && sch != nil {
			log.Printf("Line %d: %s (not accumulated)", row.LineNum(), sch.RecordType)
		}

		// For non-keyed modes, batches may be returned during iteration
		if batch != nil {
			workers.Submit(batch)
		}
	}

	// Dispatch all remaining batches (for keyed modes, this is where groups are emitted)
	for _, batch := range acc.Drain() {
		workers.Submit(batch)
	}

	return nil
}
