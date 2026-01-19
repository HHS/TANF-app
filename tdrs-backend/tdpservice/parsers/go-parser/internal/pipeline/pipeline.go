package pipeline

import (
	"context"
	"fmt"
	"log"
	"os"
	"sync"
	"time"

	"github.com/jackc/pgx/v5/pgxpool"

	"go-parser/internal/decoder"
	"go-parser/internal/filespec"
	"go-parser/internal/parser"
	"go-parser/internal/registry"
	"go-parser/internal/writer"
)

// Pipeline orchestrates the full file parsing process.
type Pipeline struct {
	pool     *pgxpool.Pool
	registry *registry.Registry
	config   PipelineConfig
}

// ProcessParams contains the inputs for processing a file.
type ProcessParams struct {
	Program    string
	Section    int
	FilePath   string
	DatafileID int32
}

// ProcessResult contains statistics from the processing run.
type ProcessResult struct {
	RecordCounts map[string]int64
	ErrorCount   int64
	Duration     time.Duration
}

// New creates a Pipeline with the given configuration.
func NewPipline(pool *pgxpool.Pool, reg *registry.Registry, config PipelineConfig) *Pipeline {
	return &Pipeline{
		pool:     pool,
		registry: reg,
		config:   config,
	}
}

// ProcessFile parses a file and writes records to the database.
// This is the main entry point for file processing.
func (p *Pipeline) ProcessFile(ctx context.Context, params ProcessParams) (*ProcessResult, error) {
	// Step 1: Get the file specification
	spec := p.registry.GetFileSpec(params.Program, params.Section)
	if spec == nil {
		return nil, fmt.Errorf("no file spec for %s section %d", params.Program, params.Section)
	}

	log.Printf("Processing %s Section %d file: %s", params.Program, params.Section, params.FilePath)
	log.Printf("Format: %s, KeyFields: %v, BatchSize: %d",
		spec.Format, spec.Accumulator.HasKeyFields(), spec.Accumulator.BatchSize)

	// Step 2: Open the file and create decoder
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
	router := writer.NewRouter(p.pool, params.DatafileID, spec, p.registry, p.config.PoolPrewarmSize)
	router.Start(ctx)

	// Step 4: Read and parse header (for positional files)
	headerRow, err := dec.ReadFirst()
	if err != nil {
		return nil, fmt.Errorf("failed to read header: %w", err)
	}

	headerSchema := p.registry.GetSchema(parser.HeaderSchemaPath)
	parseCtx, err := parser.ParseHeader(headerRow, headerSchema)
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

	// Step 6: Create parser worker pool
	parsers := parser.NewParserPool(spec.Format, p.config.toWorkerConfig(), parseCtx)
	parsers.Start(ctx)

	// Step 7: Start result collector with parallel dispatchers
	var collectorErr error
	var wg sync.WaitGroup
	wg.Add(1)
	go func() {
		defer wg.Done()
		collectorErr = routeResults(ctx, parsers, router, p.config.NumRouters)
	}()

	// Step 8: Process rows through the accumulator
	err = processRows(dec, spec, detector, parsers)
	if err != nil {
		parsers.CloseInputs()
		parsers.Wait()
		return nil, err
	}

	// Step 9: Wait for everything to complete
	parsers.CloseInputs()
	parsers.Wait()
	wg.Wait()

	if collectorErr != nil {
		return nil, collectorErr
	}

	// Calculate duration
	duration := time.Since(startTime)
	log.Printf("Time to parse: %s", duration)

	// Collect stats from router
	recordCounts, errorCount := router.Stats()

	return &ProcessResult{
		RecordCounts: recordCounts,
		ErrorCount:   errorCount,
		Duration:     duration,
	}, nil
}

// processRows uses the Accumulator to process all rows.
// The Accumulator handles all four modes (keyed, batched, both, neither)
// based on the AccumulatorConfig in the FileSpec.
func processRows(
	dec decoder.Decoder,
	spec *filespec.FileSpec,
	detector *parser.RecordTypeDetector,
	pool *parser.ParserPool,
) error {
	acc := parser.NewAccumulator(spec, detector)

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
			pool.Submit(batch)
		}
	}

	// Dispatch all remaining batches (for keyed modes, this is where groups are emitted)
	for _, batch := range acc.Drain() {
		pool.Submit(batch)
	}

	return nil
}
