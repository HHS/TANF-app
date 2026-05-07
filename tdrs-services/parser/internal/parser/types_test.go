package parser

import (
	"testing"

	"go-parser/internal/config/schema"
)

// newSchema creates a minimal CompiledSchema for testing.
func newSchema(recordType string, fieldNames ...string) *schema.CompiledSchema {
	sdef := &schema.SchemaDef{
		RecordType: recordType,
		Shared:     make([]schema.FieldDef, len(fieldNames)),
	}
	for i, name := range fieldNames {
		sdef.Shared[i] = schema.FieldDef{Name: name, Type: "string"}
	}
	return sdef.Compile()
}

// newRecord creates a ParsedRecord with field values for testing.
func newRecord(s *schema.CompiledSchema, lineNum int, values map[string]any) *ParsedRecord {
	rec := &ParsedRecord{
		Schema:      s,
		LineNumber:  lineNum,
		DecodedSize: 156,
		Fields:      make([]ParsedField, s.FieldCount),
	}
	for i := range s.Shared {
		rec.Fields[i].Def = &s.Shared[i]
	}
	for name, val := range values {
		rec.Set(name, val)
	}
	return rec
}

// newGroup creates a ParsedGroup with default key fields for testing.
func newGroup(records ...*ParsedRecord) *ParsedGroup {
	return &ParsedGroup{
		Key:          "202401|12345",
		RptMonthYear: "202401",
		CaseNumber:   "12345",
		Records:      records,
	}
}

// --- DecodedGroup tests ---

func TestDecodedGroup_TotalRecords(t *testing.T) {
	tests := []struct {
		name    string
		records []DecodedRecord
		want    int
	}{
		{"empty", nil, 0},
		{"one record", make([]DecodedRecord, 1), 1},
		{"multiple records", make([]DecodedRecord, 5), 5},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			g := &DecodedGroup{DecodedRecords: tt.records}
			if got := g.TotalRecords(); got != tt.want {
				t.Errorf("TotalRecords() = %d, want %d", got, tt.want)
			}
		})
	}
}

// --- DecodedBatch tests ---

func TestDecodedBatch_TotalGroups(t *testing.T) {
	tests := []struct {
		name   string
		groups []*DecodedGroup
		want   int
	}{
		{"empty", nil, 0},
		{"one group", []*DecodedGroup{{}}, 1},
		{"three groups", []*DecodedGroup{{}, {}, {}}, 3},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			b := &DecodedBatch{DecodedGroups: tt.groups}
			if got := b.TotalGroups(); got != tt.want {
				t.Errorf("TotalGroups() = %d, want %d", got, tt.want)
			}
		})
	}
}

func TestDecodedBatch_TotalRecords(t *testing.T) {
	tests := []struct {
		name   string
		groups []*DecodedGroup
		want   int
	}{
		{"empty batch", nil, 0},
		{"empty groups", []*DecodedGroup{{}, {}}, 0},
		{
			"mixed groups",
			[]*DecodedGroup{
				{DecodedRecords: make([]DecodedRecord, 3)},
				{DecodedRecords: make([]DecodedRecord, 2)},
			},
			5,
		},
		{
			"single group single record",
			[]*DecodedGroup{
				{DecodedRecords: make([]DecodedRecord, 1)},
			},
			1,
		},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			b := &DecodedBatch{DecodedGroups: tt.groups}
			if got := b.TotalRecords(); got != tt.want {
				t.Errorf("TotalRecords() = %d, want %d", got, tt.want)
			}
		})
	}
}

// --- ParsedRecord tests ---

func TestParsedRecord_Reset(t *testing.T) {
	s := newSchema("T1", "FIELD_A", "FIELD_B")
	rec := newRecord(s, 10, map[string]any{
		"FIELD_A": "hello",
		"FIELD_B": 42,
	})
	rec.SegmentIndex = 2

	rec.Reset()

	if rec.LineNumber != 0 {
		t.Errorf("Reset() LineNumber = %d, want 0", rec.LineNumber)
	}
	if rec.SegmentIndex != 0 {
		t.Errorf("Reset() SegmentIndex = %d, want 0", rec.SegmentIndex)
	}
	for i, f := range rec.Fields {
		if f.Def != nil {
			t.Errorf("Reset() Fields[%d].Def = %v, want nil", i, f.Def)
		}
		if f.Value != nil {
			t.Errorf("Reset() Fields[%d].Value = %v, want nil", i, f.Value)
		}
	}
}

func TestParsedRecord_Reset_PreservesSchemaAndSize(t *testing.T) {
	s := newSchema("T1", "F")
	rec := newRecord(s, 5, map[string]any{"F": "val"})
	rec.Reset()

	if rec.Schema != s {
		t.Error("Reset() should not clear Schema")
	}
	if rec.DecodedSize != 156 {
		t.Errorf("Reset() should not clear DecodedSize, got %d", rec.DecodedSize)
	}
	if len(rec.Fields) != s.FieldCount {
		t.Errorf("Reset() should not shrink Fields slice, got len %d", len(rec.Fields))
	}
}

func TestParsedRecord_Get(t *testing.T) {
	s := newSchema("T1", "NAME", "AGE")
	rec := newRecord(s, 1, map[string]any{
		"NAME": "Alice",
		"AGE":  30,
	})

	tests := []struct {
		name      string
		fieldName string
		want      any
	}{
		{"string field", "NAME", "Alice"},
		{"int field", "AGE", 30},
		{"nonexistent field", "MISSING", nil},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			if got := rec.Get(tt.fieldName); got != tt.want {
				t.Errorf("Get(%s) = %v, want %v", tt.fieldName, got, tt.want)
			}
		})
	}
}

func TestParsedRecord_Get_NilValue(t *testing.T) {
	s := newSchema("T1", "EMPTY")
	rec := newRecord(s, 1, nil)
	if got := rec.Get("EMPTY"); got != nil {
		t.Errorf("Get(EMPTY) = %v, want nil", got)
	}
}

func TestParsedRecord_GetField(t *testing.T) {
	s := newSchema("T1", "X")
	rec := newRecord(s, 1, map[string]any{"X": "val"})

	if got := rec.GetField("X"); got != "val" {
		t.Errorf("GetField(X) = %v, want val", got)
	}
	if got := rec.GetField("NOPE"); got != nil {
		t.Errorf("GetField(NOPE) = %v, want nil", got)
	}
}

func TestParsedRecord_Set(t *testing.T) {
	s := newSchema("T1", "A", "B")
	rec := newRecord(s, 1, nil)

	t.Run("set existing field", func(t *testing.T) {
		rec.Set("A", "hello")
		if got := rec.Get("A"); got != "hello" {
			t.Errorf("after Set(A, hello), Get(A) = %v", got)
		}
	})

	t.Run("overwrite existing field", func(t *testing.T) {
		rec.Set("A", "world")
		if got := rec.Get("A"); got != "world" {
			t.Errorf("after Set(A, world), Get(A) = %v", got)
		}
	})

	t.Run("set nonexistent field is no-op", func(t *testing.T) {
		rec.Set("MISSING", "value")
		if got := rec.Get("MISSING"); got != nil {
			t.Errorf("Set on nonexistent field should be no-op, got %v", got)
		}
	})

	t.Run("set nil value", func(t *testing.T) {
		rec.Set("B", nil)
		if got := rec.Get("B"); got != nil {
			t.Errorf("Set(B, nil) then Get(B) = %v, want nil", got)
		}
	})
}

func TestParsedRecord_SetField(t *testing.T) {
	s := newSchema("T1", "F1")
	rec := newRecord(s, 1, nil)

	def := &schema.FieldDef{Name: "F1", Type: "string", Required: true}
	rec.SetField(def, "test_value")

	pf := rec.GetParsedField("F1")
	if pf == nil {
		t.Fatal("GetParsedField(F1) returned nil after SetField")
	}
	if pf.Def != def {
		t.Errorf("SetField() Def pointer mismatch")
	}
	if pf.Value != "test_value" {
		t.Errorf("SetField() Value = %v, want test_value", pf.Value)
	}
}

func TestParsedRecord_SetField_UnknownName(t *testing.T) {
	s := newSchema("T1", "F1")
	rec := newRecord(s, 1, nil)

	unknownDef := &schema.FieldDef{Name: "UNKNOWN", Type: "string"}
	rec.SetField(unknownDef, "nope") // should not panic

	if got := rec.Get("UNKNOWN"); got != nil {
		t.Errorf("SetField with unknown name should be no-op, got %v", got)
	}
}

func TestParsedRecord_GetParsedField(t *testing.T) {
	s := newSchema("T1", "X")
	rec := newRecord(s, 1, map[string]any{"X": "val"})

	t.Run("existing field", func(t *testing.T) {
		pf := rec.GetParsedField("X")
		if pf == nil {
			t.Fatal("GetParsedField(X) = nil")
		}
		if pf.Value != "val" {
			t.Errorf("GetParsedField(X).Value = %v, want val", pf.Value)
		}
		if pf.Def == nil {
			t.Error("GetParsedField(X).Def = nil, want non-nil")
		}
	})

	t.Run("nonexistent field", func(t *testing.T) {
		pf := rec.GetParsedField("NOPE")
		if pf != nil {
			t.Errorf("GetParsedField(NOPE) = %v, want nil", pf)
		}
	})
}

func TestParsedRecord_GetParsedField_ReturnsPointerToSliceElement(t *testing.T) {
	s := newSchema("T1", "F")
	rec := newRecord(s, 1, map[string]any{"F": "original"})

	pf := rec.GetParsedField("F")
	pf.Value = "modified"

	if got := rec.Get("F"); got != "modified" {
		t.Errorf("Modifying returned ParsedField should affect record, got %v", got)
	}
}

func TestParsedRecord_GetString(t *testing.T) {
	s := newSchema("T1", "STR", "INT", "NIL", "BOOL")
	rec := newRecord(s, 1, map[string]any{
		"STR":  "hello",
		"INT":  42,
		"BOOL": true,
		// NIL left unset
	})

	tests := []struct {
		name      string
		fieldName string
		want      string
	}{
		{"string value", "STR", "hello"},
		{"int value", "INT", "42"},
		{"nil value", "NIL", ""},
		{"bool value uses fmt", "BOOL", "true"},
		{"nonexistent field", "MISSING", ""},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			if got := rec.GetString(tt.fieldName); got != tt.want {
				t.Errorf("GetString(%s) = %q, want %q", tt.fieldName, got, tt.want)
			}
		})
	}
}

func TestParsedRecord_GetString_NegativeInt(t *testing.T) {
	s := newSchema("T1", "N")
	rec := newRecord(s, 1, map[string]any{"N": -7})
	if got := rec.GetString("N"); got != "-7" {
		t.Errorf("GetString(N) = %q, want -7", got)
	}
}

func TestParsedRecord_GetInt(t *testing.T) {
	s := newSchema("T1", "INT", "STR_NUM", "STR_EMPTY", "STR_BAD", "NIL", "BOOL", "STR_NEG")
	rec := newRecord(s, 1, map[string]any{
		"INT":       99,
		"STR_NUM":   "123",
		"STR_EMPTY": "",
		"STR_BAD":   "abc",
		"BOOL":      true,
		"STR_NEG":   "-5",
		// NIL left unset
	})

	tests := []struct {
		name      string
		fieldName string
		want      int
	}{
		{"int value", "INT", 99},
		{"numeric string", "STR_NUM", 123},
		{"empty string", "STR_EMPTY", 0},
		{"non-numeric string", "STR_BAD", 0},
		{"nil value", "NIL", 0},
		{"unsupported type", "BOOL", 0},
		{"nonexistent field", "MISSING", 0},
		{"negative numeric string", "STR_NEG", -5},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			if got := rec.GetInt(tt.fieldName); got != tt.want {
				t.Errorf("GetInt(%s) = %d, want %d", tt.fieldName, got, tt.want)
			}
		})
	}
}

func TestParsedRecord_SumFields(t *testing.T) {
	s := newSchema("T1", "A", "B", "C", "TEXT")
	rec := newRecord(s, 1, map[string]any{
		"A":    10,
		"B":    "20",
		"C":    "",
		"TEXT": "nope",
	})

	tests := []struct {
		name       string
		fieldNames []any
		want       int
	}{
		{"sums numeric fields", []any{"A", "B"}, 30},
		{"ignores blanks and non-numeric values", []any{"A", "C", "TEXT"}, 10},
		{"ignores missing and non-string field names", []any{"A", "MISSING", 123}, 10},
		{"empty input", nil, 0},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			if got := rec.SumFields(tt.fieldNames); got != tt.want {
				t.Errorf("SumFields(%v) = %d, want %d", tt.fieldNames, got, tt.want)
			}
		})
	}
}

func TestParsedRecord_GetRecordType(t *testing.T) {
	tests := []struct {
		recordType string
	}{
		{"T1"},
		{"T5"},
		{"HEADER"},
	}
	for _, tt := range tests {
		t.Run(tt.recordType, func(t *testing.T) {
			s := newSchema(tt.recordType, "F")
			rec := newRecord(s, 1, nil)
			if got := rec.GetRecordType(); got != tt.recordType {
				t.Errorf("GetRecordType() = %s, want %s", got, tt.recordType)
			}
		})
	}
}

func TestParsedRecord_GetLineNumber(t *testing.T) {
	s := newSchema("T1", "F")
	rec := newRecord(s, 42, nil)
	if got := rec.GetLineNumber(); got != 42 {
		t.Errorf("GetLineNumber() = %d, want 42", got)
	}
}

func TestParsedRecord_GetDecodedSize(t *testing.T) {
	s := newSchema("T1", "F")
	rec := newRecord(s, 1, nil)

	if got := rec.GetDecodedSize(); got != 156 {
		t.Errorf("GetDecodedSize() = %d, want 156", got)
	}

	rec.DecodedSize = 200
	if got := rec.GetDecodedSize(); got != 200 {
		t.Errorf("GetDecodedSize() = %d, want 200", got)
	}
}

func TestParsedRecord_IsFieldRequired(t *testing.T) {
	s := newSchema("T1", "REQ", "OPT")
	s.Shared[0].Required = true

	rec := newRecord(s, 1, map[string]any{
		"REQ": "val",
		"OPT": "val",
	})

	tests := []struct {
		name      string
		fieldName string
		want      bool
	}{
		{"required field", "REQ", true},
		{"optional field", "OPT", false},
		{"nonexistent field", "MISSING", false},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			if got := rec.IsFieldRequired(tt.fieldName); got != tt.want {
				t.Errorf("IsFieldRequired(%s) = %v, want %v", tt.fieldName, got, tt.want)
			}
		})
	}
}

func TestParsedRecord_IsFieldRequired_NilDef(t *testing.T) {
	s := newSchema("T1", "F")
	rec := &ParsedRecord{
		Schema: s,
		Fields: make([]ParsedField, s.FieldCount),
	}
	// Fields[0].Def is nil by default
	if rec.IsFieldRequired("F") {
		t.Error("IsFieldRequired should return false when Def is nil")
	}
}

func TestParsedRecord_EqualFields(t *testing.T) {
	s := newSchema("T1", "A", "B")

	t.Run("equal records", func(t *testing.T) {
		r1 := newRecord(s, 1, map[string]any{"A": "x", "B": "y"})
		r2 := newRecord(s, 2, map[string]any{"A": "x", "B": "y"})
		if !r1.EqualFields(r2) {
			t.Error("EqualFields() = false for identical field values")
		}
	})

	t.Run("different values", func(t *testing.T) {
		r1 := newRecord(s, 1, map[string]any{"A": "x", "B": "y"})
		r2 := newRecord(s, 1, map[string]any{"A": "x", "B": "z"})
		if r1.EqualFields(r2) {
			t.Error("EqualFields() = true for different field values")
		}
	})

	t.Run("nil vs value", func(t *testing.T) {
		r1 := newRecord(s, 1, map[string]any{"A": "x"})
		r2 := newRecord(s, 1, map[string]any{"A": "x", "B": "y"})
		if r1.EqualFields(r2) {
			t.Error("EqualFields() = true when one has nil, other has value")
		}
	})

	t.Run("both empty", func(t *testing.T) {
		r1 := newRecord(s, 1, nil)
		r2 := newRecord(s, 1, nil)
		if !r1.EqualFields(r2) {
			t.Error("EqualFields() = false for two records with no values set")
		}
	})

	t.Run("different def pointers", func(t *testing.T) {
		r1 := newRecord(s, 1, nil)
		r2 := &ParsedRecord{
			Schema: s,
			Fields: make([]ParsedField, s.FieldCount),
		}
		// r2 has nil Def pointers, r1 has them set from shared fields
		if r1.EqualFields(r2) {
			t.Error("EqualFields() = true when Def pointers differ")
		}
	})
}

// --- ParsedGroup tests ---

func TestParsedGroup_Getters(t *testing.T) {
	rec := newRecord(newSchema("T1", "F"), 1, nil)
	g := newGroup(rec)

	if got := g.GetKey(); got != "202401|12345" {
		t.Errorf("GetKey() = %s, want 202401|12345", got)
	}
	if got := g.GetRptMonthYear(); got != "202401" {
		t.Errorf("GetRptMonthYear() = %s, want 202401", got)
	}
	if got := g.GetCaseNumber(); got != "12345" {
		t.Errorf("GetCaseNumber() = %s, want 12345", got)
	}
}

func TestParsedGroup_EmptyKey(t *testing.T) {
	g := &ParsedGroup{Key: "", RptMonthYear: "", CaseNumber: ""}
	if got := g.GetKey(); got != "" {
		t.Errorf("GetKey() = %q, want empty", got)
	}
	if got := g.GetRptMonthYear(); got != "" {
		t.Errorf("GetRptMonthYear() = %q, want empty", got)
	}
	if got := g.GetCaseNumber(); got != "" {
		t.Errorf("GetCaseNumber() = %q, want empty", got)
	}
}

// --- ParsedBatch tests ---

func TestParsedBatch_TotalRecords(t *testing.T) {
	s := newSchema("T1", "F")

	tests := []struct {
		name   string
		groups []*ParsedGroup
		want   int
	}{
		{"nil groups", nil, 0},
		{"empty groups", []*ParsedGroup{{}, {}}, 0},
		{
			"mixed groups",
			[]*ParsedGroup{
				{Records: []*ParsedRecord{
					newRecord(s, 1, nil),
					newRecord(s, 2, nil),
				}},
				{Records: []*ParsedRecord{
					newRecord(s, 3, nil),
				}},
			},
			3,
		},
		{
			"single record",
			[]*ParsedGroup{
				{Records: []*ParsedRecord{
					newRecord(s, 1, nil),
				}},
			},
			1,
		},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			pb := &ParsedBatch{Groups: tt.groups}
			if got := pb.TotalRecords(); got != tt.want {
				t.Errorf("TotalRecords() = %d, want %d", got, tt.want)
			}
		})
	}
}
