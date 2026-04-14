package decoder

import "testing"

// --- PositionalRow tests ---

func TestNewPositionalRow(t *testing.T) {
	row := NewPositionalRow(5, "T1", 30, "T1202401CASE001    rest-of-data")

	if row.LineNum() != 5 {
		t.Errorf("LineNum() = %d, want 5", row.LineNum())
	}
	if row.RecordType() != "T1" {
		t.Errorf("RecordType() = %q, want %q", row.RecordType(), "T1")
	}
	if row.DecodedLength() != 30 {
		t.Errorf("DecodedLength() = %d, want 30", row.DecodedLength())
	}
	if row.Data() != "T1202401CASE001    rest-of-data" {
		t.Errorf("Data() = %q, want %q", row.Data(), "T1202401CASE001    rest-of-data")
	}
	if row.RawData() != "T1202401CASE001    rest-of-data" {
		t.Errorf("RawData() = %q, want row data string", row.RawData())
	}
}

func TestPositionalRow_Slice(t *testing.T) {
	row := NewPositionalRow(1, "T1", 20, "T1202401CASE001   ")

	tests := []struct {
		name  string
		start int
		end   int
		want  string
	}{
		{"valid range", 2, 8, "202401"},
		{"first two chars", 0, 2, "T1"},
		{"full data", 0, len(row.Data()), row.Data()},
		{"negative start", -1, 5, ""},
		{"end past length", 0, 100, ""},
		{"start equals end", 5, 5, ""},
		{"start greater than end", 8, 2, ""},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			got := row.Slice(tt.start, tt.end)
			if got != tt.want {
				t.Errorf("Slice(%d, %d) = %q, want %q", tt.start, tt.end, got, tt.want)
			}
		})
	}
}

func TestPositionalRow_ImplementsRow(t *testing.T) {
	var _ Row = (*PositionalRow)(nil)
}

// --- ColumnarRow tests ---

func TestNewColumnarRow(t *testing.T) {
	cols := []any{"val1", 42, 3.14, "val4"}
	row := NewColumnarRow(3, "TE1", 4, cols)

	if row.LineNum() != 3 {
		t.Errorf("LineNum() = %d, want 3", row.LineNum())
	}
	if row.RecordType() != "TE1" {
		t.Errorf("RecordType() = %q, want %q", row.RecordType(), "TE1")
	}
	if row.DecodedLength() != 4 {
		t.Errorf("DecodedLength() = %d, want 4", row.DecodedLength())
	}
	if row.ColumnCount() != 4 {
		t.Errorf("ColumnCount() = %d, want 4", row.ColumnCount())
	}

	rawData, ok := row.RawData().([]any)
	if !ok {
		t.Fatalf("RawData() type = %T, want []any", row.RawData())
	}
	if len(rawData) != 4 {
		t.Errorf("RawData() length = %d, want 4", len(rawData))
	}
}

func TestColumnarRow_Column(t *testing.T) {
	cols := []any{"val1", 42, 3.14}
	row := NewColumnarRow(1, "TE1", 3, cols)

	tests := []struct {
		name  string
		index int
		want  any
	}{
		{"first column", 0, "val1"},
		{"second column", 1, 42},
		{"third column", 2, 3.14},
		{"negative index", -1, nil},
		{"index out of bounds", 5, nil},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			got := row.Column(tt.index)
			if got != tt.want {
				t.Errorf("Column(%d) = %v, want %v", tt.index, got, tt.want)
			}
		})
	}
}

func TestColumnarRow_EmptyColumns(t *testing.T) {
	row := NewColumnarRow(1, "TE1", 0, []any{})

	if row.ColumnCount() != 0 {
		t.Errorf("ColumnCount() = %d, want 0", row.ColumnCount())
	}
	if row.Column(0) != nil {
		t.Errorf("Column(0) = %v, want nil", row.Column(0))
	}
}

func TestColumnarRow_ImplementsRow(t *testing.T) {
	var _ Row = (*ColumnarRow)(nil)
}
