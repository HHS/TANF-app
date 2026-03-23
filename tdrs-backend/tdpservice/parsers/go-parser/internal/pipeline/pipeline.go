package pipeline

import (
	"context"
	"fmt"
	"log"
	"os"
	"sync"
	"time"

	"github.com/jackc/pgx/v5/pgxpool"

	"go-parser/internal/config"
	"go-parser/internal/config/filespec"
	"go-parser/internal/decoder"
	"go-parser/internal/parser"
	"go-parser/internal/validation"
	"go-parser/internal/writer"
)

// Pipeline orchestrates the full file parsing process.
type Pipeline struct {
	dbPool     *pgxpool.Pool
	registry   *config.Registry
	validators *validation.ValidatorRegistry
	config     PipelineConfig
}

// DataFileParams contains the inputs for processing a file.
type DataFileParams struct {
	Program    string
	Section    int
	FilePath   string
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
func NewPipline(dbPool *pgxpool.Pool, reg *config.Registry, validators *validation.ValidatorRegistry, config PipelineConfig) *Pipeline {
	return &Pipeline{
		dbPool:     dbPool,
		registry:   reg,
		validators: validators,
		config:     config,
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

	// Step 2: Open the file and create decoder
	// TODO: This needs to be abstracted/generalized for local, s3, and http
	file, err := os.Open(params.FilePath)
	if err != nil {
		return nil, fmt.Errorf("failed to open file: %w", err)
	}
	defer file.Close()

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
	detector := parser.NewRecordTypeDetector(spec, p.registry)

	// Step 6: Create parsing orchestrator
	parsingOrchestrator := parser.NewParsingOrchestrator(spec.Format, parseCtx)

	// Step 7: Create validation orchestrator
	filespecKey := fmt.Sprintf("%s:%d", params.Program, params.Section)
	validationOrchestrator := validation.NewValidationOrchestrator(p.validators)

	// Step 8: Create pipeline worker pool
	workers := NewWorkerPool(parsingOrchestrator, validationOrchestrator, filespecKey, WorkerPoolConfig{
		NumWorkers:       p.config.NumWorkers,
		WorkBufferSize:   p.config.WorkBufferSize,
		ResultBufferSize: p.config.ResultBufferSize,
	})
	workers.Start(ctx)

	// Step 9: Start result collector with parallel dispatchers
	// TODO: I hate this. I feel like it can be better.
	var collectorErr error
	var routeStats *RouteStats
	var wg sync.WaitGroup
	wg.Add(1)
	go func() {
		defer wg.Done()
		routeStats, collectorErr = routeResults(ctx, workers, router, p.config.NumRouters, params.DatafileID)
	}()

	// Step 10: Process rows through the accumulator
	// TODO: I feel like step 8 and this step should be apart of the worker pool
	err = processRows(dec, spec, detector, workers)
	if err != nil {
		workers.CloseInputs()
		workers.Wait()
		return nil, err
	}

	// Step 11: Wait for everything to complete
	workers.CloseInputs()
	workers.Wait()
	wg.Wait()

	if collectorErr != nil {
		return nil, collectorErr
	}

	// Calculate duration
	duration := time.Since(startTime)
	log.Printf("Time to parse: %s", duration)

	// Collect stats from router
	recordCounts, errorCount := router.Stats()

	// Include error count in the record counts map for consistent reporting
	recordCounts["parser_error"] = errorCount

	// Log validation error summary
	if routeStats != nil {
		log.Printf("Validation errors: RecordPreCheck=%d, FieldValue=%d, ValueConsistency=%d, CaseConsistency=%d, Total=%d",
			routeStats.RecordPreCheck, routeStats.FieldValue, routeStats.ValueConsistency, routeStats.CaseConsistency, routeStats.Total())
		log.Printf("Batches: %d, Groups: %d", routeStats.BatchCount, routeStats.GroupCount)
	}

	var errorStats *ErrorStats
	if routeStats != nil {
		errorStats = &routeStats.ErrorStats
	}

	return &ParsingResult{
		RecordCounts: recordCounts,
		ErrorCount:   errorCount,
		ErrorStats:   errorStats,
		BatchCount:   routeStats.BatchCount,
		GroupCount:   routeStats.GroupCount,
		Duration:     duration,
	}, nil
}

// processRows uses the Accumulator to process all rows.
// The Accumulator handles all four modes (keyed, batched, both, neither)
// based on the AccumulatorConfig in the FileSpec.
//
// When presort is enabled, all data rows are read into memory and stable-sorted
// by key fields before feeding to the accumulator. This guarantees records for
// the same case are adjacent, enabling streaming accumulation and in-memory
// duplicate detection regardless of input order
// TODO: I hate having different code paths. Sorted vs non sorted files should not generally change the
// functionality/code path. The sorting of the file should occur in the "reader" abstraction we create that handles
// acquiring the raw file from disk, http, s3, etc...
func processRows(
	dec decoder.Decoder,
	fileSpec *filespec.FileSpec,
	recordDetector *parser.RecordTypeDetector,
	workers *WorkerPool,
) error {
	acc := parser.NewAccumulator(fileSpec, recordDetector)

	if fileSpec.Accumulator.Presort && fileSpec.Accumulator.HasKeyFields() {
		return processRowsPresorted(dec, fileSpec, recordDetector, acc, workers)
	}

	return processRowsStreaming(dec, acc, workers)
}

// processRowsPresorted reads all rows, sorts by key, then feeds to accumulator.
func processRowsPresorted(
	dec decoder.Decoder,
	fileSpec *filespec.FileSpec,
	recordDetector *parser.RecordTypeDetector,
	acc *parser.Accumulator,
	workers *WorkerPool,
) error {
	sorter := parser.NewSorter(fileSpec, recordDetector)
	sortResult, err := sorter.Sort(dec)
	if err != nil {
		return fmt.Errorf("presort failed: %w", err)
	}

	log.Printf("Presort complete: %d data rows sorted, %d unkeyed rows",
		len(sortResult.SortedRows), len(sortResult.UnkeyedRows))

	if sortResult.Trailer != nil {
		log.Printf("Line %d: TRAILER (not accumulated)", sortResult.Trailer.LineNum())
	}

	// Feed sorted data rows to accumulator
	for _, row := range sortResult.SortedRows {
		batch, _, _, err := acc.Add(row)
		if err != nil {
			log.Printf("Line %d: %v", row.LineNum(), err)
			continue
		}
		if batch != nil {
			workers.Submit(batch)
		}
	}

	// Process unkeyed rows (malformed, unrecognized) for error reporting
	for _, row := range sortResult.UnkeyedRows {
		batch, _, _, err := acc.Add(row)
		if err != nil {
			log.Printf("Line %d: %v", row.LineNum(), err)
			continue
		}
		if batch != nil {
			workers.Submit(batch)
		}
	}

	// Drain remaining groups
	for _, batch := range acc.Drain() {
		workers.Submit(batch)
	}

	return nil
}

// processRowsStreaming processes rows in file order without sorting.
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
