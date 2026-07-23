package validation

import (
	"testing"

	"go-parser/internal/parser"
)

func mustExprValidator(t testing.TB, id string, scope string, ce *CompiledExpr, resultMode string) *CompiledValidator {
	t.Helper()
	executor, err := newExprExecutor(ce, scope, resultMode)
	if err != nil {
		t.Fatalf("newExprExecutor failed: %v", err)
	}
	return &CompiledValidator{
		ID:         id,
		Scope:      scope,
		ResultMode: resultMode,
		Engine:     ValidationEngineExpr,
		Expression: ce.Expr,
		Executor:   executor,
	}
}

func mustExprExecutor(t testing.TB, ce *CompiledExpr, scope string, resultMode string) ValidatorExecutor {
	t.Helper()
	executor, err := newExprExecutor(ce, scope, resultMode)
	if err != nil {
		t.Fatalf("newExprExecutor failed: %v", err)
	}
	return executor
}

func newTestValidationOrchestrator(t testing.TB, registry *ValidatorRegistry, shortCircuit bool) *ValidationOrchestrator {
	t.Helper()
	hydrateRegistryExecutors(t, registry)
	return NewValidationOrchestrator(registry, shortCircuit)
}

func hydrateRegistryExecutors(t testing.TB, registry *ValidatorRegistry) {
	t.Helper()
	for _, fields := range registry.field {
		for _, validators := range fields {
			for _, cv := range validators {
				hydrateExprValidator(t, cv)
			}
		}
	}
	for _, validators := range registry.record {
		for _, cv := range validators {
			hydrateExprValidator(t, cv)
		}
	}
	for _, validators := range registry.group {
		for _, cv := range validators {
			hydrateExprValidator(t, cv)
		}
	}
}

func hydrateExprValidator(t testing.TB, cv *CompiledValidator) {
	t.Helper()
	if cv == nil || cv.Executor != nil || cv.Expr == nil {
		return
	}
	resultMode := cv.ResultMode
	if resultMode == "" {
		resultMode = "single"
		cv.ResultMode = resultMode
	}
	cv.Engine = ValidationEngineExpr
	cv.Expression = cv.Expr.Expr
	cv.Executor = mustExprExecutor(t, cv.Expr, cv.Scope, resultMode)
}

func fieldState(value any) *ValidationState {
	return &ValidationState{Scope: ScopeField, Value: value}
}

func recordState(rec *parser.ParsedRecord) *ValidationState {
	return NewRecordValidationState(rec, nil)
}

func groupState(group *parser.ParsedGroup) *ValidationState {
	return NewGroupValidationState(group, nil)
}
