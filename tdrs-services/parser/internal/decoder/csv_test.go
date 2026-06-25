package decoder

import (
	"strings"
	"testing"

	"go-parser/internal/config/filespec"
)

func newTestCSVDecoder(content, recordType string) *CSVDecoder {
	return NewCSVDecoder(nopCloser{strings.NewReader(content)}, recordType)
}

func TestCSVDecoder_Format(t *testing.T) {
	dec := newTestCSVDecoder("", "TE1")
	if dec.Format() != filespec.FormatColumnar {
		t.Errorf("Format() = %s, want %s", dec.Format(), filespec.FormatColumnar)
	}
}

func TestCSVDecoder_ReadFirst_BuffersFirstRow(t *testing.T) {
	dec := newTestCSVDecoder("a,b,c\nd,e,f\n", "TE1")
	defer dec.Close()

	row, err := dec.ReadFirst()
	if err != nil {
		t.Fatalf("ReadFirst() error: %v", err)
	}
	cr := row.(*ColumnarRow)
	if cr.ColumnCount() != 3 {
		t.Fatalf("ReadFirst() ColumnCount() = %d, want 3", cr.ColumnCount())
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

func TestCSVDecoder_Rows(t *testing.T) {
	content := "val1,val2,val3\nval4,val5,val6\nval7,val8,val9\n"
	dec := newTestCSVDecoder(content, "TE1")
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

	// Check first row columns
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

func TestCSVDecoder_Rows_SkipsComments(t *testing.T) {
	content := "val1,val2\n# comment line\nval3,val4\n"
	dec := newTestCSVDecoder(content, "TE1")
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

func TestCSVDecoder_Rows_EmptyFile(t *testing.T) {
	dec := newTestCSVDecoder("", "TE1")
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

func TestCSVDecoder_Rows_VariableFieldCount(t *testing.T) {
	content := "a,b,c\nd,e\nf,g,h,i\n"
	dec := newTestCSVDecoder(content, "TE1")
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

	// Verify variable column counts
	expectedCounts := []int{3, 2, 4}
	for i, row := range rows {
		cr := row.(*ColumnarRow)
		if cr.ColumnCount() != expectedCounts[i] {
			t.Errorf("row %d: ColumnCount() = %d, want %d", i, cr.ColumnCount(), expectedCounts[i])
		}
	}
}

func TestCSVDecoder_Rows_DecodedLength(t *testing.T) {
	content := "a,b,c\n"
	dec := newTestCSVDecoder(content, "TE1")
	defer dec.Close()

	for row, err := range dec.Rows() {
		if err != nil {
			t.Fatalf("Rows() error: %v", err)
		}
		// DecodedLength for CSV is the number of columns
		if row.DecodedLength() != 3 {
			t.Errorf("DecodedLength() = %d, want 3", row.DecodedLength())
		}
	}
}

func TestCSVDecoder_Rows_TrimLeadingSpace(t *testing.T) {
	content := "  val1,  val2,  val3\n"
	dec := newTestCSVDecoder(content, "TE1")
	defer dec.Close()

	for row, err := range dec.Rows() {
		if err != nil {
			t.Fatalf("Rows() error: %v", err)
		}
		cr := row.(*ColumnarRow)
		if cr.Column(0) != "val1" {
			t.Errorf("Column(0) = %v, want %q (leading space should be trimmed)", cr.Column(0), "val1")
		}
	}
}

func TestCSVDecoder_Rows_EarlyBreak(t *testing.T) {
	content := "a,b\nc,d\ne,f\n"
	dec := newTestCSVDecoder(content, "TE1")
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

func TestCSVDecoder_Close(t *testing.T) {
	dec := newTestCSVDecoder("a,b\n", "TE1")
	if err := dec.Close(); err != nil {
		t.Errorf("Close() error: %v", err)
	}
}

func TestCSVDecoder_Rows_QuotedFields(t *testing.T) {
	content := "\"val,1\",\"val 2\",val3\n"
	dec := newTestCSVDecoder(content, "TE1")
	defer dec.Close()

	for row, err := range dec.Rows() {
		if err != nil {
			t.Fatalf("Rows() error: %v", err)
		}
		cr := row.(*ColumnarRow)
		if cr.ColumnCount() != 3 {
			t.Fatalf("ColumnCount() = %d, want 3", cr.ColumnCount())
		}
		if cr.Column(0) != "val,1" {
			t.Errorf("Column(0) = %v, want %q", cr.Column(0), "val,1")
		}
		if cr.Column(1) != "val 2" {
			t.Errorf("Column(1) = %v, want %q", cr.Column(1), "val 2")
		}
	}
}
