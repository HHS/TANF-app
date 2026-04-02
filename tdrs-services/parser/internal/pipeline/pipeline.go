package pipeline

import (
	"context"
	"fmt"
	"log"
	"time"

	"go-parser/internal/config"
	"go-parser/internal/decoder"
	"go-parser/internal/parser"
	"go-parser/internal/storage/writer"
	"go-parser/internal/validation"
)

// Pipeline orchestrates the full file parsing process.
// The pipeline is agnostic to where input comes from and where output goes —
// the caller provides a Decoder and a Sink.
type Pipeline struct {
	sink       writer.Sink
	registry   *config.Registry
	validators *validation.ValidatorRegistry
	config     PipelineConfig
}

// ProcessParams contains the metadata for a processing run.
type ProcessParams struct {
	Program    string
	Section    int
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

// NewPipeline creates a Pipeline with the given configuration.
// The sink determines where records/errors are written (database, files, etc).
func NewPipeline(sink writer.Sink, reg *config.Registry, validators *validation.ValidatorRegistry, config PipelineConfig) *Pipeline {
	return &Pipeline{
		sink:       sink,
		registry:   reg,
		validators: validators,
		config:     config,
	}
}

// Process parses data from the decoder and writes records via the sink.
// The caller is responsible for creating and closing the decoder.
func (p *Pipeline) Process(ctx context.Context, dec decoder.Decoder, params ProcessParams) (*ParsingResult, error) {
	// Step 1: Get the file specification
	spec := p.registry.GetFileSpec(params.Program, params.Section)
	if spec == nil {
		return nil, fmt.Errorf("no file spec for %s section %d", params.Program, params.Section)
	}

	log.Printf("Processing %s Section %d", params.Program, params.Section)
	log.Printf("Format: %s, KeyFields: %v, BatchSize: %d",
		spec.Format, spec.Accumulator.HasKeyFields(), spec.Accumulator.EffectiveBatchSize())

	// Start timing for performance measurement
	startTime := time.Now()

	// Step 2: Create router/initialize object pools
	// TODO: It feels wrong that we have to initialize the object pools on the schemas in NewRouter.
	router := writer.NewRouter(p.sink, params.DatafileID, spec, p.registry, writer.RouterConfig{
		PoolPrewarmSize:     p.config.PoolPrewarmSize,
		FlushThreshold:      p.config.FlushThreshold,
		ErrorFlushThreshold: p.config.ErrorFlushThreshold,
		IncludeSchemas:      p.config.IncludeSchemas,
		IncludeRecords:      p.config.IncludeRecords,
		IncludeErrors:       p.config.IncludeErrors,
	})
	router.Start(ctx)

	// Step 3: Read and parse header (for positional files)
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

	// Step 4: Create record type detector
	detector := decoder.NewRecordTypeDetector(spec, p.registry)

	// Step 4b: Sort the file if presort is enabled
	if spec.Accumulator.Presort && spec.Accumulator.HasKeyFields() {
		if err := dec.Sort(detector, decoder.NewKeyExtractor(spec), spec.Accumulator.GroupedSchemas); err != nil {
			return nil, fmt.Errorf("presort failed: %w", err)
		}
	}

	// Step 5: Create parsing orchestrator
	parsingOrchestrator := parser.NewParsingOrchestrator(spec.Format, parseCtx)

	// Step 6: Create validation orchestrator
	filespecKey := fmt.Sprintf("%s:%d", params.Program, params.Section)
	validationOrchestrator := validation.NewValidationOrchestrator(p.validators, p.config.ShortCircuit)

	// Step 7: Create pipeline worker pool (workers parse, validate, and route)
	workers := NewWorkerPool(parsingOrchestrator, validationOrchestrator, filespecKey, router, params.DatafileID, WorkerPoolConfig{
		NumWorkers:     p.config.NumWorkers,
		WorkBufferSize: p.config.WorkBufferSize,
	})
	workers.Start(ctx)

	// Step 8: Process rows through the accumulator
	// TODO: I feel like accumulateBatches can live as a receiver on the accumulator instead a standalone function.
	acc := parser.NewAccumulator(spec, detector)
	err = accumulateBatches(dec, acc, workers)
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

// accumulateBatches processes rows in file order.
func accumulateBatches(
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
