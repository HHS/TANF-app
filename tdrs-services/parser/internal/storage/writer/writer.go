package writer

import (
	"context"
	"fmt"
	"log"
	"sync"
	"sync/atomic"

	"go-parser/internal/sentinel"
)

const (
	// DefaultFlushThreshold is the number of records per table before auto-flush.
	// With ~1KB per record, 100000 records = ~100MB per writer.
	DefaultFlushThreshold = 50000

	// MaxFlushThreshold is a hard cap to prevent memory issues.
	MaxFlushThreshold = 200000
)

// TableWriter runs in its own goroutine and handles buffering and flushing
// []any rows to the database. Conversion is done upstream by the WriterManager.
type TableWriter struct {
	tableName string
	columns   []string
	threshold int

	// Async operation - channel carries []any rows (already converted)
	rowChan   chan []any
	abortCh   chan struct{}
	sink      Sink
	wg        sync.WaitGroup
	stopOnce  sync.Once
	abortOnce sync.Once

	// Internal buffer (owned by the goroutine - no locks needed)
	rows [][]any

	// Stats (thread-safe)
	totalWritten atomic.Int64
	aborted      atomic.Bool

	// Error propagation
	err   error
	errMu sync.RWMutex
}

// NewTableWriter creates a writer for the specified table.
// The writer receives pre-converted []any rows from WriterManager.
func NewTableWriter(
	tableName string,
	columns []string,
	threshold int,
) *TableWriter {
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
		// Channel buffer sized for rows
		rowChan: make(chan []any, threshold),
		abortCh: make(chan struct{}),
		rows:    make([][]any, 0, threshold),
	}
}

// Start launches the writer goroutine with the given sink.
func (tw *TableWriter) Start(ctx context.Context, sink Sink) {
	tw.sink = sink
	tw.wg.Add(1)
	go tw.run(ctx)
}

// run is the main writer loop - handles buffering and flushing
func (tw *TableWriter) run(ctx context.Context) {
	defer tw.wg.Done()

	for {
		if tw.aborted.Load() {
			tw.discard()
			return
		}

		select {
		case row, ok := <-tw.rowChan:
			if !ok {
				if !tw.aborted.Load() {
					tw.flush(ctx)
				}
				return
			}
			if tw.aborted.Load() {
				tw.discard()
				return
			}

			// Just buffer the pre-converted row
			tw.rows = append(tw.rows, row)
			if len(tw.rows) >= tw.threshold {
				if err := tw.flush(ctx); err != nil {
					tw.setError(err)
					tw.drain()
					return
				}
			}

		case <-tw.abortCh:
			tw.discard()
			return

		case <-ctx.Done():
			tw.discard()
			return
		}
	}
}

// SendRow queues a pre-converted []any row for writing
func (tw *TableWriter) SendRow(ctx context.Context, row []any) error {
	if tw.aborted.Load() {
		return sentinel.ErrWriterAborted
	}
	// Check for prior errors
	if err := tw.getError(); err != nil {
		return err
	}

	select {
	case tw.rowChan <- row:
		return nil
	case <-tw.abortCh:
		return sentinel.ErrWriterAborted
	case <-ctx.Done():
		return ctx.Err()
	}
}

// SendRows queues multiple pre-converted []any rows for writing.
// More efficient than calling SendRow in a loop — reduces per-row error checks
// and context switch overhead when sending many rows (e.g., error batches).
func (tw *TableWriter) SendRows(ctx context.Context, rows [][]any) error {
	if tw.aborted.Load() {
		return sentinel.ErrWriterAborted
	}
	if err := tw.getError(); err != nil {
		return err
	}
	for _, row := range rows {
		select {
		case tw.rowChan <- row:
		case <-tw.abortCh:
			return sentinel.ErrWriterAborted
		case <-ctx.Done():
			return ctx.Err()
		}
	}
	return nil
}

// Stop closes the channel and waits for the goroutine to finish
func (tw *TableWriter) Stop() error {
	tw.stopOnce.Do(func() {
		close(tw.rowChan)
	})
	tw.wg.Wait()
	return tw.getError()
}

// Abort stops this per-run writer without flushing buffered or queued rows.
func (tw *TableWriter) Abort() error {
	tw.aborted.Store(true)
	tw.abortOnce.Do(func() {
		close(tw.abortCh)
	})
	tw.wg.Wait()
	return tw.getError()
}

func (tw *TableWriter) flush(ctx context.Context) error {
	if len(tw.rows) == 0 {
		return nil
	}

	rows := tw.rows
	tw.rows = make([][]any, 0, tw.threshold)

	count, err := tw.sink.Flush(ctx, tw.tableName, tw.columns, rows)
	if err != nil {
		return fmt.Errorf("flush to %s: %w", tw.tableName, err)
	}

	tw.totalWritten.Add(count)
	log.Printf("Flushed %d %s records", count, tw.tableName)
	return nil
}

func (tw *TableWriter) discard() {
	tw.rows = make([][]any, 0, tw.threshold)
}

func (tw *TableWriter) drain() {
	for {
		select {
		case _, ok := <-tw.rowChan:
			if !ok {
				return
			}
			// Discard remaining rows to unblock senders
		case <-tw.abortCh:
			return
		}
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

// TotalWritten returns the total number of records written by this writer.
func (tw *TableWriter) TotalWritten() int64 {
	return tw.totalWritten.Load()
}

// TableName returns the table this writer targets.
func (tw *TableWriter) TableName() string {
	return tw.tableName
}
