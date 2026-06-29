package validation

import (
	"testing"

	"go-parser/internal/testutil"
)

func TestExprEnvFactoryBuildsScopedEnvsFromValidationState(t *testing.T) {
	params := map[string]any{"min": 1}
	dfCtx := &DataFileContext{FiscalYear: 2024, FiscalQuarter: "Q1"}

	t.Run("field", func(t *testing.T) {
		state := &ValidationState{
			Value:           "abc",
			Params:          params,
			DataFileContext: dfCtx,
		}

		env, ok := exprEnvFactory(ScopeField)(state).(*FieldEnv)
		if !ok {
			t.Fatalf("expected *FieldEnv, got %T", env)
		}
		if state.Scope != ScopeField {
			t.Fatalf("expected state scope %q, got %q", ScopeField, state.Scope)
		}
		if env.Value != "abc" || env.Params["min"] != 1 || env.DataFileContext != dfCtx {
			t.Fatalf("field env did not preserve state values: %#v", env)
		}
	})

	t.Run("record", func(t *testing.T) {
		rec := testutil.NewTestRecord(t1Schema, 12, map[string]any{"CASE_NUMBER": "123"})
		state := NewRecordValidationState(rec, dfCtx)
		state.Params = params

		env, ok := exprEnvFactory(ScopeRecord)(state).(*RecordEnv)
		if !ok {
			t.Fatalf("expected *RecordEnv, got %T", env)
		}
		if env.ParsedRecord != rec || env.RecordType != "T1" || env.LineNumber != 12 || env.Params["min"] != 1 || env.DataFileContext != dfCtx {
			t.Fatalf("record env did not preserve state values: %#v", env)
		}
	})

	t.Run("group", func(t *testing.T) {
		group := testutil.NewTestGroup(
			testutil.NewTestRecord(t1Schema, 1, nil),
			testutil.NewTestRecord(t2Schema, 2, nil),
		)
		state := NewGroupValidationState(group, dfCtx)
		state.Params = params

		env, ok := exprEnvFactory(ScopeGroup)(state).(*GroupEnv)
		if !ok {
			t.Fatalf("expected *GroupEnv, got %T", env)
		}
		if env.Group != group || env.TotalRecords != 2 || env.RecordCounts["T1"] != 1 || env.RecordCounts["T2"] != 1 || env.Params["min"] != 1 || env.DataFileContext != dfCtx {
			t.Fatalf("group env did not preserve state values: %#v", env)
		}
	})
}
