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

// routeResults receives parsed batches from the parser.pool, validates them, and routes them to database writers.
// Multiple router goroutines compete on the Results channel for parallel processing.
// Returns error stats and any processing errors.
func routeResults(
	ctx context.Context,
	pool *parser.ParserPool,
	router *writer.Router,
	orchestrator *validation.Orchestrator,
	filespecKey string,
	numRouters int,
	datafileID int32,
) (*ErrorStats, error) {
	var wg sync.WaitGroup
	errChan := make(chan error, numRouters)

	// Atomic counters for error stats (safe for concurrent access)
	var recordPreCheck, fieldValue, valueConsistency, caseConsistency int64

	// Spawn multiple routers reading from the same channel
	for range numRouters {
		wg.Add(1)
		go func() {
			defer wg.Done()
			for pb := range pool.Results() {
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

	stats := &ErrorStats{
		RecordPreCheck:   recordPreCheck,
		FieldValue:       fieldValue,
		ValueConsistency: valueConsistency,
		CaseConsistency:  caseConsistency,
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
		// Wrap the ParsedGroup to satisfy the validation interfaces
		wrappedRecords := make([]validation.Record, len(group.Records))
		for i, rec := range group.Records {
			wrappedRecords[i] = rec
		}
		wrappedGroup := validation.WrapGroup(group, wrappedRecords)

		// Run validation
		result := orchestrator.ValidateGroup(wrappedGroup, filespecKey)

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
func routeValidatedBatch(ctx context.Context, router *writer.Router, contexts []*GroupValidationContext, datafileID int32) error {
	for _, gctx := range contexts {
		// Route group-level errors (use first record for context)
		if len(gctx.Result.GroupErrors) > 0 && len(gctx.Group.Records) > 0 {
			firstRec := gctx.Group.Records[0]
			for _, groupErr := range gctx.Result.GroupErrors {
				row := convert.ConvertError(groupErr, firstRec, nil, datafileID, nil)
				if err := router.RouteErrorRow(ctx, row); err != nil {
					return err
				}
			}
		}

		// Handle blocked groups: convert all errors, release records, skip record writing
		if gctx.Result.HasBlockingGroupErrors() {
			log.Printf("Skipping group %s: blocking group validation failed", gctx.Group.Key)
			// Convert all record/field errors while records available
			for i, recResult := range gctx.Result.RecordResults {
				record := gctx.Group.Records[i]
				if err := convertAndRouteRecordErrors(ctx, router, recResult, record, nil, datafileID); err != nil {
					return err
				}
				record.Schema.ReleaseRecord(record)
			}
			continue
		}

		// Process each record in the group
		for i, recResult := range gctx.Result.RecordResults {
			record := gctx.Group.Records[i]

			if recResult.HasBlockingErrors() {
				log.Printf("Skipping record (line %d, type %s): blocking record validation failed",
					record.LineNumber, record.Schema.RecordType)
				// Convert errors while record available (no ObjectID - record won't be written)
				if err := convertAndRouteRecordErrors(ctx, router, recResult, record, nil, datafileID); err != nil {
					return err
				}
				record.Schema.ReleaseRecord(record)
				continue
			}

			// Record will be written - check if it has a writer
			if !router.HasWriter(record.Schema.Path) {
				// No writer for this schema (e.g., header/trailer) - skip silently
				record.Schema.ReleaseRecord(record)
				continue
			}

			// Convert record to get UUID, then convert errors with UUID linking
			rows, recordUUID, err := router.ConvertRecord(record)
			if err != nil {
				record.Schema.ReleaseRecord(record)
				return err
			}

			// Convert non-blocking errors with ObjectID linking (while record still available)
			if err := convertAndRouteRecordErrors(ctx, router, recResult, record, recordUUID, datafileID); err != nil {
				record.Schema.ReleaseRecord(record)
				return err
			}

			// Capture schema path before releasing record
			schemaPath := record.Schema.Path

			// Release record back to pool - no longer needed after conversion
			record.Schema.ReleaseRecord(record)

			// Send converted record rows to writer
			if err := router.SendRecordRowsByPath(ctx, schemaPath, rows); err != nil {
				return err
			}
		}
	}
	return nil
}

// convertAndRouteRecordErrors converts all errors for a record to rows and routes them.
// Must be called BEFORE record is released to pool.
// recordUUID is set for records that will be written (for error linking), nil otherwise.
func convertAndRouteRecordErrors(
	ctx context.Context,
	router *writer.Router,
	recResult *validation.RecordValidationResult,
	record *parser.ParsedRecord,
	recordUUID *pgtype.UUID,
	datafileID int32,
) error {
	allErrors := recResult.AllErrors()
	if len(allErrors) == 0 {
		return nil
	}

	for _, vr := range allErrors {
		row := convert.ConvertError(vr, record, recordUUID, datafileID, nil)
		if err := router.RouteErrorRow(ctx, row); err != nil {
			log.Printf("Error routing error row: %v", err)
			return err
		}
	}
	return nil
}
