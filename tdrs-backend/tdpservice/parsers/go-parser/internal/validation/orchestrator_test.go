package validation

import (
	"testing"

	"go-parser/internal/parser"
	"go-parser/internal/testutil"
)

// TestOrchestratorExecutionOrder tests that validation runs in order: group → record precheck → field → record consistency
func TestOrchestratorExecutionOrder(t *testing.T) {
	// Create a registry with validators for each scope
	registry := NewValidatorRegistry()

	// Add validators programmatically since we're testing
	registry.exprOpts = RegisterFunctions()

	// Compile group validator that always passes
	groupExpr, _ := registry.getOrCompileExpr(ScopeGroup, "TotalRecords > 0", "single")
	registry.group["TEST:1"] = []*CompiledValidator{
		{ID: "group_check", Scope: ScopeGroup, ErrorType: ErrorTypeCaseConsistency, Expr: groupExpr},
	}

	// Compile record validator (precheck) that always passes
	recordPrecheckExpr, _ := registry.getOrCompileExpr(ScopeRecord, "RecordLength > 0", "single")
	registry.record["T1"] = []*CompiledValidator{
		{ID: "record_precheck", Scope: ScopeRecord, ErrorType: ErrorTypeRecordPreCheck, Expr: recordPrecheckExpr},
	}

	// Compile field validator
	fieldExpr, _ := registry.getOrCompileExpr(ScopeField, "Value > 0", "single")
	registry.field["T1"] = map[string][]*CompiledValidator{
		"AMOUNT": {{ID: "field_check", Scope: ScopeField, ErrorType: ErrorTypeFieldValue, Expr: fieldExpr}},
	}

	// Add a record consistency validator
	recordConsistencyExpr, _ := registry.getOrCompileExpr(ScopeRecord, "GetInt('AMOUNT') > 0", "single")
	registry.record["T1"] = append(registry.record["T1"],
		&CompiledValidator{ID: "record_consistency", Scope: ScopeRecord, ErrorType: ErrorTypeValueConsistency, Expr: recordConsistencyExpr})

	// Create orchestrator
	orchestrator := NewOrchestrator(registry, 0)

	// Create test data — t1Schema defined in validation_test.go (has CASE_NUMBER, AMOUNT)
	rec := testutil.NewTestRecord(t1Schema, 1, map[string]any{"AMOUNT": 50})
	group := testutil.NewTestGroup(rec)

	// Run validation
	result := orchestrator.ValidateGroup(group, "TEST:1")

	// All validators should pass, so no errors
	if result.HasErrors() {
		t.Errorf("expected no errors, got %d", result.TotalErrorCount())
	}

	// Should have processed all records
	if len(result.RecordResults) != 1 {
		t.Errorf("expected 1 record result, got %d", len(result.RecordResults))
	}

	// Record should not be skipped
	if result.RecordResults[0].Skipped {
		t.Error("record should not be skipped")
	}
}

// TestOrchestratorShortCircuitOnGroupFailure tests that field and consistency validators are skipped when group fails
func TestOrchestratorShortCircuitOnGroupFailure(t *testing.T) {
	registry := NewValidatorRegistry()
	registry.exprOpts = RegisterFunctions()

	// Group validator that always fails
	groupExpr, _ := registry.getOrCompileExpr(ScopeGroup, "TotalRecords > 100", "single")
	registry.group["TEST:1"] = []*CompiledValidator{
		{ID: "group_fail", Scope: ScopeGroup, ErrorType: ErrorTypeCaseConsistency, Expr: groupExpr},
	}

	// Record precheck validator that passes
	recordPrecheckExpr, _ := registry.getOrCompileExpr(ScopeRecord, "RecordLength > 0", "single")
	registry.record["T1"] = []*CompiledValidator{
		{ID: "record_precheck", Scope: ScopeRecord, ErrorType: ErrorTypeRecordPreCheck, Expr: recordPrecheckExpr},
	}

	// Field validator (should be skipped)
	fieldExpr, _ := registry.getOrCompileExpr(ScopeField, "Value > 0", "single")
	registry.field["T1"] = map[string][]*CompiledValidator{
		"AMOUNT": {{ID: "field_check", Scope: ScopeField, ErrorType: ErrorTypeFieldValue, Expr: fieldExpr}},
	}

	orchestrator := NewOrchestrator(registry, 0)

	rec := testutil.NewTestRecord(t1Schema, 1, map[string]any{"AMOUNT": -50}) // Would fail field check if not skipped
	group := testutil.NewTestGroup(rec)

	result := orchestrator.ValidateGroup(group, "TEST:1")

	// Should have group error
	if len(result.GroupErrors) != 1 {
		t.Errorf("expected 1 group error, got %d", len(result.GroupErrors))
	}

	// Record should be marked as skipped
	if !result.RecordResults[0].Skipped {
		t.Error("record should be skipped due to group failure")
	}

	// Should have no field errors (skipped)
	if len(result.RecordResults[0].FieldErrors) != 0 {
		t.Error("field validators should be skipped")
	}
}

// TestOrchestratorShortCircuitOnRecordPrecheckFailure tests that field validators are skipped when record precheck fails
func TestOrchestratorShortCircuitOnRecordPrecheckFailure(t *testing.T) {
	registry := NewValidatorRegistry()
	registry.exprOpts = RegisterFunctions()

	// Record precheck validator that fails (default DecodedSize=156 < 200)
	recordPrecheckExpr, _ := registry.getOrCompileExpr(ScopeRecord, "RecordLength > 200", "single")
	registry.record["T1"] = []*CompiledValidator{
		{ID: "record_precheck_fail", Scope: ScopeRecord, ErrorType: ErrorTypeRecordPreCheck, Expr: recordPrecheckExpr},
	}

	// Field validator (should be skipped)
	fieldExpr, _ := registry.getOrCompileExpr(ScopeField, "Value > 0", "single")
	registry.field["T1"] = map[string][]*CompiledValidator{
		"AMOUNT": {{ID: "field_check", Scope: ScopeField, ErrorType: ErrorTypeFieldValue, Expr: fieldExpr}},
	}

	orchestrator := NewOrchestrator(registry, 0)

	rec := testutil.NewTestRecord(t1Schema, 1, map[string]any{"AMOUNT": -50}) // Would fail field check if not skipped
	group := testutil.NewTestGroup(rec)

	result := orchestrator.ValidateGroup(group, "TEST:1")

	// Should have record error (precheck)
	precheckErrors := 0
	for _, err := range result.RecordResults[0].RecordErrors {
		if err.ErrorType == ErrorTypeRecordPreCheck {
			precheckErrors++
		}
	}
	if precheckErrors != 1 {
		t.Errorf("expected 1 precheck error, got %d", precheckErrors)
	}

	// Record should be marked as skipped
	if !result.RecordResults[0].Skipped {
		t.Error("record should be skipped due to precheck failure")
	}

	// Should have no field errors (skipped)
	if len(result.RecordResults[0].FieldErrors) != 0 {
		t.Error("field validators should be skipped")
	}
}

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
