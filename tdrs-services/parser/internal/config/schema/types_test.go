package schema

import (
	"testing"
)

func TestCompile_SingleSegment(t *testing.T) {
	s := &SchemaDef{
		RecordType: "T1",
		Program:    "TAN",
		Section:    1,
		Format:     "positional",
		Shared: []FieldDef{
			{Name: "RecordType", Item: "0", Start: 0, End: 2, Type: "string", Required: true},
			{Name: "RPT_MONTH_YEAR", Item: "4", Start: 2, End: 8, Type: "string", Required: true},
		},
		Segments: []SegmentDef{
			{
				Fields: []FieldDef{
					{Name: "COUNTY_FIPS_CODE", Item: "2", Start: 19, End: 22, Type: "string", Required: true},
					{Name: "ZIP_CODE", Item: "7", Start: 24, End: 29, Type: "string", Required: true},
				},
			},
		},
	}

	cs := s.Compile()

	// Verify shared fields lookup
	if cs.SharedFieldsByName["RecordType"] == nil {
		t.Error("expected RecordType in SharedFieldsByName")
	}
	if cs.SharedFieldsByName["RPT_MONTH_YEAR"] == nil {
		t.Error("expected RPT_MONTH_YEAR in SharedFieldsByName")
	}

	// Verify segment count
	if cs.NumSegments() != 1 {
		t.Errorf("expected 1 segment, got %d", cs.NumSegments())
	}

	// Verify segment field access
	if cs.GetSegmentField(0, "COUNTY_FIPS_CODE") == nil {
		t.Error("expected COUNTY_FIPS_CODE in segment 0")
	}
	if cs.GetSegmentField(0, "ZIP_CODE") == nil {
		t.Error("expected ZIP_CODE in segment 0")
	}
}

func TestCompile_MultiSegment(t *testing.T) {
	// T3-like schema with 2 segments (Child 1 and Child 2)
	s := &SchemaDef{
		RecordType: "T3",
		Program:    "TAN",
		Section:    1,
		Format:     "positional",
		Shared: []FieldDef{
			{Name: "RecordType", Item: "0", Start: 0, End: 2, Type: "string", Required: true},
			{Name: "RPT_MONTH_YEAR", Item: "4", Start: 2, End: 8, Type: "string", Required: true},
			{Name: "CASE_NUMBER", Item: "6", Start: 8, End: 19, Type: "string", Required: true},
		},
		Segments: []SegmentDef{
			{
				Fields: []FieldDef{
					{Name: "FAMILY_AFFILIATION", Item: "67", Start: 19, End: 20, Type: "integer", Required: true},
					{Name: "DATE_OF_BIRTH", Item: "68", Start: 20, End: 28, Type: "string", Required: true},
				},
			},
			{
				Fields: []FieldDef{
					{Name: "FAMILY_AFFILIATION", Item: "67", Start: 60, End: 61, Type: "integer", Required: false},
					{Name: "DATE_OF_BIRTH", Item: "68", Start: 61, End: 69, Type: "string", Required: false},
				},
			},
		},
	}

	cs := s.Compile()

	// Verify shared fields
	if len(cs.SharedFieldsByName) != 3 {
		t.Errorf("expected 3 shared fields, got %d", len(cs.SharedFieldsByName))
	}

	// Verify segment count
	if cs.NumSegments() != 2 {
		t.Errorf("expected 2 segments, got %d", cs.NumSegments())
	}

	// Verify segment 0 (Child 1)
	fa1 := cs.GetSegmentField(0, "FAMILY_AFFILIATION")
	if fa1 == nil {
		t.Error("expected FAMILY_AFFILIATION in segment 0")
	} else if fa1.Start != 19 || fa1.End != 20 {
		t.Errorf("expected segment 0 FAMILY_AFFILIATION at 19-20, got %d-%d", fa1.Start, fa1.End)
	}

	// Verify segment 1 (Child 2)
	fa2 := cs.GetSegmentField(1, "FAMILY_AFFILIATION")
	if fa2 == nil {
		t.Error("expected FAMILY_AFFILIATION in segment 1")
	} else if fa2.Start != 60 || fa2.End != 61 {
		t.Errorf("expected segment 1 FAMILY_AFFILIATION at 60-61, got %d-%d", fa2.Start, fa2.End)
	}

	// Same field name in different segments should have different byte positions
	if fa1 != nil && fa2 != nil && fa1.Start == fa2.Start {
		t.Error("expected different byte positions for same field in different segments")
	}
}

func TestGetSegmentField_OutOfBounds(t *testing.T) {
	s := &SchemaDef{
		RecordType: "T1",
		Program:    "TAN",
		Shared:     []FieldDef{},
		Segments: []SegmentDef{
			{Fields: []FieldDef{{Name: "FIELD1", Type: "string"}}},
		},
	}

	cs := s.Compile()

	// Negative index
	if cs.GetSegmentField(-1, "FIELD1") != nil {
		t.Error("expected nil for negative segment index")
	}

	// Index past end
	if cs.GetSegmentField(5, "FIELD1") != nil {
		t.Error("expected nil for out-of-bounds segment index")
	}

	// Non-existent field
	if cs.GetSegmentField(0, "NONEXISTENT") != nil {
		t.Error("expected nil for non-existent field")
	}
}

func TestFieldIndex(t *testing.T) {
	s := &SchemaDef{
		RecordType: "T1",
		Program:    "TAN",
		Shared: []FieldDef{
			{Name: "RecordType", Type: "string"},
			{Name: "RPT_MONTH_YEAR", Type: "string"},
		},
		Segments: []SegmentDef{
			{
				Fields: []FieldDef{
					{Name: "COUNTY_FIPS_CODE", Type: "string"},
					{Name: "ZIP_CODE", Type: "string"},
				},
			},
		},
	}

	cs := s.Compile()

	// Verify FieldCount
	if cs.FieldCount != 4 {
		t.Errorf("expected FieldCount 4, got %d", cs.FieldCount)
	}

	// Verify FieldIndex mapping
	expectedIndices := map[string]int{
		"RecordType":       0,
		"RPT_MONTH_YEAR":   1,
		"COUNTY_FIPS_CODE": 2,
		"ZIP_CODE":         3,
	}

	for name, expectedIdx := range expectedIndices {
		idx, ok := cs.FieldIndex[name]
		if !ok {
			t.Errorf("expected field %s in FieldIndex", name)
		} else if idx != expectedIdx {
			t.Errorf("expected FieldIndex[%s] = %d, got %d", name, expectedIdx, idx)
		}
	}
}
