package parser

import (
	"fmt"
	"math"
	"strconv"
	"strings"
	"time"

	"github.com/xuri/excelize/v2"
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
	"fra_exit_date":             FRAExitDate,
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

// ssnDecryptTable is a pre-computed lookup table for SSN decryption.
// Using a byte array avoids allocating a map on every call and gives O(1) lookup.
var ssnDecryptTable [256]byte

func init() {
	// Identity mapping by default
	for i := range ssnDecryptTable {
		ssnDecryptTable[i] = byte(i)
	}
	// Decryption overrides
	ssnDecryptTable['@'] = '1'
	ssnDecryptTable['9'] = '2'
	ssnDecryptTable['Z'] = '3'
	ssnDecryptTable['P'] = '4'
	ssnDecryptTable['0'] = '5'
	ssnDecryptTable['#'] = '6'
	ssnDecryptTable['Y'] = '7'
	ssnDecryptTable['B'] = '8'
	ssnDecryptTable['W'] = '9'
	ssnDecryptTable['T'] = '0'
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

	buf := make([]byte, len(value))
	for i := 0; i < len(value); i++ {
		buf[i] = ssnDecryptTable[value[i]]
	}
	return string(buf), nil
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

// FRAExitDate normalizes FRA EXIT_DATE values to YYYYMM.
// FRA XLSX files may contain a real Excel date cell, which excelize exposes as
// either a formatted date string or an Excel serial number depending on styling.
func FRAExitDate(value string, _ map[string]any, _ *ParseContext) (string, error) {
	trimmed := strings.TrimSpace(value)
	if trimmed == "" {
		return "", nil
	}

	if isYYYYMM(trimmed) {
		return trimmed, nil
	}

	if len(trimmed) == 6 && isDigits(trimmed) {
		return value, nil
	}

	if f, err := strconv.ParseFloat(trimmed, 64); err == nil {
		if math.Trunc(f) == f {
			if serialDate, err := excelize.ExcelDateToTime(f, false); err == nil {
				return serialDate.Format("200601"), nil
			}
		}
	}

	for _, layout := range fraExitDateLayouts {
		if parsed, err := time.Parse(layout, trimmed); err == nil {
			return parsed.Format("200601"), nil
		}
	}

	return value, nil
}

var fraExitDateLayouts = []string{
	"2006-01-02",
	"2006-1-2",
	"2006/01/02",
	"2006/1/2",
	"1/2/2006",
	"01/02/2006",
	"1/2/06",
	"01/02/06",
	"1-2-2006",
	"01-02-2006",
	"1-2-06",
	"01-02-06",
	"2006-01-02 15:04:05",
	"2006/01/02 15:04:05",
	"1/2/2006 15:04:05",
	"01/02/2006 15:04:05",
	"Jan-06",
	"January-06",
	"Jan 2006",
	"January 2006",
}

func isYYYYMM(value string) bool {
	if len(value) != 6 {
		return false
	}
	if !isDigits(value) {
		return false
	}
	year, err := strconv.Atoi(value[:4])
	if err != nil || year < 1900 {
		return false
	}
	month, err := strconv.Atoi(value[4:])
	if err != nil {
		return false
	}
	return month >= 1 && month <= 12
}

func isDigits(value string) bool {
	for _, r := range value {
		if r < '0' || r > '9' {
			return false
		}
	}
	return value != ""
}
