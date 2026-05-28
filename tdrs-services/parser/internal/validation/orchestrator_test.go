package validation

import (
	"testing"

	"go-parser/internal/testutil"
)

var defaultTestDataFileContext = &DataFileContext{}

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
		results = append(results, orchestrator.ValidateGroup(group, "TEST:1", defaultTestDataFileContext))
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

	result := orchestrator.ValidateGroup(group, "TEST:1", defaultTestDataFileContext)

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

	result := orchestrator.ValidateGroup(group, "TEST:1", defaultTestDataFileContext)

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

	optionalSchema := testutil.NewTestSchema("T1", "AMOUNT")
	rec := testutil.NewTestRecord(optionalSchema, 1, map[string]any{"AMOUNT": nil})
	group := testutil.NewTestGroup(rec)

	result := orchestrator.ValidateGroup(group, "TEST:1", defaultTestDataFileContext)

	// Should have NO errors - optional nil field skips validation entirely
	if len(result.RecordResults[0].FieldErrors) != 0 {
		t.Errorf("expected 0 field errors for nil optional field, got %d", len(result.RecordResults[0].FieldErrors))
	}
}

func TestOrchestratorOptionalFieldWithValueSkipsValidators(t *testing.T) {
	registry := newValidatorRegistry()
	registry.exprOpts = RegisterFunctions()

	fieldExpr, _ := registry.getOrCompileExpr(ScopeField, "Value > 0", "single")
	registry.field["T1"] = map[string][]*CompiledValidator{
		"AMOUNT": {{ID: "positive_amount", Scope: ScopeField, ErrorType: ErrorTypeFieldValue, Expr: fieldExpr}},
	}

	orchestrator := NewValidationOrchestrator(registry, true)

	optionalSchema := testutil.NewTestSchema("T1", "AMOUNT")
	rec := testutil.NewTestRecord(optionalSchema, 1, map[string]any{"AMOUNT": -10})
	group := testutil.NewTestGroup(rec)

	result := orchestrator.ValidateGroup(group, "TEST:1", defaultTestDataFileContext)

	if len(result.RecordResults[0].FieldErrors) != 0 {
		t.Errorf("expected 0 field errors for populated optional field, got %d", len(result.RecordResults[0].FieldErrors))
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
	result := orchestrator.ValidateGroup(group, "TEST:1", defaultTestDataFileContext)

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
	result := orchestrator.ValidateGroup(group, "TEST:1", defaultTestDataFileContext)

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
	result := orchestrator.ValidateGroup(group, "TEST:1", defaultTestDataFileContext)

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

// TestOrchestratorRecordConsistencyValidation tests that record consistency validators
// (non-precheck record validators) run after field validators.
func TestOrchestratorRecordConsistencyValidation(t *testing.T) {
	registry := newValidatorRegistry()
	registry.exprOpts = RegisterFunctions()

	// Record consistency validator
	consistencyExpr, _ := registry.getOrCompileExpr(ScopeRecord, "GetInt('AMOUNT') > 0 or GetString('CASE_NUMBER') != ''", "single")
	registry.record["T1"] = []*CompiledValidator{
		{ID: "consistency_check", Scope: ScopeRecord, ErrorType: ErrorTypeValueConsistency, Expr: consistencyExpr},
	}

	orchestrator := NewValidationOrchestrator(registry, true)

	t.Run("consistency check passes", func(t *testing.T) {
		rec := testutil.NewTestRecord(t1Schema, 1, map[string]any{"AMOUNT": 100, "CASE_NUMBER": "12345"})
		group := testutil.NewTestGroup(rec)
		result := orchestrator.ValidateGroup(group, "TEST:1", defaultTestDataFileContext)

		if result.HasErrors() {
			t.Error("expected no errors when consistency check passes")
		}
	})

	t.Run("consistency check fails", func(t *testing.T) {
		rec := testutil.NewTestRecord(t1Schema, 1, map[string]any{"AMOUNT": 0, "CASE_NUMBER": ""})
		group := testutil.NewTestGroup(rec)
		result := orchestrator.ValidateGroup(group, "TEST:1", defaultTestDataFileContext)

		if len(result.RecordResults[0].RecordErrors) != 1 {
			t.Fatalf("expected 1 record error, got %d", len(result.RecordResults[0].RecordErrors))
		}
		err := result.RecordResults[0].RecordErrors[0]
		if err.ErrorType != ErrorTypeValueConsistency {
			t.Errorf("expected VALUE_CONSISTENCY, got %s", err.ErrorType)
		}
	})
}

// TestOrchestratorShortCircuitSkipsConsistencyValidation tests that record consistency
// validators are also skipped when precheck fails and short-circuit is enabled.
func TestOrchestratorShortCircuitSkipsConsistencyValidation(t *testing.T) {
	registry := newValidatorRegistry()
	registry.exprOpts = RegisterFunctions()

	// Record precheck that always fails
	precheckExpr, _ := registry.getOrCompileExpr(ScopeRecord, "false", "single")
	// Record consistency that would also fail
	consistencyExpr, _ := registry.getOrCompileExpr(ScopeRecord, "false", "single")
	registry.record["T1"] = []*CompiledValidator{
		{ID: "precheck_fail", Scope: ScopeRecord, ErrorType: ErrorTypeRecordPreCheck, Expr: precheckExpr},
		{ID: "consistency_fail", Scope: ScopeRecord, ErrorType: ErrorTypeValueConsistency, Expr: consistencyExpr},
	}

	orchestrator := NewValidationOrchestrator(registry, true)

	rec := testutil.NewTestRecord(t1Schema, 1, nil)
	group := testutil.NewTestGroup(rec)
	result := orchestrator.ValidateGroup(group, "TEST:1", defaultTestDataFileContext)

	// Only precheck error should exist, consistency should be skipped
	if len(result.RecordResults[0].RecordErrors) != 1 {
		t.Fatalf("expected 1 record error (precheck only), got %d", len(result.RecordResults[0].RecordErrors))
	}
	if result.RecordResults[0].RecordErrors[0].ValidatorID != "precheck_fail" {
		t.Errorf("expected precheck_fail error, got %s", result.RecordResults[0].RecordErrors[0].ValidatorID)
	}
	if !result.RecordResults[0].Skipped {
		t.Error("expected Skipped=true")
	}
}

func TestValidateHeaderDoesNotShortCircuitOnFieldOrConsistencyErrors(t *testing.T) {
	registry := newValidatorRegistry()
	registry.exprOpts = RegisterFunctions()

	fieldExpr, _ := registry.getOrCompileExpr(ScopeField, "Value > 0", "single")
	registry.field["T1"] = map[string][]*CompiledValidator{
		"AMOUNT": {{ID: "positive_amount", Scope: ScopeField, ErrorType: ErrorTypeFieldValue, Expr: fieldExpr}},
	}

	consistencyExpr, _ := registry.getOrCompileExpr(ScopeRecord, "GetString('CASE_NUMBER') != ''", "single")
	registry.record["T1"] = []*CompiledValidator{
		{ID: "consistency_fail", Scope: ScopeRecord, ErrorType: ErrorTypeValueConsistency, Expr: consistencyExpr},
	}

	orchestrator := NewValidationOrchestrator(registry, true)

	headerRec := testutil.NewTestRecord(t1Schema, 1, map[string]any{"AMOUNT": -10, "CASE_NUMBER": ""})
	result := orchestrator.ValidateHeader(headerRec, &DataFileContext{})

	if result.Skipped {
		t.Fatal("expected Skipped=false for field and consistency errors")
	}
	if len(result.FieldErrors) != 1 {
		t.Fatalf("expected 1 field error, got %d", len(result.FieldErrors))
	}
	if len(result.RecordErrors) != 1 {
		t.Fatalf("expected 1 record error, got %d", len(result.RecordErrors))
	}
	if result.RecordErrors[0].ErrorType != ErrorTypeValueConsistency {
		t.Fatalf("expected VALUE_CONSISTENCY, got %s", result.RecordErrors[0].ErrorType)
	}
}

func TestValidateHeaderOptionalFieldWithValueSkipsValidators(t *testing.T) {
	registry := newValidatorRegistry()
	registry.exprOpts = RegisterFunctions()

	fieldExpr, _ := registry.getOrCompileExpr(ScopeField, "Value > 0", "single")
	registry.field["T1"] = map[string][]*CompiledValidator{
		"AMOUNT": {{ID: "positive_amount", Scope: ScopeField, ErrorType: ErrorTypeFieldValue, Expr: fieldExpr}},
	}

	orchestrator := NewValidationOrchestrator(registry, true)

	optionalSchema := testutil.NewTestSchema("T1", "AMOUNT")
	headerRec := testutil.NewTestRecord(optionalSchema, 1, map[string]any{"AMOUNT": -10})
	result := orchestrator.ValidateHeader(headerRec, &DataFileContext{})

	if len(result.FieldErrors) != 0 {
		t.Fatalf("expected 0 field errors for populated optional header field, got %d", len(result.FieldErrors))
	}
}

func TestValidateGroup_RecordValidatorUsesDataFileContext(t *testing.T) {
	registry := newValidatorRegistry()
	registry.exprOpts = RegisterFunctions()

	recordExpr, _ := registry.getOrCompileExpr(
		ScopeRecord,
		"year(GetString('RPT_MONTH_YEAR')) == fiscalToCalendarYear(DataFileContext.FiscalYear, DataFileContext.FiscalQuarter) and string(quarter(GetString('RPT_MONTH_YEAR'))) == fiscalToCalendarQuarter(DataFileContext.FiscalYear, DataFileContext.FiscalQuarter)",
		"single",
	)
	registry.record["T1"] = []*CompiledValidator{
		{
			ID:        "rpt_month_year_matches_header_year_quarter",
			Scope:     ScopeRecord,
			ErrorType: ErrorTypeRecordPreCheck,
			Expr:      recordExpr,
			Fields:    []string{"RPT_MONTH_YEAR"},
		},
	}

	orchestrator := NewValidationOrchestrator(registry, true)
	recordSchema := testutil.NewTestSchema("T1", "RPT_MONTH_YEAR")
	dfCtx := &DataFileContext{FiscalYear: 2024, FiscalQuarter: "Q2"}

	validGroup := testutil.NewTestGroup(
		testutil.NewTestRecord(recordSchema, 1, map[string]any{"RPT_MONTH_YEAR": "202401"}),
	)
	validResult := orchestrator.ValidateGroup(validGroup, "TEST:1", dfCtx)
	if len(validResult.RecordResults[0].RecordErrors) != 0 {
		t.Fatalf("expected no record errors for matching reporting period, got %d", len(validResult.RecordResults[0].RecordErrors))
	}

	invalidGroup := testutil.NewTestGroup(
		testutil.NewTestRecord(recordSchema, 1, map[string]any{"RPT_MONTH_YEAR": "202310"}),
	)
	invalidResult := orchestrator.ValidateGroup(invalidGroup, "TEST:1", dfCtx)
	if len(invalidResult.RecordResults[0].RecordErrors) != 1 {
		t.Fatalf("expected 1 record error for mismatched reporting period, got %d", len(invalidResult.RecordResults[0].RecordErrors))
	}
}

// TestOrchestratorGroupBlockingWithShortCircuit tests that group-level blocking errors
// cause field and consistency validators to be skipped when short-circuit is enabled.
func TestOrchestratorGroupBlockingWithShortCircuit(t *testing.T) {
	registry := newValidatorRegistry()
	registry.exprOpts = RegisterFunctions()

	// Group validator that always fails with CASE_CONSISTENCY
	groupExpr, _ := registry.getOrCompileExpr(ScopeGroup, "false", "single")
	registry.group["TEST:1"] = []*CompiledValidator{
		{ID: "group_block", Scope: ScopeGroup, ErrorType: ErrorTypeCaseConsistency, Expr: groupExpr},
	}

	// Field and consistency validators that would fail
	fieldExpr, _ := registry.getOrCompileExpr(ScopeField, "Value > 0", "single")
	registry.field["T1"] = map[string][]*CompiledValidator{
		"AMOUNT": {{ID: "positive_amount", Scope: ScopeField, ErrorType: ErrorTypeFieldValue, Expr: fieldExpr}},
	}

	consistencyExpr, _ := registry.getOrCompileExpr(ScopeRecord, "false", "single")
	registry.record["T1"] = []*CompiledValidator{
		{ID: "consistency_fail", Scope: ScopeRecord, ErrorType: ErrorTypeValueConsistency, Expr: consistencyExpr},
	}

	orchestrator := NewValidationOrchestrator(registry, true)

	rec := testutil.NewTestRecord(t1Schema, 1, map[string]any{"AMOUNT": -10})
	group := testutil.NewTestGroup(rec)
	result := orchestrator.ValidateGroup(group, "TEST:1", defaultTestDataFileContext)

	// Group error should exist
	if len(result.GroupErrors) != 1 {
		t.Fatalf("expected 1 group error, got %d", len(result.GroupErrors))
	}

	// Field and consistency should be skipped
	if len(result.RecordResults[0].FieldErrors) != 0 {
		t.Errorf("expected 0 field errors (group blocked), got %d", len(result.RecordResults[0].FieldErrors))
	}
	if len(result.RecordResults[0].RecordErrors) != 0 {
		t.Errorf("expected 0 record errors (group blocked), got %d", len(result.RecordResults[0].RecordErrors))
	}
	if !result.RecordResults[0].Skipped {
		t.Error("expected Skipped=true when group is blocked")
	}
}

// TestOrchestratorPerRecordGroupValidation tests group validators with per_record result mode.
func TestOrchestratorPerRecordGroupValidation(t *testing.T) {
	registry := newValidatorRegistry()
	registry.exprOpts = RegisterFunctions()

	// Group validator that returns duplicate records
	dupExpr, _ := registry.getOrCompileExpr(ScopeGroup, "getExactDuplicates(Group, 'T2')", "per_record")
	registry.group["TEST:1"] = []*CompiledValidator{
		{ID: "exact_duplicates", Scope: ScopeGroup, ErrorType: ErrorTypeCaseConsistency, ResultMode: "per_record", Expr: dupExpr},
	}

	orchestrator := NewValidationOrchestrator(registry, true)

	t.Run("no duplicates", func(t *testing.T) {
		group := testutil.NewTestGroup(
			testutil.NewTestRecord(t2Schema, 1, map[string]any{"SSN": "111111111", "FAMILY_AFFILIATION": 1}),
			testutil.NewTestRecord(t2Schema, 2, map[string]any{"SSN": "222222222", "FAMILY_AFFILIATION": 2}),
		)
		result := orchestrator.ValidateGroup(group, "TEST:1", defaultTestDataFileContext)

		if result.HasErrors() {
			t.Error("expected no errors when no duplicates")
		}
	})

	t.Run("with exact duplicates", func(t *testing.T) {
		group := testutil.NewTestGroup(
			testutil.NewTestRecord(t2Schema, 1, map[string]any{"SSN": "111111111", "FAMILY_AFFILIATION": 1}),
			testutil.NewTestRecord(t2Schema, 2, map[string]any{"SSN": "111111111", "FAMILY_AFFILIATION": 1}),
		)
		result := orchestrator.ValidateGroup(group, "TEST:1", defaultTestDataFileContext)

		if !result.HasErrors() {
			t.Error("expected errors with duplicates")
		}

		// Error should be attributed to line 2 (the duplicate)
		if len(result.RecordResults[1].RecordErrors) != 1 {
			t.Fatalf("expected 1 error on duplicate record, got %d", len(result.RecordResults[1].RecordErrors))
		}
		err := result.RecordResults[1].RecordErrors[0]
		if err.ValidatorID != "exact_duplicates" {
			t.Errorf("expected exact_duplicates, got %s", err.ValidatorID)
		}
		if err.LineNumber != 2 {
			t.Errorf("expected LineNumber=2, got %d", err.LineNumber)
		}
		if err.RecordType != "T2" {
			t.Errorf("expected RecordType=T2, got %s", err.RecordType)
		}
	})
}

// TestOrchestratorMultipleFieldValidators tests that multiple validators on the same field all run.
func TestOrchestratorMultipleFieldValidators(t *testing.T) {
	registry := newValidatorRegistry()
	registry.exprOpts = RegisterFunctions()

	expr1, _ := registry.getOrCompileExpr(ScopeField, "Value > 0", "single")
	expr2, _ := registry.getOrCompileExpr(ScopeField, "Value < 100", "single")
	registry.field["T1"] = map[string][]*CompiledValidator{
		"AMOUNT": {
			{ID: "min_check", Scope: ScopeField, ErrorType: ErrorTypeFieldValue, Expr: expr1},
			{ID: "max_check", Scope: ScopeField, ErrorType: ErrorTypeFieldValue, Expr: expr2},
		},
	}

	orchestrator := NewValidationOrchestrator(registry, true)

	t.Run("both pass", func(t *testing.T) {
		rec := testutil.NewTestRecord(t1Schema, 1, map[string]any{"AMOUNT": 50})
		group := testutil.NewTestGroup(rec)
		result := orchestrator.ValidateGroup(group, "TEST:1", defaultTestDataFileContext)
		if len(result.RecordResults[0].FieldErrors) != 0 {
			t.Errorf("expected 0 errors, got %d", len(result.RecordResults[0].FieldErrors))
		}
	})

	t.Run("both fail", func(t *testing.T) {
		rec := testutil.NewTestRecord(t1Schema, 1, map[string]any{"AMOUNT": -200})
		group := testutil.NewTestGroup(rec)
		result := orchestrator.ValidateGroup(group, "TEST:1", defaultTestDataFileContext)
		if len(result.RecordResults[0].FieldErrors) != 1 {
			// Only first fails (Value > 0), second passes (Value < 100 is true for -200)
			t.Errorf("expected 1 field error, got %d", len(result.RecordResults[0].FieldErrors))
		}
	})

	t.Run("value exceeds max only", func(t *testing.T) {
		rec := testutil.NewTestRecord(t1Schema, 1, map[string]any{"AMOUNT": 200})
		group := testutil.NewTestGroup(rec)
		result := orchestrator.ValidateGroup(group, "TEST:1", defaultTestDataFileContext)
		if len(result.RecordResults[0].FieldErrors) != 1 {
			t.Errorf("expected 1 field error (max_check), got %d", len(result.RecordResults[0].FieldErrors))
		}
		if result.RecordResults[0].FieldErrors[0].ValidatorID != "max_check" {
			t.Errorf("expected max_check error, got %s", result.RecordResults[0].FieldErrors[0].ValidatorID)
		}
	})
}

// TestOrchestratorMultiRecordGroup tests validation of a group with multiple records of different types.
func TestOrchestratorMultiRecordGroup(t *testing.T) {
	registry := newValidatorRegistry()
	registry.exprOpts = RegisterFunctions()

	// Different validators for different record types
	t1FieldExpr, _ := registry.getOrCompileExpr(ScopeField, "isNotEmpty(Value)", "single")
	t2FieldExpr, _ := registry.getOrCompileExpr(ScopeField, "isNotEmpty(Value)", "single")

	registry.field["T1"] = map[string][]*CompiledValidator{
		"CASE_NUMBER": {{ID: "case_required", Scope: ScopeField, ErrorType: ErrorTypeFieldValue, Expr: t1FieldExpr}},
	}
	registry.field["T2"] = map[string][]*CompiledValidator{
		"SSN": {{ID: "ssn_required", Scope: ScopeField, ErrorType: ErrorTypeFieldValue, Expr: t2FieldExpr}},
	}

	orchestrator := NewValidationOrchestrator(registry, true)

	rec1 := testutil.NewTestRecord(t1Schema, 1, map[string]any{"CASE_NUMBER": "12345"})
	rec2 := testutil.NewTestRecord(t2Schema, 2, map[string]any{"SSN": ""}) // empty - should fail

	group := testutil.NewTestGroup(rec1, rec2)
	result := orchestrator.ValidateGroup(group, "TEST:1", defaultTestDataFileContext)

	// T1 record should pass
	if result.RecordResults[0].HasErrors() {
		t.Error("expected T1 record to have no errors")
	}

	// T2 record should fail
	if !result.RecordResults[1].HasErrors() {
		t.Error("expected T2 record to have errors")
	}
	if len(result.RecordResults[1].FieldErrors) != 1 {
		t.Fatalf("expected 1 field error on T2, got %d", len(result.RecordResults[1].FieldErrors))
	}
	if result.RecordResults[1].FieldErrors[0].FieldName != "SSN" {
		t.Errorf("expected field error on SSN, got %s", result.RecordResults[1].FieldErrors[0].FieldName)
	}
}

// TestOrchestratorPrecheckAlwaysRuns tests that precheck validators always run,
// even when group-level is blocked (they run before short-circuit check).
func TestOrchestratorPrecheckAlwaysRuns(t *testing.T) {
	registry := newValidatorRegistry()
	registry.exprOpts = RegisterFunctions()

	// Group validator that always fails
	groupExpr, _ := registry.getOrCompileExpr(ScopeGroup, "false", "single")
	registry.group["TEST:1"] = []*CompiledValidator{
		{ID: "group_fail", Scope: ScopeGroup, ErrorType: ErrorTypeCaseConsistency, Expr: groupExpr},
	}

	// Record precheck validator
	precheckExpr, _ := registry.getOrCompileExpr(ScopeRecord, "false", "single")
	registry.record["T1"] = []*CompiledValidator{
		{ID: "precheck", Scope: ScopeRecord, ErrorType: ErrorTypeRecordPreCheck, Expr: precheckExpr},
	}

	orchestrator := NewValidationOrchestrator(registry, true)

	rec := testutil.NewTestRecord(t1Schema, 1, nil)
	group := testutil.NewTestGroup(rec)
	result := orchestrator.ValidateGroup(group, "TEST:1", defaultTestDataFileContext)

	// Precheck should still run even though group is blocked
	if len(result.RecordResults[0].RecordErrors) != 1 {
		t.Fatalf("expected 1 record error (precheck), got %d", len(result.RecordResults[0].RecordErrors))
	}
	if result.RecordResults[0].RecordErrors[0].ValidatorID != "precheck" {
		t.Errorf("expected precheck error, got %s", result.RecordResults[0].RecordErrors[0].ValidatorID)
	}
}

// TestOrchestratorEmptyGroup tests validation of a group with no records.
func TestOrchestratorEmptyGroup(t *testing.T) {
	registry := newValidatorRegistry()
	registry.exprOpts = RegisterFunctions()

	// Group validator that checks minimum records
	groupExpr, _ := registry.getOrCompileExpr(ScopeGroup, "TotalRecords >= 1", "single")
	registry.group["TEST:1"] = []*CompiledValidator{
		{ID: "min_records", Scope: ScopeGroup, ErrorType: ErrorTypeCaseConsistency, Expr: groupExpr},
	}

	orchestrator := NewValidationOrchestrator(registry, true)

	group := testutil.NewTestGroup() // empty group
	result := orchestrator.ValidateGroup(group, "TEST:1", defaultTestDataFileContext)

	if len(result.GroupErrors) != 1 {
		t.Fatalf("expected 1 group error, got %d", len(result.GroupErrors))
	}
	if result.GroupErrors[0].ValidatorID != "min_records" {
		t.Errorf("expected min_records error, got %s", result.GroupErrors[0].ValidatorID)
	}
}

func TestOrchestratorCreateNoRecordsCreatedError(t *testing.T) {
	orchestrator := NewValidationOrchestrator(newValidatorRegistry(), true)

	result := orchestrator.CreateNoRecordsCreatedError()
	if result == nil {
		t.Fatal("CreateNoRecordsCreatedError returned nil")
	}
	if result.Valid {
		t.Error("expected invalid result")
	}
	if result.ErrorType != ErrorTypePreCheck {
		t.Errorf("ErrorType = %q, want %q", result.ErrorType, ErrorTypePreCheck)
	}
	if result.ValidatorID != "no_records_created" {
		t.Errorf("ValidatorID = %q, want %q", result.ValidatorID, "no_records_created")
	}
	if got := result.Message(nil); got != "No records created." {
		t.Errorf("Message() = %q, want %q", got, "No records created.")
	}
}

// TestExecuteGroupEdgeCases tests edge cases in ExecuteGroup.
func TestExecuteGroupEdgeCases(t *testing.T) {
	registry := newValidatorRegistry()
	registry.exprOpts = RegisterFunctions()

	t.Run("invalid program type", func(t *testing.T) {
		cv := &CompiledValidator{
			ID:         "bad",
			ResultMode: "per_record",
			Expr:       &CompiledExpr{Expr: "test", Program: "not a program"},
		}
		results := ExecuteGroup(cv, nil)
		if len(results) != 1 {
			t.Fatalf("expected 1 error result, got %d", len(results))
		}
		if results[0].Error == nil {
			t.Error("expected error for bad program type")
		}
	})

	t.Run("per_record expression returning nil", func(t *testing.T) {
		// Compile an expression that returns an empty list (no duplicates)
		ce, _ := registry.getOrCompileExpr(ScopeGroup, "getExactDuplicates(Group, 'T2')", "per_record")
		cv := &CompiledValidator{ID: "dups", Expr: ce, ResultMode: "per_record"}

		group := testutil.NewTestGroup(
			testutil.NewTestRecord(t2Schema, 1, map[string]any{"SSN": "111111111", "FAMILY_AFFILIATION": 1}),
		)
		env := NewGroupEnv(group)
		results := ExecuteGroup(cv, env)
		if len(results) != 0 {
			t.Errorf("expected 0 results, got %d", len(results))
		}
	})

	t.Run("per_record expression returning records", func(t *testing.T) {
		ce, _ := registry.getOrCompileExpr(ScopeGroup, "getExactDuplicates(Group, 'T2')", "per_record")
		cv := &CompiledValidator{ID: "dups", Expr: ce, ResultMode: "per_record"}

		group := testutil.NewTestGroup(
			testutil.NewTestRecord(t2Schema, 1, map[string]any{"SSN": "111111111", "FAMILY_AFFILIATION": 1}),
			testutil.NewTestRecord(t2Schema, 2, map[string]any{"SSN": "111111111", "FAMILY_AFFILIATION": 1}),
		)
		env := NewGroupEnv(group)
		results := ExecuteGroup(cv, env)
		if len(results) != 1 {
			t.Errorf("expected 1 result, got %d", len(results))
		}
		if len(results) > 0 && results[0].LineNumber == 0 {
			t.Error("expected LineNumber to be populated on per_record result")
		}
	})

	t.Run("single mode delegates to Execute", func(t *testing.T) {
		ce, _ := registry.getOrCompileExpr(ScopeGroup, "RecordCounts['T2'] > 0", "single")
		cv := &CompiledValidator{ID: "has_t2", Expr: ce, ResultMode: "single"}

		group := testutil.NewTestGroup(
			testutil.NewTestRecord(t1Schema, 1, nil),
		)
		env := NewGroupEnv(group)
		results := ExecuteGroup(cv, env)
		if len(results) != 1 {
			t.Fatalf("expected 1 failure result, got %d", len(results))
		}
		if results[0].LineNumber != 0 {
			t.Error("expected LineNumber to be 0 for group-level error")
		}
	})
}

// TestOrchestratorFieldValidatorWithParams tests that field validators receive correct params.
func TestOrchestratorFieldValidatorWithParams(t *testing.T) {
	registry := newValidatorRegistry()
	registry.exprOpts = RegisterFunctions()

	fieldExpr, _ := registry.getOrCompileExpr(ScopeField, "Value >= Params.min and Value <= Params.max", "single")
	registry.field["T1"] = map[string][]*CompiledValidator{
		"AMOUNT": {{
			ID:        "in_range",
			Scope:     ScopeField,
			ErrorType: ErrorTypeFieldValue,
			Expr:      fieldExpr,
			Params:    map[string]any{"min": 0, "max": 100},
		}},
	}

	orchestrator := NewValidationOrchestrator(registry, true)

	t.Run("value in range", func(t *testing.T) {
		rec := testutil.NewTestRecord(t1Schema, 1, map[string]any{"AMOUNT": 50})
		group := testutil.NewTestGroup(rec)
		result := orchestrator.ValidateGroup(group, "TEST:1", defaultTestDataFileContext)
		if result.HasErrors() {
			t.Error("expected no errors for value in range")
		}
	})

	t.Run("value out of range", func(t *testing.T) {
		rec := testutil.NewTestRecord(t1Schema, 1, map[string]any{"AMOUNT": 200})
		group := testutil.NewTestGroup(rec)
		result := orchestrator.ValidateGroup(group, "TEST:1", defaultTestDataFileContext)
		if len(result.RecordResults[0].FieldErrors) != 1 {
			t.Errorf("expected 1 error for out-of-range value, got %d", len(result.RecordResults[0].FieldErrors))
		}
	})
}
