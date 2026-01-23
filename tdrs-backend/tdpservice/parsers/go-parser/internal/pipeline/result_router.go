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

// ErrorStats tracks validation error counts by category.
type ErrorStats struct {
	Cat1 int64
	Cat2 int64
	Cat3 int64
	Cat4 int64
}

// Total returns the total number of errors across all categories.
func (s *ErrorStats) Total() int64 {
	return s.Cat1 + s.Cat2 + s.Cat3 + s.Cat4
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
	var cat1Count, cat2Count, cat3Count, cat4Count int64

	// Spawn multiple routers reading from the same channel
	for range numRouters {
		wg.Add(1)
		go func() {
			defer wg.Done()
			for pb := range pool.Results() {
				// Validate the batch's groups and collect error counts
				c1, c2, c3, c4 := validateBatch(pb, orchestrator, filespecKey)
				atomic.AddInt64(&cat1Count, c1)
				atomic.AddInt64(&cat2Count, c2)
				atomic.AddInt64(&cat3Count, c3)
				atomic.AddInt64(&cat4Count, c4)

				// Route the batch to writers
				if err := router.RouteBatch(ctx, pb); err != nil {
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
		Cat1: cat1Count,
		Cat2: cat2Count,
		Cat3: cat3Count,
		Cat4: cat4Count,
	}

	if len(errs) > 0 {
		return stats, errors.Join(errs...)
	}
	return stats, nil
}

// validateBatch validates all groups in a parsed batch and logs any validation errors.
// Returns the count of errors by category (cat1, cat2, cat3, cat4).
func validateBatch(pb *parser.ParsedBatch, orchestrator *validation.Orchestrator, filespecKey string) (cat1, cat2, cat3, cat4 int64) {
	for _, group := range pb.Groups {
		// Wrap the ParsedGroup to satisfy the validation interfaces
		wrappedRecords := make([]validation.Record, len(group.Records))
		for i, rec := range group.Records {
			wrappedRecords[i] = rec
		}
		wrappedGroup := validation.WrapGroup(group, wrappedRecords)

		// Run validation
		result := orchestrator.ValidateGroup(wrappedGroup, filespecKey)

		// Count Cat4 errors
		cat4 += int64(len(result.Cat4Errors))

		// Count record-level errors
		for _, recResult := range result.RecordResults {
			cat1 += int64(len(recResult.Cat1Errors))
			cat2 += int64(len(recResult.Cat2Errors))
			cat3 += int64(len(recResult.Cat3Errors))
		}

		// Log validation errors (for now - later these will be written to the database)
		if result.HasErrors() {
			log.Printf("Validation errors for group %s: %d errors", group.Key, result.TotalErrorCount())

			// Log Cat4 errors
			for _, err := range result.Cat4Errors {
				log.Printf("  Cat4: %s - %v", err.ValidatorID, err.Error)
			}

			// Log record-level errors
			for _, recResult := range result.RecordResults {
				if recResult.HasErrors() {
					rec := recResult.Record
					log.Printf("  Record (line %d, type %s):", rec.GetLineNumber(), rec.GetRecordType())

					for _, err := range recResult.Cat1Errors {
						log.Printf("    Cat1: %s - %v", err.ValidatorID, err.Error)
					}
					for _, err := range recResult.Cat2Errors {
						log.Printf("    Cat2 [%s]: %s - %v", err.FieldName, err.ValidatorID, err.Error)
					}
					for _, err := range recResult.Cat3Errors {
						log.Printf("    Cat3: %s - %v", err.ValidatorID, err.Error)
					}
				}
			}
		}
	}
	return
}
