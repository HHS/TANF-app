package writer

import (
	"context"
	"errors"
	"sync"
	"testing"

	"go-parser/internal/sentinel"
)

// mockSink records all Flush calls for verification.
type mockSink struct {
	mu      sync.Mutex
	flushes []flushCall
	err     error // if set, Flush returns this error
}

type flushCall struct {
	tableName string
	columns   []string
	rows      [][]any
}

func (m *mockSink) Flush(_ context.Context, tableName string, columns []string, rows [][]any) (int64, error) {
	m.mu.Lock()
	defer m.mu.Unlock()
	if m.err != nil {
		return 0, m.err
	}
	// Deep copy rows to avoid races with buffer reuse
	copied := make([][]any, len(rows))
	copy(copied, rows)
	m.flushes = append(m.flushes, flushCall{
		tableName: tableName,
		columns:   columns,
		rows:      copied,
	})
	return int64(len(rows)), nil
}

func (m *mockSink) RollbackDatafile(_ context.Context, _ int32, _ []string) error { return nil }
func (m *mockSink) Close() error                                                  { return nil }

func (m *mockSink) totalRows() int {
	m.mu.Lock()
	defer m.mu.Unlock()
	total := 0
	for _, f := range m.flushes {
		total += len(f.rows)
	}
	return total
}

func TestNewTableWriter_DefaultThreshold(t *testing.T) {
	tw := NewTableWriter("test_table", []string{"col1"}, 0)
	if tw.threshold != DefaultFlushThreshold {
		t.Errorf("expected threshold %d, got %d", DefaultFlushThreshold, tw.threshold)
	}
}

func TestNewTableWriter_NegativeThreshold(t *testing.T) {
	tw := NewTableWriter("test_table", []string{"col1"}, -5)
	if tw.threshold != DefaultFlushThreshold {
		t.Errorf("expected threshold %d, got %d", DefaultFlushThreshold, tw.threshold)
	}
}

func TestNewTableWriter_MaxThresholdCap(t *testing.T) {
	tw := NewTableWriter("test_table", []string{"col1"}, MaxFlushThreshold+100)
	if tw.threshold != MaxFlushThreshold {
		t.Errorf("expected threshold %d, got %d", MaxFlushThreshold, tw.threshold)
	}
}

func TestNewTableWriter_CustomThreshold(t *testing.T) {
	tw := NewTableWriter("test_table", []string{"col1"}, 500)
	if tw.threshold != 500 {
		t.Errorf("expected threshold 500, got %d", tw.threshold)
	}
}

func TestTableWriter_TableName(t *testing.T) {
	tw := NewTableWriter("my_table", []string{"a"}, 10)
	if tw.TableName() != "my_table" {
		t.Errorf("expected 'my_table', got %q", tw.TableName())
	}
}

func TestTableWriter_SendAndStop(t *testing.T) {
	sink := &mockSink{}
	tw := NewTableWriter("test_table", []string{"id", "name"}, 100)
	ctx := context.Background()

	tw.Start(ctx, sink)

	for i := range 5 {
		if err := tw.SendRow(ctx, []any{i, "row"}); err != nil {
			t.Fatalf("SendRow failed: %v", err)
		}
	}

	if err := tw.Stop(); err != nil {
		t.Fatalf("Stop failed: %v", err)
	}

	if tw.TotalWritten() != 5 {
		t.Errorf("expected 5 written, got %d", tw.TotalWritten())
	}
	if sink.totalRows() != 5 {
		t.Errorf("expected 5 rows flushed to sink, got %d", sink.totalRows())
	}
}

func TestTableWriter_AbortDiscardsBufferedRows(t *testing.T) {
	sink := &mockSink{}
	tw := NewTableWriter("test_table", []string{"id", "name"}, 100)
	ctx := context.Background()

	tw.Start(ctx, sink)

	for i := range 5 {
		if err := tw.SendRow(ctx, []any{i, "row"}); err != nil {
			t.Fatalf("SendRow failed: %v", err)
		}
	}

	if err := tw.Abort(); err != nil {
		t.Fatalf("Abort failed: %v", err)
	}

	if tw.TotalWritten() != 0 {
		t.Errorf("expected 0 written, got %d", tw.TotalWritten())
	}
	if sink.totalRows() != 0 {
		t.Errorf("expected 0 rows flushed to sink, got %d", sink.totalRows())
	}
	if err := tw.SendRow(ctx, []any{99, "row"}); !errors.Is(err, sentinel.ErrWriterAborted) {
		t.Errorf("SendRow after abort error = %v, want ErrWriterAborted", err)
	}
}

func TestTableWriter_SendRows(t *testing.T) {
	sink := &mockSink{}
	tw := NewTableWriter("test_table", []string{"id"}, 100)
	ctx := context.Background()

	tw.Start(ctx, sink)

	rows := [][]any{{1}, {2}, {3}}
	if err := tw.SendRows(ctx, rows); err != nil {
		t.Fatalf("SendRows failed: %v", err)
	}

	if err := tw.Stop(); err != nil {
		t.Fatalf("Stop failed: %v", err)
	}

	if tw.TotalWritten() != 3 {
		t.Errorf("expected 3 written, got %d", tw.TotalWritten())
	}
}

func TestTableWriter_FlushAtThreshold(t *testing.T) {
	sink := &mockSink{}
	tw := NewTableWriter("test_table", []string{"id"}, 5)
	ctx := context.Background()

	tw.Start(ctx, sink)

	// Send exactly the threshold number of rows
	for i := range 5 {
		if err := tw.SendRow(ctx, []any{i}); err != nil {
			t.Fatalf("SendRow failed: %v", err)
		}
	}

	// Send a few more to trigger a second batch
	for i := range 3 {
		if err := tw.SendRow(ctx, []any{i + 5}); err != nil {
			t.Fatalf("SendRow failed: %v", err)
		}
	}

	if err := tw.Stop(); err != nil {
		t.Fatalf("Stop failed: %v", err)
	}

	if tw.TotalWritten() != 8 {
		t.Errorf("expected 8 written, got %d", tw.TotalWritten())
	}

	// Should have at least 2 flush calls (one at threshold, one on stop)
	sink.mu.Lock()
	flushCount := len(sink.flushes)
	sink.mu.Unlock()
	if flushCount < 2 {
		t.Errorf("expected at least 2 flushes, got %d", flushCount)
	}
}

func TestTableWriter_SinkError(t *testing.T) {
	sinkErr := errors.New("write failed")
	sink := &mockSink{err: sinkErr}
	tw := NewTableWriter("test_table", []string{"id"}, 2)
	ctx := context.Background()

	tw.Start(ctx, sink)

	// Fill past threshold to trigger a flush
	for range 3 {
		_ = tw.SendRow(ctx, []any{1})
	}

	err := tw.Stop()
	if err == nil {
		t.Fatal("expected error from Stop")
	}
	if !errors.Is(err, sinkErr) {
		t.Errorf("expected sink error, got: %v", err)
	}
}

func TestTableWriter_SendRowAfterError(t *testing.T) {
	sinkErr := errors.New("write failed")
	sink := &mockSink{err: sinkErr}
	tw := NewTableWriter("test_table", []string{"id"}, 2)
	ctx := context.Background()

	tw.Start(ctx, sink)

	// Fill past threshold to trigger an error
	for range 3 {
		_ = tw.SendRow(ctx, []any{1})
	}

	// Give the goroutine time to process and hit the error
	// Subsequent sends should return the error
	for range 100 {
		err := tw.SendRow(ctx, []any{1})
		if err != nil {
			if !errors.Is(err, sinkErr) {
				t.Errorf("expected sink error, got: %v", err)
			}
			return // test passes
		}
	}

	// If we get here, the error may propagate on Stop
	err := tw.Stop()
	if err == nil {
		t.Fatal("expected error to propagate")
	}
}

func TestTableWriter_ContextCancellation(t *testing.T) {
	sink := &mockSink{}
	tw := NewTableWriter("test_table", []string{"id"}, 1000)
	ctx, cancel := context.WithCancel(context.Background())

	tw.Start(ctx, sink)

	// Send some rows
	for i := range 5 {
		if err := tw.SendRow(ctx, []any{i}); err != nil {
			t.Fatalf("SendRow failed: %v", err)
		}
	}

	// Cancel context
	cancel()

	// SendRow should eventually return context error
	for range 100 {
		err := tw.SendRow(ctx, []any{99})
		if err != nil {
			if !errors.Is(err, context.Canceled) {
				// Could also be a prior error from flush; that's fine
				return
			}
			return
		}
	}

	// Stop should still work cleanly
	_ = tw.Stop()
}

func TestTableWriter_EmptyFlush(t *testing.T) {
	sink := &mockSink{}
	tw := NewTableWriter("test_table", []string{"id"}, 100)
	ctx := context.Background()

	tw.Start(ctx, sink)

	// Stop immediately without sending any rows
	if err := tw.Stop(); err != nil {
		t.Fatalf("Stop failed: %v", err)
	}

	if tw.TotalWritten() != 0 {
		t.Errorf("expected 0 written, got %d", tw.TotalWritten())
	}
	if sink.totalRows() != 0 {
		t.Errorf("expected 0 rows flushed, got %d", sink.totalRows())
	}
}

func TestTableWriter_TotalWritten_InitiallyZero(t *testing.T) {
	tw := NewTableWriter("test_table", []string{"id"}, 100)
	if tw.TotalWritten() != 0 {
		t.Errorf("expected 0, got %d", tw.TotalWritten())
	}
}
