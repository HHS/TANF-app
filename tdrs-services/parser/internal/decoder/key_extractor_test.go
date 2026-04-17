package decoder

import (
	"testing"

	"go-parser/internal/config/filespec"
)

func TestPositionalKeyExtractor_ExtractKey(t *testing.T) {
	extractor := &PositionalKeyExtractor{
		RptMonthYear: filespec.PositionDef{Start: 2, End: 8},
		CaseNumber:   filespec.PositionDef{Start: 8, End: 19},
	}

	row := NewPositionalRow(1, "T1", 30, "T1202401CASE001    rest-of-data")
	key, err := extractor.ExtractKey(row)
	if err != nil {
		t.Fatalf("ExtractKey failed: %v", err)
	}
	if key != "202401|CASE001    " {
		t.Errorf("expected key '202401|CASE001    ', got %q", key)
	}
}

func TestPositionalKeyExtractor_TooShort(t *testing.T) {
	extractor := &PositionalKeyExtractor{
		RptMonthYear: filespec.PositionDef{Start: 2, End: 8},
		CaseNumber:   filespec.PositionDef{Start: 8, End: 19},
	}

	row := NewPositionalRow(1, "T1", 7, "T1short")
	_, err := extractor.ExtractKey(row)
	if err == nil {
		t.Fatal("expected error for short row")
	}
}

func TestPositionalKeyExtractor_WrongRowType(t *testing.T) {
	extractor := &PositionalKeyExtractor{
		RptMonthYear: filespec.PositionDef{Start: 2, End: 8},
		CaseNumber:   filespec.PositionDef{Start: 8, End: 19},
	}

	row := NewColumnarRow(1, "T1", 3, []any{"a", "b", "c"})
	_, err := extractor.ExtractKey(row)
	if err == nil {
		t.Fatal("expected error for columnar row")
	}
}

func TestColumnarKeyExtractor_ExtractKey(t *testing.T) {
	extractor := &ColumnarKeyExtractor{
		KeyColumns: []int{0, 1},
	}

	row := NewColumnarRow(1, "TE1", 3, []any{"202401", "CASE001", "other"})
	key, err := extractor.ExtractKey(row)
	if err != nil {
		t.Fatalf("ExtractKey failed: %v", err)
	}
	if key != "202401|CASE001" {
		t.Errorf("expected key '202401|CASE001', got %q", key)
	}
}

func TestColumnarKeyExtractor_MissingColumn(t *testing.T) {
	extractor := &ColumnarKeyExtractor{
		KeyColumns: []int{0, 5}, // column 5 doesn't exist
	}

	row := NewColumnarRow(1, "TE1", 3, []any{"202401", "CASE001", "other"})
	_, err := extractor.ExtractKey(row)
	if err == nil {
		t.Fatal("expected error for missing column")
	}
}

func TestNewKeyExtractor_NoKeyFields(t *testing.T) {
	spec := &filespec.FileSpec{
		Accumulator: filespec.AccumulatorConfig{},
	}

	ke := NewKeyExtractor(spec)
	if ke != nil {
		t.Error("expected nil KeyExtractor when no key fields configured")
	}
}

func TestNewKeyExtractor_WithKeyFields(t *testing.T) {
	spec := &filespec.FileSpec{
		Accumulator: filespec.AccumulatorConfig{
			KeyFields: &filespec.KeyFieldsConfig{
				RptMonthYear: filespec.PositionDef{Start: 2, End: 8},
				CaseNumber:   filespec.PositionDef{Start: 8, End: 19},
			},
		},
	}

	ke := NewKeyExtractor(spec)
	if ke == nil {
		t.Fatal("expected non-nil KeyExtractor")
	}

	pke, ok := ke.(*PositionalKeyExtractor)
	if !ok {
		t.Fatalf("expected *PositionalKeyExtractor, got %T", ke)
	}
	if pke.RptMonthYear.Start != 2 || pke.RptMonthYear.End != 8 {
		t.Errorf("unexpected RptMonthYear positions: %+v", pke.RptMonthYear)
	}
}
