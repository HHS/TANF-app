package validation

import (
	"testing"
)

// mockRecord implements the Record interface for testing
type mockRecord struct {
	recordType  string
	lineNumber  int
	decodedSize int
	fields      map[string]any
}

func (r *mockRecord) Get(fieldName string) any {
	return r.fields[fieldName]
}

func (r *mockRecord) GetString(fieldName string) string {
	if v, ok := r.fields[fieldName].(string); ok {
		return v
	}
	return ""
}

func (r *mockRecord) GetInt(fieldName string) int {
	if v, ok := r.fields[fieldName].(int); ok {
		return v
	}
	return 0
}

func (r *mockRecord) GetRecordType() string {
	return r.recordType
}

func (r *mockRecord) GetLineNumber() int {
	return r.lineNumber
}

func (r *mockRecord) GetDecodedSize() int {
	return r.decodedSize
}

// mockGroup implements the Group interface for testing
type mockGroup struct {
	key          string
	rptMonthYear string
	caseNumber   string
}

func (g *mockGroup) GetKey() string {
	return g.key
}

func (g *mockGroup) GetRptMonthYear() string {
	return g.rptMonthYear
}

func (g *mockGroup) GetCaseNumber() string {
	return g.caseNumber
}

// newMockWrappedGroup creates a WrappedGroup for testing
func newMockWrappedGroup(records []Record) *GroupWrapper {
	return WrapGroup(&mockGroup{
		key:          "202401|12345",
		rptMonthYear: "202401",
		caseNumber:   "12345",
	}, records)
}

// TestFieldEnv tests the FieldEnv creation
func TestFieldEnv(t *testing.T) {
	tests := []struct {
		name  string
		value any
	}{
		{"string value", "hello"},
		{"int value", 42},
		{"nil value", nil},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			env := NewFieldEnv(tt.value)
			if env.Value != tt.value {
				t.Errorf("expected Value=%v, got %v", tt.value, env.Value)
			}
		})
	}
}

// TestRecordEnv tests the RecordEnv creation
func TestRecordEnv(t *testing.T) {
	rec := &mockRecord{
		recordType:  "T1",
		lineNumber:  10,
		decodedSize: 156,
		fields: map[string]any{
			"CASE_NUMBER": "12345",
		},
	}

	env := NewRecordEnv(rec)

	if env.RecordType != "T1" {
		t.Errorf("expected RecordType=T1, got %s", env.RecordType)
	}
	if env.LineNumber != 10 {
		t.Errorf("expected LineNumber=10, got %d", env.LineNumber)
	}
	if env.RecordLength != 156 {
		t.Errorf("expected RecordLength=156, got %d", env.RecordLength)
	}
}

// TestGroupEnv tests the GroupEnv creation with aggregates
func TestGroupEnv(t *testing.T) {
	records := []Record{
		&mockRecord{recordType: "T1"},
		&mockRecord{recordType: "T2"},
		&mockRecord{recordType: "T2"},
		&mockRecord{recordType: "T3"},
	}

	group := newMockWrappedGroup(records)
	env := NewGroupEnv(group)

	if env.TotalRecords != 4 {
		t.Errorf("expected TotalRecords=4, got %d", env.TotalRecords)
	}

	if env.RecordCounts["T1"] != 1 {
		t.Errorf("expected T1 count=1, got %d", env.RecordCounts["T1"])
	}
	if env.RecordCounts["T2"] != 2 {
		t.Errorf("expected T2 count=2, got %d", env.RecordCounts["T2"])
	}
	if env.RecordCounts["T3"] != 1 {
		t.Errorf("expected T3 count=1, got %d", env.RecordCounts["T3"])
	}

	if !env.HasType["T1"] {
		t.Error("expected HasType[T1]=true")
	}
	if !env.HasType["T2"] {
		t.Error("expected HasType[T2]=true")
	}
	if env.HasType["T4"] {
		t.Error("expected HasType[T4]=false")
	}
}

// TestCustomFunctions tests the custom validation functions
func TestCustomFunctions(t *testing.T) {
	t.Run("isEmpty", func(t *testing.T) {
		if !isEmpty(nil) {
			t.Error("expected isEmpty(nil)=true")
		}
		if !isEmpty("") {
			t.Error("expected isEmpty('')=true")
		}
		if !isEmpty(0) {
			t.Error("expected isEmpty(0)=true")
		}
		if isEmpty("hello") {
			t.Error("expected isEmpty('hello')=false")
		}
		if isEmpty(42) {
			t.Error("expected isEmpty(42)=false")
		}
	})

	t.Run("isNotEmpty", func(t *testing.T) {
		if isNotEmpty(nil) {
			t.Error("expected isNotEmpty(nil)=false")
		}
		if !isNotEmpty("hello") {
			t.Error("expected isNotEmpty('hello')=true")
		}
	})

	t.Run("isBlank", func(t *testing.T) {
		if !isBlank(nil) {
			t.Error("expected isBlank(nil)=true")
		}
		if !isBlank("   ") {
			t.Error("expected isBlank('   ')=true")
		}
		if isBlank("hello") {
			t.Error("expected isBlank('hello')=false")
		}
	})

	t.Run("extractYear", func(t *testing.T) {
		if extractYear("20240115") != 2024 {
			t.Error("expected year=2024")
		}
		if extractYear("202401") != 2024 {
			t.Error("expected year=2024 from YYYYMM")
		}
		if extractYear("abc") != 0 {
			t.Error("expected year=0 for invalid input")
		}
	})

	t.Run("extractMonth", func(t *testing.T) {
		if extractMonth("20240115") != 1 {
			t.Error("expected month=1")
		}
		if extractMonth("20241231") != 12 {
			t.Error("expected month=12")
		}
	})

	t.Run("extractDay", func(t *testing.T) {
		if extractDay("20240115") != 15 {
			t.Error("expected day=15")
		}
	})

	t.Run("extractQuarter", func(t *testing.T) {
		tests := []struct {
			date     string
			expected int
		}{
			{"20240115", 1},
			{"20240415", 2},
			{"20240815", 3},
			{"20241015", 4},
		}
		for _, tt := range tests {
			if q := extractQuarter(tt.date); q != tt.expected {
				t.Errorf("extractQuarter(%s)=%d, expected %d", tt.date, q, tt.expected)
			}
		}
	})

	t.Run("isValidDate", func(t *testing.T) {
		if !isValidDate("20240115") {
			t.Error("expected isValidDate('20240115')=true")
		}
		if !isValidDate("202401") {
			t.Error("expected isValidDate('202401')=true")
		}
		if isValidDate("20241301") {
			t.Error("expected isValidDate('20241301')=false (invalid month)")
		}
		if isValidDate("invalid") {
			t.Error("expected isValidDate('invalid')=false")
		}
	})

	t.Run("isNumeric", func(t *testing.T) {
		if !isNumeric("12345") {
			t.Error("expected isNumeric('12345')=true")
		}
		if isNumeric("12a45") {
			t.Error("expected isNumeric('12a45')=false")
		}
		if isNumeric("") {
			t.Error("expected isNumeric('')=false")
		}
	})

	t.Run("isAlphaNumeric", func(t *testing.T) {
		if !isAlphaNumeric("abc123") {
			t.Error("expected isAlphaNumeric('abc123')=true")
		}
		if isAlphaNumeric("abc-123") {
			t.Error("expected isAlphaNumeric('abc-123')=false")
		}
	})

	t.Run("toString", func(t *testing.T) {
		if toString(nil) != "" {
			t.Error("expected toString(nil)=''")
		}
		if toString(42) != "42" {
			t.Error("expected toString(42)='42'")
		}
		if toString("hello") != "hello" {
			t.Error("expected toString('hello')='hello'")
		}
	})

	t.Run("toInt", func(t *testing.T) {
		if toInt(nil) != 0 {
			t.Error("expected toInt(nil)=0")
		}
		if toInt("42") != 42 {
			t.Error("expected toInt('42')=42")
		}
		if toInt(42) != 42 {
			t.Error("expected toInt(42)=42")
		}
	})

	t.Run("strLen", func(t *testing.T) {
		if strLen("hello") != 5 {
			t.Error("expected strLen('hello')=5")
		}
		if strLen(12345) != 5 {
			t.Error("expected strLen(12345)=5")
		}
	})

	t.Run("regexMatch", func(t *testing.T) {
		if !regexMatch("hello123", "^[a-z]+[0-9]+$") {
			t.Error("expected match")
		}
		if regexMatch("hello", "^[0-9]+$") {
			t.Error("expected no match")
		}
	})
}

// TestValidateT1HasChildren tests the Cat4 function
func TestValidateT1HasChildren(t *testing.T) {
	t.Run("no T1 records", func(t *testing.T) {
		records := []Record{
			&mockRecord{recordType: "T2"},
		}
		group := newMockWrappedGroup(records)
		if !validateT1HasChildren(group) {
			t.Error("expected true when no T1 records")
		}
	})

	t.Run("T1 with T2 child", func(t *testing.T) {
		records := []Record{
			&mockRecord{recordType: "T1"},
			&mockRecord{recordType: "T2"},
		}
		group := newMockWrappedGroup(records)
		if !validateT1HasChildren(group) {
			t.Error("expected true when T1 has T2 child")
		}
	})

	t.Run("T1 with T3 child", func(t *testing.T) {
		records := []Record{
			&mockRecord{recordType: "T1"},
			&mockRecord{recordType: "T3"},
		}
		group := newMockWrappedGroup(records)
		if !validateT1HasChildren(group) {
			t.Error("expected true when T1 has T3 child")
		}
	})

	t.Run("T1 without children", func(t *testing.T) {
		records := []Record{
			&mockRecord{recordType: "T1"},
		}
		group := newMockWrappedGroup(records)
		if validateT1HasChildren(group) {
			t.Error("expected false when T1 has no children")
		}
	})
}

// TestHasDuplicateField tests the duplicate detection function
func TestHasDuplicateField(t *testing.T) {
	t.Run("no duplicates", func(t *testing.T) {
		records := []Record{
			&mockRecord{recordType: "T2", fields: map[string]any{"SSN": "111111111"}},
			&mockRecord{recordType: "T2", fields: map[string]any{"SSN": "222222222"}},
		}
		group := newMockWrappedGroup(records)
		if hasDuplicateField(group, "T2", "SSN") {
			t.Error("expected no duplicates")
		}
	})

	t.Run("with duplicates", func(t *testing.T) {
		records := []Record{
			&mockRecord{recordType: "T2", fields: map[string]any{"SSN": "111111111"}},
			&mockRecord{recordType: "T2", fields: map[string]any{"SSN": "111111111"}},
		}
		group := newMockWrappedGroup(records)
		if !hasDuplicateField(group, "T2", "SSN") {
			t.Error("expected duplicates")
		}
	})

	t.Run("different record types", func(t *testing.T) {
		records := []Record{
			&mockRecord{recordType: "T2", fields: map[string]any{"SSN": "111111111"}},
			&mockRecord{recordType: "T3", fields: map[string]any{"SSN": "111111111"}},
		}
		group := newMockWrappedGroup(records)
		if hasDuplicateField(group, "T2", "SSN") {
			t.Error("expected no duplicates (different record types)")
		}
	})
}

// TestGetRecordsOfType tests record type filtering
func TestGetRecordsOfType(t *testing.T) {
	records := []Record{
		&mockRecord{recordType: "T1"},
		&mockRecord{recordType: "T2"},
		&mockRecord{recordType: "T2"},
		&mockRecord{recordType: "T3"},
	}
	group := newMockWrappedGroup(records)

	t2Records := getRecordsOfType(group, "T2")
	if len(t2Records) != 2 {
		t.Errorf("expected 2 T2 records, got %d", len(t2Records))
	}

	t4Records := getRecordsOfType(group, "T4")
	if len(t4Records) != 0 {
		t.Errorf("expected 0 T4 records, got %d", len(t4Records))
	}
}

// TestValidationResult tests validation result methods
func TestValidationResult(t *testing.T) {
	t.Run("HasErrors", func(t *testing.T) {
		result := &RecordValidationResult{}
		if result.HasErrors() {
			t.Error("expected no errors")
		}

		result.Cat1Errors = []*ValidationResult{{Valid: false}}
		if !result.HasErrors() {
			t.Error("expected errors")
		}
	})

	t.Run("AllErrors", func(t *testing.T) {
		result := &RecordValidationResult{
			Cat1Errors: []*ValidationResult{{ValidatorID: "v1"}},
			Cat2Errors: []*ValidationResult{{ValidatorID: "v2"}, {ValidatorID: "v3"}},
			Cat3Errors: []*ValidationResult{{ValidatorID: "v4"}},
		}

		all := result.AllErrors()
		if len(all) != 4 {
			t.Errorf("expected 4 errors, got %d", len(all))
		}
	})
}

// TestGroupValidationResult tests group validation result methods
func TestGroupValidationResult(t *testing.T) {
	t.Run("HasErrors with Cat4", func(t *testing.T) {
		result := &GroupValidationResult{
			Cat4Errors: []*ValidationResult{{Valid: false}},
		}
		if !result.HasErrors() {
			t.Error("expected errors")
		}
	})

	t.Run("HasErrors with record errors", func(t *testing.T) {
		result := &GroupValidationResult{
			RecordResults: []*RecordValidationResult{
				{Cat2Errors: []*ValidationResult{{Valid: false}}},
			},
		}
		if !result.HasErrors() {
			t.Error("expected errors")
		}
	})

	t.Run("TotalErrorCount", func(t *testing.T) {
		result := &GroupValidationResult{
			Cat4Errors: []*ValidationResult{{}, {}},
			RecordResults: []*RecordValidationResult{
				{
					Cat1Errors: []*ValidationResult{{}},
					Cat2Errors: []*ValidationResult{{}, {}},
				},
			},
		}
		if count := result.TotalErrorCount(); count != 5 {
			t.Errorf("expected 5 errors, got %d", count)
		}
	})
}

// TestWrapGroup tests the GroupWrapper
func TestWrapGroup(t *testing.T) {
	records := []Record{
		&mockRecord{recordType: "T1"},
		&mockRecord{recordType: "T2"},
	}

	group := &mockGroup{
		key:          "key1",
		rptMonthYear: "202401",
		caseNumber:   "12345",
	}

	wrapped := WrapGroup(group, records)

	if wrapped.GetKey() != "key1" {
		t.Errorf("expected key=key1, got %s", wrapped.GetKey())
	}
	if wrapped.GetRptMonthYear() != "202401" {
		t.Errorf("expected rptMonthYear=202401, got %s", wrapped.GetRptMonthYear())
	}
	if wrapped.GetCaseNumber() != "12345" {
		t.Errorf("expected caseNumber=12345, got %s", wrapped.GetCaseNumber())
	}
	if len(wrapped.GetRecords()) != 2 {
		t.Errorf("expected 2 records, got %d", len(wrapped.GetRecords()))
	}
}
