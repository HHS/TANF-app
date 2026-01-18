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
// Multiple router goroutines compete on the Results channel for parallel processing.
func routeResults(
	ctx context.Context,
	pool *parser.ParserPool,
	router *writer.Router,
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
