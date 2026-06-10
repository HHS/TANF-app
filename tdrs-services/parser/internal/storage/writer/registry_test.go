package writer

import (
	"testing"

	"go-parser/internal/config/schema"
)

func TestGetConverter_AllRegistered(t *testing.T) {
	// Verify all expected schema paths have converters
	expected := []string{
		"tanf/t1", "tanf/t2", "tanf/t3", "tanf/t4", "tanf/t5", "tanf/t6", "tanf/t7",
		"ssp/m1", "ssp/m2", "ssp/m3", "ssp/m4", "ssp/m5", "ssp/m6", "ssp/m7",
		"tribal_tanf/t1", "tribal_tanf/t2", "tribal_tanf/t3", "tribal_tanf/t4",
		"tribal_tanf/t5", "tribal_tanf/t6", "tribal_tanf/t7",
		"fra/te1",
	}

	for _, path := range expected {
		conv := GetSerializer(path)
		if conv == nil {
			t.Errorf("expected converter for %q, got nil", path)
		}
	}
}

func TestGetConverter_Unknown(t *testing.T) {
	conv := GetSerializer("unknown/x1")
	if conv != nil {
		t.Errorf("expected nil for unknown schema path, got %v", conv)
	}
}

func TestGetConverter_EmptyPath(t *testing.T) {
	conv := GetSerializer("")
	if conv != nil {
		t.Errorf("expected nil for empty path, got %v", conv)
	}
}

func TestConverterRegistryCount(t *testing.T) {
	// 7 TANF + 7 SSP + 7 Tribal + 1 FRA = 22
	if len(serializerRegistry) != 22 {
		t.Errorf("expected 22 converters in registry, got %d", len(serializerRegistry))
	}
}

func TestSerializeSspM6UsesParsedSspmoeFamiliesField(t *testing.T) {
	cs := makeTestSchema("M6", []schema.FieldDef{
		{Name: "RecordType"},
		{Name: "CALENDAR_QUARTER"},
		{Name: "RPT_MONTH_YEAR"},
		{Name: "SSPMOE_FAMILIES"},
		{Name: "NUM_2_PARENTS"},
		{Name: "NUM_1_PARENTS"},
		{Name: "NUM_NO_PARENTS"},
		{Name: "NUM_RECIPIENTS"},
		{Name: "ADULT_RECIPIENTS"},
		{Name: "CHILD_RECIPIENTS"},
		{Name: "NONCUSTODIALS"},
		{Name: "AMT_ASSISTANCE"},
		{Name: "CLOSED_CASES"},
	})
	cs.Path = "ssp/m6"
	rec := makeTestRecord(cs, 7, map[string]any{
		"RecordType":       "M6",
		"CALENDAR_QUARTER": 20214,
		"RPT_MONTH_YEAR":   202112,
		"SSPMOE_FAMILIES":  15869,
		"NUM_2_PARENTS":    1,
		"NUM_1_PARENTS":    2,
		"NUM_NO_PARENTS":   3,
		"NUM_RECIPIENTS":   4,
		"ADULT_RECIPIENTS": 5,
		"CHILD_RECIPIENTS": 6,
		"NONCUSTODIALS":    7,
		"AMT_ASSISTANCE":   8,
		"CLOSED_CASES":     9,
	})

	rows := serializeSspM6(rec, 101)
	if len(rows) != 1 {
		t.Fatalf("expected 1 row, got %d", len(rows))
	}
	if got := rows[0][3]; got != 15869 {
		t.Errorf("expected SSPMOE_FAMILIES at column 3 to be 15869, got %v", got)
	}
}
