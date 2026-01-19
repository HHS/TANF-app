package validators

import (
	"testing"

	"go-parser/internal/parser"
	"go-parser/internal/schema"
	"go-parser/internal/validation"
	"go-parser/internal/validation/registry"
)

func TestIsEqualFactory(t *testing.T) {
	tests := []struct {
		name      string
		params    map[string]any
		value     any
		wantValid bool
		wantErr   bool
	}{
		{
			name:      "int equals int",
			params:    map[string]any{"value": 5},
			value:     5,
			wantValid: true,
		},
		{
			name:      "int not equals int",
			params:    map[string]any{"value": 5},
			value:     10,
			wantValid: false,
		},
		{
			name:      "string equals string",
			params:    map[string]any{"value": "hello"},
			value:     "hello",
			wantValid: true,
		},
		{
			name:      "string not equals string",
			params:    map[string]any{"value": "hello"},
			value:     "world",
			wantValid: false,
		},
		{
			name:    "missing value param",
			params:  map[string]any{},
			value:   5,
			wantErr: true,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			validator, err := IsEqualFactory(tt.params)
			if (err != nil) != tt.wantErr {
				t.Errorf("IsEqualFactory() error = %v, wantErr %v", err, tt.wantErr)
				return
			}
			if tt.wantErr {
				return
			}

			ctx := createTestContext(tt.value)
			result := validator(ctx)
			if result.Valid != tt.wantValid {
				t.Errorf("validator() valid = %v, want %v", result.Valid, tt.wantValid)
			}
		})
	}
}

func TestIsGreaterThanFactory(t *testing.T) {
	tests := []struct {
		name      string
		params    map[string]any
		value     any
		wantValid bool
	}{
		{
			name:      "10 > 5",
			params:    map[string]any{"value": 5},
			value:     10,
			wantValid: true,
		},
		{
			name:      "5 > 5",
			params:    map[string]any{"value": 5},
			value:     5,
			wantValid: false,
		},
		{
			name:      "3 > 5",
			params:    map[string]any{"value": 5},
			value:     3,
			wantValid: false,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			validator, err := IsGreaterThanFactory(tt.params)
			if err != nil {
				t.Fatalf("IsGreaterThanFactory() error = %v", err)
			}

			ctx := createTestContext(tt.value)
			result := validator(ctx)
			if result.Valid != tt.wantValid {
				t.Errorf("validator() valid = %v, want %v", result.Valid, tt.wantValid)
			}
		})
	}
}

func TestIsBetweenFactory(t *testing.T) {
	tests := []struct {
		name      string
		params    map[string]any
		value     any
		wantValid bool
	}{
		{
			name:      "5 between 1 and 10 (inclusive)",
			params:    map[string]any{"min": 1, "max": 10, "inclusive": true},
			value:     5,
			wantValid: true,
		},
		{
			name:      "1 between 1 and 10 (inclusive)",
			params:    map[string]any{"min": 1, "max": 10, "inclusive": true},
			value:     1,
			wantValid: true,
		},
		{
			name:      "10 between 1 and 10 (inclusive)",
			params:    map[string]any{"min": 1, "max": 10, "inclusive": true},
			value:     10,
			wantValid: true,
		},
		{
			name:      "0 between 1 and 10 (inclusive)",
			params:    map[string]any{"min": 1, "max": 10, "inclusive": true},
			value:     0,
			wantValid: false,
		},
		{
			name:      "5 between 1 and 10 (exclusive)",
			params:    map[string]any{"min": 1, "max": 10, "inclusive": false},
			value:     5,
			wantValid: true,
		},
		{
			name:      "1 between 1 and 10 (exclusive)",
			params:    map[string]any{"min": 1, "max": 10, "inclusive": false},
			value:     1,
			wantValid: false,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			validator, err := IsBetweenFactory(tt.params)
			if err != nil {
				t.Fatalf("IsBetweenFactory() error = %v", err)
			}

			ctx := createTestContext(tt.value)
			result := validator(ctx)
			if result.Valid != tt.wantValid {
				t.Errorf("validator() valid = %v, want %v", result.Valid, tt.wantValid)
			}
		})
	}
}

func TestIsOneOfFactory(t *testing.T) {
	tests := []struct {
		name      string
		params    map[string]any
		value     any
		wantValid bool
	}{
		{
			name:      "value in list",
			params:    map[string]any{"values": []any{1, 2, 3}},
			value:     2,
			wantValid: true,
		},
		{
			name:      "value not in list",
			params:    map[string]any{"values": []any{1, 2, 3}},
			value:     5,
			wantValid: false,
		},
		{
			name:      "string in list",
			params:    map[string]any{"values": []any{"a", "b", "c"}},
			value:     "b",
			wantValid: true,
		},
		{
			name:      "string not in list",
			params:    map[string]any{"values": []any{"a", "b", "c"}},
			value:     "d",
			wantValid: false,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			validator, err := IsOneOfFactory(tt.params)
			if err != nil {
				t.Fatalf("IsOneOfFactory() error = %v", err)
			}

			ctx := createTestContext(tt.value)
			result := validator(ctx)
			if result.Valid != tt.wantValid {
				t.Errorf("validator() valid = %v, want %v", result.Valid, tt.wantValid)
			}
		})
	}
}

func TestRegistryComposition(t *testing.T) {
	reg := registry.NewValidatorRegistry()
	RegisterComparison(reg)

	tests := []struct {
		name      string
		config    validation.ValidatorConfig
		value     any
		wantValid bool
	}{
		{
			name: "and composition - both pass",
			config: validation.ValidatorConfig{
				ID:      "positive_under_100",
				Compose: "and",
				Validators: []validation.ValidatorConfig{
					{ID: "isGreaterThan", Params: map[string]any{"value": 0}},
					{ID: "isLessThan", Params: map[string]any{"value": 100}},
				},
			},
			value:     50,
			wantValid: true,
		},
		{
			name: "and composition - first fails",
			config: validation.ValidatorConfig{
				ID:      "positive_under_100",
				Compose: "and",
				Validators: []validation.ValidatorConfig{
					{ID: "isGreaterThan", Params: map[string]any{"value": 0}},
					{ID: "isLessThan", Params: map[string]any{"value": 100}},
				},
			},
			value:     -5,
			wantValid: false,
		},
		{
			name: "or composition - one passes",
			config: validation.ValidatorConfig{
				ID:      "one_or_two",
				Compose: "or",
				Validators: []validation.ValidatorConfig{
					{ID: "isEqual", Params: map[string]any{"value": 1}},
					{ID: "isEqual", Params: map[string]any{"value": 2}},
				},
			},
			value:     2,
			wantValid: true,
		},
		{
			name: "or composition - none pass",
			config: validation.ValidatorConfig{
				ID:      "one_or_two",
				Compose: "or",
				Validators: []validation.ValidatorConfig{
					{ID: "isEqual", Params: map[string]any{"value": 1}},
					{ID: "isEqual", Params: map[string]any{"value": 2}},
				},
			},
			value:     5,
			wantValid: false,
		},
		{
			name: "not composition - negates pass",
			config: validation.ValidatorConfig{
				ID:      "not_zero",
				Compose: "not",
				Validators: []validation.ValidatorConfig{
					{ID: "isEqual", Params: map[string]any{"value": 0}},
				},
			},
			value:     5,
			wantValid: true,
		},
		{
			name: "not composition - negates fail",
			config: validation.ValidatorConfig{
				ID:      "not_zero",
				Compose: "not",
				Validators: []validation.ValidatorConfig{
					{ID: "isEqual", Params: map[string]any{"value": 0}},
				},
			},
			value:     0,
			wantValid: false,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			validator, err := reg.Build(tt.config)
			if err != nil {
				t.Fatalf("Build() error = %v", err)
			}

			ctx := createTestContext(tt.value)
			result := validator(ctx)
			if result.Valid != tt.wantValid {
				t.Errorf("validator() valid = %v, want %v", result.Valid, tt.wantValid)
			}
		})
	}
}

// createTestContext creates a simple validation context for testing.
func createTestContext(value any) *validation.ValidationContext {
	// Create a minimal compiled schema
	schemaDef := &schema.SchemaDef{
		RecordType: "TEST",
		Shared: []schema.FieldDef{
			{Name: "TEST_FIELD", Item: "1", FriendlyName: "Test Field", Type: "integer"},
		},
	}
	compiledSchema := schemaDef.Compile()

	// Create a record with the test value
	record := &parser.ParsedRecord{
		Schema:     compiledSchema,
		LineNumber: 1,
		Fields:     make([]any, compiledSchema.FieldCount),
	}
	record.Fields[0] = value

	return &validation.ValidationContext{
		Record:     record,
		Schema:     compiledSchema,
		FieldIndex: 0,
		Category:   validation.CategoryFieldValue,
	}
}
