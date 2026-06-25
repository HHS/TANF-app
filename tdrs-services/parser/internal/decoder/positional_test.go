package decoder

import (
	"io"
	"strings"
	"testing"

	"go-parser/internal/config/filespec"
)

// nopCloser wraps an io.Reader to satisfy io.ReadCloser.
type nopCloser struct {
	io.Reader
}

func (nopCloser) Close() error { return nil }

func newTestPositionalDecoder(content string) *PostitionalDecoder {
	return NewPostitionalDecoder(nopCloser{strings.NewReader(content)})
}

func TestPositionalDecoder_Format(t *testing.T) {
	dec := newTestPositionalDecoder("")
	if dec.Format() != filespec.FormatPositional {
		t.Errorf("Format() = %s, want %s", dec.Format(), filespec.FormatPositional)
	}
}

func TestPositionalDecoder_ReadFirst(t *testing.T) {
	content := "HEADER202401 some data\nT1202401CASE001    rest-of-data\n"
	dec := newTestPositionalDecoder(content)
	defer dec.Close()

	row, err := dec.ReadFirst()
	if err != nil {
		t.Fatalf("ReadFirst() error: %v", err)
	}
	if row == nil {
		t.Fatal("ReadFirst() returned nil row")
	}
	if row.LineNum() != 1 {
		t.Errorf("LineNum() = %d, want 1", row.LineNum())
	}
	if row.RecordType() != "HEADER" {
		t.Errorf("RecordType() = %q, want %q", row.RecordType(), "HEADER")
	}

	pr, ok := row.(*PositionalRow)
	if !ok {
		t.Fatalf("row type = %T, want *PositionalRow", row)
	}
	if pr.Data() != "HEADER202401 some data" {
		t.Errorf("Data() = %q, want %q", pr.Data(), "HEADER202401 some data")
	}
}

func TestPositionalDecoder_ReadFirst_Idempotent(t *testing.T) {
	content := "HEADER202401 some data\nT1202401CASE001    rest-of-data\n"
	dec := newTestPositionalDecoder(content)
	defer dec.Close()

	row1, err := dec.ReadFirst()
	if err != nil {
		t.Fatalf("first ReadFirst() error: %v", err)
	}

	row2, err := dec.ReadFirst()
	if err != nil {
		t.Fatalf("second ReadFirst() error: %v", err)
	}

	if row1 != row2 {
		t.Error("second ReadFirst() returned different row")
	}
}

func TestPositionalDecoder_ReadFirst_EmptyFile(t *testing.T) {
	dec := newTestPositionalDecoder("")
	defer dec.Close()

	row, err := dec.ReadFirst()
	if err != nil {
		t.Fatalf("ReadFirst() error: %v", err)
	}
	if row != nil {
		t.Errorf("ReadFirst() = %v, want nil for empty file", row)
	}
}

func TestPositionalDecoder_Rows(t *testing.T) {
	content := "HEADER202401 data\nT1202401CASE001    rest\nT2202401CASE001    rest\n"
	dec := newTestPositionalDecoder(content)
	defer dec.Close()

	// Read header first
	_, err := dec.ReadFirst()
	if err != nil {
		t.Fatalf("ReadFirst() error: %v", err)
	}

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

	if rows[0].LineNum() != 2 {
		t.Errorf("first row LineNum() = %d, want 2", rows[0].LineNum())
	}
	if rows[0].RecordType() != "T1" {
		t.Errorf("first row RecordType() = %q, want %q", rows[0].RecordType(), "T1")
	}
	if rows[1].LineNum() != 3 {
		t.Errorf("second row LineNum() = %d, want 3", rows[1].LineNum())
	}
	if rows[1].RecordType() != "T2" {
		t.Errorf("second row RecordType() = %q, want %q", rows[1].RecordType(), "T2")
	}
}

func TestPositionalDecoder_Rows_ReturnsFinalLineWithoutNewline(t *testing.T) {
	content := "HEADER202401 data\nTRAILER0000000         "
	dec := newTestPositionalDecoder(content)
	defer dec.Close()

	_, err := dec.ReadFirst()
	if err != nil {
		t.Fatalf("ReadFirst() error: %v", err)
	}

	var rows []Row
	for row, err := range dec.Rows() {
		if err != nil {
			t.Fatalf("Rows() error: %v", err)
		}
		rows = append(rows, row)
	}

	if len(rows) != 1 {
		t.Fatalf("got %d rows, want 1", len(rows))
	}
	if rows[0].LineNum() != 2 {
		t.Errorf("LineNum() = %d, want 2", rows[0].LineNum())
	}
	if rows[0].RecordType() != "TRAILER" {
		t.Errorf("RecordType() = %q, want TRAILER", rows[0].RecordType())
	}
}

func TestPositionalDecoder_Rows_WithoutReadFirst(t *testing.T) {
	content := "HEADER202401 data\nT1202401CASE001    rest\n"
	dec := newTestPositionalDecoder(content)
	defer dec.Close()

	var rows []Row
	for row, err := range dec.Rows() {
		if err != nil {
			t.Fatalf("Rows() error: %v", err)
		}
		rows = append(rows, row)
	}

	// Without ReadFirst, the first row (HEADER) is included
	if len(rows) != 2 {
		t.Fatalf("got %d rows, want 2", len(rows))
	}
	if rows[0].RecordType() != "HEADER" {
		t.Errorf("first row RecordType() = %q, want %q", rows[0].RecordType(), "HEADER")
	}
}

func TestPositionalDecoder_Rows_SkipsComments(t *testing.T) {
	content := "T1202401CASE001    data\n# this is a comment\nT2202401CASE001    data\n"
	dec := newTestPositionalDecoder(content)
	defer dec.Close()

	var rows []Row
	for row, err := range dec.Rows() {
		if err != nil {
			t.Fatalf("Rows() error: %v", err)
		}
		rows = append(rows, row)
	}

	if len(rows) != 2 {
		t.Fatalf("got %d rows, want 2 (comment should be skipped)", len(rows))
	}
}

func TestPositionalDecoder_Rows_HandlesCarriageReturn(t *testing.T) {
	content := "T1202401CASE001    data\r\nT2202401CASE001    data\r\n"
	dec := newTestPositionalDecoder(content)
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

	pr := rows[0].(*PositionalRow)
	if strings.ContainsRune(pr.Data(), '\r') {
		t.Error("row data should not contain carriage return")
	}
}

func TestPositionalDecoder_Rows_EmptyFile(t *testing.T) {
	dec := newTestPositionalDecoder("")
	defer dec.Close()

	var count int
	for _, err := range dec.Rows() {
		if err != nil {
			t.Fatalf("Rows() error: %v", err)
		}
		count++
	}

	if count != 0 {
		t.Errorf("got %d rows, want 0 for empty file", count)
	}
}

func TestPositionalDecoder_Rows_DecodedLength(t *testing.T) {
	line := "T1202401CASE001    data"
	content := line + "\n"
	dec := newTestPositionalDecoder(content)
	defer dec.Close()

	for row, err := range dec.Rows() {
		if err != nil {
			t.Fatalf("Rows() error: %v", err)
		}
		// DecodedLength should be the trimmed line length (newlines/CR stripped)
		if row.DecodedLength() != len(line) {
			t.Errorf("DecodedLength() = %d, want %d", row.DecodedLength(), len(line))
		}
	}
}

func TestPositionalDecoder_Close(t *testing.T) {
	dec := newTestPositionalDecoder("some data\n")
	if err := dec.Close(); err != nil {
		t.Errorf("Close() error: %v", err)
	}
}

func TestPositionalDecoder_Rows_EarlyBreak(t *testing.T) {
	content := "T1line1\nT2line2\nT3line3\n"
	dec := newTestPositionalDecoder(content)
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

func TestDetectRecordTypeFromPrefix(t *testing.T) {
	tests := []struct {
		line string
		want string
	}{
		{"HEADER202401 some data", "HEADER"},
		{"TRAILER0000001000", "TRAILER"},
		{"T1202401CASE001", "T1"},
		{"T2202401CASE001", "T2"},
		{"T3202401CASE001", "T3"},
		{"AB", "AB"},
		{"X", ""},
		{"", ""},
	}

	for _, tt := range tests {
		t.Run(tt.line, func(t *testing.T) {
			got := detectRecordTypeFromPrefix(tt.line)
			if got != tt.want {
				t.Errorf("detectRecordTypeFromPrefix(%q) = %q, want %q", tt.line, got, tt.want)
			}
		})
	}
}
