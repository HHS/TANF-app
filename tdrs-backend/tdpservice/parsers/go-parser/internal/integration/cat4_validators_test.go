//go:build integration

package integration

import (
	"testing"

	"go-parser/internal/validation"
)

// =============================================================================
// Mock types for testing
// =============================================================================

// mockRecord implements the validation.Record interface for testing
type mockRecord struct {
	recordType string
	lineNumber int
	fields     map[string]any
}

func (r *mockRecord) Get(fieldName string) any {
	return r.fields[fieldName]
}

func (r *mockRecord) GetString(fieldName string) string {
	v := r.fields[fieldName]
	if v == nil {
		return ""
	}
	if s, ok := v.(string); ok {
		return s
	}
	return ""
}

func (r *mockRecord) GetInt(fieldName string) int {
	v := r.fields[fieldName]
	if v == nil {
		return 0
	}
	if i, ok := v.(int); ok {
		return i
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
	return 156
}

func (r *mockRecord) IsFieldRequired(fieldName string) bool {
	return false
}

// mockGroup implements the validation.Group interface for testing
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

// newMockGroup creates a WrappedGroup for testing
func newMockGroup(records []validation.Record) validation.WrappedGroup {
	return validation.WrapGroup(&mockGroup{
		key:          "202401|12345",
		rptMonthYear: "202401",
		caseNumber:   "12345",
	}, records)
}

// =============================================================================
// Helper functions
// =============================================================================

// runCat4Validator runs a specific cat4 validator against a group
func runCat4Validator(t *testing.T, filespecKey string, validatorID string, group validation.WrappedGroup) *validation.ValidationResult {
	t.Helper()

	validators := testRegistry.Validators().GetCat4Validators(filespecKey)
	if len(validators) == 0 {
		t.Fatalf("No cat4 validators found for filespec %s", filespecKey)
	}

	// Find the specific validator
	var cv *validation.CompiledValidator
	for _, v := range validators {
		if v.ID == validatorID {
			cv = v
			break
		}
	}
	if cv == nil {
		t.Fatalf("Validator %s not found in filespec %s", validatorID, filespecKey)
	}

	// Run the validator
	env := validation.NewGroupEnv(group)
	env.Params = cv.Params
	return validation.Execute(cv, env)
}

// =============================================================================
// TANF Section 1 Cat4 Validators
// =============================================================================

func TestCat4_T1HasT2OrT3(t *testing.T) {
	const filespecKey = "TANF:1"
	const validatorID = "t1_has_t2_or_t3"

	t.Run("no T1 records - should pass", func(t *testing.T) {
		records := []validation.Record{
			&mockRecord{recordType: "T2", lineNumber: 1},
		}
		group := newMockGroup(records)
		result := runCat4Validator(t, filespecKey, validatorID, group)
		if !result.Valid {
			t.Errorf("expected valid when no T1 records")
		}
	})

	t.Run("T1 with T2 - should pass", func(t *testing.T) {
		records := []validation.Record{
			&mockRecord{recordType: "T1", lineNumber: 1},
			&mockRecord{recordType: "T2", lineNumber: 2},
		}
		group := newMockGroup(records)
		result := runCat4Validator(t, filespecKey, validatorID, group)
		if !result.Valid {
			t.Errorf("expected valid when T1 has T2")
		}
	})

	t.Run("T1 with T3 - should pass", func(t *testing.T) {
		records := []validation.Record{
			&mockRecord{recordType: "T1", lineNumber: 1},
			&mockRecord{recordType: "T3", lineNumber: 2},
		}
		group := newMockGroup(records)
		result := runCat4Validator(t, filespecKey, validatorID, group)
		if !result.Valid {
			t.Errorf("expected valid when T1 has T3")
		}
	})

	t.Run("T1 without T2 or T3 - should fail", func(t *testing.T) {
		records := []validation.Record{
			&mockRecord{recordType: "T1", lineNumber: 1},
		}
		group := newMockGroup(records)
		result := runCat4Validator(t, filespecKey, validatorID, group)
		if result.Valid {
			t.Errorf("expected invalid when T1 has no T2/T3")
		}
	})
}

func TestCat4_T1FamilyAffiliation(t *testing.T) {
	const filespecKey = "TANF:1"
	const validatorID = "t1_family_affiliation"

	t.Run("no T1 records - should pass", func(t *testing.T) {
		records := []validation.Record{
			&mockRecord{recordType: "T2", lineNumber: 1, fields: map[string]any{"FAMILY_AFFILIATION": 2}},
		}
		group := newMockGroup(records)
		result := runCat4Validator(t, filespecKey, validatorID, group)
		if !result.Valid {
			t.Errorf("expected valid when no T1 records")
		}
	})

	t.Run("T1 with T2 FAMILY_AFFILIATION=1 - should pass", func(t *testing.T) {
		records := []validation.Record{
			&mockRecord{recordType: "T1", lineNumber: 1},
			&mockRecord{recordType: "T2", lineNumber: 2, fields: map[string]any{"FAMILY_AFFILIATION": 1}},
		}
		group := newMockGroup(records)
		result := runCat4Validator(t, filespecKey, validatorID, group)
		if !result.Valid {
			t.Errorf("expected valid when T2 has FAMILY_AFFILIATION=1")
		}
	})

	t.Run("T1 with T3 FAMILY_AFFILIATION=1 - should pass", func(t *testing.T) {
		records := []validation.Record{
			&mockRecord{recordType: "T1", lineNumber: 1},
			&mockRecord{recordType: "T3", lineNumber: 2, fields: map[string]any{"FAMILY_AFFILIATION": 1}},
		}
		group := newMockGroup(records)
		result := runCat4Validator(t, filespecKey, validatorID, group)
		if !result.Valid {
			t.Errorf("expected valid when T3 has FAMILY_AFFILIATION=1")
		}
	})

	t.Run("T1 with T2 FAMILY_AFFILIATION=2 only - should fail", func(t *testing.T) {
		records := []validation.Record{
			&mockRecord{recordType: "T1", lineNumber: 1},
			&mockRecord{recordType: "T2", lineNumber: 2, fields: map[string]any{"FAMILY_AFFILIATION": 2}},
		}
		group := newMockGroup(records)
		result := runCat4Validator(t, filespecKey, validatorID, group)
		if result.Valid {
			t.Errorf("expected invalid when no T2/T3 has FAMILY_AFFILIATION=1")
		}
	})

	t.Run("T1 with no T2/T3 - should fail", func(t *testing.T) {
		records := []validation.Record{
			&mockRecord{recordType: "T1", lineNumber: 1},
		}
		group := newMockGroup(records)
		result := runCat4Validator(t, filespecKey, validatorID, group)
		if result.Valid {
			t.Errorf("expected invalid when T1 has no T2/T3")
		}
	})

	t.Run("T1 with multiple T2s, one has FAMILY_AFFILIATION=1 - should pass", func(t *testing.T) {
		records := []validation.Record{
			&mockRecord{recordType: "T1", lineNumber: 1},
			&mockRecord{recordType: "T2", lineNumber: 2, fields: map[string]any{"FAMILY_AFFILIATION": 2}},
			&mockRecord{recordType: "T2", lineNumber: 3, fields: map[string]any{"FAMILY_AFFILIATION": 1}},
			&mockRecord{recordType: "T2", lineNumber: 4, fields: map[string]any{"FAMILY_AFFILIATION": 3}},
		}
		group := newMockGroup(records)
		result := runCat4Validator(t, filespecKey, validatorID, group)
		if !result.Valid {
			t.Errorf("expected valid when at least one T2 has FAMILY_AFFILIATION=1")
		}
	})

	t.Run("T1 with mixed T2/T3, T3 has FAMILY_AFFILIATION=1 - should pass", func(t *testing.T) {
		records := []validation.Record{
			&mockRecord{recordType: "T1", lineNumber: 1},
			&mockRecord{recordType: "T2", lineNumber: 2, fields: map[string]any{"FAMILY_AFFILIATION": 2}},
			&mockRecord{recordType: "T3", lineNumber: 3, fields: map[string]any{"FAMILY_AFFILIATION": 1}},
		}
		group := newMockGroup(records)
		result := runCat4Validator(t, filespecKey, validatorID, group)
		if !result.Valid {
			t.Errorf("expected valid when T3 has FAMILY_AFFILIATION=1")
		}
	})
}

func TestCat4_T2RequiresT1(t *testing.T) {
	const filespecKey = "TANF:1"
	const validatorID = "t2_requires_t1"

	t.Run("no T2 records - should pass", func(t *testing.T) {
		records := []validation.Record{
			&mockRecord{recordType: "T1", lineNumber: 1},
		}
		group := newMockGroup(records)
		result := runCat4Validator(t, filespecKey, validatorID, group)
		if !result.Valid {
			t.Errorf("expected valid when no T2 records")
		}
	})

	t.Run("T2 with T1 - should pass", func(t *testing.T) {
		records := []validation.Record{
			&mockRecord{recordType: "T1", lineNumber: 1},
			&mockRecord{recordType: "T2", lineNumber: 2},
		}
		group := newMockGroup(records)
		result := runCat4Validator(t, filespecKey, validatorID, group)
		if !result.Valid {
			t.Errorf("expected valid when T2 has corresponding T1")
		}
	})

	t.Run("T2 without T1 - should fail", func(t *testing.T) {
		records := []validation.Record{
			&mockRecord{recordType: "T2", lineNumber: 1},
		}
		group := newMockGroup(records)
		result := runCat4Validator(t, filespecKey, validatorID, group)
		if result.Valid {
			t.Errorf("expected invalid when T2 has no corresponding T1")
		}
	})

	t.Run("multiple T2s without T1 - should fail", func(t *testing.T) {
		records := []validation.Record{
			&mockRecord{recordType: "T2", lineNumber: 1},
			&mockRecord{recordType: "T2", lineNumber: 2},
			&mockRecord{recordType: "T3", lineNumber: 3},
		}
		group := newMockGroup(records)
		result := runCat4Validator(t, filespecKey, validatorID, group)
		if result.Valid {
			t.Errorf("expected invalid when T2s have no corresponding T1")
		}
	})
}

func TestCat4_T3RequiresT1(t *testing.T) {
	const filespecKey = "TANF:1"
	const validatorID = "t3_requires_t1"

	t.Run("no T3 records - should pass", func(t *testing.T) {
		records := []validation.Record{
			&mockRecord{recordType: "T1", lineNumber: 1},
		}
		group := newMockGroup(records)
		result := runCat4Validator(t, filespecKey, validatorID, group)
		if !result.Valid {
			t.Errorf("expected valid when no T3 records")
		}
	})

	t.Run("T3 with T1 - should pass", func(t *testing.T) {
		records := []validation.Record{
			&mockRecord{recordType: "T1", lineNumber: 1},
			&mockRecord{recordType: "T3", lineNumber: 2},
		}
		group := newMockGroup(records)
		result := runCat4Validator(t, filespecKey, validatorID, group)
		if !result.Valid {
			t.Errorf("expected valid when T3 has corresponding T1")
		}
	})

	t.Run("T3 without T1 - should fail", func(t *testing.T) {
		records := []validation.Record{
			&mockRecord{recordType: "T3", lineNumber: 1},
		}
		group := newMockGroup(records)
		result := runCat4Validator(t, filespecKey, validatorID, group)
		if result.Valid {
			t.Errorf("expected invalid when T3 has no corresponding T1")
		}
	})

	t.Run("multiple T3s without T1 - should fail", func(t *testing.T) {
		records := []validation.Record{
			&mockRecord{recordType: "T2", lineNumber: 1},
			&mockRecord{recordType: "T3", lineNumber: 2},
			&mockRecord{recordType: "T3", lineNumber: 3},
		}
		group := newMockGroup(records)
		result := runCat4Validator(t, filespecKey, validatorID, group)
		if result.Valid {
			t.Errorf("expected invalid when T3s have no corresponding T1")
		}
	})
}

// =============================================================================
// TANF Section 2 Cat4 Validators
// =============================================================================

func TestCat4_T4RequiresT5(t *testing.T) {
	const filespecKey = "TANF:2"
	const validatorID = "t4_requires_t5"

	t.Run("no T4 records - should pass", func(t *testing.T) {
		records := []validation.Record{
			&mockRecord{recordType: "T5", lineNumber: 1},
		}
		group := newMockGroup(records)
		result := runCat4Validator(t, filespecKey, validatorID, group)
		if !result.Valid {
			t.Errorf("expected valid when no T4 records")
		}
	})

	t.Run("T4 with T5 - should pass", func(t *testing.T) {
		records := []validation.Record{
			&mockRecord{recordType: "T4", lineNumber: 1},
			&mockRecord{recordType: "T5", lineNumber: 2},
		}
		group := newMockGroup(records)
		result := runCat4Validator(t, filespecKey, validatorID, group)
		if !result.Valid {
			t.Errorf("expected valid when T4 has corresponding T5")
		}
	})

	t.Run("T4 without T5 - should fail", func(t *testing.T) {
		records := []validation.Record{
			&mockRecord{recordType: "T4", lineNumber: 1},
		}
		group := newMockGroup(records)
		result := runCat4Validator(t, filespecKey, validatorID, group)
		if result.Valid {
			t.Errorf("expected invalid when T4 has no corresponding T5")
		}
	})

	t.Run("multiple T4s with T5 - should pass", func(t *testing.T) {
		records := []validation.Record{
			&mockRecord{recordType: "T4", lineNumber: 1},
			&mockRecord{recordType: "T4", lineNumber: 2},
			&mockRecord{recordType: "T5", lineNumber: 3},
		}
		group := newMockGroup(records)
		result := runCat4Validator(t, filespecKey, validatorID, group)
		if !result.Valid {
			t.Errorf("expected valid when T4s have corresponding T5")
		}
	})
}

func TestCat4_T5RequiresT4(t *testing.T) {
	const filespecKey = "TANF:2"
	const validatorID = "t5_requires_t4"

	t.Run("no T5 records - should pass", func(t *testing.T) {
		records := []validation.Record{
			&mockRecord{recordType: "T4", lineNumber: 1},
		}
		group := newMockGroup(records)
		result := runCat4Validator(t, filespecKey, validatorID, group)
		if !result.Valid {
			t.Errorf("expected valid when no T5 records")
		}
	})

	t.Run("T5 with T4 - should pass", func(t *testing.T) {
		records := []validation.Record{
			&mockRecord{recordType: "T4", lineNumber: 1},
			&mockRecord{recordType: "T5", lineNumber: 2},
		}
		group := newMockGroup(records)
		result := runCat4Validator(t, filespecKey, validatorID, group)
		if !result.Valid {
			t.Errorf("expected valid when T5 has corresponding T4")
		}
	})

	t.Run("T5 without T4 - should fail", func(t *testing.T) {
		records := []validation.Record{
			&mockRecord{recordType: "T5", lineNumber: 1},
		}
		group := newMockGroup(records)
		result := runCat4Validator(t, filespecKey, validatorID, group)
		if result.Valid {
			t.Errorf("expected invalid when T5 has no corresponding T4")
		}
	})

	t.Run("multiple T5s without T4 - should fail", func(t *testing.T) {
		records := []validation.Record{
			&mockRecord{recordType: "T5", lineNumber: 1},
			&mockRecord{recordType: "T5", lineNumber: 2},
		}
		group := newMockGroup(records)
		result := runCat4Validator(t, filespecKey, validatorID, group)
		if result.Valid {
			t.Errorf("expected invalid when T5s have no corresponding T4")
		}
	})

	t.Run("multiple T5s with T4 - should pass", func(t *testing.T) {
		records := []validation.Record{
			&mockRecord{recordType: "T4", lineNumber: 1},
			&mockRecord{recordType: "T5", lineNumber: 2},
			&mockRecord{recordType: "T5", lineNumber: 3},
			&mockRecord{recordType: "T5", lineNumber: 4},
		}
		group := newMockGroup(records)
		result := runCat4Validator(t, filespecKey, validatorID, group)
		if !result.Valid {
			t.Errorf("expected valid when T5s have corresponding T4")
		}
	})
}
