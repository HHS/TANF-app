package pipeline

import (
	"context"
	"errors"
	"fmt"
	"log"
	"time"

	"go-parser/internal/config"
	"go-parser/internal/decoder"
	"go-parser/internal/parser"
	"go-parser/internal/storage/writer"
	"go-parser/internal/validation"
)

// errMultipleHeaders is a sentinel error returned when a second HEADER record
// is detected during row iteration.
var errMultipleHeaders = errors.New("Multiple headers found.")

// Pipeline orchestrates the full file parsing process.
// The pipeline is agnostic to where input comes from and where output goes —
// the caller provides a Decoder and a Sink.
type Pipeline struct {
	sink       writer.Sink
	registry   *config.Registry
	validators *validation.ValidatorRegistry
	config     PipelineConfig
}

// DataFileContext contains the metadata for a processing run, combining
// pipeline routing info with DataFile submission metadata used for header
// cross-validation.
type DataFileContext struct {
	Program       string // Program type matching DB values ("TAN", "SSP", "TRIBAL", "FRA")
	Section       int
	DatafileID    int32
	FiscalYear    int    // Fiscal year from the DataFile (e.g., 2021)
	FiscalQuarter string // Fiscal quarter from the DataFile ("Q1", "Q2", "Q3", "Q4")
	SectionName   string // Submission section ("Active Case Data", "Closed Case Data", etc.)
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
func (p *Pipeline) Process(ctx context.Context, dec decoder.Decoder, dfCtx DataFileContext) (*ParsingResult, error) {
	// Step 1: Get the file specification
	spec := p.registry.GetFileSpec(dfCtx.Program, dfCtx.Section)
	if spec == nil {
		return nil, fmt.Errorf("no file spec for %s section %d", dfCtx.Program, dfCtx.Section)
	}

	log.Printf("Processing %s Section %d", dfCtx.Program, dfCtx.Section)
	log.Printf("Format: %s, KeyFields: %v, BatchSize: %d",
		spec.Format, spec.Accumulator.HasKeyFields(), spec.Accumulator.EffectiveBatchSize())

	// Start timing for performance measurement
	startTime := time.Now()

	// Step 2: Create router/initialize object pools
	// TODO: It feels wrong that we have to initialize the object pools on the schemas in NewRouter.
	router := writer.NewRouter(p.sink, dfCtx.DatafileID, spec, p.registry, writer.RouterConfig{
		PoolPrewarmSize:     p.config.PoolPrewarmSize,
		FlushThreshold:      p.config.FlushThreshold,
		ErrorFlushThreshold: p.config.ErrorFlushThreshold,
		IncludeSchemas:      p.config.IncludeSchemas,
		IncludeRecords:      p.config.IncludeRecords,
		IncludeErrors:       p.config.IncludeErrors,
		TablePrefix:         p.config.TablePrefix,
	})
	router.Start(ctx)

	// Step 3: Read and parse header (for positional files)
	headerRow, err := dec.ReadFirst()
	if err != nil {
		return nil, fmt.Errorf("failed to read header: %w", err)
	}

	headerSchema := p.registry.GetSchema(parser.HeaderSchemaPath)
	parseCtx, err := parser.ParseHeader(headerRow, headerSchema)
	if err != nil {
		return handleHeaderParseInvalid(err, ctx, dfCtx, router, startTime)
	}

	// steap 3a: Create new validation orchestrator
	validationOrchestrator := validation.NewValidationOrchestrator(p.validators, p.config.ShortCircuit)

	// Step 3b: Validate header (skip for FRA/columnar files where parseCtx is nil)
	if parseCtx != nil {
		parseCtx.DatafileID = dfCtx.DatafileID
		log.Printf("Header: Year=%d, Quarter=%s, Encrypted=%v",
			parseCtx.Year, parseCtx.Quarter, parseCtx.IsEncrypted)
		log.Printf("Header fields: %v", parseCtx.Header.Fields)

		valDfCtx := &validation.DataFileContext{
			FiscalYear:    dfCtx.FiscalYear,
			FiscalQuarter: dfCtx.FiscalQuarter,
			SectionName:   dfCtx.SectionName,
			Program:       dfCtx.Program,
		}
		headerResult := validationOrchestrator.ValidateHeader(parseCtx.Header, valDfCtx)
		if headerResult.HasBlockingErrors() {
			return handleHeaderValidationFail(headerResult, ctx, dfCtx, parseCtx, valDfCtx, router, startTime)
		}
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

	// Step 6: Create pipeline worker pool (workers parse, validate, and route)
	filespecKey := fmt.Sprintf("%s:%d", dfCtx.Program, dfCtx.Section)
	workers := NewWorkerPool(parsingOrchestrator, validationOrchestrator, filespecKey, router, dfCtx.DatafileID, WorkerPoolConfig{
		NumWorkers:     p.config.NumWorkers,
		WorkBufferSize: p.config.WorkBufferSize,
	})
	workers.Start(ctx)

	// Step 7: Process rows through the accumulator
	// TODO: I feel like accumulateBatches can live as a receiver on the accumulator instead a standalone function.
	acc := parser.NewAccumulator(spec, detector)
	err = accumulateBatches(dec, acc, workers)

	// Step 8: Wait for everything to complete
	workers.CloseInputs()
	workers.Wait()

	if err != nil {
		if errors.Is(err, errMultipleHeaders) {
			return p.handleMultipleHeaders(ctx, dfCtx, router, startTime)
		}
		return nil, err
	}

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

// renderHeaderErrorMessage renders a validation result's message template
// with context from the header record. This is similar to writer.renderErrorMessage
// but adds DataFileContext and Values for header cross-validation messages.
func renderHeaderErrorMessage(vr *validation.ValidationResult, header *parser.ParsedRecord, dfCtx *validation.DataFileContext) string {
	if vr.Validator == nil || vr.Validator.Message == nil {
		return vr.ValidatorID + " validation failed"
	}

	ctx := make(map[string]any, 10)
	ctx["RecordType"] = header.Schema.RecordType
	ctx["LineNumber"] = header.LineNumber
	ctx["RecordLength"] = header.GetDecodedSize()

	// Field-specific context
	if vr.FieldName != "" {
		ctx["Value"] = header.Get(vr.FieldName)
		if fd := header.Schema.GetSegmentField(0, vr.FieldName); fd != nil {
			ctx["Item"] = fd.Item
			ctx["FriendlyName"] = fd.FriendlyName
		}
	}

	// Validator params
	if vr.Validator.Params != nil {
		ctx["Params"] = vr.Validator.Params
	}

	// DataFileContext for cross-validation message templates
	ctx["DataFileContext"] = dfCtx

	// Involved fields
	if vr.Validator.Fields != nil {
		ctx["Fields"] = vr.Validator.Fields
		// Build Values map from involved fields
		values := make(map[string]any, len(vr.Validator.Fields))
		for _, f := range vr.Validator.Fields {
			values[f] = header.Get(f)
		}
		ctx["Values"] = values
	}

	return vr.Message(ctx)
}

// Handle creating multiple headers error and rolling back serialized data
func (p *Pipeline) handleMultipleHeaders(ctx context.Context, dfCtx DataFileContext, router *writer.Router, startTime time.Time) (*ParsingResult, error) {
	// Multiple headers detected: stop writers, rollback all records/errors
	// already written, then write a single PRE_CHECK error directly via sink.
	if stopErr := router.Stop(); stopErr != nil {
		log.Printf("failed to stop router: %v", stopErr)
	}
	if rollbackErr := p.sink.RollbackDatafile(ctx, dfCtx.DatafileID, router.TableNames(), router.ErrorTableName()); rollbackErr != nil {
		log.Printf("failed to rollback datafile records: %v", rollbackErr)
	}

	log.Printf("Header validation failed: Multiple headers found.")
	headerErr := writer.SerializeHeaderError(
		"Multiple headers found.",
		validation.ErrorTypePreCheck,
		dfCtx.DatafileID,
	)
	if _, flushErr := p.sink.Flush(ctx, router.ErrorTableName(), writer.ParserErrorColumns(), [][]any{headerErr}); flushErr != nil {
		log.Printf("failed to write multiple headers error: %v", flushErr)
	}
	return &ParsingResult{
		RecordCounts: map[string]int64{"parser_error": 1},
		ErrorCount:   1,
		Duration:     time.Since(startTime),
	}, nil
}

// Handle creating HEADER errors and failing pipeline
func handleHeaderValidationFail(headerResult *validation.RecordValidationResult, ctx context.Context, dfCtx DataFileContext, parseCtx *parser.ParseContext, valDfCtx *validation.DataFileContext, router *writer.Router, startTime time.Time) (*ParsingResult, error) {
	allErrors := headerResult.AllErrors()
	log.Printf("Header validation failed with %d error(s):", len(allErrors))
	for _, vr := range allErrors {
		msg := renderHeaderErrorMessage(vr, parseCtx.Header, valDfCtx)
		log.Printf("  [%s] %s", vr.ErrorType, msg)
		row := writer.SerializeHeaderError(msg, vr.ErrorType, dfCtx.DatafileID)
		if routeErr := router.RouteErrorRow(ctx, row); routeErr != nil {
			log.Printf("failed to write header error: %v", routeErr)
		}
	}
	if stopErr := router.Stop(); stopErr != nil {
		log.Printf("failed to stop router: %v", stopErr)
	}
	return &ParsingResult{
		RecordCounts: map[string]int64{"parser_error": int64(len(allErrors))},
		ErrorCount:   int64(len(allErrors)),
		Duration:     time.Since(startTime),
	}, nil
}

// When HEADER parsing fails, generate Error and fail pipeline
func handleHeaderParseInvalid(err error, ctx context.Context, dfCtx DataFileContext, router *writer.Router, startTime time.Time) (*ParsingResult, error) {
	// First line is not a HEADER record or other error — generate a PRE_CHECK error and stop
	log.Printf("Header validation failed: %s.", err.Error())
	headerErr := writer.SerializeHeaderError(
		err.Error(),
		validation.ErrorTypePreCheck,
		dfCtx.DatafileID,
	)
	if routeErr := router.RouteErrorRow(ctx, headerErr); routeErr != nil {
		log.Printf("failed to write header error: %v", routeErr)
	}
	if stopErr := router.Stop(); stopErr != nil {
		log.Printf("failed to stop router: %v", stopErr)
	}
	return &ParsingResult{
		RecordCounts: map[string]int64{"parser_error": 1},
		ErrorCount:   1,
		Duration:     time.Since(startTime),
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

		if !isAccumulated && sch != nil {
			if row.RecordType() == "HEADER" {
				return errMultipleHeaders
			}
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
