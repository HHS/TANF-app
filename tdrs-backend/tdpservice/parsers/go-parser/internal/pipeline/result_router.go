package pipeline

import (
	"context"
	"errors"
	"log"
	"sync"

	"go-parser/internal/parser"
	"go-parser/internal/validation"
	"go-parser/internal/writer"
)

// routeResults receives parsed batches from the parser.pool, validates them, and routes them to database writers.
// Multiple router goroutines compete on the Results channel for parallel processing.
func routeResults(
	ctx context.Context,
	pool *parser.ParserPool,
	router *writer.Router,
	orchestrator *validation.Orchestrator,
	filespecKey string,
	numRouters int,
) error {
	var wg sync.WaitGroup
	errChan := make(chan error, numRouters)

	// Spawn multiple routers reading from the same channel
	for range numRouters {
		wg.Add(1)
		go func() {
			defer wg.Done()
			for pb := range pool.Results() {
				// Validate the batch's groups
				validateBatch(pb, orchestrator, filespecKey)

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

	if len(errs) > 0 {
		return errors.Join(errs...)

	}
	return nil
}

// validateBatch validates all groups in a parsed batch and logs any validation errors.
func validateBatch(pb *parser.ParsedBatch, orchestrator *validation.Orchestrator, filespecKey string) {
	for _, group := range pb.Groups {
		// Wrap the ParsedGroup to satisfy the validation interfaces
		wrappedRecords := make([]validation.Record, len(group.Records))
		for i, rec := range group.Records {
			wrappedRecords[i] = rec
		}
		wrappedGroup := validation.WrapGroup(group, wrappedRecords)

		// Run validation
		result := orchestrator.ValidateGroup(wrappedGroup, filespecKey)

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
}
