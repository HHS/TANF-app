package decoder

import (
	"testing"

	"go-parser/internal/config/filespec"
)

func TestPositionalRow_ExtractKey(t *testing.T) {
	row := NewPositionalRow(1, "T1", 30, "T1202401CASE001    rest-of-data")
	key, err := row.ExtractKey(positionalKeyFields())
	if err != nil {
		t.Fatalf("ExtractKey failed: %v", err)
	}
	if key != "202401|CASE001    " {
		t.Errorf("expected key '202401|CASE001    ', got %q", key)
	}
}

func TestPositionalRow_ExtractKeyTooShort(t *testing.T) {
	row := NewPositionalRow(1, "T1", 7, "T1short")
	_, err := row.ExtractKey(positionalKeyFields())
	if err == nil {
		t.Fatal("expected error for short row")
	}
}

func TestColumnarRow_ExtractKey(t *testing.T) {
	row := NewColumnarRow(1, "TE1", 3, []any{"202401", "CASE001", "other"})
	key, err := row.ExtractKey(columnarKeyFields())
	if err != nil {
		t.Fatalf("ExtractKey failed: %v", err)
	}
	if key != "202401|CASE001" {
		t.Errorf("expected key '202401|CASE001', got %q", key)
	}
}

func TestColumnarRow_ExtractKeyMissingColumn(t *testing.T) {
	row := NewColumnarRow(1, "TE1", 3, []any{"202401", "CASE001", "other"})
	_, err := row.ExtractKey([]filespec.KeyFieldDef{
		{Name: "exit_date", PositionDef: filespec.PositionDef{Start: 0, End: 1}},
		{Name: "ssn", PositionDef: filespec.PositionDef{Start: 5, End: 6}},
	})
	if err == nil {
		t.Fatal("expected error for missing column")
	}
}

func positionalKeyFields() []filespec.KeyFieldDef {
	return []filespec.KeyFieldDef{
		{Name: "rpt_month_year", PositionDef: filespec.PositionDef{Start: 2, End: 8}},
		{Name: "case_number", PositionDef: filespec.PositionDef{Start: 8, End: 19}},
	}
}

func columnarKeyFields() []filespec.KeyFieldDef {
	return []filespec.KeyFieldDef{
		{Name: "exit_date", PositionDef: filespec.PositionDef{Start: 0, End: 1}},
		{Name: "ssn", PositionDef: filespec.PositionDef{Start: 1, End: 2}},
	}
}
