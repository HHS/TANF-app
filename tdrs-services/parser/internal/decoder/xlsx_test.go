package decoder

import (
	"os"
	"path/filepath"
	"testing"

	"github.com/xuri/excelize/v2"

	"go-parser/internal/config/filespec"
)

// createTestXLSX creates a temporary .xlsx file with the given rows and returns its path.
// Caller is responsible for removing the file.
func createTestXLSX(t *testing.T, rows [][]string) string {
	t.Helper()

	f := excelize.NewFile()
	sheet := f.GetSheetName(0)

	for i, row := range rows {
		for j, val := range row {
			cell, err := excelize.CoordinatesToCellName(j+1, i+1)
			if err != nil {
				t.Fatalf("CoordinatesToCellName(%d, %d) error: %v", j+1, i+1, err)
			}
			if err := f.SetCellValue(sheet, cell, val); err != nil {
				t.Fatalf("SetCellValue(%s, %q) error: %v", cell, val, err)
			}
		}
	}

	path := filepath.Join(t.TempDir(), "test.xlsx")
	if err := f.SaveAs(path); err != nil {
		t.Fatalf("SaveAs(%s) error: %v", path, err)
	}
	if err := f.Close(); err != nil {
		t.Fatalf("Close() error: %v", err)
	}

	return path
}

func TestXLSXDecoder_Format(t *testing.T) {
	path := createTestXLSX(t, [][]string{{"a", "b"}})

	dec, err := NewXLSXDecoder(path, "TE1")
	if err != nil {
		t.Fatalf("NewXLSXDecoder() error: %v", err)
	}
	defer dec.Close()

	if dec.Format() != filespec.FormatColumnar {
		t.Errorf("Format() = %s, want %s", dec.Format(), filespec.FormatColumnar)
	}
}

func TestXLSXDecoder_ReadFirst_BuffersFirstRow(t *testing.T) {
	path := createTestXLSX(t, [][]string{{"a", "b"}, {"c", "d"}})

	dec, err := NewXLSXDecoder(path, "TE1")
	if err != nil {
		t.Fatalf("NewXLSXDecoder() error: %v", err)
	}
	defer dec.Close()

	row, err := dec.ReadFirst()
	if err != nil {
		t.Fatalf("ReadFirst() error: %v", err)
	}
	cr := row.(*ColumnarRow)
	if cr.ColumnCount() != 2 {
		t.Fatalf("ReadFirst() ColumnCount() = %d, want 2", cr.ColumnCount())
	}
	if got := cr.Column(0); got != "a" {
		t.Errorf("ReadFirst() Column(0) = %v, want %q", got, "a")
	}

	var rows []Row
	for row, err := range dec.Rows() {
		if err != nil {
			t.Fatalf("Rows() error: %v", err)
		}
		rows = append(rows, row)
	}
	if len(rows) != 2 {
		t.Fatalf("Rows() got %d rows, want 2", len(rows))
	}
	if got := rows[0].(*ColumnarRow).Column(0); got != "a" {
		t.Errorf("Rows() first row Column(0) = %v, want buffered first row", got)
	}
}

func TestXLSXDecoder_Rows(t *testing.T) {
	path := createTestXLSX(t, [][]string{
		{"val1", "val2", "val3"},
		{"val4", "val5", "val6"},
		{"val7", "val8", "val9"},
	})

	dec, err := NewXLSXDecoder(path, "TE1")
	if err != nil {
		t.Fatalf("NewXLSXDecoder() error: %v", err)
	}
	defer dec.Close()

	var rows []Row
	for row, err := range dec.Rows() {
		if err != nil {
			t.Fatalf("Rows() error: %v", err)
		}
		rows = append(rows, row)
	}

	if len(rows) != 3 {
		t.Fatalf("got %d rows, want 3", len(rows))
	}

	for i, row := range rows {
		if row.LineNum() != i+1 {
			t.Errorf("row %d: LineNum() = %d, want %d", i, row.LineNum(), i+1)
		}
		if row.RecordType() != "TE1" {
			t.Errorf("row %d: RecordType() = %q, want %q", i, row.RecordType(), "TE1")
		}
	}

	// Check first row column values
	cr := rows[0].(*ColumnarRow)
	if cr.ColumnCount() != 3 {
		t.Errorf("first row ColumnCount() = %d, want 3", cr.ColumnCount())
	}
	if cr.Column(0) != "val1" {
		t.Errorf("first row Column(0) = %v, want %q", cr.Column(0), "val1")
	}
	if cr.Column(2) != "val3" {
		t.Errorf("first row Column(2) = %v, want %q", cr.Column(2), "val3")
	}
}

func TestXLSXDecoder_Rows_SkipsEmptyRows(t *testing.T) {
	path := createTestXLSX(t, [][]string{
		{"val1", "val2"},
		{"", ""},
		{"val3", "val4"},
	})

	dec, err := NewXLSXDecoder(path, "TE1")
	if err != nil {
		t.Fatalf("NewXLSXDecoder() error: %v", err)
	}
	defer dec.Close()

	var rows []Row
	for row, err := range dec.Rows() {
		if err != nil {
			t.Fatalf("Rows() error: %v", err)
		}
		rows = append(rows, row)
	}

	if len(rows) != 2 {
		t.Fatalf("got %d rows, want 2 (empty row should be skipped)", len(rows))
	}
}

func TestXLSXDecoder_Rows_SkipsComments(t *testing.T) {
	path := createTestXLSX(t, [][]string{
		{"val1", "val2"},
		{"# this is a comment", "ignored"},
		{"val3", "val4"},
	})

	dec, err := NewXLSXDecoder(path, "TE1")
	if err != nil {
		t.Fatalf("NewXLSXDecoder() error: %v", err)
	}
	defer dec.Close()

	var rows []Row
	for row, err := range dec.Rows() {
		if err != nil {
			t.Fatalf("Rows() error: %v", err)
		}
		rows = append(rows, row)
	}

	if len(rows) != 2 {
		t.Fatalf("got %d rows, want 2 (comment row should be skipped)", len(rows))
	}
}

func TestXLSXDecoder_Rows_DecodedLength(t *testing.T) {
	path := createTestXLSX(t, [][]string{
		{"a", "b", "c", "d"},
	})

	dec, err := NewXLSXDecoder(path, "TE1")
	if err != nil {
		t.Fatalf("NewXLSXDecoder() error: %v", err)
	}
	defer dec.Close()

	for row, err := range dec.Rows() {
		if err != nil {
			t.Fatalf("Rows() error: %v", err)
		}
		if row.DecodedLength() != 4 {
			t.Errorf("DecodedLength() = %d, want 4", row.DecodedLength())
		}
	}
}

func TestXLSXDecoder_Rows_EarlyBreak(t *testing.T) {
	path := createTestXLSX(t, [][]string{
		{"a", "b"},
		{"c", "d"},
		{"e", "f"},
	})

	dec, err := NewXLSXDecoder(path, "TE1")
	if err != nil {
		t.Fatalf("NewXLSXDecoder() error: %v", err)
	}
	defer dec.Close()

	var count int
	for _, err := range dec.Rows() {
		if err != nil {
			t.Fatalf("Rows() error: %v", err)
		}
		count++
		if count == 1 {
			break
		}
	}

	if count != 1 {
		t.Errorf("got %d rows before break, want 1", count)
	}
}

func TestXLSXDecoder_Close(t *testing.T) {
	path := createTestXLSX(t, [][]string{{"a"}})

	dec, err := NewXLSXDecoder(path, "TE1")
	if err != nil {
		t.Fatalf("NewXLSXDecoder() error: %v", err)
	}

	if err := dec.Close(); err != nil {
		t.Errorf("Close() error: %v", err)
	}
}

func TestNewXLSXDecoder_InvalidPath(t *testing.T) {
	_, err := NewXLSXDecoder("/nonexistent/path/file.xlsx", "TE1")
	if err == nil {
		t.Fatal("NewXLSXDecoder() expected error for invalid path")
	}
}

func TestNewXLSXDecoder_InvalidFile(t *testing.T) {
	// Create a file that isn't valid XLSX
	path := filepath.Join(t.TempDir(), "notxlsx.xlsx")
	if err := os.WriteFile(path, []byte("not an xlsx file"), 0644); err != nil {
		t.Fatalf("WriteFile() error: %v", err)
	}

	_, err := NewXLSXDecoder(path, "TE1")
	if err == nil {
		t.Fatal("NewXLSXDecoder() expected error for invalid XLSX file")
	}
}

func TestXLSXDecoder_Rows_SingleColumn(t *testing.T) {
	path := createTestXLSX(t, [][]string{
		{"only_col"},
		{"another"},
	})

	dec, err := NewXLSXDecoder(path, "TE1")
	if err != nil {
		t.Fatalf("NewXLSXDecoder() error: %v", err)
	}
	defer dec.Close()

	var rows []Row
	for row, err := range dec.Rows() {
		if err != nil {
			t.Fatalf("Rows() error: %v", err)
		}
		rows = append(rows, row)
	}

	if len(rows) != 2 {
		t.Fatalf("got %d rows, want 2", len(rows))
	}

	cr := rows[0].(*ColumnarRow)
	if cr.ColumnCount() != 1 {
		t.Errorf("ColumnCount() = %d, want 1", cr.ColumnCount())
	}
	if cr.Column(0) != "only_col" {
		t.Errorf("Column(0) = %v, want %q", cr.Column(0), "only_col")
	}
}

// --- allEmpty tests ---

func TestAllEmpty(t *testing.T) {
	tests := []struct {
		name string
		cols []string
		want bool
	}{
		{"all empty strings", []string{"", "", ""}, true},
		{"all whitespace", []string{"  ", "\t", " \t "}, true},
		{"one non-empty", []string{"", "val", ""}, false},
		{"all non-empty", []string{"a", "b", "c"}, false},
		{"empty slice", []string{}, true},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			got := allEmpty(tt.cols)
			if got != tt.want {
				t.Errorf("allEmpty(%v) = %v, want %v", tt.cols, got, tt.want)
			}
		})
	}
}
