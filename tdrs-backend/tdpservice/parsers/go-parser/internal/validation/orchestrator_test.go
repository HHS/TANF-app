package validation

import (
	"testing"
)

// TestOrchestratorExecutionOrder tests that validation runs in order 4 → 1 → 2 → 3
func TestOrchestratorExecutionOrder(t *testing.T) {
	// Create a registry with validators for each category
	registry := NewValidatorRegistry()

	// Add validators programmatically since we're testing
	registry.exprOpts = RegisterFunctions()

	// Compile Cat4 validator that always passes
	cat4Expr, _ := registry.getOrCompileExpr(Cat4, "TotalRecords > 0")
	registry.cat4["TEST:1"] = []*CompiledValidator{
		{ID: "cat4_check", Category: Cat4, Expr: cat4Expr},
	}

	// Compile Cat1 validator that always passes
	cat1Expr, _ := registry.getOrCompileExpr(Cat1, "RecordLength > 0")
	registry.cat1["T1"] = []*CompiledValidator{
		{ID: "cat1_check", Category: Cat1, Expr: cat1Expr},
	}

	// Compile Cat2 validator
	cat2Expr, _ := registry.getOrCompileExpr(Cat2, "Value > 0")
	registry.cat2["T1"] = map[string][]*CompiledValidator{
		"AMOUNT": {{ID: "cat2_check", Category: Cat2, Expr: cat2Expr}},
	}

	// Compile Cat3 validator
	cat3Expr, _ := registry.getOrCompileExpr(Cat3, "GetInt('AMOUNT') > 0")
	registry.cat3["T1"] = []*CompiledValidator{
		{ID: "cat3_check", Category: Cat3, Expr: cat3Expr},
	}

	// Create orchestrator
	orchestrator := NewOrchestrator(registry, 0)

	// Create test data
	records := []Record{
		&mockRecord{
			recordType:  "T1",
			lineNumber:  1,
			decodedSize: 100,
			fields:      map[string]any{"AMOUNT": 50},
		},
	}
	group := newMockWrappedGroup(records)

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

// TestOrchestratorShortCircuitOnCat4Failure tests that Cat2/Cat3 are skipped when Cat4 fails
func TestOrchestratorShortCircuitOnCat4Failure(t *testing.T) {
	registry := NewValidatorRegistry()
	registry.exprOpts = RegisterFunctions()

	// Cat4 validator that always fails
	cat4Expr, _ := registry.getOrCompileExpr(Cat4, "TotalRecords > 100")
	registry.cat4["TEST:1"] = []*CompiledValidator{
		{ID: "cat4_fail", Category: Cat4, Expr: cat4Expr},
	}

	// Cat1 validator that passes
	cat1Expr, _ := registry.getOrCompileExpr(Cat1, "RecordLength > 0")
	registry.cat1["T1"] = []*CompiledValidator{
		{ID: "cat1_pass", Category: Cat1, Expr: cat1Expr},
	}

	// Cat2 and Cat3 validators (should be skipped)
	cat2Expr, _ := registry.getOrCompileExpr(Cat2, "Value > 0")
	registry.cat2["T1"] = map[string][]*CompiledValidator{
		"AMOUNT": {{ID: "cat2_check", Category: Cat2, Expr: cat2Expr}},
	}

	orchestrator := NewOrchestrator(registry, 0)

	records := []Record{
		&mockRecord{
			recordType:  "T1",
			lineNumber:  1,
			decodedSize: 100,
			fields:      map[string]any{"AMOUNT": -50}, // Would fail Cat2 if not skipped
		},
	}
	group := newMockWrappedGroup(records)

	result := orchestrator.ValidateGroup(group, "TEST:1")

	// Should have Cat4 error
	if len(result.Cat4Errors) != 1 {
		t.Errorf("expected 1 Cat4 error, got %d", len(result.Cat4Errors))
	}

	// Record should be marked as skipped
	if !result.RecordResults[0].Skipped {
		t.Error("record should be skipped due to Cat4 failure")
	}

	// Should have no Cat2 errors (skipped)
	if len(result.RecordResults[0].Cat2Errors) != 0 {
		t.Error("Cat2 should be skipped")
	}
}

// TestOrchestratorShortCircuitOnCat1Failure tests that Cat2/Cat3 are skipped when Cat1 fails
func TestOrchestratorShortCircuitOnCat1Failure(t *testing.T) {
	registry := NewValidatorRegistry()
	registry.exprOpts = RegisterFunctions()

	// Cat1 validator that fails
	cat1Expr, _ := registry.getOrCompileExpr(Cat1, "RecordLength > 200")
	registry.cat1["T1"] = []*CompiledValidator{
		{ID: "cat1_fail", Category: Cat1, Expr: cat1Expr},
	}

	// Cat2 validator (should be skipped)
	cat2Expr, _ := registry.getOrCompileExpr(Cat2, "Value > 0")
	registry.cat2["T1"] = map[string][]*CompiledValidator{
		"AMOUNT": {{ID: "cat2_check", Category: Cat2, Expr: cat2Expr}},
	}

	orchestrator := NewOrchestrator(registry, 0)

	records := []Record{
		&mockRecord{
			recordType:  "T1",
			lineNumber:  1,
			decodedSize: 100, // Will fail Cat1 (requires > 200)
			fields:      map[string]any{"AMOUNT": -50}, // Would fail Cat2 if not skipped
		},
	}
	group := newMockWrappedGroup(records)

	result := orchestrator.ValidateGroup(group, "TEST:1")

	// Should have Cat1 error
	if len(result.RecordResults[0].Cat1Errors) != 1 {
		t.Errorf("expected 1 Cat1 error, got %d", len(result.RecordResults[0].Cat1Errors))
	}

	// Record should be marked as skipped
	if !result.RecordResults[0].Skipped {
		t.Error("record should be skipped due to Cat1 failure")
	}

	// Should have no Cat2 errors (skipped)
	if len(result.RecordResults[0].Cat2Errors) != 0 {
		t.Error("Cat2 should be skipped")
	}
}

// TestOrchestratorParallelValidation tests parallel group validation
func TestOrchestratorParallelValidation(t *testing.T) {
	registry := NewValidatorRegistry()
	registry.exprOpts = RegisterFunctions()

	// Simple passing Cat4 validator
	cat4Expr, _ := registry.getOrCompileExpr(Cat4, "TotalRecords >= 0")
	registry.cat4["TEST:1"] = []*CompiledValidator{
		{ID: "cat4_pass", Category: Cat4, Expr: cat4Expr},
	}

	// Create orchestrator with 4 workers
	orchestrator := NewOrchestrator(registry, 4)

	// Create multiple groups
	var groups []WrappedGroup
	for i := 0; i < 10; i++ {
		records := []Record{
			&mockRecord{recordType: "T1", decodedSize: 100},
		}
		groups = append(groups, newMockWrappedGroup(records))
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

// TestOrchestratorCat2FieldValidation tests that Cat2 validates specific fields
func TestOrchestratorCat2FieldValidation(t *testing.T) {
	registry := NewValidatorRegistry()
	registry.exprOpts = RegisterFunctions()

	// Cat2 validator for AMOUNT field
	cat2Expr, _ := registry.getOrCompileExpr(Cat2, "Value > 0")
	registry.cat2["T1"] = map[string][]*CompiledValidator{
		"AMOUNT": {{ID: "positive_amount", Category: Cat2, Expr: cat2Expr}},
	}

	orchestrator := NewOrchestrator(registry, 0)

	records := []Record{
		&mockRecord{
			recordType:  "T1",
			decodedSize: 100,
			fields:      map[string]any{"AMOUNT": -10}, // Negative - should fail
		},
	}
	group := newMockWrappedGroup(records)

	result := orchestrator.ValidateGroup(group, "TEST:1")

	// Should have Cat2 error
	if len(result.RecordResults[0].Cat2Errors) != 1 {
		t.Errorf("expected 1 Cat2 error, got %d", len(result.RecordResults[0].Cat2Errors))
	}

	// Check field name is set
	if result.RecordResults[0].Cat2Errors[0].FieldName != "AMOUNT" {
		t.Errorf("expected FieldName=AMOUNT, got %s", result.RecordResults[0].Cat2Errors[0].FieldName)
	}
}
