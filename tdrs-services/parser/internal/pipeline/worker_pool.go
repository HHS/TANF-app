package pipeline

import (
	"context"
	"log"
	"sync"

	"go-parser/internal/parser"
	"go-parser/internal/storage/writer"
	"go-parser/internal/validation"
)

// validatedGroup pairs a parsed group with its validation result.
type validatedGroup struct {
	Group  *parser.ParsedGroup
	Result *validation.GroupValidationResult
}

// validatedBatch is the output of processBatch: parsed and validated records
// ready for routing to database writers.
type validatedBatch struct {
	BatchID int
	Groups  []*validatedGroup
}

// WorkerPool manages goroutines that parse, validate, and route batches.
// Each worker composes parsing, validation, and database routing in a single
// goroutine. TableWriter instances (owned by writer.Router) handle the actual
// database I/O in their own goroutines.
type WorkerPool struct {
	parsingOrchestrator *parser.ParsingOrchestrator
	orchestrator        *validation.ValidationOrchestrator
	dataFileContext     *validation.DataFileContext
	filespecKey         string
	numWorkers          int

	router     *writer.Router
	datafileID int32

	decodedBatches chan *parser.DecodedBatch
	wg             sync.WaitGroup

	workerStats []RouteStats
	workerErr   error
	errOnce     sync.Once
}

// WorkerPoolConfig configures the worker pool.
type WorkerPoolConfig struct {
	NumWorkers     int
	WorkBufferSize int
}

// NewWorkerPool creates a pool that parses, validates, and routes batches.
func NewWorkerPool(
	parsingOrchestrator *parser.ParsingOrchestrator,
	orchestrator *validation.ValidationOrchestrator,
	dataFileContext *validation.DataFileContext,
	filespecKey string,
	router *writer.Router,
	datafileID int32,
	config WorkerPoolConfig,
) *WorkerPool {
	return &WorkerPool{
		parsingOrchestrator: parsingOrchestrator,
		orchestrator:        orchestrator,
		dataFileContext:     dataFileContext,
		filespecKey:         filespecKey,
		numWorkers:          config.NumWorkers,
		router:              router,
		datafileID:          datafileID,
		decodedBatches:      make(chan *parser.DecodedBatch, config.WorkBufferSize),
		workerStats:         make([]RouteStats, config.NumWorkers),
	}
}

// Start launches the worker goroutines.
func (wp *WorkerPool) Start(ctx context.Context) {
	for i := 0; i < wp.numWorkers; i++ {
		wp.wg.Add(1)
		go wp.worker(ctx, i)
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

// Wait blocks until all workers finish.
func (wp *WorkerPool) Wait() {
	wp.wg.Wait()
	log.Print("All lines in file have been parsed, validated, and routed to writers.")
}

// Err returns the first routing error encountered by any worker, or nil.
func (wp *WorkerPool) Err() error {
	return wp.workerErr
}

// AggregateStats returns combined stats from all workers.
// Must be called after Wait().
func (wp *WorkerPool) AggregateStats() *RouteStats {
	var total RouteStats
	for i := range wp.workerStats {
		s := &wp.workerStats[i]
		total.RecordPreCheck += s.RecordPreCheck
		total.FieldValue += s.FieldValue
		total.ValueConsistency += s.ValueConsistency
		total.CaseConsistency += s.CaseConsistency
		total.BatchCount += s.BatchCount
		total.GroupCount += s.GroupCount
	}
	return &total
}

func (wp *WorkerPool) worker(ctx context.Context, workerID int) {
	defer wp.wg.Done()
	stats := &wp.workerStats[workerID]
	var errorRows [][]any // reusable buffer across batches

	for {
		select {
		case <-ctx.Done():
			return

		case batch, ok := <-wp.decodedBatches:
			if !ok {
				return
			}
			vb := wp.processBatch(batch)

			// Tally errors (direct addition, no atomics needed per single goroutine)
			rpc, fv, vc, cc := countErrors(vb)
			stats.RecordPreCheck += rpc
			stats.FieldValue += fv
			stats.ValueConsistency += vc
			stats.CaseConsistency += cc
			stats.BatchCount++
			stats.GroupCount += int64(len(vb.Groups))

			// Route to writers
			if err := routeValidatedBatch(ctx, wp.router, vb.Groups, wp.datafileID, &errorRows); err != nil {
				log.Printf("Worker %d: batch %d error: %v", workerID, vb.BatchID, err)
				wp.errOnce.Do(func() { wp.workerErr = err })
				return
			}
		}
	}
}

func (wp *WorkerPool) processBatch(batch *parser.DecodedBatch) *validatedBatch {
	parsed := wp.parsingOrchestrator.ParseBatch(batch)

	groups := make([]*validatedGroup, 0, len(parsed.Groups))
	for _, group := range parsed.Groups {
		vr := wp.orchestrator.ValidateGroup(group, wp.filespecKey, wp.dataFileContext)
		groups = append(groups, &validatedGroup{
			Group:  group,
			Result: vr,
		})
	}

	return &validatedBatch{
		BatchID: parsed.BatchID,
		Groups:  groups,
	}
}
