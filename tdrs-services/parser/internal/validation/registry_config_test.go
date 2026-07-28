package validation

import (
	"os"
	"path/filepath"
	"testing"

	"go-parser/internal/config"
	"go-parser/internal/testutil"
)

func productionConfigDir(t *testing.T) string {
	t.Helper()

	dir := filepath.Join("..", "..", "config")
	if _, err := os.Stat(dir); os.IsNotExist(err) {
		t.Fatal("real config directory not found -- tests must run from go-parser root")
	}

	return dir
}

func TestProductionValidators_LoadAndCompile(t *testing.T) {
	cfg := config.DefaultConfig()
	cfg.Global.ConfigDir = productionConfigDir(t)

	reg, err := config.NewRegistry(cfg)
	if err != nil {
		t.Fatalf("config.NewRegistry failed: %v", err)
	}

	validators, err := NewRegistry(cfg, reg)
	if err != nil {
		t.Fatalf("validation.NewRegistry failed: %v", err)
	}

	if validators == nil {
		t.Fatal("expected validator registry to be initialized")
	}
}

func TestProductionValidators_T5M5OASDIAgeValidatorsBySchema(t *testing.T) {
	cfg := config.DefaultConfig()
	cfg.Global.ConfigDir = productionConfigDir(t)

	reg, err := config.NewRegistry(cfg)
	if err != nil {
		t.Fatalf("config.NewRegistry failed: %v", err)
	}

	validators, err := NewRegistry(cfg, reg)
	if err != nil {
		t.Fatalf("validation.NewRegistry failed: %v", err)
	}

	tests := []struct {
		schemaKey string
		item      string
	}{
		{schemaKey: "tanf/t5", item: "19A"},
		{schemaKey: "ssp/m5", item: "18A"},
		{schemaKey: "tribal_tanf/t5", item: "19A"},
	}

	for _, tt := range tests {
		t.Run(tt.schemaKey, func(t *testing.T) {
			schema := reg.GetSchema(tt.schemaKey)
			if schema == nil {
				t.Fatalf("expected schema %s to be loaded", tt.schemaKey)
			}

			oasdiField := schema.GetSegmentField(0, "REC_OASDI_INSURANCE")
			if oasdiField == nil {
				t.Fatal("expected REC_OASDI_INSURANCE field")
			}
			if oasdiField.Item != tt.item {
				t.Fatalf("expected REC_OASDI_INSURANCE item %s, got %s", tt.item, oasdiField.Item)
			}

			recordValidators := validators.GetRecordValidators(tt.schemaKey)
			count := 0
			for _, validator := range recordValidators {
				if validator.ID == "t5_age_oasdi" {
					count++
				}
			}
			if count != 1 {
				t.Fatalf("expected one t5_age_oasdi validator for %s, got %d", tt.schemaKey, count)
			}
		})
	}

	if validators.GetRecordValidators("T5") != nil {
		t.Fatal("expected no production validators keyed only by record type T5")
	}
}

func TestProductionValidators_T5M5OASDIAgeValidatorBehavior(t *testing.T) {
	cfg := config.DefaultConfig()
	cfg.Global.ConfigDir = productionConfigDir(t)

	reg, err := config.NewRegistry(cfg)
	if err != nil {
		t.Fatalf("config.NewRegistry failed: %v", err)
	}

	validators, err := NewRegistry(cfg, reg)
	if err != nil {
		t.Fatalf("validation.NewRegistry failed: %v", err)
	}

	tests := []struct {
		schemaKey string
		values    map[string]any
		valid     bool
	}{
		{
			schemaKey: "tanf/t5",
			values: map[string]any{
				"DATE_OF_BIRTH":       "20060901",
				"RPT_MONTH_YEAR":      "202410",
				"REC_OASDI_INSURANCE": 0,
			},
			valid: false,
		},
		{
			schemaKey: "tanf/t5",
			values: map[string]any{
				"DATE_OF_BIRTH":       "20061002",
				"RPT_MONTH_YEAR":      "202410",
				"REC_OASDI_INSURANCE": 0,
			},
			valid: true,
		},
		{
			schemaKey: "ssp/m5",
			values: map[string]any{
				"DATE_OF_BIRTH":       "20060901",
				"RPT_MONTH_YEAR":      "202410",
				"REC_OASDI_INSURANCE": 0,
			},
			valid: false,
		},
		{
			schemaKey: "ssp/m5",
			values: map[string]any{
				"DATE_OF_BIRTH":       "20061002",
				"RPT_MONTH_YEAR":      "202410",
				"REC_OASDI_INSURANCE": 0,
			},
			valid: true,
		},
		{
			schemaKey: "tribal_tanf/t5",
			values: map[string]any{
				"DATE_OF_BIRTH":       "20060901",
				"RPT_MONTH_YEAR":      "202410",
				"REC_OASDI_INSURANCE": 0,
			},
			valid: false,
		},
		{
			schemaKey: "tribal_tanf/t5",
			values: map[string]any{
				"DATE_OF_BIRTH":       "20061002",
				"RPT_MONTH_YEAR":      "202410",
				"REC_OASDI_INSURANCE": 0,
			},
			valid: true,
		},
		{
			schemaKey: "tanf/t5",
			values: map[string]any{
				"DATE_OF_BIRTH":       "20060901",
				"RPT_MONTH_YEAR":      "202410",
				"REC_OASDI_INSURANCE": 1,
			},
			valid: true,
		},
	}

	for _, tt := range tests {
		t.Run(tt.schemaKey, func(t *testing.T) {
			cs := reg.GetSchema(tt.schemaKey)
			if cs == nil {
				t.Fatalf("expected schema %s to be loaded", tt.schemaKey)
			}

			var oasdiValidator *CompiledValidator
			for _, validator := range validators.GetRecordValidators(tt.schemaKey) {
				if validator.ID == "t5_age_oasdi" {
					oasdiValidator = validator
					break
				}
			}
			if oasdiValidator == nil {
				t.Fatalf("expected t5_age_oasdi validator for %s", tt.schemaKey)
			}

			rec := testutil.NewTestRecord(cs, 1, tt.values)
			result := Execute(oasdiValidator, NewRecordValidationState(rec, nil))
			if result.Valid != tt.valid {
				t.Fatalf("expected valid=%v, got %v", tt.valid, result.Valid)
			}
		})
	}
}
