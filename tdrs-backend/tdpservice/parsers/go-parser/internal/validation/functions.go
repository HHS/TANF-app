package validation

import (
	"fmt"
	"regexp"
	"strconv"
	"strings"
	"time"

	"github.com/expr-lang/expr"
)

// RegisterFunctions returns expr options for all custom validation functions.
func RegisterFunctions() []expr.Option {
	return []expr.Option{
		// Value checking
		expr.Function("isEmpty", wrapFunc1(isEmpty), new(func(any) bool)),
		expr.Function("isNotEmpty", wrapFunc1(isNotEmpty), new(func(any) bool)),
		expr.Function("isBlank", wrapFunc1(isBlank), new(func(any) bool)),
		expr.Function("isNotBlank", wrapFunc1(isNotBlank), new(func(any) bool)),

		// Date functions
		expr.Function("year", wrapFunc1Int(extractYear), new(func(any) int)),
		expr.Function("month", wrapFunc1Int(extractMonth), new(func(any) int)),
		expr.Function("day", wrapFunc1Int(extractDay), new(func(any) int)),
		expr.Function("quarter", wrapFunc1Int(extractQuarter), new(func(any) int)),
		expr.Function("isValidDate", wrapFunc1(isValidDate), new(func(any) bool)),

		// String functions
		expr.Function("matches", wrapFunc2Bool(regexMatch), new(func(string, string) bool)),
		expr.Function("isNumeric", wrapFunc1StrBool(isNumeric), new(func(string) bool)),
		expr.Function("isAlphaNumeric", wrapFunc1StrBool(isAlphaNumeric), new(func(string) bool)),
		expr.Function("trim", wrapFunc1StrStr(strings.TrimSpace), new(func(string) string)),
		expr.Function("len", wrapFunc1Int(strLen), new(func(any) int)),

		// Type conversion
		expr.Function("str", wrapFunc1Str(toString), new(func(any) string)),
		expr.Function("toInt", wrapFunc1Int(toInt), new(func(any) int)),

		// Cat4 complex validators (take group explicitly)
		expr.Function("validateT1HasChildren", wrapGroupFunc(validateT1HasChildren),
			new(func(WrappedGroup) bool)),
		expr.Function("hasDuplicateField", wrapGroupFunc3(hasDuplicateField),
			new(func(WrappedGroup, string, string) bool)),
		expr.Function("getRecordsOfType", wrapGroupFunc2(getRecordsOfType),
			new(func(WrappedGroup, string) []Record)),
	}
}

// Wrapper functions to convert typed functions to variadic expr functions

func wrapFunc1(fn func(any) bool) func(...any) (any, error) {
	return func(params ...any) (any, error) {
		if len(params) != 1 {
			return nil, fmt.Errorf("expected 1 argument, got %d", len(params))
		}
		return fn(params[0]), nil
	}
}

func wrapFunc1Int(fn func(any) int) func(...any) (any, error) {
	return func(params ...any) (any, error) {
		if len(params) != 1 {
			return nil, fmt.Errorf("expected 1 argument, got %d", len(params))
		}
		return fn(params[0]), nil
	}
}

func wrapFunc1Str(fn func(any) string) func(...any) (any, error) {
	return func(params ...any) (any, error) {
		if len(params) != 1 {
			return nil, fmt.Errorf("expected 1 argument, got %d", len(params))
		}
		return fn(params[0]), nil
	}
}

func wrapFunc1StrBool(fn func(string) bool) func(...any) (any, error) {
	return func(params ...any) (any, error) {
		if len(params) != 1 {
			return nil, fmt.Errorf("expected 1 argument, got %d", len(params))
		}
		s, ok := params[0].(string)
		if !ok {
			return nil, fmt.Errorf("expected string argument")
		}
		return fn(s), nil
	}
}

func wrapFunc1StrStr(fn func(string) string) func(...any) (any, error) {
	return func(params ...any) (any, error) {
		if len(params) != 1 {
			return nil, fmt.Errorf("expected 1 argument, got %d", len(params))
		}
		s, ok := params[0].(string)
		if !ok {
			return nil, fmt.Errorf("expected string argument")
		}
		return fn(s), nil
	}
}

func wrapFunc2Bool(fn func(string, string) bool) func(...any) (any, error) {
	return func(params ...any) (any, error) {
		if len(params) != 2 {
			return nil, fmt.Errorf("expected 2 arguments, got %d", len(params))
		}
		s1, ok1 := params[0].(string)
		s2, ok2 := params[1].(string)
		if !ok1 || !ok2 {
			return nil, fmt.Errorf("expected string arguments")
		}
		return fn(s1, s2), nil
	}
}

func wrapGroupFunc(fn func(WrappedGroup) bool) func(...any) (any, error) {
	return func(params ...any) (any, error) {
		if len(params) != 1 {
			return nil, fmt.Errorf("expected 1 argument, got %d", len(params))
		}
		g, ok := params[0].(WrappedGroup)
		if !ok {
			return nil, fmt.Errorf("expected WrappedGroup argument")
		}
		return fn(g), nil
	}
}

func wrapGroupFunc2(fn func(WrappedGroup, string) []Record) func(...any) (any, error) {
	return func(params ...any) (any, error) {
		if len(params) != 2 {
			return nil, fmt.Errorf("expected 2 arguments, got %d", len(params))
		}
		g, ok1 := params[0].(WrappedGroup)
		s, ok2 := params[1].(string)
		if !ok1 || !ok2 {
			return nil, fmt.Errorf("expected WrappedGroup and string arguments")
		}
		return fn(g, s), nil
	}
}

func wrapGroupFunc3(fn func(WrappedGroup, string, string) bool) func(...any) (any, error) {
	return func(params ...any) (any, error) {
		if len(params) != 3 {
			return nil, fmt.Errorf("expected 3 arguments, got %d", len(params))
		}
		g, ok1 := params[0].(WrappedGroup)
		s1, ok2 := params[1].(string)
		s2, ok3 := params[2].(string)
		if !ok1 || !ok2 || !ok3 {
			return nil, fmt.Errorf("expected WrappedGroup and two string arguments")
		}
		return fn(g, s1, s2), nil
	}
}

// isEmpty returns true if the value is nil, empty string, or zero.
func isEmpty(v any) bool {
	if v == nil {
		return true
	}
	switch val := v.(type) {
	case string:
		return val == ""
	case int:
		return val == 0
	case int64:
		return val == 0
	case float64:
		return val == 0
	default:
		return false
	}
}

// isNotEmpty returns true if the value is not empty.
func isNotEmpty(v any) bool {
	return !isEmpty(v)
}

// isBlank returns true if the value is nil or a blank string (whitespace only).
func isBlank(v any) bool {
	if v == nil {
		return true
	}
	if s, ok := v.(string); ok {
		return strings.TrimSpace(s) == ""
	}
	return isEmpty(v)
}

// isNotBlank returns true if the value is not blank.
func isNotBlank(v any) bool {
	return !isBlank(v)
}

// extractYear extracts the year from a date string (YYYYMMDD or YYYYMM format).
func extractYear(v any) int {
	s := toString(v)
	if len(s) < 4 {
		return 0
	}
	year, _ := strconv.Atoi(s[:4])
	return year
}

// extractMonth extracts the month from a date string (YYYYMMDD or YYYYMM format).
func extractMonth(v any) int {
	s := toString(v)
	if len(s) < 6 {
		return 0
	}
	month, _ := strconv.Atoi(s[4:6])
	return month
}

// extractDay extracts the day from a date string (YYYYMMDD format).
func extractDay(v any) int {
	s := toString(v)
	if len(s) < 8 {
		return 0
	}
	day, _ := strconv.Atoi(s[6:8])
	return day
}

// extractQuarter returns the quarter (1-4) from a date string.
func extractQuarter(v any) int {
	month := extractMonth(v)
	if month == 0 {
		return 0
	}
	return (month-1)/3 + 1
}

// isValidDate checks if a value represents a valid date.
// Supports YYYYMMDD and YYYYMM formats.
func isValidDate(v any) bool {
	s := toString(v)
	if len(s) == 8 {
		// YYYYMMDD format
		_, err := time.Parse("20060102", s)
		return err == nil
	}
	if len(s) == 6 {
		// YYYYMM format - check year and month are valid
		year := extractYear(v)
		month := extractMonth(v)
		return year >= 1900 && year <= 2100 && month >= 1 && month <= 12
	}
	return false
}

// regexMatch checks if a string matches a regular expression pattern.
func regexMatch(s, pattern string) bool {
	matched, err := regexp.MatchString(pattern, s)
	if err != nil {
		return false
	}
	return matched
}

// isNumeric checks if a string contains only numeric characters.
func isNumeric(s string) bool {
	if s == "" {
		return false
	}
	for _, c := range s {
		if c < '0' || c > '9' {
			return false
		}
	}
	return true
}

// isAlphaNumeric checks if a string contains only alphanumeric characters.
func isAlphaNumeric(s string) bool {
	if s == "" {
		return false
	}
	for _, c := range s {
		if !((c >= 'a' && c <= 'z') || (c >= 'A' && c <= 'Z') || (c >= '0' && c <= '9')) {
			return false
		}
	}
	return true
}

// strLen returns the length of any value converted to string.
func strLen(v any) int {
	return len(toString(v))
}

// toString converts any value to a string.
func toString(v any) string {
	if v == nil {
		return ""
	}
	switch val := v.(type) {
	case string:
		return val
	case int:
		return strconv.Itoa(val)
	case int64:
		return strconv.FormatInt(val, 10)
	case float64:
		return strconv.FormatFloat(val, 'f', -1, 64)
	default:
		return ""
	}
}

// toInt converts any value to an integer.
func toInt(v any) int {
	if v == nil {
		return 0
	}
	switch val := v.(type) {
	case int:
		return val
	case int64:
		return int(val)
	case float64:
		return int(val)
	case string:
		i, _ := strconv.Atoi(strings.TrimSpace(val))
		return i
	default:
		return 0
	}
}

// validateT1HasChildren validates that if T1 exists, it has at least one T2 or T3 child.
// Returns true if validation passes (either no T1, or T1 with children).
func validateT1HasChildren(group WrappedGroup) bool {
	t1Count := 0
	t2Count := 0
	t3Count := 0
	for _, rec := range group.GetRecords() {
		switch rec.GetRecordType() {
		case "T1":
			t1Count++
		case "T2":
			t2Count++
		case "T3":
			t3Count++
		}
	}
	// If no T1 records, validation passes (nothing to validate)
	// If T1 exists, must have at least one T2 or T3
	return t1Count == 0 || (t2Count+t3Count) > 0
}

// hasDuplicateField checks if any records of the given type have duplicate values
// for the specified field.
func hasDuplicateField(group WrappedGroup, recordType, fieldName string) bool {
	seen := make(map[any]bool)
	for _, rec := range group.GetRecords() {
		if rec.GetRecordType() != recordType {
			continue
		}
		value := rec.Get(fieldName)
		if value == nil {
			continue
		}
		if seen[value] {
			return true
		}
		seen[value] = true
	}
	return false
}

// getRecordsOfType returns all records of the given type from a group.
func getRecordsOfType(group WrappedGroup, recordType string) []Record {
	var result []Record
	for _, rec := range group.GetRecords() {
		if rec.GetRecordType() == recordType {
			result = append(result, rec)
		}
	}
	return result
}
