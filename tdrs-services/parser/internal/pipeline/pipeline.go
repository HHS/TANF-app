package pipeline

import (
	"context"
	"errors"
	"fmt"
	"log"
	"strings"
	"time"

	"go-parser/internal/config"
	"go-parser/internal/config/filespec"
	"go-parser/internal/config/schema"
	"go-parser/internal/decoder"
	"go-parser/internal/parser"
	"go-parser/internal/sentinel"
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
	RecordCounts      map[string]int64
	DetailRecordCount int64
	ErrorCount        int64
	ErrorStats        *ErrorStats // Validation error counts by category
	BatchCount        int64       // Number of batches processed
	GroupCount        int64       // Number of groups processed
	Duration          time.Duration
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
	runCtx, cancelRun := context.WithCancel(ctx)
	defer cancelRun()

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

	valDfCtx := &validation.DataFileContext{
		FiscalYear:    dfCtx.FiscalYear,
		FiscalQuarter: dfCtx.FiscalQuarter,
		SectionName:   dfCtx.SectionName,
		Program:       dfCtx.Program,
	}

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
	router.Start(runCtx)

	// Step 2a: Create validation orchestrator shared across all pipeline paths.
	validationOrchestrator := validation.NewValidationOrchestrator(p.validators, p.config.ShortCircuit)
	var headerStats ErrorStats
	var result *ParsingResult

	// Step 3: Read first row. Positional files use it as HEADER; FRA uses it
	// for a first-data-row sanity check and then processes it normally.
	firstRow, err := dec.ReadFirst()
	if err != nil {
		err = fmt.Errorf("failed to read first row: %w", err)
		if rollbackErr := p.abortAndRollback(ctx, cancelRun, dfCtx, router); rollbackErr != nil {
			return nil, errors.Join(err, rollbackErr)
		}
		return nil, err
	}

	// TODO: We could probably abstract this branch into an interface. Helpful if we get more file types with different
	// header semantics.
	var parseCtx *parser.ParseContext
	if spec.Format == filespec.FormatColumnar {
		if dfCtx.Program == "FRA" && !isValidFRAFirstRow(firstRow) {
			return p.handleFRAFirstRowInvalid(ctx, dfCtx, router, startTime), nil
		}
	} else {
		headerSchema := p.registry.GetSchema(parser.HeaderSchemaPath)
		parseCtx, err = parser.ParseHeader(firstRow, headerSchema)
		if err != nil {
			return p.handleHeaderParseInvalid(err, ctx, dfCtx, router, validationOrchestrator, startTime)
		}
	}

	// Step 3b: Validate header (skip for FRA/columnar files where parseCtx is nil)
	if parseCtx != nil {
		parseCtx.DatafileID = dfCtx.DatafileID
		log.Printf("Header: Year=%d, Quarter=%s, Encrypted=%v",
			parseCtx.Year, parseCtx.Quarter, parseCtx.IsEncrypted)
		log.Printf("Header fields: %v", parseCtx.Header.Fields)

		headerResult := validationOrchestrator.ValidateHeader(parseCtx.Header, valDfCtx)
		headerStats, result = p.handleHeaderValidationResult(
			ctx,
			headerResult,
			dfCtx,
			parseCtx,
			valDfCtx,
			router,
			validationOrchestrator,
			startTime,
		)
		if result != nil {
			return result, nil
		}
	}

	// Step 4: Create record type detector
	detector := decoder.NewRecordTypeDetector(spec, p.registry)

	// Step 4b: Sort the file if presort is enabled
	if spec.Accumulator.Presort && spec.Accumulator.HasKeyFields() {
		if err := dec.Sort(detector, spec.Accumulator.KeyFields.OrderedFields(), spec.Accumulator.GroupedSchemas); err != nil {
			err = fmt.Errorf("presort failed: %w", err)
			if rollbackErr := p.abortAndRollback(ctx, cancelRun, dfCtx, router); rollbackErr != nil {
				return nil, errors.Join(err, rollbackErr)
			}
			return nil, err
		}
	}

	// Step 5: Create parsing orchestrator
	parsingOrchestrator := parser.NewParsingOrchestrator(spec.Format, parseCtx)
	trailerSchema := p.registry.GetSchema(parser.TrailerSchemaPath)

	// Step 6: Create pipeline worker pool (workers parse, validate, and route)
	filespecKey := fmt.Sprintf("%s:%d", dfCtx.Program, dfCtx.Section)
	workers := NewWorkerPool(parsingOrchestrator, validationOrchestrator, valDfCtx, filespecKey, router, dfCtx.DatafileID, WorkerPoolConfig{
		NumWorkers:     p.config.NumWorkers,
		WorkBufferSize: p.config.WorkBufferSize,
	})
	workers.Start(runCtx)

	// Step 7: Process rows through the accumulator
	// TODO: I feel like accumulateBatches can live as a receiver on the accumulator instead a standalone function.
	acc := parser.NewAccumulator(spec, detector)
	fileStats := validation.NewFileRecordStats(parseCtx)
	requireTrailer := spec.Format == filespec.FormatPositional
	err = accumulateBatches(runCtx, dec, acc, workers, router, dfCtx.DatafileID, trailerSchema, validationOrchestrator, valDfCtx, fileStats, requireTrailer)
	if firstRow != nil {
		fileStats.MaxLineNumber = max(fileStats.MaxLineNumber, firstRow.LineNum())
	}

	// Step 8: Wait for everything to complete
	if err != nil {
		var multipleHeaders *sentinel.MultipleHeadersError
		if errors.As(err, &multipleHeaders) {
			workers.CloseInputs()
			workers.Wait()
			return p.handleMultipleHeaders(ctx, cancelRun, dfCtx, router, multipleHeaders.RowNumber(), startTime)
		}

		cancelRun()
		workers.CloseInputs()
		workers.Wait()
		if rollbackErr := p.abortAndRollback(ctx, cancelRun, dfCtx, router); rollbackErr != nil {
			return nil, errors.Join(err, rollbackErr)
		}
		return nil, err
	}
	workers.CloseInputs()
	workers.Wait()

	if err := workers.Err(); err != nil {
		if rollbackErr := p.abortAndRollback(ctx, cancelRun, dfCtx, router); rollbackErr != nil {
			return nil, errors.Join(err, rollbackErr)
		}
		return nil, err
	}

	addedTrailerCountError, err := p.writeTrailerRecordCountError(ctx, router, dfCtx.DatafileID, fileStats)
	if err != nil {
		return nil, err
	}

	// Flush remaining rows in all writers
	if err := router.Stop(); err != nil {
		if rollbackErr := p.rollbackDatafile(ctx, dfCtx, router); rollbackErr != nil {
			return nil, errors.Join(err, rollbackErr)
		}
		return nil, err
	}

	routeStats := workers.AggregateStats()
	addErrorStats(&routeStats.ErrorStats, headerStats)
	recordCounts, errorCount := router.Stats()
	routeStats.RecordPreCheck += addedTrailerCountError
	if p.config.IncludeRecords && p.config.IncludeErrors && totalWrittenRecords(recordCounts) == 0 {
		var headerRecord *parser.ParsedRecord
		if parseCtx != nil {
			headerRecord = parseCtx.Header
		}
		addedErrorCount, err := p.writeNoRecordsCreatedError(ctx, validationOrchestrator, dfCtx.DatafileID, headerRecord, validationOrchestrator.IsValidZeroRecordSubmission(dfCtx.SectionName, fileStats), func(row []any) error {
			_, err := p.sink.Flush(ctx, router.ErrorTableName(), writer.ParserErrorColumns(), [][]any{row})
			return err
		})
		if err != nil {
			return nil, err
		}
		errorCount += addedErrorCount
		routeStats.RecordPreCheck += addedErrorCount
	}
	recordCounts["parser_error"] = errorCount

	// Calculate duration
	duration := time.Since(startTime)
	log.Printf("Time to parse: %s", duration)

	log.Printf("Validation errors: RecordPreCheck=%d, FieldValue=%d, ValueConsistency=%d, CaseConsistency=%d, Total=%d",
		routeStats.RecordPreCheck, routeStats.FieldValue, routeStats.ValueConsistency, routeStats.CaseConsistency, routeStats.Total())
	log.Printf("Batches: %d, Groups: %d", routeStats.BatchCount, routeStats.GroupCount)

	return &ParsingResult{
		RecordCounts:      recordCounts,
		DetailRecordCount: fileStats.DetailRows,
		ErrorCount:        errorCount,
		ErrorStats:        &routeStats.ErrorStats,
		BatchCount:        routeStats.BatchCount,
		GroupCount:        routeStats.GroupCount,
		Duration:          duration,
	}, nil
}

func countHeaderRecordValidationErrors(headerResult *validation.RecordValidationResult) ErrorStats {
	var stats ErrorStats
	if headerResult == nil {
		return stats
	}

	for _, vr := range headerResult.RecordErrors {
		switch vr.ErrorType {
		case validation.ErrorTypePreCheck, validation.ErrorTypeRecordPreCheck:
			stats.RecordPreCheck++
		case validation.ErrorTypeValueConsistency:
			stats.ValueConsistency++
		case validation.ErrorTypeCaseConsistency:
			stats.CaseConsistency++
		}
	}

	stats.FieldValue = int64(len(headerResult.FieldErrors))
	return stats
}

func addErrorStats(dst *ErrorStats, src ErrorStats) {
	dst.RecordPreCheck += src.RecordPreCheck
	dst.FieldValue += src.FieldValue
	dst.ValueConsistency += src.ValueConsistency
	dst.CaseConsistency += src.CaseConsistency
}

func isValidFRAFirstRow(row decoder.Row) bool {
	cr, ok := row.(*decoder.ColumnarRow)
	if !ok || cr.ColumnCount() != 2 {
		return false
	}

	for i := 0; i < cr.ColumnCount(); i++ {
		if strings.TrimSpace(fmt.Sprintf("%v", cr.Column(i))) == "" {
			return false
		}
	}

	return true
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

func totalWrittenRecords(recordCounts map[string]int64) int64 {
	var total int64
	for _, count := range recordCounts {
		total += count
	}
	return total
}

func (p *Pipeline) writeNoRecordsCreatedError(
	ctx context.Context,
	validationOrchestrator *validation.ValidationOrchestrator,
	datafileID int32,
	headerRecord *parser.ParsedRecord,
	validZeroRecordSubmission bool,
	writeRow func([]any) error,
) (int64, error) {
	if !p.config.IncludeRecords || !p.config.IncludeErrors || validZeroRecordSubmission {
		return 0, nil
	}

	noRecordsCreated := validationOrchestrator.CreateNoRecordsCreatedError()
	row := writer.SerializeParserError(
		noRecordsCreated.LineNumber,
		noRecordsCreated.Message(nil),
		noRecordsCreated.ErrorType,
		datafileID,
	)
	if err := writeRow(row); err != nil {
		return 0, err
	}

	return 1, nil
}

func (p *Pipeline) writeTrailerRecordCountError(ctx context.Context, router *writer.Router, datafileID int32, stats *validation.FileRecordStats) (int64, error) {
	if !p.config.IncludeErrors || stats == nil || stats.DetailRows != 0 || stats.TrailerCount != 1 || !stats.TrailerValid {
		return 0, nil
	}
	if int64(stats.TrailerRecordCount) == stats.DetailRows {
		return 0, nil
	}

	row := writer.SerializeParserError(
		stats.TrailerRowNumber,
		fmt.Sprintf("The number of records in the TRAILER row count: %d, does not match the number of records detected in the file: %d.", stats.TrailerRecordCount, stats.DetailRows),
		validation.ErrorTypePreCheck,
		datafileID,
	)
	if err := router.RouteErrorRow(ctx, row); err != nil {
		return 0, err
	}
	return 1, nil
}

func (p *Pipeline) abortAndRollback(ctx context.Context, cancelRun context.CancelFunc, dfCtx DataFileContext, router *writer.Router) error {
	cancelRun()
	cleanupCtx := context.WithoutCancel(ctx)

	var errs []error
	if abortErr := router.Abort(); abortErr != nil {
		errs = append(errs, fmt.Errorf("abort writers: %w", abortErr))
	}
	if rollbackErr := p.rollbackDatafile(cleanupCtx, dfCtx, router); rollbackErr != nil {
		errs = append(errs, rollbackErr)
	}
	return errors.Join(errs...)
}

func (p *Pipeline) rollbackDatafile(ctx context.Context, dfCtx DataFileContext, router *writer.Router) error {
	rollbackCtx := context.WithoutCancel(ctx)
	if rollbackErr := p.sink.RollbackDatafile(rollbackCtx, dfCtx.DatafileID, router.TableNames(), router.ErrorTableName()); rollbackErr != nil {
		return fmt.Errorf("rollback datafile %d: %w", dfCtx.DatafileID, rollbackErr)
	}
	return nil
}

// Handle creating multiple headers error and rolling back serialized data.
func (p *Pipeline) handleMultipleHeaders(ctx context.Context, cancelRun context.CancelFunc, dfCtx DataFileContext, router *writer.Router, rowNumber int, startTime time.Time) (*ParsingResult, error) {
	// Multiple headers detected: stop writers, rollback all records/errors
	// already written, then write a single PRE_CHECK error directly via sink.
	cleanupCtx := context.WithoutCancel(ctx)
	var errs []error
	if abortErr := router.Abort(); abortErr != nil {
		errs = append(errs, fmt.Errorf("abort writers: %w", abortErr))
	}
	cancelRun()
	if rollbackErr := p.rollbackDatafile(cleanupCtx, dfCtx, router); rollbackErr != nil {
		errs = append(errs, rollbackErr)
	}
	if err := errors.Join(errs...); err != nil {
		log.Printf("failed to rollback datafile records: %v", err)
		return nil, err
	}

	log.Printf("Header validation failed: Multiple headers found.")
	headerErr := writer.SerializeParserError(
		rowNumber,
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

func (p *Pipeline) handleFRAFirstRowInvalid(ctx context.Context, dfCtx DataFileContext, router *writer.Router, startTime time.Time) *ParsingResult {
	log.Printf("FRA first-row validation failed: File does not begin with FRA data.")
	parserErr := writer.SerializeParserError(
		1,
		"File does not begin with FRA data.",
		validation.ErrorTypePreCheck,
		dfCtx.DatafileID,
	)
	if routeErr := router.RouteErrorRow(ctx, parserErr); routeErr != nil {
		log.Printf("failed to write FRA first-row error: %v", routeErr)
	}
	if stopErr := router.Stop(); stopErr != nil {
		log.Printf("failed to stop router: %v", stopErr)
	}

	return &ParsingResult{
		RecordCounts: map[string]int64{"parser_error": 1},
		ErrorCount:   1,
		ErrorStats:   &ErrorStats{RecordPreCheck: 1},
		Duration:     time.Since(startTime),
	}
}

func (p *Pipeline) handleHeaderValidationResult(
	ctx context.Context,
	headerResult *validation.RecordValidationResult,
	dfCtx DataFileContext,
	parseCtx *parser.ParseContext,
	valDfCtx *validation.DataFileContext,
	router *writer.Router,
	validationOrchestrator *validation.ValidationOrchestrator,
	startTime time.Time,
) (ErrorStats, *ParsingResult) {
	if headerResult == nil || !headerResult.HasErrors() {
		return ErrorStats{}, nil
	}

	allErrors := headerResult.AllErrors()
	headerStats := countHeaderRecordValidationErrors(headerResult)

	log.Printf("Header validation produced %d error(s):", len(allErrors))
	for _, vr := range allErrors {
		msg := renderHeaderErrorMessage(vr, parseCtx.Header, valDfCtx)
		log.Printf("  [%s] %s", vr.ErrorType, msg)
		row := writer.SerializeParserError(parseCtx.Header.LineNumber, msg, vr.ErrorType, dfCtx.DatafileID)
		if routeErr := router.RouteErrorRow(ctx, row); routeErr != nil {
			log.Printf("failed to write header error: %v", routeErr)
		}
	}

	if !headerResult.HasBlockingErrors() {
		return headerStats, nil
	}

	log.Printf("Header validation failed with %d error(s); stopping pipeline.", len(allErrors))
	addedErrorCount, err := p.writeNoRecordsCreatedError(ctx, validationOrchestrator, dfCtx.DatafileID, parseCtx.Header, false, func(row []any) error {
		return router.RouteErrorRow(ctx, row)
	})
	if err != nil {
		log.Printf("failed to write no-records-created error: %v", err)
	}
	if stopErr := router.Stop(); stopErr != nil {
		log.Printf("failed to stop router: %v", stopErr)
	}
	return headerStats, &ParsingResult{
		RecordCounts: map[string]int64{"parser_error": int64(len(allErrors)) + addedErrorCount},
		ErrorCount:   int64(len(allErrors)) + addedErrorCount,
		ErrorStats:   &headerStats,
		Duration:     time.Since(startTime),
	}
}

// When HEADER parsing fails, generate Error and fail pipeline
func (p *Pipeline) handleHeaderParseInvalid(err error, ctx context.Context, dfCtx DataFileContext, router *writer.Router, validationOrchestrator *validation.ValidationOrchestrator, startTime time.Time) (*ParsingResult, error) {
	// First line is not a HEADER record or other error — generate a PRE_CHECK error and stop
	log.Printf("Header validation failed: %s.", err.Error())
	headerErr := writer.SerializeParserError(
		1,
		err.Error(),
		validation.ErrorTypePreCheck,
		dfCtx.DatafileID,
	)
	if routeErr := router.RouteErrorRow(ctx, headerErr); routeErr != nil {
		log.Printf("failed to write header error: %v", routeErr)
	}
	addedErrorCount, writeErr := p.writeNoRecordsCreatedError(ctx, validationOrchestrator, dfCtx.DatafileID, nil, false, func(row []any) error {
		return router.RouteErrorRow(ctx, row)
	})
	if writeErr != nil {
		log.Printf("failed to write no-records-created error: %v", writeErr)
	}
	if stopErr := router.Stop(); stopErr != nil {
		log.Printf("failed to stop router: %v", stopErr)
	}
	return &ParsingResult{
		RecordCounts: map[string]int64{"parser_error": 1 + addedErrorCount},
		ErrorCount:   1 + addedErrorCount,
		Duration:     time.Since(startTime),
	}, nil
}

// accumulateBatches processes rows in file order.
func accumulateBatches(
	ctx context.Context,
	dec decoder.Decoder,
	acc *parser.Accumulator,
	workers *WorkerPool,
	router *writer.Router,
	datafileID int32,
	trailerSchema *schema.CompiledSchema,
	validationOrchestrator *validation.ValidationOrchestrator,
	dfCtx *validation.DataFileContext,
	stats *validation.FileRecordStats,
	requireTrailer bool,
) error {
	if stats == nil {
		stats = &validation.FileRecordStats{}
	}
	for row, err := range dec.Rows() {
		if err != nil {
			return err
		}
		stats.MaxLineNumber = max(stats.MaxLineNumber, row.LineNum())

		batch, sch, isAccumulated, err := acc.Add(row)
		if err != nil {
			if row.RecordType() != "HEADER" && row.RecordType() != "TRAILER" {
				stats.DetailRows++
			}
			if errors.Is(err, sentinel.ErrUnknownRecordType) {
				parserErr := writer.SerializeParserError(
					row.LineNum(),
					"Unknown record type was found.",
					validation.ErrorTypeRecordPreCheck,
					datafileID,
				)
				if routeErr := router.RouteErrorRow(ctx, parserErr); routeErr != nil {
					return routeErr
				}
			}
			log.Printf("Line %d: %v", row.LineNum(), err)
			continue
		}

		if !isAccumulated && sch != nil {
			if row.RecordType() == "HEADER" {
				stats.HeaderCount++
				return sentinel.NewMultipleHeadersError(row.LineNum())
			}
			if row.RecordType() == "TRAILER" {
				result := validationOrchestrator.ValidateTrailerRow(
					row,
					trailerSchema,
					dfCtx,
					stats,
				)
				if err := routeTrailerRowValidationResult(ctx, row, router, datafileID, result); err != nil {
					return err
				}
				continue
			}
			log.Printf("Line %d: %s (not accumulated)", row.LineNum(), sch.RecordType)
		}

		if isAccumulated {
			stats.DetailRows++
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

	if requireTrailer {
		if err := validateTrailerFileContext(ctx, router, datafileID, stats); err != nil {
			return err
		}
	}

	return nil
}

func routeTrailerRowValidationResult(
	ctx context.Context,
	row decoder.Row,
	router *writer.Router,
	datafileID int32,
	result *validation.TrailerRowValidationResult,
) error {
	if result.MultipleTrailers {
		parserErr := writer.SerializeParserError(
			row.LineNum(),
			"Multiple trailers found.",
			validation.ErrorTypePreCheck,
			datafileID,
		)
		if routeErr := router.RouteErrorRow(ctx, parserErr); routeErr != nil {
			return routeErr
		}
	}

	if result.ParseError != nil {
		parserErr := writer.SerializeParserError(
			row.LineNum(),
			result.ParseError.Error(),
			validation.ErrorTypePreCheck,
			datafileID,
		)
		return router.RouteErrorRow(ctx, parserErr)
	}

	if result.Record == nil || result.ValidationResult == nil {
		return nil
	}

	for _, vr := range result.ValidationResult.AllErrors() {
		if err := router.RouteErrorRow(ctx, writer.SerializeError(vr, result.Record, nil, datafileID, nil)); err != nil {
			result.Record.Schema.ReleaseRecord(result.Record)
			return err
		}
	}

	result.Record.Schema.ReleaseRecord(result.Record)
	return nil
}

func validateTrailerFileContext(ctx context.Context, router *writer.Router, datafileID int32, stats *validation.FileRecordStats) error {
	if stats.TrailerCount == 0 {
		rowNumber := stats.MaxLineNumber
		parserErr := writer.SerializeParserError(
			rowNumber,
			"Your file does not end with a TRAILER record.",
			validation.ErrorTypePreCheck,
			datafileID,
		)
		return router.RouteErrorRow(ctx, parserErr)
	}
	if stats.TrailerCount == 1 && stats.TrailerRowNumber != stats.MaxLineNumber {
		parserErr := writer.SerializeParserError(
			stats.MaxLineNumber,
			"Your file does not end with a TRAILER record.",
			validation.ErrorTypePreCheck,
			datafileID,
		)
		return router.RouteErrorRow(ctx, parserErr)
	}
	return nil
}
