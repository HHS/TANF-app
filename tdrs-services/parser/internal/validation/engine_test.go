package validation

import (
	"testing"

	configpkg "go-parser/internal/config"
	"go-parser/internal/config/schema"
	configValidation "go-parser/internal/config/validation"
	"go-parser/internal/testutil"
)

func TestProductionValidators_LoadHybridAndNative(t *testing.T) {
	for _, engine := range []string{ValidationEngineHybrid, ValidationEngineNative} {
		t.Run(engine, func(t *testing.T) {
			cfg := configpkg.DefaultConfig()
			cfg.Global.ConfigDir = realConfigDir(t)
			cfg.Validation.Engine = engine

			reg, err := configpkg.NewRegistry(cfg)
			if err != nil {
				t.Fatalf("config.NewRegistry failed: %v", err)
			}

			validators, err := NewRegistry(cfg, reg)
			if err != nil {
				t.Fatalf("NewRegistry(%s) failed: %v", engine, err)
			}
			if validators == nil {
				t.Fatal("expected validator registry")
			}
		})
	}
}

func TestValidationEngineRejectsUnknownValue(t *testing.T) {
	cfg := configpkg.DefaultConfig()
	cfg.Global.ConfigDir = realConfigDir(t)
	cfg.Validation.Engine = "fast-ish"

	reg, err := configpkg.NewRegistry(cfg)
	if err != nil {
		t.Fatalf("config.NewRegistry failed: %v", err)
	}

	if _, err := NewRegistry(cfg, reg); err == nil {
		t.Fatal("expected unknown validation engine to fail")
	}
}

func TestNativeEngineRejectsMissingNativeExecutor(t *testing.T) {
	registry := newValidatorRegistry()
	registry.engine = ValidationEngineNative
	registry.exprOpts = RegisterFunctions()

	_, err := registry.resolveValidatorByScope(ScopeField, &configValidation.ValidatorDef{
		ID:   "ad_hoc_expr_only",
		Expr: "Value > 0",
	}, "")
	if err == nil {
		t.Fatal("expected native engine to reject validator without native executor")
	}
}

func TestHybridEngineFallsBackToExpr(t *testing.T) {
	registry := newValidatorRegistry()
	registry.engine = ValidationEngineHybrid
	registry.exprOpts = RegisterFunctions()

	cv, err := registry.resolveValidatorByScope(ScopeField, &configValidation.ValidatorDef{
		ID:   "ad_hoc_expr_only",
		Expr: "Value > 0",
	}, "")
	if err != nil {
		t.Fatalf("resolveValidatorByScope failed: %v", err)
	}
	if cv.Native != nil {
		t.Fatal("expected ad hoc validator to use expr fallback")
	}

	env := &FieldEnv{Value: 1, Params: cv.Params}
	if result := Execute(cv, env); !result.Valid {
		t.Fatalf("expected hybrid expr fallback to pass, got error %v", result.Error)
	}
}

func TestProductionNativeParityRepresentativeValidators(t *testing.T) {
	exprRegistry, reg := loadProductionValidatorsForEngine(t, ValidationEngineExpr)
	nativeRegistry, _ := loadProductionValidatorsForEngine(t, ValidationEngineNative)

	t.Run("field in_range_int", func(t *testing.T) {
		schemaKey, fieldName, exprCV := findProductionFieldValidator(t, exprRegistry, "in_range_int")
		nativeCV := validatorByID(nativeRegistry.GetFieldValidators(schemaKey, fieldName), exprCV.ID)
		min := mustIntParam(t, exprCV.Params, "min")

		assertExecuteParity(t, exprCV, nativeCV, &FieldEnv{Value: min})
		assertExecuteParity(t, exprCV, nativeCV, &FieldEnv{Value: min - 1})
	})

	t.Run("field in_values", func(t *testing.T) {
		schemaKey, fieldName, exprCV := findProductionFieldValidator(t, exprRegistry, "in_values")
		nativeCV := validatorByID(nativeRegistry.GetFieldValidators(schemaKey, fieldName), exprCV.ID)
		values := mustAnySliceParam(t, exprCV.Params, "values")

		assertExecuteParity(t, exprCV, nativeCV, &FieldEnv{Value: values[0]})
		assertExecuteParity(t, exprCV, nativeCV, &FieldEnv{Value: "__not_allowed__"})
	})

	t.Run("record ifthenalso_range_to_range", func(t *testing.T) {
		schemaKey, exprCV := findProductionRecordValidator(t, exprRegistry, "ifthenalso_range_to_range")
		nativeCV := validatorByID(nativeRegistry.GetRecordValidators(schemaKey), exprCV.ID)
		cs := reg.GetSchema(schemaKey)
		conditionField := mustStringParam(t, exprCV.Params, "condition_field")
		targetField := mustStringParam(t, exprCV.Params, "target_field")
		conditionMin := mustIntParam(t, exprCV.Params, "condition_min")
		targetMin := mustIntParam(t, exprCV.Params, "target_min")

		valid := testutil.NewTestRecord(cs, 10, map[string]any{
			conditionField: conditionMin,
			targetField:    targetMin,
		})
		invalid := testutil.NewTestRecord(cs, 11, map[string]any{
			conditionField: conditionMin,
			targetField:    targetMin - 1,
		})

		assertExecuteParity(t, exprCV, nativeCV, NewRecordEnv(valid))
		assertExecuteParity(t, exprCV, nativeCV, NewRecordEnv(invalid))
	})

	t.Run("record rpt_month_year_matches_header_year_quarter", func(t *testing.T) {
		schemaKey, exprCV := findProductionRecordValidator(t, exprRegistry, "rpt_month_year_matches_header_year_quarter")
		nativeCV := validatorByID(nativeRegistry.GetRecordValidators(schemaKey), exprCV.ID)
		cs := reg.GetSchema(schemaKey)
		dfCtx := &DataFileContext{FiscalYear: 2024, FiscalQuarter: "Q1"}

		valid := NewRecordEnv(testutil.NewTestRecord(cs, 12, map[string]any{"RPT_MONTH_YEAR": "202310"}))
		valid.DataFileContext = dfCtx
		invalid := NewRecordEnv(testutil.NewTestRecord(cs, 13, map[string]any{"RPT_MONTH_YEAR": "202401"}))
		invalid.DataFileContext = dfCtx

		assertExecuteParity(t, exprCV, nativeCV, valid)
		assertExecuteParity(t, exprCV, nativeCV, invalid)
	})

	t.Run("group requires_related_record", func(t *testing.T) {
		filespecKey, exprCV := findProductionGroupValidator(t, exprRegistry, "requires_related_record")
		nativeCV := validatorByID(nativeRegistry.GetGroupValidators(filespecKey), exprCV.ID)
		recordType := mustStringParam(t, exprCV.Params, "record_type")
		recordSchema := schemaForRecordType(t, reg, recordType)
		group := testutil.NewTestGroup(testutil.NewTestRecord(recordSchema, 20, nil))

		assertExecuteGroupParity(t, exprCV, nativeCV, NewGroupEnv(group))
	})

	t.Run("group exact_duplicates", func(t *testing.T) {
		filespecKey, exprCV := findProductionGroupValidator(t, exprRegistry, "exact_duplicates")
		nativeCV := validatorByID(nativeRegistry.GetGroupValidators(filespecKey), exprCV.ID)
		recordType := mustStringParam(t, exprCV.Params, "record_type")
		recordSchema := schemaForRecordType(t, reg, recordType)
		group := testutil.NewTestGroup(
			testutil.NewTestRecord(recordSchema, 30, map[string]any{"CASE_NUMBER": "1"}),
			testutil.NewTestRecord(recordSchema, 31, map[string]any{"CASE_NUMBER": "1"}),
		)

		assertExecuteGroupParity(t, exprCV, nativeCV, NewGroupEnv(group))
	})
}

func loadProductionValidatorsForEngine(t *testing.T, engine string) (*ValidatorRegistry, *configpkg.Registry) {
	t.Helper()

	cfg := configpkg.DefaultConfig()
	cfg.Global.ConfigDir = realConfigDir(t)
	cfg.Validation.Engine = engine

	reg, err := configpkg.NewRegistry(cfg)
	if err != nil {
		t.Fatalf("config.NewRegistry failed: %v", err)
	}

	validators, err := NewRegistry(cfg, reg)
	if err != nil {
		t.Fatalf("NewRegistry(%s) failed: %v", engine, err)
	}
	return validators, reg
}

func findProductionFieldValidator(t *testing.T, registry *ValidatorRegistry, id string) (string, string, *CompiledValidator) {
	t.Helper()

	for schemaKey, fields := range registry.field {
		for fieldName, validators := range fields {
			if cv := validatorByID(validators, id); cv != nil {
				return schemaKey, fieldName, cv
			}
		}
	}
	t.Fatalf("missing field validator %s", id)
	return "", "", nil
}

func findProductionRecordValidator(t *testing.T, registry *ValidatorRegistry, id string) (string, *CompiledValidator) {
	t.Helper()

	for schemaKey, validators := range registry.record {
		if cv := validatorByID(validators, id); cv != nil {
			return schemaKey, cv
		}
	}
	t.Fatalf("missing record validator %s", id)
	return "", nil
}

func findProductionGroupValidator(t *testing.T, registry *ValidatorRegistry, id string) (string, *CompiledValidator) {
	t.Helper()

	for filespecKey, validators := range registry.group {
		if cv := validatorByID(validators, id); cv != nil {
			return filespecKey, cv
		}
	}
	t.Fatalf("missing group validator %s", id)
	return "", nil
}

func validatorByID(validators []*CompiledValidator, id string) *CompiledValidator {
	for _, validator := range validators {
		if validator.ID == id {
			return validator
		}
	}
	return nil
}

func assertExecuteParity(t *testing.T, exprCV *CompiledValidator, nativeCV *CompiledValidator, env any) {
	t.Helper()

	exprResult := Execute(exprCV, cloneEnvWithParams(env, exprCV.Params))
	nativeResult := Execute(nativeCV, cloneEnvWithParams(env, nativeCV.Params))
	if exprResult.Valid != nativeResult.Valid {
		t.Fatalf("%s parity mismatch: expr valid=%v err=%v, native valid=%v err=%v",
			exprCV.ID, exprResult.Valid, exprResult.Error, nativeResult.Valid, nativeResult.Error)
	}
}

func assertExecuteGroupParity(t *testing.T, exprCV *CompiledValidator, nativeCV *CompiledValidator, env *GroupEnv) {
	t.Helper()

	exprResults := ExecuteGroup(exprCV, cloneEnvWithParams(env, exprCV.Params).(*GroupEnv))
	nativeResults := ExecuteGroup(nativeCV, cloneEnvWithParams(env, nativeCV.Params).(*GroupEnv))
	if len(exprResults) != len(nativeResults) {
		t.Fatalf("%s group result count mismatch: expr=%d native=%d", exprCV.ID, len(exprResults), len(nativeResults))
	}
	for i := range exprResults {
		if exprResults[i].LineNumber != nativeResults[i].LineNumber || exprResults[i].RecordType != nativeResults[i].RecordType {
			t.Fatalf("%s group result %d mismatch: expr line/type=%d/%s native line/type=%d/%s",
				exprCV.ID,
				i,
				exprResults[i].LineNumber,
				exprResults[i].RecordType,
				nativeResults[i].LineNumber,
				nativeResults[i].RecordType,
			)
		}
	}
}

func cloneEnvWithParams(env any, params map[string]any) any {
	switch typed := env.(type) {
	case *FieldEnv:
		clone := *typed
		clone.Params = params
		return &clone
	case *RecordEnv:
		clone := *typed
		clone.Params = params
		return &clone
	case *GroupEnv:
		clone := *typed
		clone.Params = params
		return &clone
	default:
		return env
	}
}

func mustStringParam(t *testing.T, params map[string]any, key string) string {
	t.Helper()
	value, err := requiredStringParam(params, key)
	if err != nil {
		t.Fatal(err)
	}
	return value
}

func mustIntParam(t *testing.T, params map[string]any, key string) int {
	t.Helper()
	value, err := requiredIntParam(params, key)
	if err != nil {
		t.Fatal(err)
	}
	return value
}

func mustAnySliceParam(t *testing.T, params map[string]any, key string) []any {
	t.Helper()
	value, err := requiredAnySliceParam(params, key)
	if err != nil {
		t.Fatal(err)
	}
	return value
}

func schemaForRecordType(t *testing.T, reg *configpkg.Registry, recordType string) *schema.CompiledSchema {
	t.Helper()
	for _, cs := range reg.Schemas() {
		if cs.RecordType == recordType {
			return cs
		}
	}
	t.Fatalf("missing schema for record type %s", recordType)
	return nil
}
