package validation

import (
	"os"
	"path/filepath"
	"testing"

	configpkg "go-parser/internal/config"
	"go-parser/internal/config/schema"
	"go-parser/internal/parser"
	"go-parser/internal/testutil"
)

func BenchmarkValidationFieldHotset(b *testing.B) {
	for _, engine := range benchmarkEngines() {
		b.Run(engine, func(b *testing.B) {
			validators, _ := loadProductionValidatorsForBenchmark(b, engine)
			items := []struct {
				cv    *CompiledValidator
				value any
			}{
				fieldBenchmarkItem(b, validators, "in_range_int"),
				fieldBenchmarkItem(b, validators, "in_values"),
				{cv: mustFieldValidatorForBenchmark(b, validators, "is_numeric"), value: "12345"},
				{cv: mustFieldValidatorForBenchmark(b, validators, "not_negative"), value: 0},
			}
			state := NewFieldValidationState(nil, "", nil, nil)

			b.ReportAllocs()
			b.ResetTimer()
			for i := 0; i < b.N; i++ {
				for _, item := range items {
					state.Value = item.value
					if result := Execute(item.cv, state); !result.Valid {
						b.Fatalf("validator %s failed: %v", item.cv.ID, result.Error)
					}
				}
			}
		})
	}
}

func BenchmarkValidationRecordHotset(b *testing.B) {
	for _, engine := range benchmarkEngines() {
		b.Run(engine, func(b *testing.B) {
			validators, reg := loadProductionValidatorsForBenchmark(b, engine)
			items := []struct {
				cv  *CompiledValidator
				env *ValidationState
			}{
				recordLengthBenchmarkItem(b, validators, reg),
				recordIfThenRangeBenchmarkItem(b, validators, reg),
				recordAmountRequiresPositiveBenchmarkItem(b, validators, reg),
				recordRptMonthYearBenchmarkItem(b, validators, reg),
			}

			b.ReportAllocs()
			b.ResetTimer()
			for i := 0; i < b.N; i++ {
				for _, item := range items {
					if result := Execute(item.cv, item.env); !result.Valid {
						b.Fatalf("validator %s failed: %v", item.cv.ID, result.Error)
					}
				}
			}
		})
	}
}

func BenchmarkValidationGroupHotset(b *testing.B) {
	for _, engine := range benchmarkEngines() {
		b.Run(engine, func(b *testing.B) {
			validators, reg := loadProductionValidatorsForBenchmark(b, engine)
			items := []struct {
				cv  *CompiledValidator
				env *ValidationState
			}{
				groupMaxRecordsBenchmarkItem(b, validators, reg),
				groupExactDuplicatesBenchmarkItem(b, validators, reg),
				groupRequiresRelatedBenchmarkItem(b, validators, reg),
			}

			b.ReportAllocs()
			b.ResetTimer()
			for i := 0; i < b.N; i++ {
				for _, item := range items {
					_ = ExecuteGroup(item.cv, item.env)
				}
			}
		})
	}
}

func BenchmarkValidationProductionGroup(b *testing.B) {
	for _, engine := range benchmarkEngines() {
		b.Run(engine, func(b *testing.B) {
			validators, reg := loadProductionValidatorsForBenchmark(b, engine)
			orchestrator := NewValidationOrchestrator(validators, false)
			group := productionLikeTANFSection1Group(b, reg)
			dfCtx := &DataFileContext{FiscalYear: 2024, FiscalQuarter: "Q1", SectionName: "Active Case Data", Program: "TAN"}

			b.ReportAllocs()
			b.ResetTimer()
			for i := 0; i < b.N; i++ {
				_ = orchestrator.ValidateGroup(group, "TAN:1", dfCtx)
			}
		})
	}
}

func benchmarkEngines() []string {
	return []string{ValidationEngineExpr, ValidationEngineHybrid, ValidationEngineNative}
}

func loadProductionValidatorsForBenchmark(b *testing.B, engine string) (*ValidatorRegistry, *configpkg.Registry) {
	b.Helper()

	cfg := configpkg.DefaultConfig()
	cfg.Global.ConfigDir = benchmarkConfigDir(b)
	cfg.Validation.Engine = engine

	reg, err := configpkg.NewRegistry(cfg)
	if err != nil {
		b.Fatalf("config.NewRegistry failed: %v", err)
	}
	validators, err := NewRegistry(cfg, reg)
	if err != nil {
		b.Fatalf("NewRegistry(%s) failed: %v", engine, err)
	}
	return validators, reg
}

func benchmarkConfigDir(b *testing.B) string {
	b.Helper()

	dir := filepath.Join("..", "..", "config")
	if _, err := os.Stat(dir); os.IsNotExist(err) {
		b.Fatal("real config directory not found -- benchmarks must run from go-parser root")
	}
	return dir
}

func fieldBenchmarkItem(b *testing.B, validators *ValidatorRegistry, id string) struct {
	cv    *CompiledValidator
	value any
} {
	b.Helper()

	cv := mustFieldValidatorForBenchmark(b, validators, id)
	switch id {
	case "in_range_int":
		return struct {
			cv    *CompiledValidator
			value any
		}{cv: cv, value: mustIntParamBenchmark(b, cv.Params, "min")}
	case "in_values":
		values := mustAnySliceParamBenchmark(b, cv.Params, "values")
		return struct {
			cv    *CompiledValidator
			value any
		}{cv: cv, value: values[0]}
	default:
		b.Fatalf("unsupported field benchmark validator %s", id)
		return struct {
			cv    *CompiledValidator
			value any
		}{}
	}
}

func mustFieldValidatorForBenchmark(b *testing.B, validators *ValidatorRegistry, id string) *CompiledValidator {
	b.Helper()
	_, _, cv := findFieldValidatorForBenchmark(b, validators, id)
	return cv
}

func findFieldValidatorForBenchmark(b *testing.B, validators *ValidatorRegistry, id string) (string, string, *CompiledValidator) {
	b.Helper()
	for schemaKey, fields := range validators.field {
		for fieldName, fieldValidators := range fields {
			if cv := validatorByID(fieldValidators, id); cv != nil {
				return schemaKey, fieldName, cv
			}
		}
	}
	b.Fatalf("missing field validator %s", id)
	return "", "", nil
}

func recordLengthBenchmarkItem(b *testing.B, validators *ValidatorRegistry, reg *configpkg.Registry) struct {
	cv  *CompiledValidator
	env *ValidationState
} {
	b.Helper()
	schemaKey, cv := findRecordValidatorForBenchmark(b, validators, "record_length_min")
	rec := testutil.NewTestRecord(reg.GetSchema(schemaKey), 1, nil)
	rec.DecodedSize = mustIntParamBenchmark(b, cv.Params, "min")
	return struct {
		cv  *CompiledValidator
		env *ValidationState
	}{cv: cv, env: NewRecordValidationState(rec, nil)}
}

func recordIfThenRangeBenchmarkItem(b *testing.B, validators *ValidatorRegistry, reg *configpkg.Registry) struct {
	cv  *CompiledValidator
	env *ValidationState
} {
	b.Helper()
	schemaKey, cv := findRecordValidatorForBenchmark(b, validators, "ifthenalso_range_to_range")
	rec := testutil.NewTestRecord(reg.GetSchema(schemaKey), 2, map[string]any{
		mustStringParamBenchmark(b, cv.Params, "condition_field"): mustIntParamBenchmark(b, cv.Params, "condition_min"),
		mustStringParamBenchmark(b, cv.Params, "target_field"):    mustIntParamBenchmark(b, cv.Params, "target_min"),
	})
	return struct {
		cv  *CompiledValidator
		env *ValidationState
	}{cv: cv, env: NewRecordValidationState(rec, nil)}
}

func recordAmountRequiresPositiveBenchmarkItem(b *testing.B, validators *ValidatorRegistry, reg *configpkg.Registry) struct {
	cv  *CompiledValidator
	env *ValidationState
} {
	b.Helper()
	schemaKey, cv := findRecordValidatorForBenchmark(b, validators, "amount_requires_positive")
	rec := testutil.NewTestRecord(reg.GetSchema(schemaKey), 3, map[string]any{
		mustStringParamBenchmark(b, cv.Params, "amount_field"):   1,
		mustStringParamBenchmark(b, cv.Params, "required_field"): 1,
	})
	return struct {
		cv  *CompiledValidator
		env *ValidationState
	}{cv: cv, env: NewRecordValidationState(rec, nil)}
}

func recordRptMonthYearBenchmarkItem(b *testing.B, validators *ValidatorRegistry, reg *configpkg.Registry) struct {
	cv  *CompiledValidator
	env *ValidationState
} {
	b.Helper()
	schemaKey, cv := findRecordValidatorForBenchmark(b, validators, "rpt_month_year_matches_header_year_quarter")
	env := NewRecordValidationState(
		testutil.NewTestRecord(reg.GetSchema(schemaKey), 4, map[string]any{"RPT_MONTH_YEAR": "202310"}),
		&DataFileContext{FiscalYear: 2024, FiscalQuarter: "Q1"},
	)
	return struct {
		cv  *CompiledValidator
		env *ValidationState
	}{cv: cv, env: env}
}

func findRecordValidatorForBenchmark(b *testing.B, validators *ValidatorRegistry, id string) (string, *CompiledValidator) {
	b.Helper()
	for schemaKey, recordValidators := range validators.record {
		if cv := validatorByID(recordValidators, id); cv != nil {
			return schemaKey, cv
		}
	}
	b.Fatalf("missing record validator %s", id)
	return "", nil
}

func groupMaxRecordsBenchmarkItem(b *testing.B, validators *ValidatorRegistry, reg *configpkg.Registry) struct {
	cv  *CompiledValidator
	env *ValidationState
} {
	b.Helper()
	_, cv := findGroupValidatorForBenchmark(b, validators, "max_records_per_case")
	group := testutil.NewTestGroup(testutil.NewTestRecord(schemaForRecordTypeBenchmark(b, reg, "T1"), 10, nil))
	return struct {
		cv  *CompiledValidator
		env *ValidationState
	}{cv: cv, env: NewGroupValidationState(group, nil)}
}

func groupExactDuplicatesBenchmarkItem(b *testing.B, validators *ValidatorRegistry, reg *configpkg.Registry) struct {
	cv  *CompiledValidator
	env *ValidationState
} {
	b.Helper()
	_, cv := findGroupValidatorForBenchmark(b, validators, "exact_duplicates")
	recordType := mustStringParamBenchmark(b, cv.Params, "record_type")
	cs := schemaForRecordTypeBenchmark(b, reg, recordType)
	group := testutil.NewTestGroup(
		testutil.NewTestRecord(cs, 11, map[string]any{"CASE_NUMBER": "1"}),
		testutil.NewTestRecord(cs, 12, map[string]any{"CASE_NUMBER": "1"}),
	)
	return struct {
		cv  *CompiledValidator
		env *ValidationState
	}{cv: cv, env: NewGroupValidationState(group, nil)}
}

func groupRequiresRelatedBenchmarkItem(b *testing.B, validators *ValidatorRegistry, reg *configpkg.Registry) struct {
	cv  *CompiledValidator
	env *ValidationState
} {
	b.Helper()
	_, cv := findGroupValidatorForBenchmark(b, validators, "requires_related_record")
	recordType := mustStringParamBenchmark(b, cv.Params, "record_type")
	group := testutil.NewTestGroup(testutil.NewTestRecord(schemaForRecordTypeBenchmark(b, reg, recordType), 13, nil))
	return struct {
		cv  *CompiledValidator
		env *ValidationState
	}{cv: cv, env: NewGroupValidationState(group, nil)}
}

func findGroupValidatorForBenchmark(b *testing.B, validators *ValidatorRegistry, id string) (string, *CompiledValidator) {
	b.Helper()
	for filespecKey, groupValidators := range validators.group {
		if cv := validatorByID(groupValidators, id); cv != nil {
			return filespecKey, cv
		}
	}
	b.Fatalf("missing group validator %s", id)
	return "", nil
}

func productionLikeTANFSection1Group(b *testing.B, reg *configpkg.Registry) *parser.ParsedGroup {
	b.Helper()
	t1 := testutil.NewTestRecord(reg.GetSchema("tanf/t1"), 100, map[string]any{
		"RPT_MONTH_YEAR": "202310",
		"CASE_NUMBER":    "12345",
		"FUNDING_STREAM": 1,
	})
	t2 := testutil.NewTestRecord(reg.GetSchema("tanf/t2"), 101, map[string]any{
		"RPT_MONTH_YEAR":     "202310",
		"CASE_NUMBER":        "12345",
		"FAMILY_AFFILIATION": 1,
		"SSN":                "123456789",
	})
	return testutil.NewTestGroup(t1, t2)
}

func schemaForRecordTypeBenchmark(b *testing.B, reg *configpkg.Registry, recordType string) *schema.CompiledSchema {
	b.Helper()
	for _, cs := range reg.Schemas() {
		if cs.RecordType == recordType {
			return cs
		}
	}
	b.Fatalf("missing schema for record type %s", recordType)
	return nil
}

func mustStringParamBenchmark(b *testing.B, params map[string]any, key string) string {
	b.Helper()
	value, err := requiredStringParam(params, key)
	if err != nil {
		b.Fatal(err)
	}
	return value
}

func mustIntParamBenchmark(b *testing.B, params map[string]any, key string) int {
	b.Helper()
	value, err := requiredIntParam(params, key)
	if err != nil {
		b.Fatal(err)
	}
	return value
}

func mustAnySliceParamBenchmark(b *testing.B, params map[string]any, key string) []any {
	b.Helper()
	value, err := requiredAnySliceParam(params, key)
	if err != nil {
		b.Fatal(err)
	}
	return value
}
