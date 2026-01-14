# Parallel Writer Architecture Design

## Problem Statement

The current Go parser architecture has a sequential bottleneck in the database write path:

1. **Single collector goroutine** receives parsed batches from the worker pool
2. **Sequential WriteBatch** iterates through records one-by-one
3. **Blocking Flush** - when T1 flushes, T2 and T3 wait

This means even though parsing is parallel, database writes are serialized. With COPY operations taking ~500ms on loaded databases, this creates significant latency.

### Performance Observations

| Scenario | COPY Duration | Total Parse Time |
|----------|---------------|------------------|
| Fresh DB | ~40ms | ~4.5s |
| 7M rows/table | ~500ms | ~25s |

Additional findings:
- Checkpoint storms (`max_wal_size` too low) caused significant overhead
- Increasing batch size from 5K to 100K saved ~4 seconds
- Removing indexes did NOT help (PK index cannot be dropped without dropping constraint)

## Proposed Architecture

### Pipeline Overview

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Decoder   │     │   Workers   │     │ Dispatchers │     │   Writers   │
│  (1 reader) │ ──▶ │  (N parse)  │ ──▶ │ (M route)   │ ──▶ │ (K flush)   │
└─────────────┘     └─────────────┘     └─────────────┘     └─────────────┘
      │                   │                   │                   │
   single            goroutine           goroutine           goroutine
   thread              pool                pool              per table
```

### Detailed Data Flow

```
                         ┌─────────────────┐
                         │  Worker Pool    │
                         │   (parsing)     │
                         └────────┬────────┘
                                  │
                                  ▼
                         ┌─────────────────┐
                         │ pool.Results()  │
                         │    channel      │
                         └────────┬────────┘
                                  │
        ┌─────────────────────────┼─────────────────────────┐
        │                         │                         │
        ▼                         ▼                         ▼
  ┌───────────┐             ┌───────────┐             ┌───────────┐
  │Dispatcher │             │Dispatcher │             │Dispatcher │
  │     1     │             │     2     │             │     N     │
  └─────┬─────┘             └─────┬─────┘             └─────┬─────┘
        │                         │                         │
        └─────────────────────────┼─────────────────────────┘
                                  │
        ┌─────────────────────────┼─────────────────────────┐
        │                         │                         │
        ▼                         ▼                         ▼
  ┌───────────┐             ┌───────────┐             ┌───────────┐
  │ T1 Chan   │             │ T2 Chan   │             │ T3 Chan   │
  │ (buffered)│             │ (buffered)│             │ (buffered)│
  └─────┬─────┘             └─────┬─────┘             └─────┬─────┘
        │                         │                         │
        ▼                         ▼                         ▼
  ┌───────────┐             ┌───────────┐             ┌───────────┐
  │ T1 Writer │             │ T2 Writer │             │ T3 Writer │
  │ Goroutine │             │ Goroutine │             │ Goroutine │
  └─────┬─────┘             └─────┬─────┘             └─────┬─────┘
        │                         │                         │
        └─────────────────────────┼─────────────────────────┘
                                  │
                                  ▼
                    ┌───────────────────────────┐
                    │   PostgreSQL (parallel    │
                    │   COPY per connection)    │
                    └───────────────────────────┘
```

## Implementation

### TableWriter (writer.go)

The TableWriter is updated to run in its own goroutine with a buffered input channel:

```go
package writer

import (
	"context"
	"fmt"
	"log"
	"sync"
	"sync/atomic"

	"github.com/jackc/pgx/v5"
	"github.com/jackc/pgx/v5/pgxpool"
)

const (
	DefaultFlushThreshold = 100000
	MaxFlushThreshold     = 200000
)

type TableWriter struct {
	tableName string
	columns   []string
	threshold int

	// Async operation
	rowChan chan []any
	pool    *pgxpool.Pool
	wg      sync.WaitGroup

	// Internal buffer (owned by the goroutine - no locks needed)
	rows [][]any

	// Stats (thread-safe)
	totalWritten atomic.Int64

	// Error propagation
	err   error
	errMu sync.RWMutex
}

func NewTableWriter(tableName string, columns []string, threshold int) *TableWriter {
	if threshold <= 0 {
		threshold = DefaultFlushThreshold
	}
	if threshold > MaxFlushThreshold {
		threshold = MaxFlushThreshold
	}
	return &TableWriter{
		tableName: tableName,
		columns:   columns,
		threshold: threshold,
		// Channel buffer = 2x threshold for backpressure headroom
		rowChan: make(chan []any, threshold*2),
		rows:    make([][]any, 0, threshold),
	}
}

// Start launches the writer goroutine
func (tw *TableWriter) Start(ctx context.Context, pool *pgxpool.Pool) {
	tw.pool = pool
	tw.wg.Add(1)
	go tw.run(ctx)
}

// run is the main writer loop - owns all buffer operations
func (tw *TableWriter) run(ctx context.Context) {
	defer tw.wg.Done()

	for {
		select {
		case row, ok := <-tw.rowChan:
			if !ok {
				// Channel closed - flush remaining and exit
				tw.flush(ctx)
				return
			}
			tw.rows = append(tw.rows, row)
			if len(tw.rows) >= tw.threshold {
				if err := tw.flush(ctx); err != nil {
					tw.setError(err)
					// Drain channel to unblock senders
					tw.drain()
					return
				}
			}

		case <-ctx.Done():
			tw.flush(context.Background()) // Best-effort flush
			tw.drain()
			return
		}
	}
}

// Send queues a row for writing (called from dispatcher)
func (tw *TableWriter) Send(ctx context.Context, row []any) error {
	// Check for prior errors
	if err := tw.getError(); err != nil {
		return err
	}

	select {
	case tw.rowChan <- row:
		return nil
	case <-ctx.Done():
		return ctx.Err()
	}
}

// Stop closes the channel and waits for the goroutine to finish
func (tw *TableWriter) Stop() error {
	close(tw.rowChan)
	tw.wg.Wait()
	return tw.getError()
}

func (tw *TableWriter) flush(ctx context.Context) error {
	if len(tw.rows) == 0 {
		return nil
	}

	rows := tw.rows
	tw.rows = make([][]any, 0, tw.threshold)

	count, err := tw.pool.CopyFrom(
		ctx,
		pgx.Identifier{tw.tableName},
		tw.columns,
		pgx.CopyFromRows(rows),
	)
	if err != nil {
		return fmt.Errorf("COPY to %s: %w", tw.tableName, err)
	}

	tw.totalWritten.Add(count)
	log.Printf("Flushed %d %s records", count, tw.tableName)
	return nil
}

func (tw *TableWriter) drain() {
	for range tw.rowChan {
		// Discard remaining rows to unblock senders
	}
}

func (tw *TableWriter) setError(err error) {
	tw.errMu.Lock()
	defer tw.errMu.Unlock()
	if tw.err == nil {
		tw.err = err
	}
}

func (tw *TableWriter) getError() error {
	tw.errMu.RLock()
	defer tw.errMu.RUnlock()
	return tw.err
}

func (tw *TableWriter) TotalWritten() int64 {
	return tw.totalWritten.Load()
}

func (tw *TableWriter) TableName() string {
	return tw.tableName
}
```

### WriterManager (manager.go)

The WriterManager coordinates starting/stopping all writers and routing records:

```go
package writer

import (
	"context"
	"errors"
	"fmt"
	"log"
	"sync"

	"github.com/jackc/pgx/v5/pgxpool"

	"go-parser/internal/converter"
	"go-parser/internal/filespec"
	"go-parser/internal/registry"
	"go-parser/internal/schema"
	"go-parser/internal/worker"
)

type RecordWriter struct {
	writer    *TableWriter
	converter converter.RowConverter
}

type WriterManager struct {
	pool        *pgxpool.Pool
	datafileID  int32
	writers     map[string]*RecordWriter
	errorWriter *TableWriter
}

var parserErrorColumns = []string{
	"row_number", "column_number", "item_number", "field_name",
	"case_number", "rpt_month_year", "error_message", "error_type",
	"created_at", "fields_json", "content_type_id", "file_id",
	"object_id", "deprecated", "values_json",
}

func NewWriterManager(
	pool *pgxpool.Pool,
	datafileID int32,
	spec *filespec.FileSpec,
	reg *registry.Registry,
) *WriterManager {
	wm := &WriterManager{
		pool:       pool,
		datafileID: datafileID,
		writers:    make(map[string]*RecordWriter),
	}

	for _, schemaPath := range spec.Schemas {
		schema := reg.GetSchema(schemaPath)
		if schema.RecordType == "HEADER" || schema.RecordType == "TRAILER" {
			continue
		}

		meta := reg.GetSchemaMetadata(schemaPath)
		if meta == nil {
			continue
		}

		conv := converter.GetConverter(schemaPath)
		if conv == nil {
			log.Printf("Warning: no converter for schema %s", schemaPath)
			continue
		}

		wm.writers[schemaPath] = &RecordWriter{
			writer:    NewTableWriter(meta.TableName, meta.Columns, DefaultFlushThreshold),
			converter: conv,
		}

		log.Printf("Created writer for %s -> %s (%d columns)",
			schemaPath, meta.TableName, len(meta.Columns))
	}

	wm.errorWriter = NewTableWriter("parser_error", parserErrorColumns, DefaultFlushThreshold)

	return wm
}

// Start launches all writer goroutines
func (wm *WriterManager) Start(ctx context.Context) {
	for _, rw := range wm.writers {
		rw.writer.Start(ctx, wm.pool)
	}
	if wm.errorWriter != nil {
		wm.errorWriter.Start(ctx, wm.pool)
	}
}

// WriteRecord routes a record to the appropriate writer's channel
func (wm *WriterManager) WriteRecord(ctx context.Context, record *schema.ParsedRecord) error {
	rw, ok := wm.writers[record.Schema.Path]
	if !ok {
		return fmt.Errorf("no writer for schema: %s", record.Schema.Path)
	}

	rows := rw.converter(record, wm.datafileID)
	for _, row := range rows {
		if err := rw.writer.Send(ctx, row); err != nil {
			return err
		}
	}
	return nil
}

// WriteBatch routes all records in a batch to appropriate writers
func (wm *WriterManager) WriteBatch(ctx context.Context, batch *worker.ParsedBatch) error {
	for _, group := range batch.Groups {
		for _, record := range group.Records {
			if err := wm.WriteRecord(ctx, record); err != nil {
				return err
			}
		}
	}
	return nil
}

// Stop closes all channels and waits for goroutines to finish
func (wm *WriterManager) Stop() error {
	var errs []error
	var wg sync.WaitGroup
	var errMu sync.Mutex

	// Stop all writers in parallel
	for name, rw := range wm.writers {
		wg.Add(1)
		go func(name string, rw *RecordWriter) {
			defer wg.Done()
			if err := rw.writer.Stop(); err != nil {
				errMu.Lock()
				errs = append(errs, fmt.Errorf("%s: %w", name, err))
				errMu.Unlock()
			}
		}(name, rw)
	}
	wg.Wait()

	if wm.errorWriter != nil {
		if err := wm.errorWriter.Stop(); err != nil {
			errs = append(errs, fmt.Errorf("error_writer: %w", err))
		}
	}

	if len(errs) > 0 {
		return errors.Join(errs...)
	}
	return nil
}

// Stats returns totals from all writers
func (wm *WriterManager) Stats() (records map[string]int64, errors int64) {
	result := make(map[string]int64)
	for path, rw := range wm.writers {
		result[path] = rw.writer.TotalWritten()
	}
	if wm.errorWriter != nil {
		errors = wm.errorWriter.TotalWritten()
	}
	return result, errors
}
```

### Parallel Dispatchers (main.go)

Multiple dispatcher goroutines compete on the Results channel:

```go
func collectResults(
	ctx context.Context,
	pool *worker.Pool,
	writerMgr *writer.WriterManager,
	numDispatchers int,
) error {
	// Start all writer goroutines
	writerMgr.Start(ctx)

	var wg sync.WaitGroup
	errChan := make(chan error, numDispatchers)

	// Spawn multiple dispatchers reading from the same channel
	for i := 0; i < numDispatchers; i++ {
		wg.Add(1)
		go func(id int) {
			defer wg.Done()
			for pb := range pool.Results() {
				if err := writerMgr.WriteBatch(ctx, pb); err != nil {
					log.Printf("Dispatcher %d: batch %d error: %v", id, pb.BatchID, err)
					errChan <- err
					return
				}
			}
		}(i)
	}

	// Wait for all dispatchers to finish
	wg.Wait()
	close(errChan)

	// Collect any errors
	var errs []error
	for err := range errChan {
		errs = append(errs, err)
	}

	// Stop writers (flushes remaining)
	if err := writerMgr.Stop(); err != nil {
		errs = append(errs, err)
	}

	records, errors := writerMgr.Stats()
	for table, count := range records {
		log.Printf("Written to %s: %d records", table, count)
	}
	log.Printf("Total errors: %d", errors)

	if len(errs) > 0 {
		return errors.Join(errs...)
	}
	return nil
}
```

### Updated processFile Call

```go
// Step 7: Start result collector with parallel dispatchers
var collectorErr error
var wg sync.WaitGroup
wg.Add(1)
go func() {
	defer wg.Done()
	numDispatchers := 4 // Tune based on CPU cores / connection pool size
	collectorErr = collectResults(ctx, workerPool, writerMgr, numDispatchers)
}()
```

## Design Decisions

| Aspect | Decision | Rationale |
|--------|----------|-----------|
| Channel buffer | `threshold * 2` | Absorbs burst without excessive memory |
| Buffer ownership | Writer goroutine only | No locks needed for row slice |
| Error handling | First error wins, drain channel | Prevents deadlock on error |
| Shutdown | Close channel → flush → wait | Graceful drain of pending rows |
| Stats | `atomic.Int64` | Lock-free reads from any goroutine |
| Stop parallelism | Parallel close, parallel wait | Faster shutdown |
| Dispatcher count | Configurable (default 4) | Balance between parallelism and overhead |

## Tuning Parameters

| Parameter | Controls | Suggested Starting Point |
|-----------|----------|--------------------------|
| `poolConfig.NumWorkers` | Parse parallelism | `runtime.NumCPU()` |
| `numDispatchers` | Batch routing parallelism | 4-8 |
| `threshold` | Rows per COPY | 100,000 |
| `rowChan buffer` | Backpressure headroom | `threshold * 2` |
| `pgxpool.MaxConns` | DB connections | `numDispatchers + numWriters + 4` |

### Connection Pool Sizing

With parallel writers and dispatchers, ensure enough connections:

```go
numWriters := len(spec.Schemas) // T1, T2, T3, etc.
config.MaxConns = int32(numDispatchers + numWriters + 4) // +4 headroom
```

Each writer goroutine holds a connection during COPY. Dispatchers only send to channels (no DB connection needed).

## PostgreSQL Configuration

Based on performance testing, these settings help with bulk loading:

```sql
-- Check current settings
SHOW max_wal_size;
SHOW checkpoint_completion_target;

-- Recommended for bulk loads
ALTER SYSTEM SET max_wal_size = '4GB';
ALTER SYSTEM SET checkpoint_completion_target = 0.9;
SELECT pg_reload_conf();
```

**Why this matters:** Without sufficient `max_wal_size`, checkpoints occur every few seconds during bulk loading, causing significant I/O overhead and blocking.

## Expected Performance Improvement

### Write Path

With 3 tables flushing in parallel instead of sequentially:

| Metric | Before (Sequential) | After (Parallel) |
|--------|---------------------|------------------|
| Flush cycle time | 3 × 500ms = 1.5s | max(500ms) = 500ms |
| Theoretical speedup | 1x | up to 3x |

### Full Pipeline

| Stage | Before | After |
|-------|--------|-------|
| Parse | Parallel (N workers) | Parallel (N workers) |
| Dispatch | Single goroutine | M dispatcher goroutines |
| Write | Sequential flush | Parallel flush per table |

Actual gains depend on:
- Connection pool size
- I/O saturation
- Table count
- Record distribution across tables

## Error Handling

### Writer Errors

When a writer encounters an error:
1. Error is stored (first error wins)
2. Channel is drained to unblock senders
3. Goroutine exits
4. Subsequent `Send()` calls return the stored error

### Dispatcher Errors

When a dispatcher encounters an error:
1. Error is sent to error channel
2. Dispatcher exits (other dispatchers continue)
3. Errors are collected after all dispatchers finish

### Graceful Shutdown

1. `pool.Results()` channel closes when worker pool is done
2. Dispatchers exit their loops
3. `writerMgr.Stop()` closes all writer channels
4. Writers flush remaining rows and exit
5. Stats are collected and reported

## Future Optimizations

1. **Multiple writers per table** - For very high throughput, could have 2-3 writers per table with round-robin distribution

2. **Adaptive batch sizing** - Adjust threshold based on observed COPY latency

3. **Connection affinity** - Pin writer goroutines to specific connections to reduce pool contention

4. **Metrics/tracing** - Add OpenTelemetry spans to identify bottlenecks

5. **Table partitioning** - Partition by datafile_id or time period for smaller indexes
