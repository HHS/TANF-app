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
┌─────────────┐     ┌─────────────┐     ┌─────────────┐     ┌───────────────────────┐
│   Decoder   │     │   Workers   │     │ Dispatchers │     │       Writers         │
│  (1 reader) │ ──▶ │  (N parse)  │ ──▶ │ (M route)   │ ──▶ │ (K convert + flush)   │
└─────────────┘     └─────────────┘     └─────────────┘     └───────────────────────┘
      │                   │                   │                        │
   single            goroutine           goroutine               goroutine
   thread              pool                pool                  per table
```

### Key Design Decision: Conversion in Writers

Conversion from `ParsedRecord` to database rows happens in the writer goroutines, not in dispatchers:

```
Old (conversion in dispatcher - SEQUENTIAL per batch):
┌────────────┐     ┌─────────────────────┐     ┌────────────┐
│ Dispatcher │ ──▶ │ convert(record)     │ ──▶ │ Send(row)  │
│            │     │ (sequential in loop)│     │            │
└────────────┘     └─────────────────────┘     └────────────┘

New (conversion in writer - PARALLEL per table):
┌────────────┐     ┌────────────┐     ┌─────────────────────────────┐
│ Dispatcher │ ──▶ │Send(record)│ ──▶ │ Writer: convert + buffer    │
│ (just route)│    │            │     │ (parallel per table)        │
└────────────┘     └────────────┘     └─────────────────────────────┘
```

**Benefits:**
- Conversion parallelized by table (T1, T2, T3 convert simultaneously)
- Dispatcher becomes a simple router (faster)
- Less data over channels (one `ParsedRecord` vs multiple rows for T3)
- Cleaner ownership - writer owns the full transform pipeline
- Eliminates `RecordWriter` wrapper - converter lives directly in `TableWriter`

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
  │ (routes   │             │ (routes   │             │ (routes   │
  │  records) │             │  records) │             │  records) │
  └─────┬─────┘             └─────┬─────┘             └─────┬─────┘
        │                         │                         │
        └─────────────────────────┼─────────────────────────┘
                                  │
                                  │ ParsedRecord (not converted rows)
                                  │
        ┌─────────────────────────┼─────────────────────────┐
        │                         │                         │
        ▼                         ▼                         ▼
  ┌───────────┐             ┌───────────┐             ┌───────────┐
  │ T1 Chan   │             │ T2 Chan   │             │ T3 Chan   │
  │(ParsedRec)│             │(ParsedRec)│             │(ParsedRec)│
  └─────┬─────┘             └─────┬─────┘             └─────┬─────┘
        │                         │                         │
        ▼                         ▼                         ▼
  ┌───────────┐             ┌───────────┐             ┌───────────┐
  │ T1 Writer │             │ T2 Writer │             │ T3 Writer │
  │ convert + │             │ convert + │             │ convert + │
  │ buffer +  │             │ buffer +  │             │ buffer +  │
  │ COPY      │             │ COPY      │             │ COPY      │
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

The TableWriter runs in its own goroutine, owns the converter, and handles the full pipeline from `ParsedRecord` to database:

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

	"go-parser/internal/converter"
	"go-parser/internal/schema"
)

const (
	DefaultFlushThreshold = 100000
	MaxFlushThreshold     = 200000
)

type TableWriter struct {
	tableName  string
	columns    []string
	threshold  int
	datafileID int32
	converter  converter.RowConverter // Converter lives here - writer owns full pipeline

	// Async operation - channel carries ParsedRecords, not rows
	recordChan chan *schema.ParsedRecord
	pool       *pgxpool.Pool
	wg         sync.WaitGroup

	// Internal buffer (owned by the goroutine - no locks needed)
	rows [][]any

	// Stats (thread-safe)
	totalWritten atomic.Int64

	// Error propagation
	err   error
	errMu sync.RWMutex
}

func NewTableWriter(
	tableName string,
	columns []string,
	threshold int,
	datafileID int32,
	conv converter.RowConverter,
) *TableWriter {
	if threshold <= 0 {
		threshold = DefaultFlushThreshold
	}
	if threshold > MaxFlushThreshold {
		threshold = MaxFlushThreshold
	}
	return &TableWriter{
		tableName:  tableName,
		columns:    columns,
		threshold:  threshold,
		datafileID: datafileID,
		converter:  conv,
		// Channel buffer sized for records, not rows
		// Records are smaller than converted rows, so this is more memory-efficient
		recordChan: make(chan *schema.ParsedRecord, threshold),
		rows:       make([][]any, 0, threshold),
	}
}

// Start launches the writer goroutine
func (tw *TableWriter) Start(ctx context.Context, pool *pgxpool.Pool) {
	tw.pool = pool
	tw.wg.Add(1)
	go tw.run(ctx)
}

// run is the main writer loop - owns conversion, buffering, and flushing
func (tw *TableWriter) run(ctx context.Context) {
	defer tw.wg.Done()

	for {
		select {
		case record, ok := <-tw.recordChan:
			if !ok {
				// Channel closed - flush remaining and exit
				tw.flush(ctx)
				return
			}

			// Conversion happens here, in the writer goroutine (parallel per table)
			rows := tw.converter(record, tw.datafileID)
			for _, row := range rows {
				tw.rows = append(tw.rows, row)
				if len(tw.rows) >= tw.threshold {
					if err := tw.flush(ctx); err != nil {
						tw.setError(err)
						tw.drain()
						return
					}
				}
			}

		case <-ctx.Done():
			tw.flush(context.Background()) // Best-effort flush
			tw.drain()
			return
		}
	}
}

// Send queues a ParsedRecord for conversion and writing
func (tw *TableWriter) Send(ctx context.Context, record *schema.ParsedRecord) error {
	// Check for prior errors
	if err := tw.getError(); err != nil {
		return err
	}

	select {
	case tw.recordChan <- record:
		return nil
	case <-ctx.Done():
		return ctx.Err()
	}
}

// Stop closes the channel and waits for the goroutine to finish
func (tw *TableWriter) Stop() error {
	close(tw.recordChan)
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
	for range tw.recordChan {
		// Discard remaining records to unblock senders
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

The WriterManager is simplified to just coordinate starting/stopping writers and routing records. No conversion logic here:

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

type WriterManager struct {
	pool        *pgxpool.Pool
	datafileID  int32
	writers     map[string]*TableWriter // Direct TableWriter reference, no wrapper
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
		writers:    make(map[string]*TableWriter),
	}

	for _, schemaPath := range spec.Schemas {
		sch := reg.GetSchema(schemaPath)
		if sch.RecordType == "HEADER" || sch.RecordType == "TRAILER" {
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

		// TableWriter now owns the converter
		wm.writers[schemaPath] = NewTableWriter(
			meta.TableName,
			meta.Columns,
			DefaultFlushThreshold,
			datafileID,
			conv,
		)

		log.Printf("Created writer for %s -> %s (%d columns)",
			schemaPath, meta.TableName, len(meta.Columns))
	}

	// Error writer doesn't need a converter (errors are already in row format)
	// For now, leave as nil or create a special error writer
	// wm.errorWriter = NewErrorWriter(...)

	return wm
}

// Start launches all writer goroutines
func (wm *WriterManager) Start(ctx context.Context) {
	for _, tw := range wm.writers {
		tw.Start(ctx, wm.pool)
	}
	if wm.errorWriter != nil {
		wm.errorWriter.Start(ctx, wm.pool)
	}
}

// WriteRecord routes a record to the appropriate writer's channel
// No conversion here - writer handles it
func (wm *WriterManager) WriteRecord(ctx context.Context, record *schema.ParsedRecord) error {
	tw, ok := wm.writers[record.Schema.Path]
	if !ok {
		return fmt.Errorf("no writer for schema: %s", record.Schema.Path)
	}
	return tw.Send(ctx, record) // Send ParsedRecord directly
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
	for name, tw := range wm.writers {
		wg.Add(1)
		go func(name string, tw *TableWriter) {
			defer wg.Done()
			if err := tw.Stop(); err != nil {
				errMu.Lock()
				errs = append(errs, fmt.Errorf("%s: %w", name, err))
				errMu.Unlock()
			}
		}(name, tw)
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
	for path, tw := range wm.writers {
		result[path] = tw.TotalWritten()
	}
	if wm.errorWriter != nil {
		errors = wm.errorWriter.TotalWritten()
	}
	return result, errors
}
```

### Parallel Dispatchers (main.go)

Multiple dispatcher goroutines compete on the Results channel. They only route - no conversion:

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
| Conversion location | Writer goroutine | Parallel per table, cleaner ownership |
| Channel payload | `*ParsedRecord` | Smaller than converted rows, especially for T3 |
| Channel buffer | `threshold` records | Matches flush batch size |
| Buffer ownership | Writer goroutine only | No locks needed for row slice |
| Error handling | First error wins, drain channel | Prevents deadlock on error |
| Shutdown | Close channel → flush → wait | Graceful drain of pending records |
| Stats | `atomic.Int64` | Lock-free reads from any goroutine |
| Stop parallelism | Parallel close, parallel wait | Faster shutdown |
| Dispatcher role | Route only, no conversion | Fast, simple, parallelizable |

## Parallelism Comparison

| Stage | Old Design | New Design |
|-------|------------|------------|
| Conversion | M dispatchers (batch-parallel, sequential within batch) | K writers (table-parallel) |
| Buffering | K writers | K writers |
| COPY | K writers | K writers |

With the new design, T1, T2, and T3 records are converted simultaneously in their respective writer goroutines, rather than sequentially in dispatcher loops.

## Tuning Parameters

| Parameter | Controls | Suggested Starting Point |
|-----------|----------|--------------------------|
| `poolConfig.NumWorkers` | Parse parallelism | `runtime.NumCPU()` |
| `numDispatchers` | Batch routing parallelism | 4-8 |
| `threshold` | Rows per COPY | 100,000 |
| `recordChan buffer` | Backpressure headroom | `threshold` |
| `pgxpool.MaxConns` | DB connections | `numWriters + 4` |

### Connection Pool Sizing

With parallel writers, ensure enough connections:

```go
numWriters := len(spec.Schemas) // T1, T2, T3, etc.
config.MaxConns = int32(numWriters + 4) // +4 headroom
```

Each writer goroutine holds a connection during COPY. Dispatchers only route to channels (no DB connection needed).

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

With 3 tables converting and flushing in parallel instead of sequentially:

| Metric | Before (Sequential) | After (Parallel) |
|--------|---------------------|------------------|
| Conversion | Sequential in dispatcher loop | Parallel per table |
| Flush cycle time | 3 × 500ms = 1.5s | max(500ms) = 500ms |
| Theoretical speedup | 1x | up to 3x |

### Full Pipeline

| Stage | Before | After |
|-------|--------|-------|
| Parse | Parallel (N workers) | Parallel (N workers) |
| Dispatch | Single goroutine, does conversion | M goroutines, routing only |
| Convert | Sequential in dispatch loop | Parallel per table writer |
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
