package pipeline

import (
	"context"
	"log"
	"sync"

	"go-parser/internal/parser"
	"go-parser/internal/validation"
)

// ValidatedGroup pairs a parsed group with its validation result.
// Produced by WorkerPool, consumed by the result router.
type ValidatedGroup struct {
	Group  *parser.ParsedGroup
	Result *validation.GroupValidationResult
}

// ValidatedBatch is the output of the WorkerPool: parsed and validated records
// ready for routing to database writers.
type ValidatedBatch struct {
	BatchID int
	Groups  []*ValidatedGroup
}

// WorkerPool manages goroutines that parse and validate batches.
// It composes parser.ParsingOrchestrator (for record extraction) with the validation
// ValidationOrchestrator (for rule evaluation), keeping both stages in one goroutine
// to maximize utilization — parsing is ~2% of runtime while validation is ~51%.
type WorkerPool struct {
	parsingOrchestrator *parser.ParsingOrchestrator
	orchestrator        *validation.ValidationOrchestrator
	filespecKey         string
	numWorkers          int

	decodedBatches   chan *parser.DecodedBatch
	validatedBatches chan *ValidatedBatch
	wg               sync.WaitGroup
}

// WorkerPoolConfig configures the worker pool.
type WorkerPoolConfig struct {
	NumWorkers       int
	WorkBufferSize   int
	ResultBufferSize int
}

// NewWorkerPool creates a pool that parses and validates batches.
func NewWorkerPool(
	parsingOrchestrator *parser.ParsingOrchestrator,
	orchestrator *validation.ValidationOrchestrator,
	filespecKey string,
	config WorkerPoolConfig,
) *WorkerPool {
	return &WorkerPool{
		parsingOrchestrator: parsingOrchestrator,
		orchestrator:        orchestrator,
		filespecKey:         filespecKey,
		numWorkers:          config.NumWorkers,
		decodedBatches:      make(chan *parser.DecodedBatch, config.WorkBufferSize),
		validatedBatches:    make(chan *ValidatedBatch, config.ResultBufferSize),
	}
}

// Start launches the worker goroutines.
func (wp *WorkerPool) Start(ctx context.Context) {
	for i := 0; i < wp.numWorkers; i++ {
		wp.wg.Add(1)
		go wp.worker(ctx)
	}
}

// Submit submits a batch for processing.
// Blocks if the work channel is full (backpressure).
func (wp *WorkerPool) Submit(batch *parser.DecodedBatch) {
	wp.decodedBatches <- batch
}

// CloseInputs signals that no more work will be submitted.
func (wp *WorkerPool) CloseInputs() {
	close(wp.decodedBatches)
}

// Wait blocks until all workers finish, then closes the results channel.
func (wp *WorkerPool) Wait() {
	wp.wg.Wait()
	close(wp.validatedBatches)
	log.Print("All lines in file have been parsed, validated, and queued for writing.")
}

// Results returns the channel for receiving validated batch results.
func (wp *WorkerPool) Results() <-chan *ValidatedBatch {
	return wp.validatedBatches
}

func (wp *WorkerPool) worker(ctx context.Context) {
	defer wp.wg.Done()

	for {
		select {
		case <-ctx.Done():
			return

		case batch, ok := <-wp.decodedBatches:
			if !ok {
				return
			}
			wp.validatedBatches <- wp.processBatch(batch)
		}
	}
}

func (wp *WorkerPool) processBatch(batch *parser.DecodedBatch) *ValidatedBatch {
	parsed := wp.parsingOrchestrator.ParseBatch(batch)

	groups := make([]*ValidatedGroup, 0, len(parsed.Groups))
	for _, group := range parsed.Groups {
		vr := wp.orchestrator.ValidateGroup(group, wp.filespecKey)
		groups = append(groups, &ValidatedGroup{
			Group:  group,
			Result: vr,
		})
	}

	return &ValidatedBatch{
		BatchID: parsed.BatchID,
		Groups:  groups,
	}
}
