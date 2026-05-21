package writer

import (
	"encoding/json"
	"testing"
	"text/template"

	"github.com/jackc/pgx/v5/pgtype"

	"go-parser/internal/config/schema"
	"go-parser/internal/parser"
	"go-parser/internal/validation"
)

// makeTestSchema builds a minimal compiled schema for testing.
func makeTestSchema(recordType string, fields []schema.FieldDef) *schema.CompiledSchema {
	sd := &schema.SchemaDef{
		RecordType: recordType,
		Shared:     fields,
		Segments:   []schema.SegmentDef{},
	}
	cs := sd.Compile()
	cs.Path = "tanf/t1"
	return cs
}

// makeTestRecord builds a ParsedRecord with field values set.
func makeTestRecord(cs *schema.CompiledSchema, lineNumber int, fieldValues map[string]any) *parser.ParsedRecord {
	rec := &parser.ParsedRecord{
		Schema:     cs,
		LineNumber: lineNumber,
		Fields:     make([]parser.ParsedField, cs.FieldCount),
	}
	// Wire up field definitions
	for i := range cs.Shared {
		fd := &cs.Shared[i]
		idx := cs.FieldIndex[fd.Name]
		rec.Fields[idx].Def = fd
	}
	for name, val := range fieldValues {
		rec.Set(name, val)
	}
	return rec
}

func TestConvertError_BasicRow(t *testing.T) {
	cs := makeTestSchema("T1", []schema.FieldDef{
		{Name: "CASE_NUMBER", FriendlyName: "Case Number", Item: "3"},
		{Name: "RPT_MONTH_YEAR", FriendlyName: "Report Month Year", Item: "2", Type: "integer"},
		{Name: "TEST_FIELD", FriendlyName: "Test Field", Item: "10"},
	})

	rec := makeTestRecord(cs, 5, map[string]any{
		"CASE_NUMBER":    "ABC123",
		"RPT_MONTH_YEAR": 202301,
		"TEST_FIELD":     "bad_value",
	})

	msgTmpl, _ := template.New("msg").Parse("Field {{.FriendlyName}} has invalid value")
	vr := &validation.ValidationResult{
		Valid:       false,
		ErrorType:   validation.ErrorTypeFieldValue,
		ValidatorID: "test_validator",
		FieldName:   "TEST_FIELD",
		Validator: &validation.CompiledValidator{
			ID:        "test_validator",
			ErrorType: validation.ErrorTypeFieldValue,
			Message:   msgTmpl,
			Fields:    []string{"TEST_FIELD"},
		},
	}

	uuid := newUUID()
	contentTypeID := int32(42)

	row := SerializeError(vr, rec, &uuid, 100, &contentTypeID)

	// Verify row has correct number of columns
	if len(row) != len(parserErrorColumns) {
		t.Fatalf("expected %d columns, got %d", len(parserErrorColumns), len(row))
	}

	// row_number
	if row[0] != int32(5) {
		t.Errorf("expected row_number=5, got %v", row[0])
	}

	// column_number (always nil)
	if row[1] != nil {
		t.Errorf("expected column_number=nil, got %v", row[1])
	}

	// field_name
	if row[3] != "TEST_FIELD" {
		t.Errorf("expected field_name='TEST_FIELD', got %v", row[3])
	}

	// case_number
	if row[4] != "ABC123" {
		t.Errorf("expected case_number='ABC123', got %v", row[4])
	}

	// rpt_month_year
	if row[5] != int32(202301) {
		t.Errorf("expected rpt_month_year=202301, got %v", row[5])
	}

	// error_type
	if row[7] != "2" { // ErrorTypeFieldValue maps to "2"
		t.Errorf("expected error_type='2', got %v", row[7])
	}

	// content_type_id
	if row[10] != int32(42) {
		t.Errorf("expected content_type_id=42, got %v", row[10])
	}

	// file_id (datafileID)
	if row[11] != int32(100) {
		t.Errorf("expected file_id=100, got %v", row[11])
	}

	// deprecated
	if row[13] != false {
		t.Errorf("expected deprecated=false, got %v", row[13])
	}
}

func TestRenderErrorMessage_WithValidationContext(t *testing.T) {
	cs := makeTestSchema("T2", []schema.FieldDef{
		{Name: "SSN", FriendlyName: "Social Security Number", Item: "9"},
	})
	rec := makeTestRecord(cs, 12, map[string]any{"SSN": "111111111"})

	msgTmpl, _ := template.New("partial_duplicate").Parse(
		"Partial duplicate record detected with record type {{.RecordType}} at line {{.LineNumber}}. Record is a partial duplicate of the record at line number {{.ExistingLineNumber}}. Duplicated fields causing error: {{.DuplicatedFields}}",
	)
	vr := &validation.ValidationResult{
		Valid:       false,
		ErrorType:   validation.ErrorTypeCaseConsistency,
		ValidatorID: "partial_duplicates",
		Context: map[string]any{
			"ExistingLineNumber": 5,
			"DuplicatedFields":   "Item 9 (Social Security Number).",
		},
		Validator: &validation.CompiledValidator{
			ID:        "partial_duplicates",
			ErrorType: validation.ErrorTypeCaseConsistency,
			Message:   msgTmpl,
		},
	}

	got := renderErrorMessage(vr, rec)
	want := "Partial duplicate record detected with record type T2 at line 12. Record is a partial duplicate of the record at line number 5. Duplicated fields causing error: Item 9 (Social Security Number)."
	if got != want {
		t.Errorf("renderErrorMessage() = %q, want %q", got, want)
	}
}

func TestConvertError_NilContentTypeID(t *testing.T) {
	cs := makeTestSchema("T1", []schema.FieldDef{
		{Name: "CASE_NUMBER"},
	})
	rec := makeTestRecord(cs, 1, nil)

	vr := &validation.ValidationResult{
		Valid:       false,
		ErrorType:   validation.ErrorTypeRecordPreCheck,
		ValidatorID: "pre_check",
	}

	row := SerializeError(vr, rec, nil, 1, nil)

	// content_type_id should be nil
	if row[10] != nil {
		t.Errorf("expected content_type_id=nil, got %v", row[10])
	}

	// object_id should be invalid UUID
	objID, ok := row[12].(pgtype.UUID)
	if !ok {
		t.Fatalf("expected pgtype.UUID, got %T", row[12])
	}
	if objID.Valid {
		t.Error("expected invalid UUID when recordUUID is nil")
	}
}

func TestConvertError_NilValidatorMessage(t *testing.T) {
	cs := makeTestSchema("T1", []schema.FieldDef{
		{Name: "CASE_NUMBER"},
	})
	rec := makeTestRecord(cs, 1, nil)

	vr := &validation.ValidationResult{
		Valid:       false,
		ErrorType:   validation.ErrorTypeFieldValue,
		ValidatorID: "my_validator",
		Validator:   nil,
	}

	row := SerializeError(vr, rec, nil, 1, nil)

	// Should fall back to default message
	msg, ok := row[6].(string)
	if !ok {
		t.Fatalf("expected string message, got %T", row[6])
	}
	if msg != "my_validator validation failed" {
		t.Errorf("expected default message, got %q", msg)
	}
}

func TestSerializeError_RecordValidatorMessageIncludesRecordLength(t *testing.T) {
	cs := makeTestSchema("T7", []schema.FieldDef{
		{Name: "RPT_MONTH_YEAR", Type: "integer"},
	})
	rec := makeTestRecord(cs, 2, map[string]any{
		"RPT_MONTH_YEAR": 202010,
	})
	rec.DecodedSize = 156

	msgTmpl, err := template.New("record_length_min").Parse(
		"{{.RecordType}}: record must be at least {{.Params.min}} characters, got {{.RecordLength}}",
	)
	if err != nil {
		t.Fatalf("failed to parse template: %v", err)
	}

	vr := &validation.ValidationResult{
		Valid:       false,
		ErrorType:   validation.ErrorTypeRecordPreCheck,
		ValidatorID: "record_length_min",
		Validator: &validation.CompiledValidator{
			ID:        "record_length_min",
			ErrorType: validation.ErrorTypeRecordPreCheck,
			Message:   msgTmpl,
			Params:    map[string]any{"min": 247},
		},
	}

	row := SerializeError(vr, rec, nil, 1, nil)

	msg, ok := row[6].(string)
	if !ok {
		t.Fatalf("expected string message, got %T", row[6])
	}
	if msg != "T7: record must be at least 247 characters, got 156" {
		t.Errorf("expected rendered record length message, got %q", msg)
	}
}

func TestMapErrorType(t *testing.T) {
	tests := []struct {
		input    string
		expected string
	}{
		{validation.ErrorTypeRecordPreCheck, "7"},
		{validation.ErrorTypeFieldValue, "2"},
		{validation.ErrorTypeValueConsistency, "3"},
		{validation.ErrorTypeCaseConsistency, "4"},
		{"UNKNOWN_TYPE", "3"}, // defaults to VALUE_CONSISTENCY
	}

	for _, tt := range tests {
		result := mapErrorType(tt.input)
		if result != tt.expected {
			t.Errorf("mapErrorType(%q) = %q, want %q", tt.input, result, tt.expected)
		}
	}
}

func TestGetInvolvedFieldNames(t *testing.T) {
	t.Run("field only", func(t *testing.T) {
		vr := &validation.ValidationResult{
			FieldName: "TEST_FIELD",
		}
		names := getInvolvedFieldNames(vr)
		if len(names) != 1 || names[0] != "TEST_FIELD" {
			t.Errorf("expected [TEST_FIELD], got %v", names)
		}
	})

	t.Run("validator fields", func(t *testing.T) {
		vr := &validation.ValidationResult{
			Validator: &validation.CompiledValidator{
				Fields: []string{"FIELD_A", "FIELD_B"},
			},
		}
		names := getInvolvedFieldNames(vr)
		if len(names) != 2 {
			t.Errorf("expected 2 fields, got %d", len(names))
		}
	})

	t.Run("field and validator fields", func(t *testing.T) {
		vr := &validation.ValidationResult{
			FieldName: "MAIN_FIELD",
			Validator: &validation.CompiledValidator{
				Fields: []string{"OTHER_FIELD"},
			},
		}
		names := getInvolvedFieldNames(vr)
		if len(names) != 2 {
			t.Errorf("expected 2 fields, got %d: %v", len(names), names)
		}
	})

	t.Run("no fields", func(t *testing.T) {
		vr := &validation.ValidationResult{}
		names := getInvolvedFieldNames(vr)
		if len(names) != 0 {
			t.Errorf("expected 0 fields, got %d", len(names))
		}
	})
}

func TestBuildFieldsJSON(t *testing.T) {
	cs := makeTestSchema("T1", []schema.FieldDef{
		{Name: "TEST_FIELD", FriendlyName: "Test Field", Item: "10"},
	})
	rec := makeTestRecord(cs, 1, map[string]any{"TEST_FIELD": "val"})

	vr := &validation.ValidationResult{
		FieldName: "TEST_FIELD",
	}

	data := buildFieldsJSON(vr, rec)
	if data == nil {
		t.Fatal("expected non-nil fields_json")
	}

	var result FieldsJSON
	if err := json.Unmarshal(data, &result); err != nil {
		t.Fatalf("failed to unmarshal fields_json: %v", err)
	}

	if result.FriendlyName["TEST_FIELD"] != "Test Field" {
		t.Errorf("expected friendly_name 'Test Field', got %q", result.FriendlyName["TEST_FIELD"])
	}
	if result.ItemNumbers["TEST_FIELD"] != "10" {
		t.Errorf("expected item_number '10', got %q", result.ItemNumbers["TEST_FIELD"])
	}
}

func TestBuildValuesJSON(t *testing.T) {
	cs := makeTestSchema("T1", []schema.FieldDef{
		{Name: "FIELD_A"},
		{Name: "FIELD_B"},
	})
	rec := makeTestRecord(cs, 1, map[string]any{
		"FIELD_A": "value_a",
		"FIELD_B": 42,
	})

	vr := &validation.ValidationResult{
		Validator: &validation.CompiledValidator{
			Fields: []string{"FIELD_A", "FIELD_B"},
		},
	}

	data := buildValuesJSON(vr, rec)
	if data == nil {
		t.Fatal("expected non-nil values_json")
	}

	var result map[string]any
	if err := json.Unmarshal(data, &result); err != nil {
		t.Fatalf("failed to unmarshal values_json: %v", err)
	}

	if result["FIELD_A"] != "value_a" {
		t.Errorf("expected FIELD_A='value_a', got %v", result["FIELD_A"])
	}
}

func TestToErrorRowNumber(t *testing.T) {
	cs := makeTestSchema("T1", nil)
	rec := makeTestRecord(cs, 42, nil)

	result := toErrorRowNumber(rec)
	if result != int32(42) {
		t.Errorf("expected 42, got %v", result)
	}

	// nil record
	if toErrorRowNumber(nil) != nil {
		t.Error("expected nil for nil record")
	}
}

func TestToErrorCaseNumber(t *testing.T) {
	cs := makeTestSchema("T1", []schema.FieldDef{
		{Name: "CASE_NUMBER"},
	})

	t.Run("with case number", func(t *testing.T) {
		rec := makeTestRecord(cs, 1, map[string]any{"CASE_NUMBER": "XYZ"})
		result := toErrorCaseNumber(rec)
		if result != "XYZ" {
			t.Errorf("expected 'XYZ', got %v", result)
		}
	})

	t.Run("empty case number", func(t *testing.T) {
		rec := makeTestRecord(cs, 1, map[string]any{"CASE_NUMBER": ""})
		result := toErrorCaseNumber(rec)
		if result != nil {
			t.Errorf("expected nil for empty case number, got %v", result)
		}
	})

	t.Run("nil record", func(t *testing.T) {
		if toErrorCaseNumber(nil) != nil {
			t.Error("expected nil for nil record")
		}
	})
}

func TestToErrorRptMonthYear(t *testing.T) {
	cs := makeTestSchema("T1", []schema.FieldDef{
		{Name: "RPT_MONTH_YEAR", Type: "integer"},
	})

	t.Run("with value", func(t *testing.T) {
		rec := makeTestRecord(cs, 1, map[string]any{"RPT_MONTH_YEAR": 202301})
		result := toErrorRptMonthYear(rec)
		if result != int32(202301) {
			t.Errorf("expected 202301, got %v", result)
		}
	})

	t.Run("zero value", func(t *testing.T) {
		rec := makeTestRecord(cs, 1, map[string]any{"RPT_MONTH_YEAR": 0})
		result := toErrorRptMonthYear(rec)
		if result != nil {
			t.Errorf("expected nil for zero, got %v", result)
		}
	})

	t.Run("nil record", func(t *testing.T) {
		if toErrorRptMonthYear(nil) != nil {
			t.Error("expected nil for nil record")
		}
	})
}

func TestToErrorMessage(t *testing.T) {
	if toErrorMessage("hello") != "hello" {
		t.Errorf("expected 'hello'")
	}
	if toErrorMessage("") != nil {
		t.Error("expected nil for empty message")
	}
}

func TestToErrorContentTypeID(t *testing.T) {
	id := int32(42)
	if toErrorContentTypeID(&id) != int32(42) {
		t.Errorf("expected 42")
	}
	if toErrorContentTypeID(nil) != nil {
		t.Error("expected nil")
	}
}

func TestToErrorObjectID(t *testing.T) {
	uuid := newUUID()
	result := toErrorObjectID(&uuid)
	if !result.Valid {
		t.Error("expected valid UUID")
	}
	if result.Bytes != uuid.Bytes {
		t.Error("expected same UUID bytes")
	}

	nilResult := toErrorObjectID(nil)
	if nilResult.Valid {
		t.Error("expected invalid UUID for nil input")
	}
}

func TestToErrorFieldName(t *testing.T) {
	vr := &validation.ValidationResult{FieldName: "MY_FIELD"}
	if toErrorFieldName(vr) != "MY_FIELD" {
		t.Errorf("expected 'MY_FIELD'")
	}

	vrEmpty := &validation.ValidationResult{}
	if toErrorFieldName(vrEmpty) != nil {
		t.Error("expected nil for empty field name")
	}
}

func TestGetFieldDef(t *testing.T) {
	cs := makeTestSchema("T1", []schema.FieldDef{
		{Name: "FIELD_A", FriendlyName: "Field A"},
	})
	rec := makeTestRecord(cs, 1, nil)

	fd := getFieldDef(rec, "FIELD_A")
	if fd == nil {
		t.Fatal("expected non-nil FieldDef")
	}
	if fd.FriendlyName != "Field A" {
		t.Errorf("expected 'Field A', got %q", fd.FriendlyName)
	}

	// Unknown field
	if getFieldDef(rec, "UNKNOWN") != nil {
		t.Error("expected nil for unknown field")
	}

	// Nil record
	if getFieldDef(nil, "FIELD_A") != nil {
		t.Error("expected nil for nil record")
	}
}
