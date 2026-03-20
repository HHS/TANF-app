package pipeline

import (
	"context"
	"errors"
	"log"
	"sync"
	"sync/atomic"

	"github.com/jackc/pgx/v5/pgtype"

	"go-parser/internal/parser"
	"go-parser/internal/validation"
	"go-parser/internal/writer"
	"go-parser/internal/writer/convert"
)

// ErrorStats tracks validation error counts by scope and type.
type ErrorStats struct {
	RecordPreCheck   int64 // Blocking record errors
	FieldValue       int64 // Field validation errors
	ValueConsistency int64 // Non-blocking record/group consistency errors
	CaseConsistency  int64 // Blocking group errors
}

// Total returns the total number of errors across all scopes.
func (s *ErrorStats) Total() int64 {
	return s.RecordPreCheck + s.FieldValue + s.ValueConsistency + s.CaseConsistency
}

// RouteStats holds batch/group counts collected during result routing.
type RouteStats struct {
	ErrorStats
	BatchCount int64
	GroupCount int64
}

// routeResults receives parsed batches from the parser.pool, validates them, and routes them to database writers.
// Multiple router goroutines compete on the Results channel for parallel processing.
// Returns route stats (including error counts) and any processing errors.
func routeResults(
	ctx context.Context,
	pool *parser.ParserPool,
	router *writer.Router,
	orchestrator *validation.Orchestrator,
	filespecKey string,
	numRouters int,
	datafileID int32,
) (*RouteStats, error) {
	var wg sync.WaitGroup
	errChan := make(chan error, numRouters)

	// Atomic counters for error stats (safe for concurrent access)
	var recordPreCheck, fieldValue, valueConsistency, caseConsistency int64

	// Atomic counters for batch/group stats
	var batchCount, groupCount int64

	// Spawn multiple routers reading from the same channel
	for range numRouters {
		wg.Add(1)
		go func() {
			defer wg.Done()
			for pb := range pool.Results() {
				atomic.AddInt64(&batchCount, 1)
				atomic.AddInt64(&groupCount, int64(len(pb.Groups)))

				// Validate the batch's groups and collect error counts
				rpc, fv, vc, cc, contexts := validateBatch(pb, orchestrator, filespecKey)
				atomic.AddInt64(&recordPreCheck, rpc)
				atomic.AddInt64(&fieldValue, fv)
				atomic.AddInt64(&valueConsistency, vc)
				atomic.AddInt64(&caseConsistency, cc)

				// Route valid records and all errors to writers
				// - Groups with CASE_CONSISTENCY errors: errors written, records rejected
				// - Records with RECORD_PRE_CHECK errors: errors written, record rejected
				// - Valid records: record and non-blocking errors written (linked via ObjectID)
				if err := routeValidatedBatch(ctx, router, contexts, datafileID); err != nil {
					log.Printf("Router: batch %d error: %v", pb.BatchID, err)
					errChan <- err
					return
				}
			}
		}()
	}

	// Wait for all routers to finish
	wg.Wait()
	close(errChan)

	// Collect any errors from routers
	var errs []error
	for err := range errChan {
		errs = append(errs, err)
	}

	// Stop writers (flushes remaining) and collect errors
	if err := router.Stop(); err != nil {
		errs = append(errs, err)
	}

	stats := &RouteStats{
		ErrorStats: ErrorStats{
			RecordPreCheck:   recordPreCheck,
			FieldValue:       fieldValue,
			ValueConsistency: valueConsistency,
			CaseConsistency:  caseConsistency,
		},
		BatchCount: batchCount,
		GroupCount: groupCount,
	}

	if len(errs) > 0 {
		return stats, errors.Join(errs...)
	}
	return stats, nil
}

// GroupValidationContext holds the validation result and parsed group together.
type GroupValidationContext struct {
	Group  *parser.ParsedGroup
	Result *validation.GroupValidationResult
}

// validateBatch validates all groups in a parsed batch and returns validation contexts.
// Returns the count of errors by error type (recordPreCheck, fieldValue, valueConsistency, caseConsistency).
func validateBatch(pb *parser.ParsedBatch, orchestrator *validation.Orchestrator, filespecKey string) (recordPreCheck, fieldValue, valueConsistency, caseConsistency int64, contexts []*GroupValidationContext) {
	contexts = make([]*GroupValidationContext, 0, len(pb.Groups))

	for _, group := range pb.Groups {
		// Run validation
		result := orchestrator.ValidateGroup(group, filespecKey)

		// Store the context for filtering during routing
		contexts = append(contexts, &GroupValidationContext{
			Group:  group,
			Result: result,
		})

		// Count group errors by error type
		for _, err := range result.GroupErrors {
			switch err.ErrorType {
			case validation.ErrorTypeCaseConsistency:
				caseConsistency++
			case validation.ErrorTypeValueConsistency:
				valueConsistency++
			}
		}

		// Count record-level errors by error type
		for _, recResult := range result.RecordResults {
			for _, err := range recResult.RecordErrors {
				switch err.ErrorType {
				case validation.ErrorTypeRecordPreCheck:
					recordPreCheck++
				case validation.ErrorTypeValueConsistency:
					valueConsistency++
				case validation.ErrorTypeCaseConsistency:
					caseConsistency++
				}
			}
			for range recResult.FieldErrors {
				fieldValue++
			}
		}
	}
	return
}

// routeValidatedBatch routes valid records and all errors to the database.
// Groups with blocking errors (CASE_CONSISTENCY) have errors written but records rejected.
// Records with blocking errors (RECORD_PRE_CHECK) have errors written but record rejected.
// Valid records are written with their non-blocking errors linked via ObjectID.
//
// Error rows are batched per group and sent in a single RouteErrorRows call to reduce
// channel send overhead (250K errors = 250K channel sends without batching).
func routeValidatedBatch(ctx context.Context, router *writer.Router, contexts []*GroupValidationContext, datafileID int32) error {
	// Reusable error row buffer across groups within this batch.
	// Avoids repeated allocation — slice is reset (not reallocated) per group.
	var errorRows [][]any

	for _, gctx := range contexts {
		// Reset buffer for this group (reuse backing array)
		errorRows = errorRows[:0]

		// Collect group-level error rows (use first record for context)
		if len(gctx.Result.GroupErrors) > 0 && len(gctx.Group.Records) > 0 {
			firstRec := gctx.Group.Records[0]
			for _, groupErr := range gctx.Result.GroupErrors {
				errorRows = append(errorRows, convert.ConvertError(groupErr, firstRec, nil, datafileID, nil))
			}
		}

		// Handle blocked groups: convert all errors, release records, skip record writing
		if gctx.Result.HasBlockingGroupErrors() {
			log.Printf("Skipping group %s: blocking group validation failed", gctx.Group.Key)
			for i, recResult := range gctx.Result.RecordResults {
				record := gctx.Group.Records[i]
				appendRecordErrors(&errorRows, recResult, record, nil, datafileID, nil)
				record.Schema.ReleaseRecord(record)
			}
			if err := router.RouteErrorRows(ctx, errorRows); err != nil {
				return err
			}
			continue
		}

		// Process each record in the group
		for i, recResult := range gctx.Result.RecordResults {
			record := gctx.Group.Records[i]

			if recResult.HasBlockingErrors() {
				log.Printf("Skipping record (line %d, type %s): blocking record validation failed",
					record.LineNumber, record.Schema.RecordType)
				appendRecordErrors(&errorRows, recResult, record, nil, datafileID, nil)
				record.Schema.ReleaseRecord(record)
				continue
			}

			// Record will be written - check if it has a writer
			if !router.HasWriter(record.Schema.Path) {
				record.Schema.ReleaseRecord(record)
				continue
			}

			// Convert record to get UUID, then convert errors with UUID linking
			rows, recordUUID, err := router.ConvertRecord(record)
			if err != nil {
				record.Schema.ReleaseRecord(record)
				return err
			}

			// Get content type ID for error linking (record will be written)
			contentTypeID := router.GetContentTypeID(record.Schema.Path)

			// Convert non-blocking errors with ObjectID linking (while record still available)
			appendRecordErrors(&errorRows, recResult, record, recordUUID, datafileID, contentTypeID)

			// Capture schema path before releasing record
			schemaPath := record.Schema.Path

			// Release record back to pool - no longer needed after conversion
			record.Schema.ReleaseRecord(record)

			// Send converted record rows to writer
			if err := router.SendRecordRowsByPath(ctx, schemaPath, rows); err != nil {
				return err
			}
		}

		// Flush all error rows for this group in one batched send
		if err := router.RouteErrorRows(ctx, errorRows); err != nil {
			return err
		}
	}
	return nil
}

// appendRecordErrors converts all errors for a record to rows and appends them to the buffer.
// Must be called BEFORE record is released to pool.
// recordUUID is set for records that will be written (for error linking), nil otherwise.
// contentTypeID is set only when recordUUID is set (for FIELD_VALUE and VALUE_CONSISTENCY errors).
func appendRecordErrors(
	buf *[][]any,
	recResult *validation.RecordValidationResult,
	record *parser.ParsedRecord,
	recordUUID *pgtype.UUID,
	datafileID int32,
	contentTypeID *int32,
) {
	allErrors := recResult.AllErrors()
	if len(allErrors) == 0 {
		return
	}

	for _, vr := range allErrors {
		// Only set content type ID for non-blocking errors (when record is written)
		// Per Python parser: FIELD_VALUE and VALUE_CONSISTENCY get content_type when record exists
		var ctID *int32
		if recordUUID != nil && (vr.ErrorType == validation.ErrorTypeFieldValue ||
			vr.ErrorType == validation.ErrorTypeValueConsistency) {
			ctID = contentTypeID
		}
		*buf = append(*buf, convert.ConvertError(vr, record, recordUUID, datafileID, ctID))
	}
}
