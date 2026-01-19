package parser

import (
	"fmt"
	"strings"
)

// TransformFunc defines the signature for all transform functions.
// Parameters:
//   - value: raw string extracted from the field position
//   - params: static configuration from schema YAML (e.g., digits for zero_pad)
//   - ctx: runtime context from header parsing (e.g., IsEncrypted)
//
// Returns the transformed string value and any error.
type TransformFunc func(value string, params map[string]any, ctx *ParseContext) (string, error)

// Registry maps transform names to their implementations.
var Registry = map[string]TransformFunc{
	"trim":                      Trim,
	"zero_pad":                  ZeroPad,
	"ssn_decrypt":               SSNDecrypt,
	"calendar_quarter_to_month": CalendarQuarterToMonth,
}

// Apply looks up and executes a transform by name.
func ApplyTransform(name, value string, params map[string]any, ctx *ParseContext) (string, error) {
	fn, ok := Registry[name]
	if !ok {
		return "", fmt.Errorf("unknown transform: %s", name)
	}
	return fn(value, params, ctx)
}

// Trim removes leading and trailing whitespace.
func Trim(value string, _ map[string]any, _ *ParseContext) (string, error) {
	return strings.TrimSpace(value), nil
}

// ZeroPad pads a string with leading zeros to reach the specified length.
// Params:
//   - digits (int): target length after padding
func ZeroPad(value string, params map[string]any, _ *ParseContext) (string, error) {
	digits, ok := params["digits"].(int)
	if !ok {
		return "", fmt.Errorf("zero_pad requires 'digits' param (int)")
	}

	trimmed := strings.TrimLeft(value, " ")
	if len(trimmed) >= digits {
		return trimmed, nil
	}
	return fmt.Sprintf("%0*s", digits, trimmed), nil
}

// SSNDecrypt decrypts TANF/SSP SSN values using character substitution.
// The encryption status is determined by:
//  1. Runtime context (ctx.IsEncrypted) - from header parsing
//  2. Static param override (params["encrypted"]) - for testing
//
// Params (optional):
//   - encrypted (bool): force encryption status, overrides runtime context
func SSNDecrypt(value string, params map[string]any, ctx *ParseContext) (string, error) {
	if value == "" {
		return "", nil
	}

	// Determine encryption status
	// Priority: static param > runtime context > default (false)
	encrypted := false
	if ctx != nil {
		encrypted = ctx.IsEncrypted
	}
	if enc, ok := params["encrypted"].(bool); ok {
		encrypted = enc // Static override
	}

	if !encrypted {
		return value, nil
	}

	// SSN decryption mapping
	decryptMap := map[rune]rune{
		'@': '1', '9': '2', 'Z': '3', 'P': '4', '0': '5',
		'#': '6', 'Y': '7', 'B': '8', 'W': '9', 'T': '0',
	}

	var result strings.Builder
	result.Grow(len(value))
	for _, c := range value {
		if decrypted, ok := decryptMap[c]; ok {
			result.WriteRune(decrypted)
		} else {
			result.WriteRune(c)
		}
	}
	return result.String(), nil
}

// CalendarQuarterToMonth converts a calendar quarter (YYYYQ) to year-month (YYYYMM).
// Params:
//   - month_index (int): which month in the quarter (0=first, 1=second, 2=third)
func CalendarQuarterToMonth(value string, params map[string]any, _ *ParseContext) (string, error) {
	monthIndex, ok := params["month_index"].(int)
	if !ok {
		return "", fmt.Errorf("calendar_quarter_to_month requires 'month_index' param (int)")
	}

	if len(value) < 5 {
		return "", fmt.Errorf("invalid quarter format (expected YYYYQ): %s", value)
	}

	year := strings.TrimSpace(value[:4])
	quarter := value[len(value)-1]

	quarterMonths := map[byte][]string{
		'1': {"01", "02", "03"}, // Q1: Jan, Feb, Mar
		'2': {"04", "05", "06"}, // Q2: Apr, May, Jun
		'3': {"07", "08", "09"}, // Q3: Jul, Aug, Sep
		'4': {"10", "11", "12"}, // Q4: Oct, Nov, Dec
	}

	months, ok := quarterMonths[quarter]
	if !ok {
		return "", fmt.Errorf("invalid quarter digit: %c", quarter)
	}

	if monthIndex < 0 || monthIndex >= 3 {
		return "", fmt.Errorf("month_index must be 0, 1, or 2: got %d", monthIndex)
	}

	return year + months[monthIndex], nil
}
