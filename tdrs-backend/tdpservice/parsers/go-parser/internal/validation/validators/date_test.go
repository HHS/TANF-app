package validators

import (
	"testing"
)

func TestDateYearIsLargerThanFactory(t *testing.T) {
	tests := []struct {
		name      string
		params    map[string]any
		value     any
		wantValid bool
	}{
		{
			name:      "YYYYMM format - year larger",
			params:    map[string]any{"year": 1998},
			value:     202301, // Jan 2023
			wantValid: true,
		},
		{
			name:      "YYYYMM format - year equal",
			params:    map[string]any{"year": 1998},
			value:     199801, // Jan 1998
			wantValid: false,
		},
		{
			name:      "YYYYMM format - year smaller",
			params:    map[string]any{"year": 1998},
			value:     199701, // Jan 1997
			wantValid: false,
		},
		{
			name:      "YYYYMMDD format - year larger",
			params:    map[string]any{"year": 1998},
			value:     20230115, // Jan 15, 2023
			wantValid: true,
		},
		{
			name:      "string YYYYMM format",
			params:    map[string]any{"year": 1998},
			value:     "202301",
			wantValid: true,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			validator, err := DateYearIsLargerThanFactory(tt.params)
			if err != nil {
				t.Fatalf("DateYearIsLargerThanFactory() error = %v", err)
			}

			ctx := createTestContext(tt.value)
			result := validator(ctx)
			if result.Valid != tt.wantValid {
				t.Errorf("validator() valid = %v, want %v", result.Valid, tt.wantValid)
			}
		})
	}
}

func TestDateMonthIsValidFactory(t *testing.T) {
	tests := []struct {
		name      string
		value     any
		wantValid bool
	}{
		{
			name:      "valid month 01",
			value:     202301,
			wantValid: true,
		},
		{
			name:      "valid month 12",
			value:     202312,
			wantValid: true,
		},
		{
			name:      "invalid month 00",
			value:     202300,
			wantValid: false,
		},
		{
			name:      "invalid month 13",
			value:     202313,
			wantValid: false,
		},
	}

	validator, err := DateMonthIsValidFactory(nil)
	if err != nil {
		t.Fatalf("DateMonthIsValidFactory() error = %v", err)
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

func TestDateIsValidFactory(t *testing.T) {
	tests := []struct {
		name      string
		value     any
		wantValid bool
	}{
		{
			name:      "valid date YYYYMMDD",
			value:     20230115,
			wantValid: true,
		},
		{
			name:      "valid date YYYYMM",
			value:     202301,
			wantValid: true,
		},
		{
			name:      "invalid day 32",
			value:     20230132,
			wantValid: false,
		},
		{
			name:      "invalid feb 30",
			value:     20230230,
			wantValid: false,
		},
		{
			name:      "valid leap year feb 29",
			value:     20240229,
			wantValid: true,
		},
		{
			name:      "invalid non-leap year feb 29",
			value:     20230229,
			wantValid: false,
		},
	}

	validator, err := DateIsValidFactory(nil)
	if err != nil {
		t.Fatalf("DateIsValidFactory() error = %v", err)
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

func TestQuarterIsValidFactory(t *testing.T) {
	tests := []struct {
		name      string
		value     any
		wantValid bool
	}{
		{
			name:      "valid quarter 1",
			value:     1,
			wantValid: true,
		},
		{
			name:      "valid quarter 4",
			value:     4,
			wantValid: true,
		},
		{
			name:      "invalid quarter 0",
			value:     0,
			wantValid: false,
		},
		{
			name:      "invalid quarter 5",
			value:     5,
			wantValid: false,
		},
		{
			name:      "YYYYQ format",
			value:     20231, // Q1 2023
			wantValid: true,
		},
	}

	validator, err := QuarterIsValidFactory(nil)
	if err != nil {
		t.Fatalf("QuarterIsValidFactory() error = %v", err)
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

func TestExtractYear(t *testing.T) {
	tests := []struct {
		name     string
		value    any
		expected int
	}{
		{"YYYYMM int", 202301, 2023},
		{"YYYYMMDD int", 20230115, 2023},
		{"YYYYMM string", "202301", 2023},
		{"YYYYMMDD string", "20230115", 2023},
		{"just year int", 2023, 2023},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			result := extractYear(tt.value)
			if result != tt.expected {
				t.Errorf("extractYear() = %v, want %v", result, tt.expected)
			}
		})
	}
}

func TestExtractMonth(t *testing.T) {
	tests := []struct {
		name     string
		value    any
		expected int
	}{
		{"YYYYMM int - Jan", 202301, 1},
		{"YYYYMM int - Dec", 202312, 12},
		{"YYYYMMDD int", 20230115, 1},
		{"YYYYMM string", "202306", 6},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			result := extractMonth(tt.value)
			if result != tt.expected {
				t.Errorf("extractMonth() = %v, want %v", result, tt.expected)
			}
		})
	}
}

func TestExtractDay(t *testing.T) {
	tests := []struct {
		name     string
		value    any
		expected int
	}{
		{"YYYYMMDD int", 20230115, 15},
		{"YYYYMM int - no day", 202301, 0},
		{"YYYYMMDD string", "20230115", 15},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			result := extractDay(tt.value)
			if result != tt.expected {
				t.Errorf("extractDay() = %v, want %v", result, tt.expected)
			}
		})
	}
}

func TestIsLeapYear(t *testing.T) {
	tests := []struct {
		year     int
		expected bool
	}{
		{2000, true},  // Divisible by 400
		{1900, false}, // Divisible by 100 but not 400
		{2024, true},  // Divisible by 4 but not 100
		{2023, false}, // Not divisible by 4
	}

	for _, tt := range tests {
		t.Run(string(rune(tt.year)), func(t *testing.T) {
			result := isLeapYear(tt.year)
			if result != tt.expected {
				t.Errorf("isLeapYear(%d) = %v, want %v", tt.year, result, tt.expected)
			}
		})
	}
}
