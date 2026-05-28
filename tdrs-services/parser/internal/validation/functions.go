package validation

import (
	"fmt"
	"strconv"
	"strings"
	"time"

	"github.com/expr-lang/expr"

	"go-parser/internal/parser"
)

// RegisterFunctions returns expr options for all custom validation functions.
func RegisterFunctions() []expr.Option {
	return []expr.Option{
		// Value checking
		expr.Function("isEmpty", wrap1(isEmpty), new(func(any) bool)),
		expr.Function("isNotEmpty", wrap1(isNotEmpty), new(func(any) bool)),
		expr.Function("isBlank", wrap1(isBlank), new(func(any) bool)),
		expr.Function("isNotBlank", wrap1(isNotBlank), new(func(any) bool)),

		// Date functions
		expr.Function("year", wrap1(extractYear), new(func(any) int)),
		expr.Function("month", wrap1(extractMonth), new(func(any) int)),
		expr.Function("day", wrap1(extractDay), new(func(any) int)),
		expr.Function("quarter", wrap1(extractQuarter), new(func(any) int)),
		expr.Function("isValidDate", wrap1(isValidDate), new(func(any) bool)),
		expr.Function("calculateAge", wrap2(calculateAge), new(func(string, string) int)),

		// String functions
		expr.Function("isNumeric", wrap1(isNumeric), new(func(string) bool)),
		expr.Function("isAlphaNumeric", wrap1(isAlphaNumeric), new(func(string) bool)),

		// SSN validation
		expr.Function("isValidSSN", wrap1(isValidSSN), new(func(string) bool)),

		// Header validation
		expr.Function("isValidFIPS", wrap1(isValidFIPS), new(func(string) bool)),
		expr.Function("isTribeCodeEmpty", wrap1(isTribeCodeEmpty), new(func(string) bool)),
		expr.Function("fiscalToCalendarYear", wrap2(fiscalToCalendarYear), new(func(int, string) int)),
		expr.Function("fiscalToCalendarQuarter", wrap2(fiscalToCalendarQuarter), new(func(int, string) string)),

		// Group validators (take group explicitly)
		expr.Function("getRecordsOfType", wrap2(getRecordsOfType),
			new(func(*parser.ParsedGroup, string) []*parser.ParsedRecord)),
		expr.Function("hasAnyRecordType", wrap2(hasAnyRecordType),
			new(func(map[string]int, []any) bool)),
		expr.Function("anyRecordOfTypesHasInt", wrap4(anyRecordOfTypesHasInt),
			new(func(*parser.ParsedGroup, []any, string, int) bool)),
		expr.Function("hasAnyRecordOfTypeWithInt", wrap4(hasAnyRecordOfTypeWithInt),
			new(func(*parser.ParsedGroup, string, string, int) bool)),

		// Duplicate detection (group scope, return []*ParsedRecord for per_record mode)
		expr.Function("getExactDuplicates", wrap2(getExactDuplicates),
			new(func(*parser.ParsedGroup, string) []*parser.ParsedRecord)),
		expr.Function("getPartialDuplicates", wrap3(getPartialDuplicates),
			new(func(*parser.ParsedGroup, string, []any) []*parser.ParsedRecord)),
		expr.Function("getPartialDuplicatesExcluding", wrap5(getPartialDuplicatesExcluding),
			new(func(*parser.ParsedGroup, string, []any, string, []any) []*parser.ParsedRecord)),
	}
}

// Generic wrappers bridge typed Go functions to the expr-lang library's required
// variadic signature: func(...any) (any, error). The expr.Function API does not
// accept typed functions directly — all custom functions must use this signature.
// These generic wrappers validate parameter count, type-assert each argument,
// and delegate to the real typed function.

func wrap1[A, R any](fn func(A) R) func(...any) (any, error) {
	return func(params ...any) (any, error) {
		if len(params) != 1 {
			return nil, fmt.Errorf("expected 1 argument, got %d", len(params))
		}
		a, ok := params[0].(A)
		if !ok {
			return nil, fmt.Errorf("argument type mismatch at position 0: got %T", params[0])
		}
		return fn(a), nil
	}
}

func wrap2[A, B, R any](fn func(A, B) R) func(...any) (any, error) {
	return func(params ...any) (any, error) {
		if len(params) != 2 {
			return nil, fmt.Errorf("expected 2 arguments, got %d", len(params))
		}
		a, ok1 := params[0].(A)
		b, ok2 := params[1].(B)
		if !ok1 || !ok2 {
			return nil, fmt.Errorf("argument type mismatch: got (%T, %T)", params[0], params[1])
		}
		return fn(a, b), nil
	}
}

func wrap3[A, B, C, R any](fn func(A, B, C) R) func(...any) (any, error) {
	return func(params ...any) (any, error) {
		if len(params) != 3 {
			return nil, fmt.Errorf("expected 3 arguments, got %d", len(params))
		}
		a, ok1 := params[0].(A)
		b, ok2 := params[1].(B)
		c, ok3 := params[2].(C)
		if !ok1 || !ok2 || !ok3 {
			return nil, fmt.Errorf("argument type mismatch: got (%T, %T, %T)", params[0], params[1], params[2])
		}
		return fn(a, b, c), nil
	}
}

func wrap4[A, B, C, D, R any](fn func(A, B, C, D) R) func(...any) (any, error) {
	return func(params ...any) (any, error) {
		if len(params) != 4 {
			return nil, fmt.Errorf("expected 4 arguments, got %d", len(params))
		}
		a, ok1 := params[0].(A)
		b, ok2 := params[1].(B)
		c, ok3 := params[2].(C)
		d, ok4 := params[3].(D)
		if !ok1 || !ok2 || !ok3 || !ok4 {
			return nil, fmt.Errorf("argument type mismatch: got (%T, %T, %T, %T)", params[0], params[1], params[2], params[3])
		}
		return fn(a, b, c, d), nil
	}
}

func wrap5[A, B, C, D, E, R any](fn func(A, B, C, D, E) R) func(...any) (any, error) {
	return func(params ...any) (any, error) {
		if len(params) != 5 {
			return nil, fmt.Errorf("expected 5 arguments, got %d", len(params))
		}
		a, ok1 := params[0].(A)
		b, ok2 := params[1].(B)
		c, ok3 := params[2].(C)
		d, ok4 := params[3].(D)
		e, ok5 := params[4].(E)
		if !ok1 || !ok2 || !ok3 || !ok4 || !ok5 {
			return nil, fmt.Errorf("argument type mismatch: got (%T, %T, %T, %T, %T)", params[0], params[1], params[2], params[3], params[4])
		}
		return fn(a, b, c, d, e), nil
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
	day, _ := strconv.Atoi(s[6:])
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

// calculateAge calculates age in years from a date of birth and a reference date.
// dob should be in YYYYMMDD format.
// rptMonthYear should be in YYYYMM format.
// Returns age in whole years, or -1 if dates are invalid.
// This matches the Python logic: (rptMonthYear - dob).days / 365.25
func calculateAge(dob, rptMonthYear string) int {
	if len(dob) != 8 || len(rptMonthYear) != 6 {
		return -1
	}

	dobTime, err := time.Parse("20060102", dob)
	if err != nil {
		return -1
	}

	// RPT_MONTH_YEAR is YYYYMM, treat as first day of month
	refTime, err := time.Parse("200601", rptMonthYear)
	if err != nil {
		return -1
	}

	// Calculate age using the same approach as Python: days / 365.25
	days := refTime.Sub(dobTime).Hours() / 24
	age := int(days / 365.25)

	return age
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

// getRecordsOfType returns all records of the given type from a group.
func getRecordsOfType(group *parser.ParsedGroup, recordType string) []*parser.ParsedRecord {
	var result []*parser.ParsedRecord
	for _, rec := range group.Records {
		if rec.GetRecordType() == recordType {
			result = append(result, rec)
		}
	}
	return result
}

// hasAnyRecordType returns true when any requested record type is present in the group.
func hasAnyRecordType(recordCounts map[string]int, recordTypes []any) bool {
	for _, recordType := range toStringSlice(recordTypes) {
		if recordCounts[recordType] > 0 {
			return true
		}
	}
	return false
}

// anyRecordOfTypesHasInt returns true when any record of the given types has
// the requested integer field value.
func anyRecordOfTypesHasInt(group *parser.ParsedGroup, recordTypes []any, fieldName string, expectedValue int) bool {
	for _, recordType := range toStringSlice(recordTypes) {
		if hasAnyRecordOfTypeWithInt(group, recordType, fieldName, expectedValue) {
			return true
		}
	}
	return false
}

// hasAnyRecordOfTypeWithInt returns true when any record of the given type has
// the requested integer field value.
func hasAnyRecordOfTypeWithInt(group *parser.ParsedGroup, recordType string, fieldName string, expectedValue int) bool {
	for _, rec := range getRecordsOfType(group, recordType) {
		if rec.GetInt(fieldName) == expectedValue {
			return true
		}
	}
	return false
}

// getExactDuplicates returns records that are exact duplicates of earlier records
// of the same type within the group. Uses EqualFields for pairwise comparison.
// The first occurrence is kept; subsequent matches are returned as duplicates.
func getExactDuplicates(group *parser.ParsedGroup, recordType string) []*parser.ParsedRecord {
	records := getRecordsOfType(group, recordType)
	var duplicates []*parser.ParsedRecord
	for i := 1; i < len(records); i++ {
		for j := 0; j < i; j++ {
			if records[i].EqualFields(records[j]) && records[i].LineNumber != records[j].LineNumber {
				duplicates = append(duplicates, records[i])
				break
			}
		}
	}
	return duplicates
}

// getPartialDuplicates returns records that are partial duplicates (matching on
// the specified key fields) but NOT exact duplicates. Exact duplicates are skipped
// because they are handled by the exact_duplicates validator.
func getPartialDuplicates(group *parser.ParsedGroup, recordType string, fields []any) []*parser.ParsedRecord {
	records := getRecordsOfType(group, recordType)
	fieldNames := toStringSlice(fields)
	seen := make(map[string]*parser.ParsedRecord)
	var duplicates []*parser.ParsedRecord
	for _, rec := range records {
		key := buildCompositeKey(rec, fieldNames)
		if first, exists := seen[key]; exists {
			if !rec.EqualFields(first) && rec.LineNumber != first.LineNumber {
				duplicates = append(duplicates, rec)
			}
		} else {
			seen[key] = rec
		}
	}
	return duplicates
}

// getPartialDuplicatesExcluding is like getPartialDuplicates but excludes records
// where excludeField's value is in excludeValues before checking for duplicates.
func getPartialDuplicatesExcluding(group *parser.ParsedGroup, recordType string, fields []any, excludeField string, excludeValues []any) []*parser.ParsedRecord {
	records := getRecordsOfType(group, recordType)
	fieldNames := toStringSlice(fields)

	// Build exclusion set for fast lookup
	excludeSet := make(map[any]bool, len(excludeValues))
	for _, v := range excludeValues {
		excludeSet[v] = true
	}

	seen := make(map[string]*parser.ParsedRecord)
	var duplicates []*parser.ParsedRecord
	for _, rec := range records {
		// Skip excluded records
		if excludeSet[rec.Get(excludeField)] {
			continue
		}
		key := buildCompositeKey(rec, fieldNames)
		if first, exists := seen[key]; exists {
			if !rec.EqualFields(first) && rec.LineNumber != first.LineNumber {
				duplicates = append(duplicates, rec)
			}
		} else {
			seen[key] = rec
		}
	}
	return duplicates
}

// buildCompositeKey builds a string key from the specified field values of a record.
func buildCompositeKey(rec *parser.ParsedRecord, fieldNames []string) string {
	var b strings.Builder
	for i, name := range fieldNames {
		if i > 0 {
			b.WriteByte('|')
		}
		b.WriteString(anyToString(rec.Get(name)))
	}
	return b.String()
}

// toStringSlice converts a []any to []string.
// The expr engine passes YAML arrays as []any.
func toStringSlice(in []any) []string {
	out := make([]string, len(in))
	for i, v := range in {
		out[i] = anyToString(v)
	}
	return out
}

// anyToString converts any value to a string without using fmt.Sprintf.
// Handles the types actually stored in ParsedRecord fields (string, int).
func anyToString(v any) string {
	switch val := v.(type) {
	case string:
		return val
	case int:
		return strconv.Itoa(val)
	case nil:
		return "<nil>"
	default:
		return fmt.Sprintf("%v", val)
	}
}

// validFIPSCodes is the set of valid US state/territory FIPS codes.
var validFIPSCodes = map[string]bool{
	"00": true, "01": true, "02": true, "04": true, "05": true,
	"06": true, "08": true, "09": true, "10": true, "11": true,
	"12": true, "13": true, "15": true, "16": true, "17": true,
	"18": true, "19": true, "20": true, "21": true, "22": true,
	"23": true, "24": true, "25": true, "26": true, "27": true,
	"28": true, "29": true, "30": true, "31": true, "32": true,
	"33": true, "34": true, "35": true, "36": true, "37": true,
	"38": true, "39": true, "40": true, "41": true, "42": true,
	"44": true, "45": true, "46": true, "47": true, "48": true,
	"49": true, "50": true, "51": true, "53": true, "54": true,
	"55": true, "56": true, "66": true, "72": true, "78": true,
}

// isValidFIPS returns true if the value is a valid US state/territory FIPS code.
func isValidFIPS(value string) bool {
	return validFIPSCodes[value]
}

// isTribeCodeEmpty returns true if a tribe code is effectively empty.
// Tribe code is empty if it's blank, all spaces, or "000".
func isTribeCodeEmpty(value string) bool {
	if isBlank(value) {
		return true
	}
	trimmed := strings.TrimSpace(value)
	if trimmed == "000" {
		return true
	}
	// Check for padding characters
	for _, c := range trimmed {
		if c != '#' && c != '_' {
			return false
		}
	}
	return true
}

// fiscalToCalendarYear converts a fiscal year and quarter to the calendar year.
// Fiscal Q1 (Oct-Dec) maps to the previous calendar year.
// Fiscal Q2-Q4 map to the same calendar year.
func fiscalToCalendarYear(fiscalYear int, fiscalQuarter string) int {
	fq := parseFiscalQuarter(fiscalQuarter)
	if fq == 1 {
		return fiscalYear - 1
	}
	return fiscalYear
}

// fiscalToCalendarQuarter converts a fiscal year and quarter to the calendar quarter.
// Fiscal Q1 -> Calendar "4", Q2 -> "1", Q3 -> "2", Q4 -> "3"
func fiscalToCalendarQuarter(fiscalYear int, fiscalQuarter string) string {
	fq := parseFiscalQuarter(fiscalQuarter)
	quarters := [4]string{"4", "1", "2", "3"} // FQ1->CQ4, FQ2->CQ1, FQ3->CQ2, FQ4->CQ3
	if fq < 1 || fq > 4 {
		return ""
	}
	return quarters[fq-1]
}

// parseFiscalQuarter extracts the quarter number from "Q1", "Q2", etc.
func parseFiscalQuarter(fq string) int {
	if len(fq) == 2 && fq[0] == 'Q' {
		n, _ := strconv.Atoi(string(fq[1]))
		return n
	}
	return 0
}

// isValidSSN validates a Social Security Number according to SSA rules.
// A valid SSN must:
// 1. Be exactly 9 digits
// 2. Be all numeric
// 3. Area number (positions 0-2) not be 000, 666, or 9xx
// 4. Group number (positions 3-4) not be 00
// 5. Serial number (positions 5-8) not be 0000
// 6. Not be a repeating digit pattern (111111111, 222222222, etc.)
func isValidSSN(ssn string) bool {
	// Check length
	if len(ssn) != 9 {
		return false
	}

	// Check all numeric
	if !isNumeric(ssn) {
		return false
	}

	// Check for repeating patterns (000000000 through 999999999)
	repeating := []string{
		"000000000", "111111111", "222222222", "333333333", "444444444",
		"555555555", "666666666", "777777777", "888888888", "999999999",
	}
	for _, pattern := range repeating {
		if ssn == pattern {
			return false
		}
	}

	// Check area number (positions 0-2)
	area := ssn[0:3]
	if area == "000" || area == "666" {
		return false
	}
	// Area numbers starting with 9 are not valid (reserved for ITIN and other purposes)
	if ssn[0] == '9' {
		return false
	}

	// Check group number (positions 3-4)
	group := ssn[3:5]
	if group == "00" {
		return false
	}

	// Check serial number (positions 5-8)
	serial := ssn[5:9]
	if serial == "0000" {
		return false
	}

	return true
}
