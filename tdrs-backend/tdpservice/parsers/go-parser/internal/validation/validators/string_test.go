package validators

import (
	"testing"
)

func TestIsNotEmptyFactory(t *testing.T) {
	tests := []struct {
		name      string
		value     any
		wantValid bool
	}{
		{
			name:      "non-empty string",
			value:     "hello",
			wantValid: true,
		},
		{
			name:      "empty string",
			value:     "",
			wantValid: false,
		},
		{
			name:      "whitespace only",
			value:     "   ",
			wantValid: false,
		},
		{
			name:      "nil value",
			value:     nil,
			wantValid: false,
		},
		{
			name:      "non-zero int",
			value:     42,
			wantValid: true,
		},
		{
			name:      "zero int is not empty",
			value:     0,
			wantValid: true, // 0 is a valid value, not "empty"
		},
	}

	validator, err := IsNotEmptyFactory(nil)
	if err != nil {
		t.Fatalf("IsNotEmptyFactory() error = %v", err)
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			ctx := createTestContext(tt.value)
			result := validator(ctx)
			if result.Valid != tt.wantValid {
				t.Errorf("validator() valid = %v, want %v", result.Valid, tt.wantValid)
			}
		})
	}
}

func TestHasLengthFactory(t *testing.T) {
	tests := []struct {
		name      string
		params    map[string]any
		value     any
		wantValid bool
	}{
		{
			name:      "exact length match",
			params:    map[string]any{"length": 5},
			value:     "hello",
			wantValid: true,
		},
		{
			name:      "too short",
			params:    map[string]any{"length": 5},
			value:     "hi",
			wantValid: false,
		},
		{
			name:      "too long",
			params:    map[string]any{"length": 5},
			value:     "hello world",
			wantValid: false,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			validator, err := HasLengthFactory(tt.params)
			if err != nil {
				t.Fatalf("HasLengthFactory() error = %v", err)
			}

			ctx := createTestContext(tt.value)
			result := validator(ctx)
			if result.Valid != tt.wantValid {
				t.Errorf("validator() valid = %v, want %v", result.Valid, tt.wantValid)
			}
		})
	}
}

func TestMatchesPatternFactory(t *testing.T) {
	tests := []struct {
		name      string
		params    map[string]any
		value     any
		wantValid bool
		wantErr   bool
	}{
		{
			name:      "matches pattern",
			params:    map[string]any{"pattern": "^[A-Z]{2}[0-9]{3}$"},
			value:     "AB123",
			wantValid: true,
		},
		{
			name:      "does not match pattern",
			params:    map[string]any{"pattern": "^[A-Z]{2}[0-9]{3}$"},
			value:     "abc123",
			wantValid: false,
		},
		{
			name:    "invalid pattern",
			params:  map[string]any{"pattern": "[invalid"},
			value:   "test",
			wantErr: true,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			validator, err := MatchesPatternFactory(tt.params)
			if (err != nil) != tt.wantErr {
				t.Errorf("MatchesPatternFactory() error = %v, wantErr %v", err, tt.wantErr)
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

func TestStartsWithFactory(t *testing.T) {
	tests := []struct {
		name      string
		params    map[string]any
		value     any
		wantValid bool
	}{
		{
			name:      "starts with prefix",
			params:    map[string]any{"prefix": "HEADER"},
			value:     "HEADER123",
			wantValid: true,
		},
		{
			name:      "does not start with prefix",
			params:    map[string]any{"prefix": "HEADER"},
			value:     "DATA123",
			wantValid: false,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			validator, err := StartsWithFactory(tt.params)
			if err != nil {
				t.Fatalf("StartsWithFactory() error = %v", err)
			}

			ctx := createTestContext(tt.value)
			result := validator(ctx)
			if result.Valid != tt.wantValid {
				t.Errorf("validator() valid = %v, want %v", result.Valid, tt.wantValid)
			}
		})
	}
}

func TestIsNumericFactory(t *testing.T) {
	tests := []struct {
		name      string
		value     any
		wantValid bool
	}{
		{
			name:      "all digits",
			value:     "12345",
			wantValid: true,
		},
		{
			name:      "contains letters",
			value:     "123abc",
			wantValid: false,
		},
		{
			name:      "empty string",
			value:     "",
			wantValid: true, // Empty string has no non-digits
		},
	}

	validator, err := IsNumericFactory(nil)
	if err != nil {
		t.Fatalf("IsNumericFactory() error = %v", err)
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			ctx := createTestContext(tt.value)
			result := validator(ctx)
			if result.Valid != tt.wantValid {
				t.Errorf("validator() valid = %v, want %v", result.Valid, tt.wantValid)
			}
		})
	}
}
