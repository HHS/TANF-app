package pipeline

import (
	"context"
	"errors"
	"log"
	"sync"
	"sync/atomic"

	"go-parser/internal/parser"
	"go-parser/internal/validation"
	"go-parser/internal/writer"
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

				// Route only valid records to writers (filter based on validation results)
				// - Groups with CASE_CONSISTENCY errors are completely rejected
				// - Records with RECORD_PRE_CHECK errors are rejected
				if err := routeValidatedBatch(ctx, router, contexts); err != nil {
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

// routeValidatedBatch routes only valid records to the database.
// Groups with blocking errors (CASE_CONSISTENCY) are completely rejected (no records written).
// Records with blocking errors (RECORD_PRE_CHECK) are rejected (not written to database).
func routeValidatedBatch(ctx context.Context, router *writer.Router, contexts []*GroupValidationContext) error {
	for _, gctx := range contexts {
		// Skip entire group if it has blocking group errors (CASE_CONSISTENCY)
		if gctx.Result.HasBlockingGroupErrors() {
			log.Printf("Skipping group %s: blocking group validation failed", gctx.Group.Key)
			// Release all records back to pool since they won't be written
			for _, record := range gctx.Group.Records {
				record.Schema.ReleaseRecord(record)
			}
			continue
		}

		// Route only records that passed blocking validation (RECORD_PRE_CHECK)
		for i, recResult := range gctx.Result.RecordResults {
			record := gctx.Group.Records[i]

			if recResult.HasBlockingErrors() {
				log.Printf("Skipping record (line %d, type %s): blocking record validation failed",
					record.LineNumber, record.Schema.RecordType)
				// Release record back to pool since it won't be written
				record.Schema.ReleaseRecord(record)
				continue
			}

			// Route valid record to database
			if err := router.RouteRecord(ctx, record); err != nil {
				return err
			}
		}
	}
	return nil
}
