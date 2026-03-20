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

// routeResults receives validated batches from the worker pool and routes them to database writers.
// Multiple router goroutines compete on the Results channel for parallel processing.
// Routers are purely I/O — validation has already been performed by the worker pool.
func routeResults(
	ctx context.Context,
	workers *WorkerPool,
	router *writer.Router,
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
			for vb := range workers.Results() {
				atomic.AddInt64(&batchCount, 1)
				atomic.AddInt64(&groupCount, int64(len(vb.Groups)))

				// Count errors from pre-computed validation results
				rpc, fv, vc, cc := countErrors(vb)
				atomic.AddInt64(&recordPreCheck, rpc)
				atomic.AddInt64(&fieldValue, fv)
				atomic.AddInt64(&valueConsistency, vc)
				atomic.AddInt64(&caseConsistency, cc)

				// Route valid records and all errors to writers
				if err := routeValidatedBatch(ctx, router, vb.Groups, datafileID); err != nil {
					log.Printf("Router: batch %d error: %v", vb.BatchID, err)
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

// countErrors tallies validation errors from a pre-validated batch.
func countErrors(vb *ValidatedBatch) (recordPreCheck, fieldValue, valueConsistency, caseConsistency int64) {
	for _, vg := range vb.Groups {
		for _, err := range vg.Result.GroupErrors {
			switch err.ErrorType {
			case validation.ErrorTypeCaseConsistency:
				caseConsistency++
			case validation.ErrorTypeValueConsistency:
				valueConsistency++
			}
		}

		for _, recResult := range vg.Result.RecordResults {
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
func routeValidatedBatch(ctx context.Context, router *writer.Router, groups []*ValidatedGroup, datafileID int32) error {
	// Reusable error row buffer across groups within this batch.
	// Avoids repeated allocation — slice is reset (not reallocated) per group.
	var errorRows [][]any

	for _, vg := range groups {
		// Reset buffer for this group (reuse backing array)
		errorRows = errorRows[:0]

		// Collect group-level error rows (use first record for context)
		if len(vg.Result.GroupErrors) > 0 && len(vg.Group.Records) > 0 {
			firstRec := vg.Group.Records[0]
			for _, groupErr := range vg.Result.GroupErrors {
				errorRows = append(errorRows, convert.ConvertError(groupErr, firstRec, nil, datafileID, nil))
			}
		}

		// Handle blocked groups: convert all errors, release records, skip record writing
		if vg.Result.HasBlockingGroupErrors() {
			log.Printf("Skipping group %s: blocking group validation failed", vg.Group.Key)
			for i, recResult := range vg.Result.RecordResults {
				record := vg.Group.Records[i]
				appendRecordErrors(&errorRows, recResult, record, nil, datafileID, nil)
				record.Schema.ReleaseRecord(record)
			}
			if err := router.RouteErrorRows(ctx, errorRows); err != nil {
				return err
			}
			continue
		}

		// Process each record in the group
		for i, recResult := range vg.Result.RecordResults {
			record := vg.Group.Records[i]

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
