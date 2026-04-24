//go:build integration

package integration

import (
	"reflect"
	"testing"

	"go-parser/internal/parser"
	"go-parser/internal/testutil"
	"go-parser/internal/validation"
)

// Package-level test schemas for integration tests.
var (
	t1IntSchema = testutil.NewTestSchema("T1")
	t2IntSchema = testutil.NewTestSchema("T2", "FAMILY_AFFILIATION")
	t3IntSchema = testutil.NewTestSchema("T3", "FAMILY_AFFILIATION")
	t4IntSchema = testutil.NewTestSchema("T4")
	t5IntSchema = testutil.NewTestSchema("T5")
	m1IntSchema = testutil.NewTestSchema("M1")
	m2IntSchema = testutil.NewTestSchema("M2", "FAMILY_AFFILIATION")
	m3IntSchema = testutil.NewTestSchema("M3", "FAMILY_AFFILIATION")
	m4IntSchema = testutil.NewTestSchema("M4")
	m5IntSchema = testutil.NewTestSchema("M5")
)

// =============================================================================
// Helper functions
// =============================================================================

// runGroupValidator runs a specific group validator against a group.
func runGroupValidator(t *testing.T, filespecKey string, validatorID string, expectedParams map[string]any, group *parser.ParsedGroup) *validation.ValidationResult {
	t.Helper()

	validators := testValidators.GetGroupValidators(filespecKey)
	if len(validators) == 0 {
		t.Fatalf("No group validators found for filespec %s", filespecKey)
	}

	var cv *validation.CompiledValidator
	for _, v := range validators {
		if v.ID == validatorID && validatorParamsMatch(v.Params, expectedParams) {
			cv = v
			break
		}
	}
	if cv == nil {
		t.Fatalf("Validator %s with params %v not found in filespec %s", validatorID, expectedParams, filespecKey)
	}

	env := validation.NewGroupEnv(group)
	env.Params = cv.Params
	return validation.Execute(cv, env)
}

func validatorParamsMatch(actual map[string]any, expected map[string]any) bool {
	if expected == nil {
		return true
	}
	return reflect.DeepEqual(actual, expected)
}

// =============================================================================
// TANF Section 1 Cat4 Validators
// =============================================================================

func TestCat4_T1HasT2OrT3(t *testing.T) {
	const filespecKey = "TAN:1"
	const validatorID = "requires_related_record"

	params := map[string]any{
		"record_type":          "T1",
		"related_record_types": []any{"T2", "T3"},
	}

	t.Run("no T1 records - should pass", func(t *testing.T) {
		rec := testutil.NewTestRecord(t2IntSchema, 1, nil)
		group := testutil.NewTestGroup(rec)
		result := runGroupValidator(t, filespecKey, validatorID, params, group)
		if !result.Valid {
			t.Errorf("expected valid when no T1 records")
		}
	})

	t.Run("T1 with T2 - should pass", func(t *testing.T) {
		r1 := testutil.NewTestRecord(t1IntSchema, 1, nil)
		r2 := testutil.NewTestRecord(t2IntSchema, 2, nil)
		group := testutil.NewTestGroup(r1, r2)
		result := runGroupValidator(t, filespecKey, validatorID, params, group)
		if !result.Valid {
			t.Errorf("expected valid when T1 has T2")
		}
	})

	t.Run("T1 with T3 - should pass", func(t *testing.T) {
		r1 := testutil.NewTestRecord(t1IntSchema, 1, nil)
		r2 := testutil.NewTestRecord(t3IntSchema, 2, nil)
		group := testutil.NewTestGroup(r1, r2)
		result := runGroupValidator(t, filespecKey, validatorID, params, group)
		if !result.Valid {
			t.Errorf("expected valid when T1 has T3")
		}
	})

	t.Run("T1 without T2 or T3 - should fail", func(t *testing.T) {
		r1 := testutil.NewTestRecord(t1IntSchema, 1, nil)
		group := testutil.NewTestGroup(r1)
		result := runGroupValidator(t, filespecKey, validatorID, params, group)
		if result.Valid {
			t.Errorf("expected invalid when T1 has no T2/T3")
		}
	})
}

func TestCat4_T1FamilyAffiliation(t *testing.T) {
	const filespecKey = "TAN:1"
	const validatorID = "requires_related_record_with_int_value"

	params := map[string]any{
		"record_type":          "T1",
		"related_record_types": []any{"T2", "T3"},
		"field_name":           "FAMILY_AFFILIATION",
		"expected_value":       1,
	}

	t.Run("no T1 records - should pass", func(t *testing.T) {
		rec := testutil.NewTestRecord(t2IntSchema, 1, map[string]any{"FAMILY_AFFILIATION": 2})
		group := testutil.NewTestGroup(rec)
		result := runGroupValidator(t, filespecKey, validatorID, params, group)
		if !result.Valid {
			t.Errorf("expected valid when no T1 records")
		}
	})

	t.Run("T1 with T2 FAMILY_AFFILIATION=1 - should pass", func(t *testing.T) {
		r1 := testutil.NewTestRecord(t1IntSchema, 1, nil)
		r2 := testutil.NewTestRecord(t2IntSchema, 2, map[string]any{"FAMILY_AFFILIATION": 1})
		group := testutil.NewTestGroup(r1, r2)
		result := runGroupValidator(t, filespecKey, validatorID, params, group)
		if !result.Valid {
			t.Errorf("expected valid when T2 has FAMILY_AFFILIATION=1")
		}
	})

	t.Run("T1 with T3 FAMILY_AFFILIATION=1 - should pass", func(t *testing.T) {
		r1 := testutil.NewTestRecord(t1IntSchema, 1, nil)
		r2 := testutil.NewTestRecord(t3IntSchema, 2, map[string]any{"FAMILY_AFFILIATION": 1})
		group := testutil.NewTestGroup(r1, r2)
		result := runGroupValidator(t, filespecKey, validatorID, params, group)
		if !result.Valid {
			t.Errorf("expected valid when T3 has FAMILY_AFFILIATION=1")
		}
	})

	t.Run("T1 with T2 FAMILY_AFFILIATION=2 only - should fail", func(t *testing.T) {
		r1 := testutil.NewTestRecord(t1IntSchema, 1, nil)
		r2 := testutil.NewTestRecord(t2IntSchema, 2, map[string]any{"FAMILY_AFFILIATION": 2})
		group := testutil.NewTestGroup(r1, r2)
		result := runGroupValidator(t, filespecKey, validatorID, params, group)
		if result.Valid {
			t.Errorf("expected invalid when no T2/T3 has FAMILY_AFFILIATION=1")
		}
	})

	t.Run("T1 with no T2/T3 - should fail", func(t *testing.T) {
		r1 := testutil.NewTestRecord(t1IntSchema, 1, nil)
		group := testutil.NewTestGroup(r1)
		result := runGroupValidator(t, filespecKey, validatorID, params, group)
		if result.Valid {
			t.Errorf("expected invalid when T1 has no T2/T3")
		}
	})

	t.Run("T1 with multiple T2s, one has FAMILY_AFFILIATION=1 - should pass", func(t *testing.T) {
		r1 := testutil.NewTestRecord(t1IntSchema, 1, nil)
		r2 := testutil.NewTestRecord(t2IntSchema, 2, map[string]any{"FAMILY_AFFILIATION": 2})
		r3 := testutil.NewTestRecord(t2IntSchema, 3, map[string]any{"FAMILY_AFFILIATION": 1})
		r4 := testutil.NewTestRecord(t2IntSchema, 4, map[string]any{"FAMILY_AFFILIATION": 3})
		group := testutil.NewTestGroup(r1, r2, r3, r4)
		result := runGroupValidator(t, filespecKey, validatorID, params, group)
		if !result.Valid {
			t.Errorf("expected valid when at least one T2 has FAMILY_AFFILIATION=1")
		}
	})

	t.Run("T1 with mixed T2/T3, T3 has FAMILY_AFFILIATION=1 - should pass", func(t *testing.T) {
		r1 := testutil.NewTestRecord(t1IntSchema, 1, nil)
		r2 := testutil.NewTestRecord(t2IntSchema, 2, map[string]any{"FAMILY_AFFILIATION": 2})
		r3 := testutil.NewTestRecord(t3IntSchema, 3, map[string]any{"FAMILY_AFFILIATION": 1})
		group := testutil.NewTestGroup(r1, r2, r3)
		result := runGroupValidator(t, filespecKey, validatorID, params, group)
		if !result.Valid {
			t.Errorf("expected valid when T3 has FAMILY_AFFILIATION=1")
		}
	})
}

func TestCat4_T2RequiresT1(t *testing.T) {
	const filespecKey = "TAN:1"
	const validatorID = "requires_corresponding_record"

	params := map[string]any{
		"record_type":          "T2",
		"required_record_type": "T1",
	}

	t.Run("no T2 records - should pass", func(t *testing.T) {
		rec := testutil.NewTestRecord(t1IntSchema, 1, nil)
		group := testutil.NewTestGroup(rec)
		result := runGroupValidator(t, filespecKey, validatorID, params, group)
		if !result.Valid {
			t.Errorf("expected valid when no T2 records")
		}
	})

	t.Run("T2 with T1 - should pass", func(t *testing.T) {
		r1 := testutil.NewTestRecord(t1IntSchema, 1, nil)
		r2 := testutil.NewTestRecord(t2IntSchema, 2, nil)
		group := testutil.NewTestGroup(r1, r2)
		result := runGroupValidator(t, filespecKey, validatorID, params, group)
		if !result.Valid {
			t.Errorf("expected valid when T2 has corresponding T1")
		}
	})

	t.Run("T2 without T1 - should fail", func(t *testing.T) {
		rec := testutil.NewTestRecord(t2IntSchema, 1, nil)
		group := testutil.NewTestGroup(rec)
		result := runGroupValidator(t, filespecKey, validatorID, params, group)
		if result.Valid {
			t.Errorf("expected invalid when T2 has no corresponding T1")
		}
	})

	t.Run("multiple T2s without T1 - should fail", func(t *testing.T) {
		r1 := testutil.NewTestRecord(t2IntSchema, 1, nil)
		r2 := testutil.NewTestRecord(t2IntSchema, 2, nil)
		r3 := testutil.NewTestRecord(t3IntSchema, 3, nil)
		group := testutil.NewTestGroup(r1, r2, r3)
		result := runGroupValidator(t, filespecKey, validatorID, params, group)
		if result.Valid {
			t.Errorf("expected invalid when T2s have no corresponding T1")
		}
	})
}

func TestCat4_T3RequiresT1(t *testing.T) {
	const filespecKey = "TAN:1"
	const validatorID = "requires_corresponding_record"

	params := map[string]any{
		"record_type":          "T3",
		"required_record_type": "T1",
	}

	t.Run("no T3 records - should pass", func(t *testing.T) {
		rec := testutil.NewTestRecord(t1IntSchema, 1, nil)
		group := testutil.NewTestGroup(rec)
		result := runGroupValidator(t, filespecKey, validatorID, params, group)
		if !result.Valid {
			t.Errorf("expected valid when no T3 records")
		}
	})

	t.Run("T3 with T1 - should pass", func(t *testing.T) {
		r1 := testutil.NewTestRecord(t1IntSchema, 1, nil)
		r2 := testutil.NewTestRecord(t3IntSchema, 2, nil)
		group := testutil.NewTestGroup(r1, r2)
		result := runGroupValidator(t, filespecKey, validatorID, params, group)
		if !result.Valid {
			t.Errorf("expected valid when T3 has corresponding T1")
		}
	})

	t.Run("T3 without T1 - should fail", func(t *testing.T) {
		rec := testutil.NewTestRecord(t3IntSchema, 1, nil)
		group := testutil.NewTestGroup(rec)
		result := runGroupValidator(t, filespecKey, validatorID, params, group)
		if result.Valid {
			t.Errorf("expected invalid when T3 has no corresponding T1")
		}
	})

	t.Run("multiple T3s without T1 - should fail", func(t *testing.T) {
		r1 := testutil.NewTestRecord(t2IntSchema, 1, nil)
		r2 := testutil.NewTestRecord(t3IntSchema, 2, nil)
		r3 := testutil.NewTestRecord(t3IntSchema, 3, nil)
		group := testutil.NewTestGroup(r1, r2, r3)
		result := runGroupValidator(t, filespecKey, validatorID, params, group)
		if result.Valid {
			t.Errorf("expected invalid when T3s have no corresponding T1")
		}
	})
}

// =============================================================================
// TANF Section 2 Cat4 Validators
// =============================================================================

func TestCat4_T4RequiresT5(t *testing.T) {
	const filespecKey = "TAN:2"
	const validatorID = "requires_corresponding_record"

	params := map[string]any{
		"record_type":          "T4",
		"required_record_type": "T5",
	}

	t.Run("no T4 records - should pass", func(t *testing.T) {
		rec := testutil.NewTestRecord(t5IntSchema, 1, nil)
		group := testutil.NewTestGroup(rec)
		result := runGroupValidator(t, filespecKey, validatorID, params, group)
		if !result.Valid {
			t.Errorf("expected valid when no T4 records")
		}
	})

	t.Run("T4 with T5 - should pass", func(t *testing.T) {
		r1 := testutil.NewTestRecord(t4IntSchema, 1, nil)
		r2 := testutil.NewTestRecord(t5IntSchema, 2, nil)
		group := testutil.NewTestGroup(r1, r2)
		result := runGroupValidator(t, filespecKey, validatorID, params, group)
		if !result.Valid {
			t.Errorf("expected valid when T4 has corresponding T5")
		}
	})

	t.Run("T4 without T5 - should fail", func(t *testing.T) {
		rec := testutil.NewTestRecord(t4IntSchema, 1, nil)
		group := testutil.NewTestGroup(rec)
		result := runGroupValidator(t, filespecKey, validatorID, params, group)
		if result.Valid {
			t.Errorf("expected invalid when T4 has no corresponding T5")
		}
	})

	t.Run("multiple T4s with T5 - should pass", func(t *testing.T) {
		r1 := testutil.NewTestRecord(t4IntSchema, 1, nil)
		r2 := testutil.NewTestRecord(t4IntSchema, 2, nil)
		r3 := testutil.NewTestRecord(t5IntSchema, 3, nil)
		group := testutil.NewTestGroup(r1, r2, r3)
		result := runGroupValidator(t, filespecKey, validatorID, params, group)
		if !result.Valid {
			t.Errorf("expected valid when T4s have corresponding T5")
		}
	})
}

func TestCat4_T5RequiresT4(t *testing.T) {
	const filespecKey = "TAN:2"
	const validatorID = "requires_corresponding_record"

	params := map[string]any{
		"record_type":          "T5",
		"required_record_type": "T4",
	}

	t.Run("no T5 records - should pass", func(t *testing.T) {
		rec := testutil.NewTestRecord(t4IntSchema, 1, nil)
		group := testutil.NewTestGroup(rec)
		result := runGroupValidator(t, filespecKey, validatorID, params, group)
		if !result.Valid {
			t.Errorf("expected valid when no T5 records")
		}
	})

	t.Run("T5 with T4 - should pass", func(t *testing.T) {
		r1 := testutil.NewTestRecord(t4IntSchema, 1, nil)
		r2 := testutil.NewTestRecord(t5IntSchema, 2, nil)
		group := testutil.NewTestGroup(r1, r2)
		result := runGroupValidator(t, filespecKey, validatorID, params, group)
		if !result.Valid {
			t.Errorf("expected valid when T5 has corresponding T4")
		}
	})

	t.Run("T5 without T4 - should fail", func(t *testing.T) {
		rec := testutil.NewTestRecord(t5IntSchema, 1, nil)
		group := testutil.NewTestGroup(rec)
		result := runGroupValidator(t, filespecKey, validatorID, params, group)
		if result.Valid {
			t.Errorf("expected invalid when T5 has no corresponding T4")
		}
	})

	t.Run("multiple T5s without T4 - should fail", func(t *testing.T) {
		r1 := testutil.NewTestRecord(t5IntSchema, 1, nil)
		r2 := testutil.NewTestRecord(t5IntSchema, 2, nil)
		group := testutil.NewTestGroup(r1, r2)
		result := runGroupValidator(t, filespecKey, validatorID, params, group)
		if result.Valid {
			t.Errorf("expected invalid when T5s have no corresponding T4")
		}
	})

	t.Run("multiple T5s with T4 - should pass", func(t *testing.T) {
		r1 := testutil.NewTestRecord(t4IntSchema, 1, nil)
		r2 := testutil.NewTestRecord(t5IntSchema, 2, nil)
		r3 := testutil.NewTestRecord(t5IntSchema, 3, nil)
		r4 := testutil.NewTestRecord(t5IntSchema, 4, nil)
		group := testutil.NewTestGroup(r1, r2, r3, r4)
		result := runGroupValidator(t, filespecKey, validatorID, params, group)
		if !result.Valid {
			t.Errorf("expected valid when T5s have corresponding T4")
		}
	})
}

func TestCat4_GenericValidatorBindingsAcrossPrograms(t *testing.T) {
	tests := []struct {
		name        string
		filespecKey string
		validatorID string
		params      map[string]any
		group       *parser.ParsedGroup
	}{
		{
			name:        "SSP section 1 maps M1 to M2/M3",
			filespecKey: "SSP:1",
			validatorID: "requires_related_record",
			params: map[string]any{
				"record_type":          "M1",
				"related_record_types": []any{"M2", "M3"},
			},
			group: testutil.NewTestGroup(
				testutil.NewTestRecord(m1IntSchema, 1, nil),
				testutil.NewTestRecord(m2IntSchema, 2, nil),
			),
		},
		{
			name:        "SSP section 2 maps M4 to M5",
			filespecKey: "SSP:2",
			validatorID: "requires_corresponding_record",
			params: map[string]any{
				"record_type":          "M4",
				"required_record_type": "M5",
			},
			group: testutil.NewTestGroup(
				testutil.NewTestRecord(m4IntSchema, 1, nil),
				testutil.NewTestRecord(m5IntSchema, 2, nil),
			),
		},
		{
			name:        "Tribal section 1 maps T1 to T2/T3",
			filespecKey: "TRIBAL:1",
			validatorID: "requires_related_record",
			params: map[string]any{
				"record_type":          "T1",
				"related_record_types": []any{"T2", "T3"},
			},
			group: testutil.NewTestGroup(
				testutil.NewTestRecord(t1IntSchema, 1, nil),
				testutil.NewTestRecord(t3IntSchema, 2, nil),
			),
		},
		{
			name:        "Tribal section 2 maps T4 to T5",
			filespecKey: "TRIBAL:2",
			validatorID: "requires_corresponding_record",
			params: map[string]any{
				"record_type":          "T4",
				"required_record_type": "T5",
			},
			group: testutil.NewTestGroup(
				testutil.NewTestRecord(t4IntSchema, 1, nil),
				testutil.NewTestRecord(t5IntSchema, 2, nil),
			),
		},
	}

	for _, tc := range tests {
		t.Run(tc.name, func(t *testing.T) {
			result := runGroupValidator(t, tc.filespecKey, tc.validatorID, tc.params, tc.group)
			if !result.Valid {
				t.Errorf("expected valid result for %s", tc.name)
			}
		})
	}
}
