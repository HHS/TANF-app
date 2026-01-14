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
	// DefaultFlushThreshold is the number of records per table before auto-flush.
	// With ~1KB per record, 100000 records = ~100MB per writer.
	DefaultFlushThreshold = 50000

	// MaxFlushThreshold is a hard cap to prevent memory issues.
	MaxFlushThreshold = 200000
)

// TableWriter runs in its own goroutine, owns the converter, and handles
// the full pipeline from ParsedRecord to database.
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

// NewTableWriter creates a writer for the specified table.
// The converter is owned by the writer - conversion happens in the writer goroutine.
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

// TotalWritten returns the total number of records written by this writer.
func (tw *TableWriter) TotalWritten() int64 {
	return tw.totalWritten.Load()
}

// TableName returns the table this writer targets.
func (tw *TableWriter) TableName() string {
	return tw.tableName
}
