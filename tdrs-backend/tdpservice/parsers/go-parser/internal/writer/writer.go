package writer

import (
	"context"
	"fmt"

	"github.com/jackc/pgx/v5"
	"github.com/jackc/pgx/v5/pgxpool"
)

const (
	// DefaultFlushThreshold is the number of records per table before auto-flush.
	// With ~1KB per record, 5000 records = ~5MB per writer.
	DefaultFlushThreshold = 5000

	// MaxFlushThreshold is a hard cap to prevent memory issues.
	MaxFlushThreshold = 10000
)

// TableWriter accumulates row data for a database table and flushes
// using PostgreSQL's COPY protocol.
//
// Memory usage: threshold * avg_row_size (e.g., 5000 * 1KB = 5MB)
type TableWriter struct {
	tableName string
	columns   []string
	rows      [][]any
	threshold int
}

// NewTableWriter creates a writer for the specified table.
// Columns are derived from the schema metadata.
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
		rows:      make([][]any, 0, threshold),
		threshold: threshold,
	}
}

// Add appends a row to the buffer.
// Returns true if the flush threshold has been reached.
func (tw *TableWriter) Add(row []any) bool {
	tw.rows = append(tw.rows, row)
	return len(tw.rows) >= tw.threshold
}

// Flush writes all buffered rows to the database via COPY protocol.
// Clears the buffer immediately after copying to release memory.
func (tw *TableWriter) Flush(ctx context.Context, pool *pgxpool.Pool) (int64, error) {
	if len(tw.rows) == 0 {
		return 0, nil
	}

	// Capture rows and clear buffer immediately to release memory
	rows := tw.rows
	tw.rows = make([][]any, 0, tw.threshold)

	count, err := pool.CopyFrom(
		ctx,
		pgx.Identifier{tw.tableName},
		tw.columns,
		pgx.CopyFromRows(rows),
	)

	if err != nil {
		return 0, fmt.Errorf("COPY to %s: %w", tw.tableName, err)
	}

	return count, nil
}

// Pending returns the number of rows waiting to be flushed.
func (tw *TableWriter) Pending() int {
	return len(tw.rows)
}

// TableName returns the table this writer targets.
func (tw *TableWriter) TableName() string {
	return tw.tableName
}
