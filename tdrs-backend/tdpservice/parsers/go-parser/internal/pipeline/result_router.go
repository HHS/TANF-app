package pipeline

import (
	"context"
	"errors"
	"log"
	"sync"

	"go-parser/internal/parser"
	"go-parser/internal/writer"
)

// routeResults receives parsed batches from the parser.pool and routes them to database writers.
// Multiple dispatcher goroutines compete on the Results channel for parallel processing.
func routeResults(
	ctx context.Context,
	pool *parser.Pool,
	router *writer.Router,
	numDispatchers int,
) error {
	var wg sync.WaitGroup
	errChan := make(chan error, numDispatchers)

	// Spawn multiple dispatchers reading from the same channel
	for range numDispatchers {
		wg.Add(1)
		go func() {
			defer wg.Done()
			for pb := range pool.Results() {
				// Route the batch to writers
				if err := router.RouteBatch(ctx, pb); err != nil {
					log.Printf("Dispatcher: batch %d error: %v", pb.BatchID, err)
					errChan <- err
					return
				}
			}
		}()
	}

	// Wait for all dispatchers to finish
	wg.Wait()
	close(errChan)

	// Collect any errors from dispatchers
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
