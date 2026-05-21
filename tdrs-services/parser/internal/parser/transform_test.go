package parser

import (
	"strings"
	"testing"
)

func TestApplyTransform_KnownTransforms(t *testing.T) {
	for name := range Registry {
		if _, ok := Registry[name]; !ok {
			t.Errorf("Registry missing expected transform: %s", name)
		}
	}
}

func TestApplyTransform_UnknownTransform(t *testing.T) {
	_, err := ApplyTransform("nonexistent", "value", nil, nil)
	if err == nil {
		t.Fatal("expected error for unknown transform")
	}
	if !strings.Contains(err.Error(), "unknown transform") {
		t.Errorf("unexpected error message: %s", err)
	}
}

func TestApplyTransform_DispatchesToCorrectFunction(t *testing.T) {
	got, err := ApplyTransform("trim", "  hello  ", nil, nil)
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	if got != "hello" {
		t.Errorf("expected %q, got %q", "hello", got)
	}
}

func TestTrim(t *testing.T) {
	tests := []struct {
		name  string
		input string
		want  string
	}{
		{"leading and trailing spaces", "  hello  ", "hello"},
		{"leading spaces only", "   world", "world"},
		{"trailing spaces only", "world   ", "world"},
		{"tabs and spaces", "\t hello \t", "hello"},
		{"newlines", "\nhello\n", "hello"},
		{"empty string", "", ""},
		{"only whitespace", "   \t\n  ", ""},
		{"no whitespace", "hello", "hello"},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			got, err := Trim(tt.input, nil, nil)
			if err != nil {
				t.Fatalf("unexpected error: %v", err)
			}
			if got != tt.want {
				t.Errorf("Trim(%q) = %q, want %q", tt.input, got, tt.want)
			}
		})
	}
}

func TestZeroPad(t *testing.T) {
	tests := []struct {
		name    string
		value   string
		params  map[string]any
		want    string
		wantErr bool
	}{
		{
			name:   "pad shorter value",
			value:  "42",
			params: map[string]any{"digits": 5},
			want:   "00042",
		},
		{
			name:   "value already at target length",
			value:  "12345",
			params: map[string]any{"digits": 5},
			want:   "12345",
		},
		{
			name:   "value longer than target",
			value:  "123456",
			params: map[string]any{"digits": 5},
			want:   "123456",
		},
		{
			name:   "single character",
			value:  "7",
			params: map[string]any{"digits": 3},
			want:   "007",
		},
		{
			name:   "empty string padded",
			value:  "",
			params: map[string]any{"digits": 3},
			want:   "000",
		},
		{
			name:   "leading spaces trimmed before padding",
			value:  "  42",
			params: map[string]any{"digits": 5},
			want:   "00042",
		},
		{
			name:    "missing digits param",
			value:   "42",
			params:  map[string]any{},
			wantErr: true,
		},
		{
			name:    "nil params",
			value:   "42",
			params:  nil,
			wantErr: true,
		},
		{
			name:    "digits param wrong type",
			value:   "42",
			params:  map[string]any{"digits": "5"},
			wantErr: true,
		},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			got, err := ZeroPad(tt.value, tt.params, nil)
			if tt.wantErr {
				if err == nil {
					t.Fatal("expected error, got nil")
				}
				return
			}
			if err != nil {
				t.Fatalf("unexpected error: %v", err)
			}
			if got != tt.want {
				t.Errorf("ZeroPad(%q) = %q, want %q", tt.value, got, tt.want)
			}
		})
	}
}

func TestSSNDecrypt_CharSubstitutions(t *testing.T) {
	// Verify each character in the decryption table individually.
	charTests := []struct {
		encrypted byte
		decrypted byte
	}{
		{'@', '1'},
		{'9', '2'},
		{'Z', '3'},
		{'P', '4'},
		{'0', '5'},
		{'#', '6'},
		{'Y', '7'},
		{'B', '8'},
		{'W', '9'},
		{'T', '0'},
	}
	params := map[string]any{"encrypted": true}
	for _, ct := range charTests {
		t.Run(string(ct.encrypted)+"->"+string(ct.decrypted), func(t *testing.T) {
			got, err := SSNDecrypt(string(ct.encrypted), params, nil)
			if err != nil {
				t.Fatalf("unexpected error: %v", err)
			}
			if got != string(ct.decrypted) {
				t.Errorf("SSNDecrypt(%q) = %q, want %q", string(ct.encrypted), got, string(ct.decrypted))
			}
		})
	}
}

func TestSSNDecrypt_FullValue(t *testing.T) {
	// A complete encrypted SSN using all substitution chars.
	params := map[string]any{"encrypted": true}
	got, err := SSNDecrypt("@9ZP0#YBW", params, nil)
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	if got != "123456789" {
		t.Errorf("got %q, want %q", got, "123456789")
	}
}

func TestSSNDecrypt(t *testing.T) {
	tests := []struct {
		name    string
		value   string
		params  map[string]any
		ctx     *ParseContext
		want    string
		wantErr bool
	}{
		{
			name:   "empty value returns empty",
			value:  "",
			params: nil,
			ctx:    nil,
			want:   "",
		},
		{
			name:   "not encrypted via nil ctx and no param",
			value:  "@9ZP0#YBW",
			params: nil,
			ctx:    nil,
			want:   "@9ZP0#YBW",
		},
		{
			name:   "not encrypted via ctx false",
			value:  "@9ZP0#YBW",
			params: nil,
			ctx:    &ParseContext{IsEncrypted: false},
			want:   "@9ZP0#YBW",
		},
		{
			name:   "encrypted via ctx",
			value:  "@9ZP0#YBW",
			params: nil,
			ctx:    &ParseContext{IsEncrypted: true},
			want:   "123456789",
		},
		{
			name:   "encrypted via param override true",
			value:  "@9ZP0#YBW",
			params: map[string]any{"encrypted": true},
			ctx:    nil,
			want:   "123456789",
		},
		{
			name:   "param override false overrides ctx true",
			value:  "@9ZP0#YBW",
			params: map[string]any{"encrypted": false},
			ctx:    &ParseContext{IsEncrypted: true},
			want:   "@9ZP0#YBW",
		},
		{
			name:   "param override true overrides ctx false",
			value:  "@9ZP0#YBW",
			params: map[string]any{"encrypted": true},
			ctx:    &ParseContext{IsEncrypted: false},
			want:   "123456789",
		},
		{
			name:   "non-mapped characters pass through",
			value:  "ABC",
			params: map[string]any{"encrypted": true},
			ctx:    nil,
			want:   "A8C",
		},
		{
			name:   "all digits pass through when not encrypted",
			value:  "123456789",
			params: nil,
			ctx:    &ParseContext{IsEncrypted: false},
			want:   "123456789",
		},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			got, err := SSNDecrypt(tt.value, tt.params, tt.ctx)
			if tt.wantErr {
				if err == nil {
					t.Fatal("expected error, got nil")
				}
				return
			}
			if err != nil {
				t.Fatalf("unexpected error: %v", err)
			}
			if got != tt.want {
				t.Errorf("SSNDecrypt(%q) = %q, want %q", tt.value, got, tt.want)
			}
		})
	}
}

func TestCalendarQuarterToMonth(t *testing.T) {
	tests := []struct {
		name    string
		value   string
		params  map[string]any
		want    string
		wantErr bool
		errMsg  string
	}{
		// All quarters, month_index=0 (first month)
		{
			name:   "Q1 first month",
			value:  "20241",
			params: map[string]any{"month_index": 0},
			want:   "202401",
		},
		{
			name:   "Q2 first month",
			value:  "20242",
			params: map[string]any{"month_index": 0},
			want:   "202404",
		},
		{
			name:   "Q3 first month",
			value:  "20243",
			params: map[string]any{"month_index": 0},
			want:   "202407",
		},
		{
			name:   "Q4 first month",
			value:  "20244",
			params: map[string]any{"month_index": 0},
			want:   "202410",
		},
		// All month indices for Q1
		{
			name:   "Q1 second month",
			value:  "20241",
			params: map[string]any{"month_index": 1},
			want:   "202402",
		},
		{
			name:   "Q1 third month",
			value:  "20241",
			params: map[string]any{"month_index": 2},
			want:   "202403",
		},
		// All month indices for Q4
		{
			name:   "Q4 second month",
			value:  "20244",
			params: map[string]any{"month_index": 1},
			want:   "202411",
		},
		{
			name:   "Q4 third month",
			value:  "20244",
			params: map[string]any{"month_index": 2},
			want:   "202412",
		},
		// Value with leading spaces in year portion
		{
			name:   "year with leading space",
			value:  " 0241",
			params: map[string]any{"month_index": 0},
			want:   "02401",
		},
		// Error cases
		{
			name:    "missing month_index param",
			value:   "20241",
			params:  map[string]any{},
			wantErr: true,
			errMsg:  "month_index",
		},
		{
			name:    "nil params",
			value:   "20241",
			params:  nil,
			wantErr: true,
			errMsg:  "month_index",
		},
		{
			name:    "month_index wrong type",
			value:   "20241",
			params:  map[string]any{"month_index": "0"},
			wantErr: true,
			errMsg:  "month_index",
		},
		{
			name:    "value too short",
			value:   "2024",
			params:  map[string]any{"month_index": 0},
			wantErr: true,
			errMsg:  "invalid quarter format",
		},
		{
			name:    "empty value",
			value:   "",
			params:  map[string]any{"month_index": 0},
			wantErr: true,
			errMsg:  "invalid quarter format",
		},
		{
			name:    "invalid quarter digit 0",
			value:   "20240",
			params:  map[string]any{"month_index": 0},
			wantErr: true,
			errMsg:  "invalid quarter digit",
		},
		{
			name:    "invalid quarter digit 5",
			value:   "20245",
			params:  map[string]any{"month_index": 0},
			wantErr: true,
			errMsg:  "invalid quarter digit",
		},
		{
			name:    "invalid quarter letter",
			value:   "2024A",
			params:  map[string]any{"month_index": 0},
			wantErr: true,
			errMsg:  "invalid quarter digit",
		},
		{
			name:    "month_index negative",
			value:   "20241",
			params:  map[string]any{"month_index": -1},
			wantErr: true,
			errMsg:  "month_index must be 0, 1, or 2",
		},
		{
			name:    "month_index too large",
			value:   "20241",
			params:  map[string]any{"month_index": 3},
			wantErr: true,
			errMsg:  "month_index must be 0, 1, or 2",
		},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			got, err := CalendarQuarterToMonth(tt.value, tt.params, nil)
			if tt.wantErr {
				if err == nil {
					t.Fatal("expected error, got nil")
				}
				if tt.errMsg != "" && !strings.Contains(err.Error(), tt.errMsg) {
					t.Errorf("error %q should contain %q", err.Error(), tt.errMsg)
				}
				return
			}
			if err != nil {
				t.Fatalf("unexpected error: %v", err)
			}
			if got != tt.want {
				t.Errorf("CalendarQuarterToMonth(%q) = %q, want %q", tt.value, got, tt.want)
			}
		})
	}
}

func TestFRAExitDate(t *testing.T) {
	tests := []struct {
		name    string
		value   string
		want    string
		wantErr bool
	}{
		{
			name:  "already YYYYMM",
			value: "202310",
			want:  "202310",
		},
		{
			name:  "xlsx formatted date with four digit year",
			value: "10/1/2023",
			want:  "202310",
		},
		{
			name:  "xlsx formatted date with two digit year",
			value: "10/1/23",
			want:  "202310",
		},
		{
			name:  "iso date",
			value: "2023-10-01",
			want:  "202310",
		},
		{
			name:  "month year",
			value: "Oct-23",
			want:  "202310",
		},
		{
			name:  "excel serial date",
			value: "45200",
			want:  "202310",
		},
		{
			name:  "empty date",
			value: "",
			want:  "",
		},
		{
			name:  "invalid date",
			value: "not-a-date",
			want:  "not-a-date",
		},
		{
			name:  "invalid YYYYMM month",
			value: "202313",
			want:  "202313",
		},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			got, err := FRAExitDate(tt.value, nil, nil)
			if tt.wantErr {
				if err == nil {
					t.Fatal("expected error, got nil")
				}
				return
			}
			if err != nil {
				t.Fatalf("unexpected error: %v", err)
			}
			if got != tt.want {
				t.Errorf("FRAExitDate(%q) = %q, want %q", tt.value, got, tt.want)
			}
		})
	}
}

func TestRegistryContainsAllTransforms(t *testing.T) {
	expected := []string{"trim", "zero_pad", "ssn_decrypt", "calendar_quarter_to_month", "fra_exit_date"}
	for _, name := range expected {
		if _, ok := Registry[name]; !ok {
			t.Errorf("Registry missing transform: %s", name)
		}
	}
	if len(Registry) != len(expected) {
		t.Errorf("Registry has %d entries, expected %d", len(Registry), len(expected))
	}
}
