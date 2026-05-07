package validation

import (
	"os"
	"path/filepath"
	"strings"
	"testing"
	"text/template"

	"github.com/expr-lang/expr"

	configpkg "go-parser/internal/config"
	"go-parser/internal/config/schema"
	configValidation "go-parser/internal/config/validation"
	"go-parser/internal/testutil"
)

// Package-level test schemas shared across tests.
var (
	t1Schema = func() *schema.CompiledSchema {
		cs := testutil.NewTestSchema("T1", "CASE_NUMBER", "AMOUNT")
		cs.Shared[0].Required = true
		cs.Shared[1].Required = true
		return cs
	}()
	t2Schema = func() *schema.CompiledSchema {
		cs := testutil.NewTestSchema("T2", "SSN", "FAMILY_AFFILIATION")
		cs.Shared[0].Required = true
		return cs
	}()
	t3Schema = testutil.NewTestSchema("T3", "FAMILY_AFFILIATION")
)

func realConfigDir(t *testing.T) string {
	t.Helper()

	dir := filepath.Join("..", "..", "config")
	if _, err := os.Stat(dir); os.IsNotExist(err) {
		t.Skip("config directory not found")
	}

	return dir
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
	rec := testutil.NewTestRecord(t1Schema, 10, map[string]any{
		"CASE_NUMBER": "12345",
	})

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
	group := testutil.NewTestGroup(
		testutil.NewTestRecord(t1Schema, 1, nil),
		testutil.NewTestRecord(t2Schema, 2, nil),
		testutil.NewTestRecord(t2Schema, 3, nil),
		testutil.NewTestRecord(t3Schema, 4, nil),
	)
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
}

// TestGetRecordsOfType tests record type filtering
func TestGetRecordsOfType(t *testing.T) {
	group := testutil.NewTestGroup(
		testutil.NewTestRecord(t1Schema, 1, nil),
		testutil.NewTestRecord(t2Schema, 2, nil),
		testutil.NewTestRecord(t2Schema, 3, nil),
		testutil.NewTestRecord(t3Schema, 4, nil),
	)

	t2Records := getRecordsOfType(group, "T2")
	if len(t2Records) != 2 {
		t.Errorf("expected 2 T2 records, got %d", len(t2Records))
	}

	t4Records := getRecordsOfType(group, "T4")
	if len(t4Records) != 0 {
		t.Errorf("expected 0 T4 records, got %d", len(t4Records))
	}
}

func TestHasAnyRecordType(t *testing.T) {
	recordCounts := map[string]int{
		"T1": 1,
		"T2": 2,
	}

	if !hasAnyRecordType(recordCounts, []any{"T3", "T2"}) {
		t.Error("expected true when one requested record type is present")
	}
	if hasAnyRecordType(recordCounts, []any{"T3", "T4"}) {
		t.Error("expected false when none of the requested record types are present")
	}
}

func TestAnyRecordOfTypesHasInt(t *testing.T) {
	group := testutil.NewTestGroup(
		testutil.NewTestRecord(t1Schema, 1, nil),
		testutil.NewTestRecord(t2Schema, 2, map[string]any{"FAMILY_AFFILIATION": 2}),
		testutil.NewTestRecord(t3Schema, 3, map[string]any{"FAMILY_AFFILIATION": 1}),
	)

	if !anyRecordOfTypesHasInt(group, []any{"T2", "T3"}, "FAMILY_AFFILIATION", 1) {
		t.Error("expected true when a related record has the requested value")
	}
	if anyRecordOfTypesHasInt(group, []any{"T2", "T3"}, "FAMILY_AFFILIATION", 9) {
		t.Error("expected false when no related record has the requested value")
	}
}

func TestHasAnyRecordOfTypeWithInt(t *testing.T) {
	group := testutil.NewTestGroup(
		testutil.NewTestRecord(t2Schema, 1, map[string]any{"FAMILY_AFFILIATION": 1}),
		testutil.NewTestRecord(t2Schema, 2, map[string]any{"FAMILY_AFFILIATION": 2}),
	)

	if !hasAnyRecordOfTypeWithInt(group, "T2", "FAMILY_AFFILIATION", 1) {
		t.Error("expected true when a matching record exists")
	}
	if hasAnyRecordOfTypeWithInt(group, "T2", "FAMILY_AFFILIATION", 9) {
		t.Error("expected false when no matching record exists")
	}
}

// TestValidationResult tests validation result methods
func TestValidationResult(t *testing.T) {
	t.Run("HasErrors", func(t *testing.T) {
		result := &RecordValidationResult{}
		if result.HasErrors() {
			t.Error("expected no errors")
		}

		result.RecordErrors = []*ValidationResult{{Valid: false}}
		if !result.HasErrors() {
			t.Error("expected errors")
		}
	})

	t.Run("AllErrors", func(t *testing.T) {
		result := &RecordValidationResult{
			RecordErrors: []*ValidationResult{{ValidatorID: "v1"}, {ValidatorID: "v4"}},
			FieldErrors:  []*ValidationResult{{ValidatorID: "v2"}, {ValidatorID: "v3"}},
		}

		all := result.AllErrors()
		if len(all) != 4 {
			t.Errorf("expected 4 errors, got %d", len(all))
		}
	})
}

// TestGroupValidationResult tests group validation result methods
func TestGroupValidationResult(t *testing.T) {
	t.Run("HasErrors with GroupErrors", func(t *testing.T) {
		result := &GroupValidationResult{
			GroupErrors: []*ValidationResult{{Valid: false}},
		}
		if !result.HasErrors() {
			t.Error("expected errors")
		}
	})

	t.Run("HasErrors with record errors", func(t *testing.T) {
		result := &GroupValidationResult{
			RecordResults: []*RecordValidationResult{
				{FieldErrors: []*ValidationResult{{Valid: false}}},
			},
		}
		if !result.HasErrors() {
			t.Error("expected errors")
		}
	})

	t.Run("TotalErrorCount", func(t *testing.T) {
		result := &GroupValidationResult{
			GroupErrors: []*ValidationResult{{}, {}},
			RecordResults: []*RecordValidationResult{
				{
					RecordErrors: []*ValidationResult{{}},
					FieldErrors:  []*ValidationResult{{}, {}},
				},
			},
		}
		if count := result.TotalErrorCount(); count != 5 {
			t.Errorf("expected 5 errors, got %d", count)
		}
	})
}

// TestFieldEnvWithParams tests FieldEnv with Params
func TestFieldEnvWithParams(t *testing.T) {
	params := map[string]any{"n": 9, "min": 0, "max": 99}
	env := NewFieldEnvWithParams("hello", params)

	if env.Value != "hello" {
		t.Errorf("expected Value='hello', got %v", env.Value)
	}
	if env.Params["n"] != 9 {
		t.Errorf("expected Params['n']=9, got %v", env.Params["n"])
	}
	if env.Params["min"] != 0 {
		t.Errorf("expected Params['min']=0, got %v", env.Params["min"])
	}
	if env.Params["max"] != 99 {
		t.Errorf("expected Params['max']=99, got %v", env.Params["max"])
	}
}

// TestRecordEnvWithParams tests RecordEnv with Params
func TestRecordEnvWithParams(t *testing.T) {
	rec := testutil.NewTestRecord(t1Schema, 10, map[string]any{"CASE_NUMBER": "12345"})
	params := map[string]any{"min": 117, "max": 156}

	env := NewRecordEnvWithParams(rec, params)

	if env.RecordType != "T1" {
		t.Errorf("expected RecordType=T1, got %s", env.RecordType)
	}
	if env.RecordLength != 156 {
		t.Errorf("expected RecordLength=156, got %d", env.RecordLength)
	}
	if env.Params["min"] != 117 {
		t.Errorf("expected Params['min']=117, got %v", env.Params["min"])
	}
	if env.Params["max"] != 156 {
		t.Errorf("expected Params['max']=156, got %v", env.Params["max"])
	}
}

// TestGroupEnvWithParams tests GroupEnv with Params
func TestGroupEnvWithParams(t *testing.T) {
	group := testutil.NewTestGroup(
		testutil.NewTestRecord(t1Schema, 1, nil),
		testutil.NewTestRecord(t2Schema, 2, nil),
	)
	params := map[string]any{"record_type": "T1", "min_count": 1}

	env := NewGroupEnvWithParams(group, params)

	if env.TotalRecords != 2 {
		t.Errorf("expected TotalRecords=2, got %d", env.TotalRecords)
	}
	if env.Params["record_type"] != "T1" {
		t.Errorf("expected Params['record_type']='T1', got %v", env.Params["record_type"])
	}
	if env.Params["min_count"] != 1 {
		t.Errorf("expected Params['min_count']=1, got %v", env.Params["min_count"])
	}
}

// TestMergeParams tests the mergeParams function
func TestMergeParams(t *testing.T) {
	t.Run("nil predefined", func(t *testing.T) {
		useSite := map[string]any{"a": 1}
		result := mergeParams(nil, useSite)
		if result["a"] != 1 {
			t.Error("expected useSite to be returned")
		}
	})

	t.Run("nil useSite", func(t *testing.T) {
		predef := map[string]any{"a": 1}
		result := mergeParams(predef, nil)
		if result["a"] != 1 {
			t.Error("expected predef to be returned")
		}
	})

	t.Run("both empty", func(t *testing.T) {
		result := mergeParams(nil, nil)
		if result != nil {
			t.Error("expected nil")
		}
	})

	t.Run("merge with override", func(t *testing.T) {
		predef := map[string]any{"a": 1, "b": 2}
		useSite := map[string]any{"b": 3, "c": 4}
		result := mergeParams(predef, useSite)

		if result["a"] != 1 {
			t.Errorf("expected a=1, got %v", result["a"])
		}
		if result["b"] != 3 {
			t.Errorf("expected b=3 (useSite overrides predef), got %v", result["b"])
		}
		if result["c"] != 4 {
			t.Errorf("expected c=4, got %v", result["c"])
		}
	})
}

// TestParamsInEnv tests that Params field can be set/mutated on environments
func TestParamsInEnv(t *testing.T) {
	t.Run("FieldEnv params mutation", func(t *testing.T) {
		env := &FieldEnv{Value: "test"}
		env.Params = map[string]any{"n": 4}
		if env.Params["n"] != 4 {
			t.Errorf("expected n=4, got %v", env.Params["n"])
		}
		// Mutate for next validator
		env.Params = map[string]any{"n": 9}
		if env.Params["n"] != 9 {
			t.Errorf("expected n=9 after mutation, got %v", env.Params["n"])
		}
	})

	t.Run("RecordEnv params mutation", func(t *testing.T) {
		rec := testutil.NewTestRecord(t1Schema, 1, nil)
		rec.DecodedSize = 100
		env := NewRecordEnv(rec)
		env.Params = map[string]any{"min": 100}
		if env.Params["min"] != 100 {
			t.Errorf("expected min=100, got %v", env.Params["min"])
		}
	})

	t.Run("GroupEnv params mutation", func(t *testing.T) {
		group := testutil.NewTestGroup(testutil.NewTestRecord(t1Schema, 1, nil))
		env := NewGroupEnv(group)
		env.Params = map[string]any{"record_type": "T1"}
		if env.Params["record_type"] != "T1" {
			t.Errorf("expected record_type=T1, got %v", env.Params["record_type"])
		}
	})
}

// TestResolveValidatorPreventsExprOverride tests that predefined validators cannot have expr overridden
func TestResolveValidatorPreventsExprOverride(t *testing.T) {
	registry := newValidatorRegistry()
	registry.predefined[ScopeField] = map[string]*configValidation.ValidatorDef{
		"in_values": {
			ID:      "in_values",
			Expr:    "Value in Params.values",
			Message: "must be one of {{.Params.values}}",
		},
	}
	registry.exprOpts = RegisterFunctions()

	t.Run("allows predefined without expr override", func(t *testing.T) {
		vdef := &configValidation.ValidatorDef{
			ID:     "in_values",
			Params: map[string]any{"values": []any{1, 2, 3}},
		}
		_, err := registry.resolveValidatorByScope(ScopeField, vdef, "")
		if err != nil {
			t.Errorf("expected no error for predefined validator without expr, got: %v", err)
		}
	})

	t.Run("rejects predefined with expr override", func(t *testing.T) {
		vdef := &configValidation.ValidatorDef{
			ID:     "in_values",
			Expr:   "Value in [1, 2, 3]",
			Params: map[string]any{"values": []any{1, 2, 3}},
		}
		_, err := registry.resolveValidatorByScope(ScopeField, vdef, "")
		if err == nil {
			t.Error("expected error when trying to override predefined validator expr")
		}
		if err != nil && !strings.Contains(err.Error(), "predefined") {
			t.Errorf("expected error message to mention 'predefined', got: %v", err)
		}
	})

	t.Run("allows novel validator with expr", func(t *testing.T) {
		vdef := &configValidation.ValidatorDef{
			ID:   "custom_check",
			Expr: "Value > 0",
		}
		_, err := registry.resolveValidatorByScope(ScopeField, vdef, "")
		if err != nil {
			t.Errorf("expected no error for novel validator with expr, got: %v", err)
		}
	})

	t.Run("rejects novel validator without expr", func(t *testing.T) {
		vdef := &configValidation.ValidatorDef{
			ID: "unknown_validator",
		}
		_, err := registry.resolveValidatorByScope(ScopeField, vdef, "")
		if err == nil {
			t.Error("expected error for unknown validator without expr")
		}
	})
}

func TestRealConfig_GroupValidatorBindingsAcrossPrograms(t *testing.T) {
	cfg := configpkg.TestConfig()
	cfg.Global.ConfigDir = realConfigDir(t)

	reg, err := configpkg.NewRegistry(cfg)
	if err != nil {
		t.Fatalf("loading config registry: %v", err)
	}

	validators, err := NewRegistry(cfg, reg)
	if err != nil {
		t.Fatalf("loading validator registry: %v", err)
	}

	tests := []struct {
		filespecKey string
		validatorID string
		params      map[string]any
	}{
		{
			filespecKey: "TAN:1",
			validatorID: "requires_related_record",
			params: map[string]any{
				"record_type":          "T1",
				"related_record_types": []any{"T2", "T3"},
			},
		},
		{
			filespecKey: "SSP:1",
			validatorID: "requires_related_record",
			params: map[string]any{
				"record_type":          "M1",
				"related_record_types": []any{"M2", "M3"},
			},
		},
		{
			filespecKey: "TRIBAL:1",
			validatorID: "requires_related_record",
			params: map[string]any{
				"record_type":          "T1",
				"related_record_types": []any{"T2", "T3"},
			},
		},
		{
			filespecKey: "TAN:2",
			validatorID: "requires_corresponding_record",
			params: map[string]any{
				"record_type":          "T4",
				"required_record_type": "T5",
			},
		},
		{
			filespecKey: "SSP:2",
			validatorID: "requires_corresponding_record",
			params: map[string]any{
				"record_type":          "M4",
				"required_record_type": "M5",
			},
		},
		{
			filespecKey: "TRIBAL:2",
			validatorID: "requires_corresponding_record",
			params: map[string]any{
				"record_type":          "T4",
				"required_record_type": "T5",
			},
		},
	}

	for _, tc := range tests {
		found := false
		for _, validator := range validators.GetGroupValidators(tc.filespecKey) {
			if validator.ID == tc.validatorID && validatorParamsEqual(validator.Params, tc.params) {
				found = true
				break
			}
		}
		if !found {
			t.Errorf("missing validator %s with params %v in %s", tc.validatorID, tc.params, tc.filespecKey)
		}
	}
}

func validatorParamsEqual(actual map[string]any, expected map[string]any) bool {
	if len(actual) != len(expected) {
		return false
	}

	for key, expectedValue := range expected {
		actualValue, ok := actual[key]
		if !ok {
			return false
		}

		expectedSlice, expectedIsSlice := expectedValue.([]any)
		if expectedIsSlice {
			actualSlice, ok := actualValue.([]any)
			if !ok || len(actualSlice) != len(expectedSlice) {
				return false
			}
			for i := range expectedSlice {
				if actualSlice[i] != expectedSlice[i] {
					return false
				}
			}
			continue
		}

		if actualValue != expectedValue {
			return false
		}
	}

	return true
}

// TestGroupValidatorParameterizedExpression tests the generalized Section 1
// relationship expression against parameterized record types.
func TestGroupValidatorParameterizedExpression(t *testing.T) {
	opts := RegisterFunctions()

	exprStr := `RecordCounts[Params.record_type] == 0 or anyRecordOfTypesHasInt(Group, Params.related_record_types, Params.field_name, Params.expected_value)`

	compileOpts := append([]expr.Option{
		expr.Env(&GroupEnv{}),
		expr.AsBool(),
		expr.AllowUndefinedVariables(),
	}, opts...)

	program, err := expr.Compile(exprStr, compileOpts...)
	if err != nil {
		t.Fatalf("failed to compile expression: %v", err)
	}

	t.Run("no T1 records - should pass", func(t *testing.T) {
		group := testutil.NewTestGroup(
			testutil.NewTestRecord(t2Schema, 1, map[string]any{"FAMILY_AFFILIATION": 2}),
		)
		env := NewGroupEnv(group)
		env.Params = map[string]any{
			"record_type":          "T1",
			"related_record_types": []any{"T2", "T3"},
			"field_name":           "FAMILY_AFFILIATION",
			"expected_value":       1,
		}

		result, err := expr.Run(program, env)
		if err != nil {
			t.Fatalf("failed to run: %v", err)
		}
		if result != true {
			t.Errorf("expected true when no T1, got %v", result)
		}
	})

	t.Run("T1 with T2 FAMILY_AFFILIATION=1 - should pass", func(t *testing.T) {
		group := testutil.NewTestGroup(
			testutil.NewTestRecord(t1Schema, 1, nil),
			testutil.NewTestRecord(t2Schema, 2, map[string]any{"FAMILY_AFFILIATION": 1}),
		)
		env := NewGroupEnv(group)
		env.Params = map[string]any{
			"record_type":          "T1",
			"related_record_types": []any{"T2", "T3"},
			"field_name":           "FAMILY_AFFILIATION",
			"expected_value":       1,
		}

		result, err := expr.Run(program, env)
		if err != nil {
			t.Fatalf("failed to run: %v", err)
		}
		if result != true {
			t.Errorf("expected true when T2 has FA=1, got %v", result)
		}
	})

	t.Run("T1 with T3 FAMILY_AFFILIATION=1 - should pass", func(t *testing.T) {
		group := testutil.NewTestGroup(
			testutil.NewTestRecord(t1Schema, 1, nil),
			testutil.NewTestRecord(t3Schema, 2, map[string]any{"FAMILY_AFFILIATION": 1}),
		)
		env := NewGroupEnv(group)
		env.Params = map[string]any{
			"record_type":          "T1",
			"related_record_types": []any{"T2", "T3"},
			"field_name":           "FAMILY_AFFILIATION",
			"expected_value":       1,
		}

		result, err := expr.Run(program, env)
		if err != nil {
			t.Fatalf("failed to run: %v", err)
		}
		if result != true {
			t.Errorf("expected true when T3 has FA=1, got %v", result)
		}
	})

	t.Run("T1 with T2 FAMILY_AFFILIATION=2 only - should fail", func(t *testing.T) {
		group := testutil.NewTestGroup(
			testutil.NewTestRecord(t1Schema, 1, nil),
			testutil.NewTestRecord(t2Schema, 2, map[string]any{"FAMILY_AFFILIATION": 2}),
		)
		env := NewGroupEnv(group)
		env.Params = map[string]any{
			"record_type":          "T1",
			"related_record_types": []any{"T2", "T3"},
			"field_name":           "FAMILY_AFFILIATION",
			"expected_value":       1,
		}

		result, err := expr.Run(program, env)
		if err != nil {
			t.Fatalf("failed to run: %v", err)
		}
		if result != false {
			t.Errorf("expected false when no T2/T3 has FA=1, got %v", result)
		}
	})

	t.Run("T1 with no T2/T3 - should fail", func(t *testing.T) {
		group := testutil.NewTestGroup(
			testutil.NewTestRecord(t1Schema, 1, nil),
		)
		env := NewGroupEnv(group)
		env.Params = map[string]any{
			"record_type":          "T1",
			"related_record_types": []any{"T2", "T3"},
			"field_name":           "FAMILY_AFFILIATION",
			"expected_value":       1,
		}

		result, err := expr.Run(program, env)
		if err != nil {
			t.Fatalf("failed to run: %v", err)
		}
		if result != false {
			t.Errorf("expected false when T1 has no T2/T3, got %v", result)
		}
	})

	t.Run("T1 with multiple T2s, one has FA=1 - should pass", func(t *testing.T) {
		group := testutil.NewTestGroup(
			testutil.NewTestRecord(t1Schema, 1, nil),
			testutil.NewTestRecord(t2Schema, 2, map[string]any{"FAMILY_AFFILIATION": 2}),
			testutil.NewTestRecord(t2Schema, 3, map[string]any{"FAMILY_AFFILIATION": 1}),
			testutil.NewTestRecord(t2Schema, 4, map[string]any{"FAMILY_AFFILIATION": 3}),
		)
		env := NewGroupEnv(group)
		env.Params = map[string]any{
			"record_type":          "T1",
			"related_record_types": []any{"T2", "T3"},
			"field_name":           "FAMILY_AFFILIATION",
			"expected_value":       1,
		}

		result, err := expr.Run(program, env)
		if err != nil {
			t.Fatalf("failed to run: %v", err)
		}
		if result != true {
			t.Errorf("expected true when at least one T2 has FA=1, got %v", result)
		}
	})
}

// TestParameterizedExpressions tests that expr library can access Params
func TestParameterizedExpressions(t *testing.T) {
	t.Run("length validator with Params.n", func(t *testing.T) {
		program, err := expr.Compile(
			"len(Value) == Params.n",
			expr.Env(&FieldEnv{}),
			expr.AsBool(),
			expr.AllowUndefinedVariables(),
		)
		if err != nil {
			t.Fatalf("failed to compile: %v", err)
		}

		env := &FieldEnv{Value: "hello", Params: map[string]any{"n": 5}}
		result, err := expr.Run(program, env)
		if err != nil {
			t.Fatalf("failed to run: %v", err)
		}
		if result != true {
			t.Errorf("expected true for len('hello')==5, got %v", result)
		}

		env.Params = map[string]any{"n": 6}
		result, err = expr.Run(program, env)
		if err != nil {
			t.Fatalf("failed to run: %v", err)
		}
		if result != false {
			t.Errorf("expected false for len('hello')==6, got %v", result)
		}
	})

	t.Run("in_values validator with Params.values", func(t *testing.T) {
		program, err := expr.Compile(
			"Value in Params.values",
			expr.Env(&FieldEnv{}),
			expr.AsBool(),
			expr.AllowUndefinedVariables(),
		)
		if err != nil {
			t.Fatalf("failed to compile: %v", err)
		}

		env := &FieldEnv{Value: 2, Params: map[string]any{"values": []any{1, 2, 3}}}
		result, err := expr.Run(program, env)
		if err != nil {
			t.Fatalf("failed to run: %v", err)
		}
		if result != true {
			t.Errorf("expected true for 2 in [1,2,3], got %v", result)
		}

		env.Value = 5
		result, err = expr.Run(program, env)
		if err != nil {
			t.Fatalf("failed to run: %v", err)
		}
		if result != false {
			t.Errorf("expected false for 5 in [1,2,3], got %v", result)
		}
	})

	t.Run("in_range_int validator with Params.min/max", func(t *testing.T) {
		program, err := expr.Compile(
			"Value >= Params.min and Value <= Params.max",
			expr.Env(&FieldEnv{}),
			expr.AsBool(),
			expr.AllowUndefinedVariables(),
		)
		if err != nil {
			t.Fatalf("failed to compile: %v", err)
		}

		env := &FieldEnv{Value: 50, Params: map[string]any{"min": 0, "max": 99}}
		result, err := expr.Run(program, env)
		if err != nil {
			t.Fatalf("failed to run: %v", err)
		}
		if result != true {
			t.Errorf("expected true for 50 in [0,99], got %v", result)
		}

		env.Value = 100
		result, err = expr.Run(program, env)
		if err != nil {
			t.Fatalf("failed to run: %v", err)
		}
		if result != false {
			t.Errorf("expected false for 100 in [0,99], got %v", result)
		}
	})

	t.Run("record_length_range with Params.min/max", func(t *testing.T) {
		program, err := expr.Compile(
			"RecordLength >= Params.min and RecordLength <= Params.max",
			expr.Env(&RecordEnv{}),
			expr.AsBool(),
			expr.AllowUndefinedVariables(),
		)
		if err != nil {
			t.Fatalf("failed to compile: %v", err)
		}

		rec := testutil.NewTestRecord(t1Schema, 1, nil)
		rec.DecodedSize = 120
		env := NewRecordEnv(rec)
		env.Params = map[string]any{"min": 117, "max": 156}

		result, err := expr.Run(program, env)
		if err != nil {
			t.Fatalf("failed to run: %v", err)
		}
		if result != true {
			t.Errorf("expected true for 120 in [117,156], got %v", result)
		}

		rec2 := testutil.NewTestRecord(t1Schema, 1, nil)
		rec2.DecodedSize = 100
		env2 := NewRecordEnv(rec2)
		env2.Params = map[string]any{"min": 117, "max": 156}

		result, err = expr.Run(program, env2)
		if err != nil {
			t.Fatalf("failed to run: %v", err)
		}
		if result != false {
			t.Errorf("expected false for 100 in [117,156], got %v", result)
		}
	})
}

// --- Additional function tests ---

func TestIsNotBlank(t *testing.T) {
	tests := []struct {
		name     string
		value    any
		expected bool
	}{
		{"nil", nil, false},
		{"empty string", "", false},
		{"whitespace only", "   ", false},
		{"tab and spaces", "  \t  ", false},
		{"non-blank string", "hello", true},
		{"string with spaces", " hello ", true},
		{"zero int", 0, false},
		{"non-zero int", 42, true},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			if got := isNotBlank(tt.value); got != tt.expected {
				t.Errorf("isNotBlank(%v) = %v, want %v", tt.value, got, tt.expected)
			}
		})
	}
}

func TestIsBlankEdgeCases(t *testing.T) {
	// isBlank with non-string, non-nil values falls through to isEmpty
	if !isBlank(0) {
		t.Error("expected isBlank(0)=true (delegates to isEmpty)")
	}
	if isBlank(42) {
		t.Error("expected isBlank(42)=false")
	}
	if !isBlank(int64(0)) {
		t.Error("expected isBlank(int64(0))=true")
	}
	if isBlank(float64(3.14)) {
		t.Error("expected isBlank(3.14)=false")
	}
}

func TestIsEmptyEdgeCases(t *testing.T) {
	tests := []struct {
		name     string
		value    any
		expected bool
	}{
		{"int64 zero", int64(0), true},
		{"int64 nonzero", int64(42), false},
		{"float64 zero", float64(0), true},
		{"float64 nonzero", float64(3.14), false},
		{"bool (unsupported type)", true, false},
		{"slice (unsupported type)", []int{1}, false},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			if got := isEmpty(tt.value); got != tt.expected {
				t.Errorf("isEmpty(%v) = %v, want %v", tt.value, got, tt.expected)
			}
		})
	}
}

func TestToStringEdgeCases(t *testing.T) {
	tests := []struct {
		name     string
		value    any
		expected string
	}{
		{"int64", int64(100), "100"},
		{"float64 integer", float64(42), "42"},
		{"float64 decimal", float64(3.14), "3.14"},
		{"unsupported type", []int{1}, ""},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			if got := toString(tt.value); got != tt.expected {
				t.Errorf("toString(%v) = %q, want %q", tt.value, got, tt.expected)
			}
		})
	}
}

func TestCalculateAge(t *testing.T) {
	tests := []struct {
		name     string
		dob      string
		rptMonth string
		expected int
	}{
		{"29 years old (days/365.25 truncation)", "19940101", "202401", 29},
		{"30 years old", "19940101", "202402", 30},
		{"exact birthday month", "19900601", "202006", 30},
		{"before birthday month", "19900601", "202005", 29},
		{"invalid dob length", "199401", "202401", -1},
		{"invalid rptMonth length", "19940101", "20240101", -1},
		{"invalid dob format", "99999999", "202401", -1},
		{"invalid rptMonth format", "19940101", "999999", -1},
		{"newborn", "20240101", "202401", 0},
		{"negative age (future dob)", "20250101", "202401", -1},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			got := calculateAge(tt.dob, tt.rptMonth)
			if got != tt.expected {
				t.Errorf("calculateAge(%q, %q) = %d, want %d", tt.dob, tt.rptMonth, got, tt.expected)
			}
		})
	}
}

func TestIsValidSSN(t *testing.T) {
	tests := []struct {
		name     string
		ssn      string
		expected bool
	}{
		{"valid SSN", "123456789", true},
		{"valid SSN 2", "001011234", true},
		{"too short", "12345678", false},
		{"too long", "1234567890", false},
		{"non-numeric", "12345678a", false},
		{"area 000", "000123456", false},
		{"area 666", "666123456", false},
		{"area starts with 9", "900123456", false},
		{"group 00", "123004567", false},
		{"serial 0000", "123450000", false},
		{"repeating 111111111", "111111111", false},
		{"repeating 555555555", "555555555", false},
		{"repeating 000000000", "000000000", false},
		{"repeating 999999999", "999999999", false},
		{"empty", "", false},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			if got := isValidSSN(tt.ssn); got != tt.expected {
				t.Errorf("isValidSSN(%q) = %v, want %v", tt.ssn, got, tt.expected)
			}
		})
	}
}

func TestExtractDateEdgeCases(t *testing.T) {
	t.Run("extractYear with short string", func(t *testing.T) {
		if extractYear("abc") != 0 {
			t.Error("expected 0 for short string")
		}
	})

	t.Run("extractMonth with short string", func(t *testing.T) {
		if extractMonth("2024") != 0 {
			t.Error("expected 0 for string shorter than 6")
		}
	})

	t.Run("extractQuarter with invalid month", func(t *testing.T) {
		if extractQuarter("abc") != 0 {
			t.Error("expected 0 for invalid date")
		}
	})

	t.Run("isValidDate with wrong length", func(t *testing.T) {
		if isValidDate("2024") {
			t.Error("expected false for 4-char string")
		}
		if isValidDate("20241301") {
			t.Error("expected false for invalid month in YYYYMMDD")
		}
	})

	t.Run("isValidDate YYYYMM bounds", func(t *testing.T) {
		if isValidDate("189912") {
			t.Error("expected false for year < 1900")
		}
		if isValidDate("210112") {
			t.Error("expected false for year > 2100")
		}
		if isValidDate("202400") {
			t.Error("expected false for month 0")
		}
		if isValidDate("202413") {
			t.Error("expected false for month 13")
		}
		if !isValidDate("190001") {
			t.Error("expected true for year 1900 month 1")
		}
		if !isValidDate("210012") {
			t.Error("expected true for year 2100 month 12")
		}
	})
}

func TestIsAlphaNumericEdgeCases(t *testing.T) {
	if isAlphaNumeric("") {
		t.Error("expected false for empty string")
	}
	if !isAlphaNumeric("ABCdef123") {
		t.Error("expected true for mixed case alphanumeric")
	}
	if isAlphaNumeric("hello world") {
		t.Error("expected false for string with space")
	}
}

func TestAnyToString(t *testing.T) {
	tests := []struct {
		name     string
		value    any
		expected string
	}{
		{"string", "hello", "hello"},
		{"int", 42, "42"},
		{"nil", nil, "<nil>"},
		{"float64", float64(3.14), "3.14"},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			if got := anyToString(tt.value); got != tt.expected {
				t.Errorf("anyToString(%v) = %q, want %q", tt.value, got, tt.expected)
			}
		})
	}
}

func TestToStringSlice(t *testing.T) {
	in := []any{"a", "b", "c"}
	out := toStringSlice(in)
	if len(out) != 3 || out[0] != "a" || out[1] != "b" || out[2] != "c" {
		t.Errorf("toStringSlice(%v) = %v, want [a b c]", in, out)
	}

	// With int values
	in2 := []any{1, 2, 3}
	out2 := toStringSlice(in2)
	if len(out2) != 3 || out2[0] != "1" || out2[1] != "2" || out2[2] != "3" {
		t.Errorf("toStringSlice(%v) = %v, want [1 2 3]", in2, out2)
	}
}

// --- Duplicate detection function tests ---

func TestGetExactDuplicates(t *testing.T) {
	t.Run("no duplicates", func(t *testing.T) {
		group := testutil.NewTestGroup(
			testutil.NewTestRecord(t2Schema, 1, map[string]any{"SSN": "111111111", "FAMILY_AFFILIATION": 1}),
			testutil.NewTestRecord(t2Schema, 2, map[string]any{"SSN": "222222222", "FAMILY_AFFILIATION": 2}),
		)
		dups := getExactDuplicates(group, "T2")
		if len(dups) != 0 {
			t.Errorf("expected 0 duplicates, got %d", len(dups))
		}
	})

	t.Run("one exact duplicate", func(t *testing.T) {
		group := testutil.NewTestGroup(
			testutil.NewTestRecord(t2Schema, 1, map[string]any{"SSN": "111111111", "FAMILY_AFFILIATION": 1}),
			testutil.NewTestRecord(t2Schema, 2, map[string]any{"SSN": "111111111", "FAMILY_AFFILIATION": 1}),
		)
		dups := getExactDuplicates(group, "T2")
		if len(dups) != 1 {
			t.Errorf("expected 1 duplicate, got %d", len(dups))
		}
		if dups[0].GetLineNumber() != 2 {
			t.Errorf("expected duplicate to be line 2, got %d", dups[0].GetLineNumber())
		}
	})

	t.Run("partial match is not exact duplicate", func(t *testing.T) {
		group := testutil.NewTestGroup(
			testutil.NewTestRecord(t2Schema, 1, map[string]any{"SSN": "111111111", "FAMILY_AFFILIATION": 1}),
			testutil.NewTestRecord(t2Schema, 2, map[string]any{"SSN": "111111111", "FAMILY_AFFILIATION": 2}),
		)
		dups := getExactDuplicates(group, "T2")
		if len(dups) != 0 {
			t.Errorf("expected 0 exact duplicates (different FA), got %d", len(dups))
		}
	})

	t.Run("filters by record type", func(t *testing.T) {
		group := testutil.NewTestGroup(
			testutil.NewTestRecord(t2Schema, 1, map[string]any{"SSN": "111111111", "FAMILY_AFFILIATION": 1}),
			testutil.NewTestRecord(t3Schema, 2, map[string]any{"FAMILY_AFFILIATION": 1}),
		)
		dups := getExactDuplicates(group, "T2")
		if len(dups) != 0 {
			t.Errorf("expected 0 duplicates for T2 only, got %d", len(dups))
		}
	})

	t.Run("triple duplicate returns two", func(t *testing.T) {
		group := testutil.NewTestGroup(
			testutil.NewTestRecord(t2Schema, 1, map[string]any{"SSN": "111111111", "FAMILY_AFFILIATION": 1}),
			testutil.NewTestRecord(t2Schema, 2, map[string]any{"SSN": "111111111", "FAMILY_AFFILIATION": 1}),
			testutil.NewTestRecord(t2Schema, 3, map[string]any{"SSN": "111111111", "FAMILY_AFFILIATION": 1}),
		)
		dups := getExactDuplicates(group, "T2")
		if len(dups) != 2 {
			t.Errorf("expected 2 duplicates (first kept), got %d", len(dups))
		}
	})
}

func TestGetPartialDuplicates(t *testing.T) {
	t.Run("no duplicates", func(t *testing.T) {
		group := testutil.NewTestGroup(
			testutil.NewTestRecord(t2Schema, 1, map[string]any{"SSN": "111111111", "FAMILY_AFFILIATION": 1}),
			testutil.NewTestRecord(t2Schema, 2, map[string]any{"SSN": "222222222", "FAMILY_AFFILIATION": 2}),
		)
		dups := getPartialDuplicates(group, "T2", []any{"SSN"})
		if len(dups) != 0 {
			t.Errorf("expected 0 partial duplicates, got %d", len(dups))
		}
	})

	t.Run("partial duplicate (same key field, different other fields)", func(t *testing.T) {
		group := testutil.NewTestGroup(
			testutil.NewTestRecord(t2Schema, 1, map[string]any{"SSN": "111111111", "FAMILY_AFFILIATION": 1}),
			testutil.NewTestRecord(t2Schema, 2, map[string]any{"SSN": "111111111", "FAMILY_AFFILIATION": 2}),
		)
		dups := getPartialDuplicates(group, "T2", []any{"SSN"})
		if len(dups) != 1 {
			t.Errorf("expected 1 partial duplicate, got %d", len(dups))
		}
	})

	t.Run("exact duplicate is excluded from partial duplicates", func(t *testing.T) {
		group := testutil.NewTestGroup(
			testutil.NewTestRecord(t2Schema, 1, map[string]any{"SSN": "111111111", "FAMILY_AFFILIATION": 1}),
			testutil.NewTestRecord(t2Schema, 2, map[string]any{"SSN": "111111111", "FAMILY_AFFILIATION": 1}),
		)
		dups := getPartialDuplicates(group, "T2", []any{"SSN"})
		if len(dups) != 0 {
			t.Errorf("expected 0 partial duplicates (exact match excluded), got %d", len(dups))
		}
	})
}

func TestGetPartialDuplicatesExcluding(t *testing.T) {
	t.Run("excludes records with specified field values", func(t *testing.T) {
		group := testutil.NewTestGroup(
			testutil.NewTestRecord(t2Schema, 1, map[string]any{"SSN": "111111111", "FAMILY_AFFILIATION": 1}),
			testutil.NewTestRecord(t2Schema, 2, map[string]any{"SSN": "111111111", "FAMILY_AFFILIATION": 2}),
			testutil.NewTestRecord(t2Schema, 3, map[string]any{"SSN": "111111111", "FAMILY_AFFILIATION": 3}),
		)
		// Exclude records where FAMILY_AFFILIATION is in [2, 3]
		dups := getPartialDuplicatesExcluding(group, "T2", []any{"SSN"}, "FAMILY_AFFILIATION", []any{2, 3})
		// After excluding FA=2 and FA=3, only FA=1 remains — no duplicates possible
		if len(dups) != 0 {
			t.Errorf("expected 0 duplicates after exclusion, got %d", len(dups))
		}
	})

	t.Run("finds duplicates among non-excluded records", func(t *testing.T) {
		group := testutil.NewTestGroup(
			testutil.NewTestRecord(t2Schema, 1, map[string]any{"SSN": "111111111", "FAMILY_AFFILIATION": 1}),
			testutil.NewTestRecord(t2Schema, 2, map[string]any{"SSN": "111111111", "FAMILY_AFFILIATION": 2}),
			testutil.NewTestRecord(t2Schema, 3, map[string]any{"SSN": "222222222", "FAMILY_AFFILIATION": 3}),
		)
		// Exclude FA=3, leaving FA=1 and FA=2 with same SSN — partial duplicate
		dups := getPartialDuplicatesExcluding(group, "T2", []any{"SSN"}, "FAMILY_AFFILIATION", []any{3})
		if len(dups) != 1 {
			t.Errorf("expected 1 partial duplicate, got %d", len(dups))
		}
	})
}

func TestBuildCompositeKey(t *testing.T) {
	rec := testutil.NewTestRecord(t2Schema, 1, map[string]any{"SSN": "111111111", "FAMILY_AFFILIATION": 1})
	key := buildCompositeKey(rec, []string{"SSN", "FAMILY_AFFILIATION"})
	if key != "111111111|1" {
		t.Errorf("expected '111111111|1', got %q", key)
	}

	// Single field
	key2 := buildCompositeKey(rec, []string{"SSN"})
	if key2 != "111111111" {
		t.Errorf("expected '111111111', got %q", key2)
	}
}

// --- ValidationResult method tests ---

func TestValidationResultBlocksRecord(t *testing.T) {
	vr := &ValidationResult{ErrorType: ErrorTypeRecordPreCheck}
	if !vr.BlocksRecord() {
		t.Error("expected RECORD_PRE_CHECK to block record")
	}

	vr2 := &ValidationResult{ErrorType: ErrorTypeFieldValue}
	if vr2.BlocksRecord() {
		t.Error("expected FIELD_VALUE not to block record")
	}
}

func TestValidationResultBlocksGroup(t *testing.T) {
	vr := &ValidationResult{ErrorType: ErrorTypeCaseConsistency}
	if !vr.BlocksGroup() {
		t.Error("expected CASE_CONSISTENCY to block group")
	}

	vr2 := &ValidationResult{ErrorType: ErrorTypeValueConsistency}
	if vr2.BlocksGroup() {
		t.Error("expected VALUE_CONSISTENCY not to block group")
	}
}

func TestValidationResultMessage(t *testing.T) {
	t.Run("valid result returns empty", func(t *testing.T) {
		vr := &ValidationResult{Valid: true}
		if msg := vr.Message(nil); msg != "" {
			t.Errorf("expected empty message for valid result, got %q", msg)
		}
	})

	t.Run("no validator returns empty", func(t *testing.T) {
		vr := &ValidationResult{Valid: false, ValidatorID: "test"}
		if msg := vr.Message(nil); msg != "" {
			t.Errorf("expected empty message with no validator, got %q", msg)
		}
	})

	t.Run("no message template returns empty", func(t *testing.T) {
		vr := &ValidationResult{
			Valid:     false,
			Validator: &CompiledValidator{ID: "test"},
		}
		if msg := vr.Message(nil); msg != "" {
			t.Errorf("expected empty message with no template, got %q", msg)
		}
	})

	t.Run("renders template with context", func(t *testing.T) {
		tmpl, _ := template.New("test").Parse("field {{.FieldName}} must be {{.Expected}}")
		vr := &ValidationResult{
			Valid:     false,
			Validator: &CompiledValidator{ID: "test", Message: tmpl},
		}
		ctx := map[string]any{"FieldName": "AMOUNT", "Expected": "positive"}
		msg := vr.Message(ctx)
		if msg != "field AMOUNT must be positive" {
			t.Errorf("expected 'field AMOUNT must be positive', got %q", msg)
		}
	})

	t.Run("template error returns fallback", func(t *testing.T) {
		// Template that calls a method on nil, causing execution error
		tmpl, _ := template.New("test").Option("missingkey=error").Parse("{{.Missing}}")
		vr := &ValidationResult{
			Valid:       false,
			ValidatorID: "bad_tmpl",
			Validator:   &CompiledValidator{ID: "bad_tmpl", Message: tmpl},
		}
		// Pass nil context to trigger template error
		msg := vr.Message(nil)
		if !strings.Contains(msg, "bad_tmpl") || !strings.Contains(msg, "template error") {
			t.Errorf("expected fallback message with validator ID and 'template error', got %q", msg)
		}
	})
}

func TestRecordValidationResultShouldSerialize(t *testing.T) {
	t.Run("no errors should serialize", func(t *testing.T) {
		rvr := &RecordValidationResult{}
		if !rvr.ShouldSerialize() {
			t.Error("expected ShouldSerialize=true with no errors")
		}
	})

	t.Run("field error should still serialize", func(t *testing.T) {
		rvr := &RecordValidationResult{
			FieldErrors: []*ValidationResult{{ErrorType: ErrorTypeFieldValue}},
		}
		if !rvr.ShouldSerialize() {
			t.Error("expected ShouldSerialize=true with only field errors")
		}
	})

	t.Run("precheck error blocks serialization", func(t *testing.T) {
		rvr := &RecordValidationResult{
			RecordErrors: []*ValidationResult{{ErrorType: ErrorTypeRecordPreCheck}},
		}
		if rvr.ShouldSerialize() {
			t.Error("expected ShouldSerialize=false with precheck error")
		}
	})

	t.Run("consistency error does not block", func(t *testing.T) {
		rvr := &RecordValidationResult{
			RecordErrors: []*ValidationResult{{ErrorType: ErrorTypeValueConsistency}},
		}
		if !rvr.ShouldSerialize() {
			t.Error("expected ShouldSerialize=true with consistency error")
		}
	})
}

func TestGroupValidationResultShouldSerialize(t *testing.T) {
	t.Run("no errors should serialize", func(t *testing.T) {
		gvr := &GroupValidationResult{}
		if !gvr.ShouldSerialize() {
			t.Error("expected ShouldSerialize=true with no errors")
		}
	})

	t.Run("case consistency error blocks group", func(t *testing.T) {
		gvr := &GroupValidationResult{
			GroupErrors: []*ValidationResult{{ErrorType: ErrorTypeCaseConsistency}},
		}
		if gvr.ShouldSerialize() {
			t.Error("expected ShouldSerialize=false with case consistency error")
		}
	})

	t.Run("field value error at group level does not block", func(t *testing.T) {
		gvr := &GroupValidationResult{
			GroupErrors: []*ValidationResult{{ErrorType: ErrorTypeFieldValue}},
		}
		if !gvr.ShouldSerialize() {
			t.Error("expected ShouldSerialize=true with non-blocking group error")
		}
	})
}

func TestHasBlockingGroupErrorsFromRecords(t *testing.T) {
	// CASE_CONSISTENCY error attributed to a record should still block the group
	gvr := &GroupValidationResult{
		RecordResults: []*RecordValidationResult{
			{
				RecordErrors: []*ValidationResult{
					{ErrorType: ErrorTypeCaseConsistency},
				},
			},
		},
	}
	if !gvr.HasBlockingGroupErrors() {
		t.Error("expected HasBlockingGroupErrors=true when per-record has CASE_CONSISTENCY")
	}
}

func TestGetSerializableRecordResults(t *testing.T) {
	rec1 := testutil.NewTestRecord(t1Schema, 1, nil)
	rec2 := testutil.NewTestRecord(t1Schema, 2, nil)
	rec3 := testutil.NewTestRecord(t1Schema, 3, nil)

	t.Run("all records serializable", func(t *testing.T) {
		gvr := &GroupValidationResult{
			RecordResults: []*RecordValidationResult{
				{Record: rec1},
				{Record: rec2},
			},
		}
		results := gvr.GetSerializableRecordResults()
		if len(results) != 2 {
			t.Errorf("expected 2 serializable records, got %d", len(results))
		}
	})

	t.Run("filters out blocked records", func(t *testing.T) {
		gvr := &GroupValidationResult{
			RecordResults: []*RecordValidationResult{
				{Record: rec1},
				{Record: rec2, RecordErrors: []*ValidationResult{{ErrorType: ErrorTypeRecordPreCheck}}},
				{Record: rec3},
			},
		}
		results := gvr.GetSerializableRecordResults()
		if len(results) != 2 {
			t.Errorf("expected 2 serializable records, got %d", len(results))
		}
	})

	t.Run("group blocking returns nil", func(t *testing.T) {
		gvr := &GroupValidationResult{
			GroupErrors: []*ValidationResult{{ErrorType: ErrorTypeCaseConsistency}},
			RecordResults: []*RecordValidationResult{
				{Record: rec1},
			},
		}
		results := gvr.GetSerializableRecordResults()
		if results != nil {
			t.Errorf("expected nil when group is blocked, got %d results", len(results))
		}
	})
}

func TestAllRecordErrors(t *testing.T) {
	gvr := &GroupValidationResult{
		RecordResults: []*RecordValidationResult{
			{
				RecordErrors: []*ValidationResult{{ValidatorID: "v1"}},
				FieldErrors:  []*ValidationResult{{ValidatorID: "v2"}},
			},
			{
				FieldErrors: []*ValidationResult{{ValidatorID: "v3"}},
			},
		},
	}
	allErrs := gvr.AllRecordErrors()
	if len(allErrs) != 3 {
		t.Errorf("expected 3 record errors, got %d", len(allErrs))
	}
}

func TestAllGroupErrors(t *testing.T) {
	t.Run("no group errors", func(t *testing.T) {
		gvr := &GroupValidationResult{}
		if gvr.AllGroupErrors() != nil {
			t.Error("expected nil for no group errors")
		}
	})

	t.Run("with group errors", func(t *testing.T) {
		gvr := &GroupValidationResult{
			GroupErrors: []*ValidationResult{{ValidatorID: "g1"}, {ValidatorID: "g2"}},
		}
		errs := gvr.AllGroupErrors()
		if len(errs) != 2 {
			t.Errorf("expected 2 group errors, got %d", len(errs))
		}
	})
}

func TestAddRecordError(t *testing.T) {
	rec1 := testutil.NewTestRecord(t1Schema, 10, nil)
	rec2 := testutil.NewTestRecord(t2Schema, 20, nil)

	gvr := &GroupValidationResult{
		RecordResults: []*RecordValidationResult{
			{Record: rec1},
			{Record: rec2},
		},
	}

	cv := &CompiledValidator{
		ID:        "dup_check",
		ErrorType: ErrorTypeCaseConsistency,
	}

	// Add error to rec2
	gvr.AddRecordError(rec2, cv, nil)

	if len(gvr.RecordResults[0].RecordErrors) != 0 {
		t.Error("expected no errors on rec1")
	}
	if len(gvr.RecordResults[1].RecordErrors) != 1 {
		t.Fatalf("expected 1 error on rec2, got %d", len(gvr.RecordResults[1].RecordErrors))
	}

	err := gvr.RecordResults[1].RecordErrors[0]
	if err.ValidatorID != "dup_check" {
		t.Errorf("expected ValidatorID=dup_check, got %s", err.ValidatorID)
	}
	if err.LineNumber != 20 {
		t.Errorf("expected LineNumber=20, got %d", err.LineNumber)
	}
	if err.RecordType != "T2" {
		t.Errorf("expected RecordType=T2, got %s", err.RecordType)
	}
}

func TestRecordValidationResultAllErrorsEmpty(t *testing.T) {
	rvr := &RecordValidationResult{}
	if rvr.AllErrors() != nil {
		t.Error("expected nil for no errors")
	}
}

// --- Registry tests ---

func TestRegistryGetters(t *testing.T) {
	registry := newValidatorRegistry()
	registry.exprOpts = RegisterFunctions()

	fieldExpr, _ := registry.getOrCompileExpr(ScopeField, "Value > 0", "single")
	recordExpr, _ := registry.getOrCompileExpr(ScopeRecord, "RecordLength > 0", "single")
	groupExpr, _ := registry.getOrCompileExpr(ScopeGroup, "TotalRecords > 0", "single")

	registry.field["T1"] = map[string][]*CompiledValidator{
		"AMOUNT": {{ID: "pos", Scope: ScopeField, Expr: fieldExpr}},
	}
	registry.record["T1"] = []*CompiledValidator{
		{ID: "len_check", Scope: ScopeRecord, Expr: recordExpr},
	}
	registry.group["TEST:1"] = []*CompiledValidator{
		{ID: "grp_check", Scope: ScopeGroup, Expr: groupExpr},
	}

	t.Run("GetFieldValidators", func(t *testing.T) {
		validators := registry.GetFieldValidators("T1", "AMOUNT")
		if len(validators) != 1 || validators[0].ID != "pos" {
			t.Errorf("expected 1 field validator 'pos', got %v", validators)
		}
		// Non-existent
		if registry.GetFieldValidators("T99", "AMOUNT") != nil {
			t.Error("expected nil for non-existent record type")
		}
		if registry.GetFieldValidators("T1", "NONEXISTENT") != nil {
			t.Error("expected nil for non-existent field")
		}
	})

	t.Run("GetFieldValidatorsForRecord", func(t *testing.T) {
		fields := registry.GetFieldValidatorsForRecord("T1")
		if len(fields) != 1 {
			t.Errorf("expected 1 field entry, got %d", len(fields))
		}
		if registry.GetFieldValidatorsForRecord("T99") != nil {
			t.Error("expected nil for non-existent record type")
		}
	})

	t.Run("GetRecordValidators", func(t *testing.T) {
		validators := registry.GetRecordValidators("T1")
		if len(validators) != 1 || validators[0].ID != "len_check" {
			t.Errorf("expected 1 record validator 'len_check', got %v", validators)
		}
		if registry.GetRecordValidators("T99") != nil {
			t.Error("expected nil for non-existent record type")
		}
	})

	t.Run("GetGroupValidators", func(t *testing.T) {
		validators := registry.GetGroupValidators("TEST:1")
		if len(validators) != 1 || validators[0].ID != "grp_check" {
			t.Errorf("expected 1 group validator 'grp_check', got %v", validators)
		}
		if registry.GetGroupValidators("NONEXISTENT") != nil {
			t.Error("expected nil for non-existent filespec")
		}
	})
}

func TestRegistryStats(t *testing.T) {
	registry := newValidatorRegistry()
	registry.exprOpts = RegisterFunctions()

	fieldExpr, _ := registry.getOrCompileExpr(ScopeField, "Value > 0", "single")
	fieldExpr2, _ := registry.getOrCompileExpr(ScopeField, "Value >= 0", "single")
	recordExpr, _ := registry.getOrCompileExpr(ScopeRecord, "RecordLength > 0", "single")
	groupExpr, _ := registry.getOrCompileExpr(ScopeGroup, "TotalRecords > 0", "single")

	registry.field["T1"] = map[string][]*CompiledValidator{
		"AMOUNT":      {{ID: "pos", Expr: fieldExpr}},
		"CASE_NUMBER": {{ID: "non_neg", Expr: fieldExpr2}},
	}
	registry.field["T2"] = map[string][]*CompiledValidator{
		"SSN": {{ID: "ssn_check", Expr: fieldExpr}},
	}
	registry.record["T1"] = []*CompiledValidator{{ID: "len_check", Expr: recordExpr}}
	registry.group["TEST:1"] = []*CompiledValidator{{ID: "grp_check", Expr: groupExpr}}

	stats := registry.Stats()

	if stats.FieldValidators != 3 {
		t.Errorf("expected 3 field validators, got %d", stats.FieldValidators)
	}
	if stats.RecordValidators != 1 {
		t.Errorf("expected 1 record validator, got %d", stats.RecordValidators)
	}
	if stats.GroupValidators != 1 {
		t.Errorf("expected 1 group validator, got %d", stats.GroupValidators)
	}
	if stats.RecordTypesWithFields != 2 {
		t.Errorf("expected 2 record types with fields, got %d", stats.RecordTypesWithFields)
	}
	if stats.RecordTypesWithRecord != 1 {
		t.Errorf("expected 1 record type with record validators, got %d", stats.RecordTypesWithRecord)
	}
	if stats.FileSpecsWithGroup != 1 {
		t.Errorf("expected 1 filespec with group validators, got %d", stats.FileSpecsWithGroup)
	}
	if stats.TotalExpressions != 4 {
		t.Errorf("expected 4 total expressions, got %d", stats.TotalExpressions)
	}
}

func TestExpressionDeduplication(t *testing.T) {
	registry := newValidatorRegistry()
	registry.exprOpts = RegisterFunctions()

	// Compile same expression twice — should return same pointer
	expr1, err := registry.getOrCompileExpr(ScopeField, "Value > 0", "single")
	if err != nil {
		t.Fatalf("first compile failed: %v", err)
	}
	expr2, err := registry.getOrCompileExpr(ScopeField, "Value > 0", "single")
	if err != nil {
		t.Fatalf("second compile failed: %v", err)
	}
	if expr1 != expr2 {
		t.Error("expected same CompiledExpr pointer for identical expression")
	}

	// Different scope, same string — should be different
	expr3, err := registry.getOrCompileExpr(ScopeRecord, "RecordLength > 0", "single")
	if err != nil {
		t.Fatalf("record compile failed: %v", err)
	}
	if expr3 == expr1 {
		t.Error("expected different CompiledExpr for different scope")
	}
}

func TestClearCompileTimeData(t *testing.T) {
	registry := newValidatorRegistry()
	registry.exprOpts = RegisterFunctions()

	// Add some data
	registry.getOrCompileExpr(ScopeField, "Value > 0", "single")
	registry.predefined[ScopeField] = map[string]*configValidation.ValidatorDef{
		"test": {ID: "test", Expr: "Value > 0"},
	}

	registry.ClearCompileTimeData()

	if registry.expressions != nil {
		t.Error("expected expressions to be nil after ClearCompileTimeData")
	}
	if registry.predefined != nil {
		t.Error("expected predefined to be nil after ClearCompileTimeData")
	}
}

func TestExecuteFunction(t *testing.T) {
	registry := newValidatorRegistry()
	registry.exprOpts = RegisterFunctions()

	t.Run("passing validation", func(t *testing.T) {
		ce, _ := registry.getOrCompileExpr(ScopeField, "Value > 0", "single")
		cv := &CompiledValidator{ID: "positive", Expr: ce}
		env := &FieldEnv{Value: 42}

		result := Execute(cv, env)
		if !result.Valid {
			t.Error("expected valid result")
		}
	})

	t.Run("failing validation", func(t *testing.T) {
		ce, _ := registry.getOrCompileExpr(ScopeField, "Value > 0", "single")
		cv := &CompiledValidator{ID: "positive", Expr: ce}
		env := &FieldEnv{Value: -1}

		result := Execute(cv, env)
		if result.Valid {
			t.Error("expected invalid result")
		}
		if result.ValidatorID != "positive" {
			t.Errorf("expected ValidatorID=positive, got %s", result.ValidatorID)
		}
		if result.Validator != cv {
			t.Error("expected Validator back-reference to be set")
		}
	})

	t.Run("invalid program type", func(t *testing.T) {
		cv := &CompiledValidator{
			ID:   "bad",
			Expr: &CompiledExpr{Expr: "test", Program: "not a program"},
		}
		result := Execute(cv, nil)
		if result.Valid {
			t.Error("expected invalid result for bad program type")
		}
		if result.Error == nil {
			t.Error("expected error to be set")
		}
	})

	t.Run("record validator can sum fields from params", func(t *testing.T) {
		sumSchema := testutil.NewTestSchema("T6", "TOTAL", "PART_A", "PART_B")
		vdef := &configValidation.ValidatorDef{
			ID:   "sum_equals",
			Expr: "GetInt(Params.total_field) == SumFields(Params.component_fields)",
			Params: map[string]any{
				"total_field":      "TOTAL",
				"component_fields": []any{"PART_A", "PART_B"},
			},
		}
		cv, err := registry.resolveValidatorByScope(ScopeRecord, vdef, "")
		if err != nil {
			t.Fatalf("unexpected compile error: %v", err)
		}

		validRec := testutil.NewTestRecord(sumSchema, 10, map[string]any{
			"TOTAL":  7,
			"PART_A": 3,
			"PART_B": "4",
		})
		validEnv := NewRecordEnvWithParams(validRec, cv.Params)
		if result := Execute(cv, validEnv); !result.Valid {
			t.Fatalf("expected valid sum_equals result, got error: %v", result.Error)
		}

		invalidRec := testutil.NewTestRecord(sumSchema, 11, map[string]any{
			"TOTAL":  8,
			"PART_A": 3,
			"PART_B": "4",
		})
		invalidEnv := NewRecordEnvWithParams(invalidRec, cv.Params)
		if result := Execute(cv, invalidEnv); result.Valid {
			t.Fatal("expected invalid sum_equals result")
		}
	})
}

func TestDeriveFieldsFromParams(t *testing.T) {
	t.Run("extracts known field param names", func(t *testing.T) {
		params := map[string]any{
			"condition_field": "FAMILY_AFFILIATION",
			"target_field":    "AMOUNT",
			"unrelated":       "ignored",
		}
		fields := deriveFieldsFromParams(params)
		if len(fields) != 2 {
			t.Errorf("expected 2 fields, got %d", len(fields))
		}
	})

	t.Run("empty params", func(t *testing.T) {
		fields := deriveFieldsFromParams(map[string]any{})
		if len(fields) != 0 {
			t.Errorf("expected 0 fields, got %d", len(fields))
		}
	})

	t.Run("skips empty string values", func(t *testing.T) {
		params := map[string]any{
			"condition_field": "",
		}
		fields := deriveFieldsFromParams(params)
		if len(fields) != 0 {
			t.Errorf("expected 0 fields for empty string value, got %d", len(fields))
		}
	})

	t.Run("skips non-string values", func(t *testing.T) {
		params := map[string]any{
			"condition_field": 42,
		}
		fields := deriveFieldsFromParams(params)
		if len(fields) != 0 {
			t.Errorf("expected 0 fields for non-string value, got %d", len(fields))
		}
	})
}

func TestResolveValidatorWithMessageTemplate(t *testing.T) {
	registry := newValidatorRegistry()
	registry.exprOpts = RegisterFunctions()

	vdef := &configValidation.ValidatorDef{
		ID:      "custom_check",
		Expr:    "Value > 0",
		Message: "Value must be positive",
	}

	cv, err := registry.resolveValidatorByScope(ScopeField, vdef, "")
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	if cv.Message == nil {
		t.Error("expected message template to be set")
	}
	if cv.ErrorType != ErrorTypeFieldValue {
		t.Errorf("expected default error type FIELD_VALUE, got %s", cv.ErrorType)
	}
}

func TestResolveValidatorDefaultErrorTypes(t *testing.T) {
	registry := newValidatorRegistry()
	registry.exprOpts = RegisterFunctions()

	tests := []struct {
		scope       string
		expr        string
		expectedErr string
	}{
		{ScopeField, "Value > 0", ErrorTypeFieldValue},
		{ScopeRecord, "RecordLength > 0", ErrorTypeValueConsistency},
		{ScopeGroup, "TotalRecords > 0", ErrorTypeCaseConsistency},
	}

	for _, tt := range tests {
		t.Run(tt.scope, func(t *testing.T) {
			vdef := &configValidation.ValidatorDef{ID: "test_" + tt.scope, Expr: tt.expr}
			cv, err := registry.resolveValidatorByScope(tt.scope, vdef, "")
			if err != nil {
				t.Fatalf("unexpected error: %v", err)
			}
			if cv.ErrorType != tt.expectedErr {
				t.Errorf("expected error type %s, got %s", tt.expectedErr, cv.ErrorType)
			}
		})
	}
}

func TestResolveValidatorWithCustomDefaultErrorType(t *testing.T) {
	registry := newValidatorRegistry()
	registry.exprOpts = RegisterFunctions()

	vdef := &configValidation.ValidatorDef{ID: "test", Expr: "Value > 0"}
	cv, err := registry.resolveValidatorByScope(ScopeField, vdef, ErrorTypeRecordPreCheck)
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	if cv.ErrorType != ErrorTypeRecordPreCheck {
		t.Errorf("expected custom default error type RECORD_PRE_CHECK, got %s", cv.ErrorType)
	}
}

func TestResolveValidatorPredefinedFieldInheritance(t *testing.T) {
	registry := newValidatorRegistry()
	registry.exprOpts = RegisterFunctions()
	registry.predefined[ScopeRecord] = map[string]*configValidation.ValidatorDef{
		"length_range": {
			ID:         "length_range",
			Expr:       "RecordLength >= Params.min and RecordLength <= Params.max",
			Message:    "record length must be between {{.Params.min}} and {{.Params.max}}",
			Params:     map[string]any{"min": 100, "max": 200},
			Fields:     []string{"RECORD_TYPE"},
			ErrorType:  ErrorTypeRecordPreCheck,
			ResultMode: "single",
		},
	}

	t.Run("inherits predefined fields when not specified at use-site", func(t *testing.T) {
		vdef := &configValidation.ValidatorDef{
			ID:     "length_range",
			Params: map[string]any{"min": 117},
		}
		cv, err := registry.resolveValidatorByScope(ScopeRecord, vdef, "")
		if err != nil {
			t.Fatalf("unexpected error: %v", err)
		}
		// Fields inherited from predefined
		if len(cv.Fields) != 1 || cv.Fields[0] != "RECORD_TYPE" {
			t.Errorf("expected inherited fields [RECORD_TYPE], got %v", cv.Fields)
		}
		// ErrorType inherited from predefined
		if cv.ErrorType != ErrorTypeRecordPreCheck {
			t.Errorf("expected inherited error type RECORD_PRE_CHECK, got %s", cv.ErrorType)
		}
		// ResultMode inherited from predefined
		if cv.ResultMode != "single" {
			t.Errorf("expected inherited result mode 'single', got %s", cv.ResultMode)
		}
		// Params merged: use-site min=117 overrides predefined min=100
		if cv.Params["min"] != 117 {
			t.Errorf("expected merged min=117, got %v", cv.Params["min"])
		}
		// Params merged: predefined max=200 retained
		if cv.Params["max"] != 200 {
			t.Errorf("expected inherited max=200, got %v", cv.Params["max"])
		}
		// Message inherited from predefined
		if cv.Message == nil {
			t.Error("expected message template inherited from predefined")
		}
	})

	t.Run("use-site message overrides predefined", func(t *testing.T) {
		vdef := &configValidation.ValidatorDef{
			ID:      "length_range",
			Message: "custom message",
		}
		cv, err := registry.resolveValidatorByScope(ScopeRecord, vdef, "")
		if err != nil {
			t.Fatalf("unexpected error: %v", err)
		}
		if cv.Message == nil {
			t.Fatal("expected message template")
		}
	})
}

func TestResolveValidatorAutoDerivesFields(t *testing.T) {
	registry := newValidatorRegistry()
	registry.exprOpts = RegisterFunctions()

	vdef := &configValidation.ValidatorDef{
		ID:   "conditional_check",
		Expr: "Value > 0",
		Params: map[string]any{
			"condition_field": "FAMILY_AFFILIATION",
			"target_field":    "AMOUNT",
		},
	}
	cv, err := registry.resolveValidatorByScope(ScopeField, vdef, "")
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	if len(cv.Fields) != 2 {
		t.Errorf("expected 2 auto-derived fields, got %d: %v", len(cv.Fields), cv.Fields)
	}
}

func TestCompileExpressionError(t *testing.T) {
	registry := newValidatorRegistry()
	registry.exprOpts = RegisterFunctions()

	_, err := registry.getOrCompileExpr(ScopeField, "this is *** invalid expr", "single")
	if err == nil {
		t.Error("expected compile error for invalid expression")
	}
}

func TestEnvTypeForScope(t *testing.T) {
	registry := newValidatorRegistry()

	if _, ok := registry.envTypeForScope(ScopeField).(*FieldEnv); !ok {
		t.Error("expected *FieldEnv for field scope")
	}
	if _, ok := registry.envTypeForScope(ScopeRecord).(*RecordEnv); !ok {
		t.Error("expected *RecordEnv for record scope")
	}
	if _, ok := registry.envTypeForScope(ScopeGroup).(*GroupEnv); !ok {
		t.Error("expected *GroupEnv for group scope")
	}
	if registry.envTypeForScope("unknown") != nil {
		t.Error("expected nil for unknown scope")
	}
}
