package validation

import (
	"testing"

	"go-parser/internal/parser"
	"go-parser/internal/testutil"
)

// TestOrchestratorParallelValidation tests parallel group validation
func TestOrchestratorParallelValidation(t *testing.T) {
	registry := NewValidatorRegistry()
	registry.exprOpts = RegisterFunctions()

	// Simple passing group validator
	groupExpr, _ := registry.getOrCompileExpr(ScopeGroup, "TotalRecords >= 0", "single")
	registry.group["TEST:1"] = []*CompiledValidator{
		{ID: "group_pass", Scope: ScopeGroup, ErrorType: ErrorTypeCaseConsistency, Expr: groupExpr},
	}

	// Create orchestrator with 4 workers
	orchestrator := NewOrchestrator(registry, 4)

	// Create multiple groups
	var groups []*parser.ParsedGroup
	for i := 0; i < 10; i++ {
		rec := testutil.NewTestRecord(t1Schema, 1, nil)
		groups = append(groups, testutil.NewTestGroup(rec))
	}

	results := orchestrator.ValidateGroups(groups, "TEST:1")

	if len(results) != 10 {
		t.Errorf("expected 10 results, got %d", len(results))
	}

	// All should pass
	for i, r := range results {
		if r.HasErrors() {
			t.Errorf("group %d should not have errors", i)
		}
	}
}

// TestOrchestratorFieldValidation tests that field validators validate specific fields
func TestOrchestratorFieldValidation(t *testing.T) {
	registry := NewValidatorRegistry()
	registry.exprOpts = RegisterFunctions()

	// Field validator for AMOUNT field
	fieldExpr, _ := registry.getOrCompileExpr(ScopeField, "Value > 0", "single")
	registry.field["T1"] = map[string][]*CompiledValidator{
		"AMOUNT": {{ID: "positive_amount", Scope: ScopeField, ErrorType: ErrorTypeFieldValue, Expr: fieldExpr}},
	}

	orchestrator := NewOrchestrator(registry, 0)

	rec := testutil.NewTestRecord(t1Schema, 1, map[string]any{"AMOUNT": -10}) // Negative - should fail
	group := testutil.NewTestGroup(rec)

	result := orchestrator.ValidateGroup(group, "TEST:1")

	// Should have field error
	if len(result.RecordResults[0].FieldErrors) != 1 {
		t.Errorf("expected 1 field error, got %d", len(result.RecordResults[0].FieldErrors))
	}

	// Check field name is set
	if result.RecordResults[0].FieldErrors[0].FieldName != "AMOUNT" {
		t.Errorf("expected FieldName=AMOUNT, got %s", result.RecordResults[0].FieldErrors[0].FieldName)
	}
}

// TestOrchestratorNilRequiredFieldSkipsValidators tests that nil required fields
// generate a field_required error and skip all validators for that field
func TestOrchestratorNilRequiredFieldSkipsValidators(t *testing.T) {
	registry := NewValidatorRegistry()
	registry.exprOpts = RegisterFunctions()

	// Field validator for AMOUNT field - would fail on nil
	fieldExpr, _ := registry.getOrCompileExpr(ScopeField, "Value > 0", "single")
	registry.field["T1"] = map[string][]*CompiledValidator{
		"AMOUNT": {{ID: "positive_amount", Scope: ScopeField, ErrorType: ErrorTypeFieldValue, Expr: fieldExpr}},
	}

	orchestrator := NewOrchestrator(registry, 0)

	// Record with nil required field — use a separate schema so Required=true
	reqSchema := testutil.NewTestSchema("T1", "AMOUNT")
	reqSchema.Shared[0].Required = true
	rec := testutil.NewTestRecord(reqSchema, 1, map[string]any{"AMOUNT": nil})
	group := testutil.NewTestGroup(rec)

	result := orchestrator.ValidateGroup(group, "TEST:1")

	// Should have exactly 1 field error (field_required)
	if len(result.RecordResults[0].FieldErrors) != 1 {
		t.Errorf("expected 1 field error, got %d", len(result.RecordResults[0].FieldErrors))
	}

	// Check it's a field_required error
	err := result.RecordResults[0].FieldErrors[0]
	if err.ValidatorID != "field_required" {
		t.Errorf("expected ValidatorID=field_required, got %s", err.ValidatorID)
	}
	if err.FieldName != "AMOUNT" {
		t.Errorf("expected FieldName=AMOUNT, got %s", err.FieldName)
	}
}

// TestOrchestratorNilOptionalFieldSkipsValidators tests that nil optional fields
// skip validators entirely (no error, no validation)
func TestOrchestratorNilOptionalFieldSkipsValidators(t *testing.T) {
	registry := NewValidatorRegistry()
	registry.exprOpts = RegisterFunctions()

	// Field validator that would fail on nil
	fieldExpr, _ := registry.getOrCompileExpr(ScopeField, "isNotEmpty(Value)", "single")
	registry.field["T1"] = map[string][]*CompiledValidator{
		"AMOUNT": {{ID: "not_empty", Scope: ScopeField, ErrorType: ErrorTypeFieldValue, Expr: fieldExpr}},
	}

	orchestrator := NewOrchestrator(registry, 0)

	// Record with nil optional field (Required defaults to false)
	rec := testutil.NewTestRecord(t1Schema, 1, map[string]any{"AMOUNT": nil})
	group := testutil.NewTestGroup(rec)

	result := orchestrator.ValidateGroup(group, "TEST:1")

	// Should have NO errors - optional nil field skips validation entirely
	if len(result.RecordResults[0].FieldErrors) != 0 {
		t.Errorf("expected 0 field errors for nil optional field, got %d", len(result.RecordResults[0].FieldErrors))
	}
}
