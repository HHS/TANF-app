package writer

import (
	"context"
	"encoding/csv"
	"encoding/json"
	"os"
	"path/filepath"
	"strings"
	"testing"
)

func TestFileSink_JSON(t *testing.T) {
	dir := t.TempDir()
	sink, err := NewFileSink(dir, "json")
	if err != nil {
		t.Fatalf("NewFileSink failed: %v", err)
	}

	ctx := context.Background()
	columns := []string{"id", "name", "value"}
	rows := [][]any{
		{1, "alice", 100},
		{2, "bob", 200},
	}

	written, err := sink.Flush(ctx, "test_table", columns, rows)
	if err != nil {
		t.Fatalf("Flush failed: %v", err)
	}
	if written != 2 {
		t.Errorf("expected 2 written, got %d", written)
	}

	if err := sink.Close(); err != nil {
		t.Fatalf("Close failed: %v", err)
	}

	// Verify NDJSON file contents
	data, err := os.ReadFile(filepath.Join(dir, "test_table.ndjson"))
	if err != nil {
		t.Fatalf("failed to read output file: %v", err)
	}

	lines := strings.Split(strings.TrimSpace(string(data)), "\n")
	if len(lines) != 2 {
		t.Fatalf("expected 2 lines, got %d", len(lines))
	}

	var obj map[string]any
	if err := json.Unmarshal([]byte(lines[0]), &obj); err != nil {
		t.Fatalf("failed to parse JSON: %v", err)
	}
	if obj["name"] != "alice" {
		t.Errorf("expected name 'alice', got %v", obj["name"])
	}
}

func TestFileSink_CSV(t *testing.T) {
	dir := t.TempDir()
	sink, err := NewFileSink(dir, "csv")
	if err != nil {
		t.Fatalf("NewFileSink failed: %v", err)
	}

	ctx := context.Background()
	columns := []string{"id", "name"}
	rows := [][]any{
		{1, "alice"},
		{2, "bob"},
	}

	written, err := sink.Flush(ctx, "test_table", columns, rows)
	if err != nil {
		t.Fatalf("Flush failed: %v", err)
	}
	if written != 2 {
		t.Errorf("expected 2 written, got %d", written)
	}

	if err := sink.Close(); err != nil {
		t.Fatalf("Close failed: %v", err)
	}

	// Verify CSV file contents
	f, err := os.Open(filepath.Join(dir, "test_table.csv"))
	if err != nil {
		t.Fatalf("failed to open CSV: %v", err)
	}
	defer f.Close()

	reader := csv.NewReader(f)
	records, err := reader.ReadAll()
	if err != nil {
		t.Fatalf("failed to read CSV: %v", err)
	}

	// Header + 2 data rows
	if len(records) != 3 {
		t.Fatalf("expected 3 CSV records (header + 2 rows), got %d", len(records))
	}
	if records[0][0] != "id" || records[0][1] != "name" {
		t.Errorf("unexpected header: %v", records[0])
	}
	if records[1][1] != "alice" {
		t.Errorf("expected 'alice', got %q", records[1][1])
	}
	if records[2][1] != "bob" {
		t.Errorf("expected 'bob', got %q", records[2][1])
	}
}

func TestFileSink_MultipleTables(t *testing.T) {
	dir := t.TempDir()
	sink, err := NewFileSink(dir, "json")
	if err != nil {
		t.Fatalf("NewFileSink failed: %v", err)
	}

	ctx := context.Background()

	// Write to two different tables
	_, err = sink.Flush(ctx, "table_a", []string{"x"}, [][]any{{1}})
	if err != nil {
		t.Fatalf("Flush table_a failed: %v", err)
	}
	_, err = sink.Flush(ctx, "table_b", []string{"y"}, [][]any{{2}})
	if err != nil {
		t.Fatalf("Flush table_b failed: %v", err)
	}

	if err := sink.Close(); err != nil {
		t.Fatalf("Close failed: %v", err)
	}

	// Both files should exist
	for _, name := range []string{"table_a.ndjson", "table_b.ndjson"} {
		if _, err := os.Stat(filepath.Join(dir, name)); err != nil {
			t.Errorf("expected file %s to exist: %v", name, err)
		}
	}
}

func TestFileSink_MultipleFlushesToSameTable(t *testing.T) {
	dir := t.TempDir()
	sink, err := NewFileSink(dir, "json")
	if err != nil {
		t.Fatalf("NewFileSink failed: %v", err)
	}

	ctx := context.Background()
	columns := []string{"id"}

	// Two separate flushes to the same table
	sink.Flush(ctx, "test_table", columns, [][]any{{1}})
	sink.Flush(ctx, "test_table", columns, [][]any{{2}})

	if err := sink.Close(); err != nil {
		t.Fatalf("Close failed: %v", err)
	}

	data, err := os.ReadFile(filepath.Join(dir, "test_table.ndjson"))
	if err != nil {
		t.Fatalf("failed to read output: %v", err)
	}

	lines := strings.Split(strings.TrimSpace(string(data)), "\n")
	if len(lines) != 2 {
		t.Errorf("expected 2 lines from two flushes, got %d", len(lines))
	}
}

func TestFileSink_RowShorterThanColumns(t *testing.T) {
	dir := t.TempDir()
	sink, err := NewFileSink(dir, "json")
	if err != nil {
		t.Fatalf("NewFileSink failed: %v", err)
	}

	ctx := context.Background()
	columns := []string{"id", "name", "value"}
	// Row has fewer values than columns
	rows := [][]any{{1}}

	written, err := sink.Flush(ctx, "test_table", columns, rows)
	if err != nil {
		t.Fatalf("Flush failed: %v", err)
	}
	if written != 1 {
		t.Errorf("expected 1 written, got %d", written)
	}

	if err := sink.Close(); err != nil {
		t.Fatalf("Close failed: %v", err)
	}

	data, err := os.ReadFile(filepath.Join(dir, "test_table.ndjson"))
	if err != nil {
		t.Fatalf("failed to read output: %v", err)
	}

	var obj map[string]any
	if err := json.Unmarshal([]byte(strings.TrimSpace(string(data))), &obj); err != nil {
		t.Fatalf("failed to parse JSON: %v", err)
	}

	// Only the first column should have a value
	if obj["id"] != float64(1) {
		t.Errorf("expected id=1, got %v", obj["id"])
	}
}

func TestFileSink_CloseWithNoWrites(t *testing.T) {
	dir := t.TempDir()
	sink, err := NewFileSink(dir, "json")
	if err != nil {
		t.Fatalf("NewFileSink failed: %v", err)
	}

	// Close without writing anything should succeed
	if err := sink.Close(); err != nil {
		t.Fatalf("Close failed: %v", err)
	}
}

func TestFileSink_InvalidDirectory(t *testing.T) {
	// Use a path that can't be created (file as parent)
	tmpFile := filepath.Join(t.TempDir(), "afile")
	if err := os.WriteFile(tmpFile, []byte("x"), 0o644); err != nil {
		t.Fatal(err)
	}

	_, err := NewFileSink(filepath.Join(tmpFile, "subdir"), "json")
	if err == nil {
		t.Fatal("expected error for invalid directory")
	}
}

func TestDatabaseSink_NilPool(t *testing.T) {
	// DatabaseSink constructor should accept nil pool (validation happens on Flush)
	sink := NewDatabaseSink(nil)
	if sink == nil {
		t.Fatal("expected non-nil DatabaseSink")
	}
	if err := sink.Close(); err != nil {
		t.Errorf("Close should succeed: %v", err)
	}
}
