package pipeline

import (
	"context"
	"log/slog"
	"strconv"
	"strings"
	"sync"
	"time"

	"go-parser/internal/logging"
	"go-parser/internal/metrics"
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
	BatchID             int
	Groups              []*validatedGroup
	ParsingDuration     time.Duration
	ValidationDurations validation.PhaseDurations
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
	metricsProgram      string
	metricsSection      int

	router     *writer.Router
	datafileID int32

	decodedBatches chan *parser.DecodedBatch
	wg             sync.WaitGroup

	workerStats []RouteStats
	workerErr   error
	errOnce     sync.Once

	startedAt    time.Time
	capacityOnce sync.Once
	metricsOnce  sync.Once
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
	metricsProgram, metricsSection := parseMetricsFilespecKey(filespecKey)
	return &WorkerPool{
		parsingOrchestrator: parsingOrchestrator,
		orchestrator:        orchestrator,
		dataFileContext:     dataFileContext,
		filespecKey:         filespecKey,
		numWorkers:          config.NumWorkers,
		metricsProgram:      metricsProgram,
		metricsSection:      metricsSection,
		router:              router,
		datafileID:          datafileID,
		decodedBatches:      make(chan *parser.DecodedBatch, config.WorkBufferSize),
		workerStats:         make([]RouteStats, config.NumWorkers),
	}
}

// Start launches the worker goroutines.
func (wp *WorkerPool) Start(ctx context.Context) {
	wp.startedAt = time.Now()
	metrics.SetWorkerPoolCapacity(wp.metricsProgram, wp.metricsSection, wp.numWorkers)
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
	wp.recordCapacityDuration()
	wp.recordWorkerMetrics()
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
		total.ParsingDuration += s.ParsingDuration
		total.RoutingDuration += s.RoutingDuration
		total.ActiveDuration += s.ActiveDuration
		total.ValidationDurations.Add(s.ValidationDurations)
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
			startedAt := wp.startWorkerTimer()
			vb := wp.processBatch(batch)

			// Tally errors (direct addition, no atomics needed per single goroutine)
			rpc, fv, vc, cc := countErrors(vb)
			stats.RecordPreCheck += rpc
			stats.FieldValue += fv
			stats.ValueConsistency += vc
			stats.CaseConsistency += cc
			stats.BatchCount++
			stats.GroupCount += int64(len(vb.Groups))
			stats.ParsingDuration += vb.ParsingDuration
			stats.ValidationDurations.Add(vb.ValidationDurations)

			// Route to writers
			routeStart := time.Now()
			if err := routeValidatedBatch(ctx, wp.router, vb.Groups, wp.datafileID, &errorRows); err != nil {
				stats.RoutingDuration += time.Since(routeStart)
				stats.ActiveDuration += wp.stopWorkerTimer(startedAt)
				logging.Error(ctx, "worker batch failed",
					slog.Int(logging.KeyFileID, int(wp.datafileID)),
					slog.Int("worker_id", workerID),
					slog.Int("batch_id", vb.BatchID),
					slog.Any(logging.KeyError, err),
				)
				wp.errOnce.Do(func() { wp.workerErr = err })
				return
			}
			stats.RoutingDuration += time.Since(routeStart)
			stats.ActiveDuration += wp.stopWorkerTimer(startedAt)
		}
	}
}

func (wp *WorkerPool) startWorkerTimer() time.Time {
	return time.Now()
}

func (wp *WorkerPool) stopWorkerTimer(startedAt time.Time) time.Duration {
	return time.Since(startedAt)
}

func (wp *WorkerPool) recordCapacityDuration() {
	wp.capacityOnce.Do(func() {
		if wp.startedAt.IsZero() {
			return
		}
		metrics.AddWorkerPoolCapacityDuration(wp.metricsProgram, wp.metricsSection, time.Since(wp.startedAt), wp.numWorkers)
	})
}

func (wp *WorkerPool) recordWorkerMetrics() {
	wp.metricsOnce.Do(func() {
		stats := wp.AggregateStats()
		metrics.ObservePipelineStage(wp.metricsProgram, wp.metricsSection, "worker_parsing", stats.ParsingDuration)
		metrics.ObservePipelineStage(wp.metricsProgram, wp.metricsSection, "worker_group_validation", stats.ValidationDurations.GroupValidation)
		metrics.ObservePipelineStage(wp.metricsProgram, wp.metricsSection, "worker_record_validation", stats.ValidationDurations.RecordValidation)
		metrics.ObservePipelineStage(wp.metricsProgram, wp.metricsSection, "worker_field_validation", stats.ValidationDurations.FieldValidation)
		metrics.ObservePipelineStage(wp.metricsProgram, wp.metricsSection, "worker_routing", stats.RoutingDuration)
		metrics.AddWorkerPoolActiveDuration(wp.metricsProgram, wp.metricsSection, stats.ActiveDuration)
	})
}

func parseMetricsFilespecKey(filespecKey string) (string, int) {
	program, sectionString, ok := strings.Cut(filespecKey, ":")
	if !ok {
		return filespecKey, 0
	}
	section, err := strconv.Atoi(sectionString)
	if err != nil {
		return program, 0
	}
	return program, section
}

func (wp *WorkerPool) processBatch(batch *parser.DecodedBatch) *validatedBatch {
	parseStart := time.Now()
	parsed := wp.parsingOrchestrator.ParseBatch(batch)
	parsingDuration := time.Since(parseStart)

	groups := make([]*validatedGroup, 0, len(parsed.Groups))
	var durations validation.PhaseDurations
	for _, group := range parsed.Groups {
		vr := wp.orchestrator.ValidateGroup(group, wp.filespecKey, wp.dataFileContext)
		durations.Add(vr.Durations)
		groups = append(groups, &validatedGroup{
			Group:  group,
			Result: vr,
		})
	}

	return &validatedBatch{
		BatchID:             parsed.BatchID,
		Groups:              groups,
		ParsingDuration:     parsingDuration,
		ValidationDurations: durations,
	}
}
