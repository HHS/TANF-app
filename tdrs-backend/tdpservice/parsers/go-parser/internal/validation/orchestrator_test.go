package validation

import (
	"testing"

	"go-parser/internal/testutil"
)

// TestOrchestratorMultiGroupValidation tests validating multiple groups
func TestOrchestratorMultiGroupValidation(t *testing.T) {
	registry := newValidatorRegistry()
	registry.exprOpts = RegisterFunctions()

	// Simple passing group validator
	groupExpr, _ := registry.getOrCompileExpr(ScopeGroup, "TotalRecords >= 0", "single")
	registry.group["TEST:1"] = []*CompiledValidator{
		{ID: "group_pass", Scope: ScopeGroup, ErrorType: ErrorTypeCaseConsistency, Expr: groupExpr},
	}

	orchestrator := NewValidationOrchestrator(registry, true)

	// Create and validate multiple groups
	var results []*GroupValidationResult
	for i := 0; i < 10; i++ {
		rec := testutil.NewTestRecord(t1Schema, 1, nil)
		group := testutil.NewTestGroup(rec)
		results = append(results, orchestrator.ValidateGroup(group, "TEST:1"))
	}

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
	registry := newValidatorRegistry()
	registry.exprOpts = RegisterFunctions()

	// Field validator for AMOUNT field
	fieldExpr, _ := registry.getOrCompileExpr(ScopeField, "Value > 0", "single")
	registry.field["T1"] = map[string][]*CompiledValidator{
		"AMOUNT": {{ID: "positive_amount", Scope: ScopeField, ErrorType: ErrorTypeFieldValue, Expr: fieldExpr}},
	}

	orchestrator := NewValidationOrchestrator(registry, true)

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
	registry := newValidatorRegistry()
	registry.exprOpts = RegisterFunctions()

	// Field validator for AMOUNT field - would fail on nil
	fieldExpr, _ := registry.getOrCompileExpr(ScopeField, "Value > 0", "single")
	registry.field["T1"] = map[string][]*CompiledValidator{
		"AMOUNT": {{ID: "positive_amount", Scope: ScopeField, ErrorType: ErrorTypeFieldValue, Expr: fieldExpr}},
	}

	orchestrator := NewValidationOrchestrator(registry, true)

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
	registry := newValidatorRegistry()
	registry.exprOpts = RegisterFunctions()

	// Field validator that would fail on nil
	fieldExpr, _ := registry.getOrCompileExpr(ScopeField, "isNotEmpty(Value)", "single")
	registry.field["T1"] = map[string][]*CompiledValidator{
		"AMOUNT": {{ID: "not_empty", Scope: ScopeField, ErrorType: ErrorTypeFieldValue, Expr: fieldExpr}},
	}

	orchestrator := NewValidationOrchestrator(registry, true)

	// Record with nil optional field (Required defaults to false)
	rec := testutil.NewTestRecord(t1Schema, 1, map[string]any{"AMOUNT": nil})
	group := testutil.NewTestGroup(rec)

	result := orchestrator.ValidateGroup(group, "TEST:1")

	// Should have NO errors - optional nil field skips validation entirely
	if len(result.RecordResults[0].FieldErrors) != 0 {
		t.Errorf("expected 0 field errors for nil optional field, got %d", len(result.RecordResults[0].FieldErrors))
	}
}

// TestOrchestratorShortCircuitSkipsFieldValidation tests that with shortCircuit=true,
// field validators are skipped when a precheck validator fails.
func TestOrchestratorShortCircuitSkipsFieldValidation(t *testing.T) {
	registry := newValidatorRegistry()
	registry.exprOpts = RegisterFunctions()

	// Record precheck that always fails
	precheckExpr, _ := registry.getOrCompileExpr(ScopeRecord, "false", "single")
	registry.record["T1"] = []*CompiledValidator{
		{ID: "always_fail", Scope: ScopeRecord, ErrorType: ErrorTypeRecordPreCheck, Expr: precheckExpr},
	}

	// Field validator that would produce an error
	fieldExpr, _ := registry.getOrCompileExpr(ScopeField, "Value > 0", "single")
	registry.field["T1"] = map[string][]*CompiledValidator{
		"AMOUNT": {{ID: "positive_amount", Scope: ScopeField, ErrorType: ErrorTypeFieldValue, Expr: fieldExpr}},
	}

	orchestrator := NewValidationOrchestrator(registry, true)

	rec := testutil.NewTestRecord(t1Schema, 1, map[string]any{"AMOUNT": -10})
	group := testutil.NewTestGroup(rec)
	result := orchestrator.ValidateGroup(group, "TEST:1")

	// Precheck error should exist
	if len(result.RecordResults[0].RecordErrors) != 1 {
		t.Fatalf("expected 1 record error, got %d", len(result.RecordResults[0].RecordErrors))
	}

	// Field validators should be skipped
	if len(result.RecordResults[0].FieldErrors) != 0 {
		t.Errorf("expected 0 field errors (short-circuited), got %d", len(result.RecordResults[0].FieldErrors))
	}

	if !result.RecordResults[0].Skipped {
		t.Error("expected Skipped=true when short-circuiting")
	}
}

// TestOrchestratorNoShortCircuitRunsAllValidation tests that with shortCircuit=false,
// field validators run even when a precheck validator fails.
func TestOrchestratorNoShortCircuitRunsAllValidation(t *testing.T) {
	registry := newValidatorRegistry()
	registry.exprOpts = RegisterFunctions()

	// Record precheck that always fails
	precheckExpr, _ := registry.getOrCompileExpr(ScopeRecord, "false", "single")
	registry.record["T1"] = []*CompiledValidator{
		{ID: "always_fail", Scope: ScopeRecord, ErrorType: ErrorTypeRecordPreCheck, Expr: precheckExpr},
	}

	// Field validator that would produce an error
	fieldExpr, _ := registry.getOrCompileExpr(ScopeField, "Value > 0", "single")
	registry.field["T1"] = map[string][]*CompiledValidator{
		"AMOUNT": {{ID: "positive_amount", Scope: ScopeField, ErrorType: ErrorTypeFieldValue, Expr: fieldExpr}},
	}

	orchestrator := NewValidationOrchestrator(registry, false)

	rec := testutil.NewTestRecord(t1Schema, 1, map[string]any{"AMOUNT": -10})
	group := testutil.NewTestGroup(rec)
	result := orchestrator.ValidateGroup(group, "TEST:1")

	// Precheck error should exist
	if len(result.RecordResults[0].RecordErrors) != 1 {
		t.Fatalf("expected 1 record error, got %d", len(result.RecordResults[0].RecordErrors))
	}

	// Field validators should still run
	if len(result.RecordResults[0].FieldErrors) != 1 {
		t.Errorf("expected 1 field error (no short-circuit), got %d", len(result.RecordResults[0].FieldErrors))
	}

	if result.RecordResults[0].Skipped {
		t.Error("expected Skipped=false when short-circuit is disabled")
	}
}

// TestOrchestratorNoShortCircuitWithGroupBlock tests that with shortCircuit=false,
// field validators run even when a group validator blocks.
func TestOrchestratorNoShortCircuitWithGroupBlock(t *testing.T) {
	registry := newValidatorRegistry()
	registry.exprOpts = RegisterFunctions()

	// Group validator that always fails
	groupExpr, _ := registry.getOrCompileExpr(ScopeGroup, "false", "single")
	registry.group["TEST:1"] = []*CompiledValidator{
		{ID: "group_fail", Scope: ScopeGroup, ErrorType: ErrorTypeCaseConsistency, Expr: groupExpr},
	}

	// Field validator that would produce an error
	fieldExpr, _ := registry.getOrCompileExpr(ScopeField, "Value > 0", "single")
	registry.field["T1"] = map[string][]*CompiledValidator{
		"AMOUNT": {{ID: "positive_amount", Scope: ScopeField, ErrorType: ErrorTypeFieldValue, Expr: fieldExpr}},
	}

	orchestrator := NewValidationOrchestrator(registry, false)

	rec := testutil.NewTestRecord(t1Schema, 1, map[string]any{"AMOUNT": -10})
	group := testutil.NewTestGroup(rec)
	result := orchestrator.ValidateGroup(group, "TEST:1")

	// Group error should exist
	if len(result.GroupErrors) != 1 {
		t.Fatalf("expected 1 group error, got %d", len(result.GroupErrors))
	}

	// Field validators should still run despite group block
	if len(result.RecordResults[0].FieldErrors) != 1 {
		t.Errorf("expected 1 field error (no short-circuit), got %d", len(result.RecordResults[0].FieldErrors))
	}

	if result.RecordResults[0].Skipped {
		t.Error("expected Skipped=false when short-circuit is disabled")
	}
}
