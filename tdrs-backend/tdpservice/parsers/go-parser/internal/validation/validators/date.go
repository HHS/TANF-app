package validators

import (
	"fmt"
	"strconv"
	"time"

	"go-parser/internal/validation"
	"go-parser/internal/validation/registry"
)

// RegisterDate registers all date validators with the registry.
func RegisterDate(r *registry.ValidatorRegistry) {
	r.Register("dateYearIsLargerThan", DateYearIsLargerThanFactory)
	r.Register("dateYearIsLessThan", DateYearIsLessThanFactory)
	r.Register("dateYearIsBetween", DateYearIsBetweenFactory)
	r.Register("dateMonthIsValid", DateMonthIsValidFactory)
	r.Register("dateDayIsValid", DateDayIsValidFactory)
	r.Register("dateIsValid", DateIsValidFactory)
	r.Register("dateIsInPast", DateIsInPastFactory)
	r.Register("dateIsInFuture", DateIsInFutureFactory)
	r.Register("quarterIsValid", QuarterIsValidFactory)
}

// DateYearIsLargerThanFactory creates a validator that checks if a date's year is larger than a threshold.
// The value can be:
//   - An integer in YYYYMM or YYYYMMDD format
//   - A string in YYYYMM or YYYYMMDD format
//
// Params:
//   - year: minimum year (exclusive)
func DateYearIsLargerThanFactory(params map[string]any) (validation.ValidatorFunc, error) {
	year, err := getIntParam(params, "year")
	if err != nil {
		return nil, fmt.Errorf("dateYearIsLargerThan: %w", err)
	}

	return func(ctx *validation.ValidationContext) *validation.ValidationResult {
		dateYear := extractYear(ctx.FieldValue())
		if dateYear > year {
			return validation.ValidResult()
		}
		result := validation.AcquireResult()
		result.Valid = false
		result.ValidatorID = "dateYearIsLargerThan"
		result.Category = ctx.Category
		result.Record = ctx.Record
		return result
	}, nil
}

// DateYearIsLessThanFactory creates a validator that checks if a date's year is less than a threshold.
func DateYearIsLessThanFactory(params map[string]any) (validation.ValidatorFunc, error) {
	year, err := getIntParam(params, "year")
	if err != nil {
		return nil, fmt.Errorf("dateYearIsLessThan: %w", err)
	}

	return func(ctx *validation.ValidationContext) *validation.ValidationResult {
		dateYear := extractYear(ctx.FieldValue())
		if dateYear < year {
			return validation.ValidResult()
		}
		result := validation.AcquireResult()
		result.Valid = false
		result.ValidatorID = "dateYearIsLessThan"
		result.Category = ctx.Category
		result.Record = ctx.Record
		return result
	}, nil
}

// DateYearIsBetweenFactory creates a validator that checks if a date's year is within a range.
func DateYearIsBetweenFactory(params map[string]any) (validation.ValidatorFunc, error) {
	minYear, err := getIntParam(params, "min")
	if err != nil {
		return nil, fmt.Errorf("dateYearIsBetween: %w", err)
	}
	maxYear, err := getIntParam(params, "max")
	if err != nil {
		return nil, fmt.Errorf("dateYearIsBetween: %w", err)
	}

	return func(ctx *validation.ValidationContext) *validation.ValidationResult {
		dateYear := extractYear(ctx.FieldValue())
		if dateYear >= minYear && dateYear <= maxYear {
			return validation.ValidResult()
		}
		result := validation.AcquireResult()
		result.Valid = false
		result.ValidatorID = "dateYearIsBetween"
		result.Category = ctx.Category
		result.Record = ctx.Record
		return result
	}, nil
}

// DateMonthIsValidFactory creates a validator that checks if a date's month is valid (01-12).
func DateMonthIsValidFactory(params map[string]any) (validation.ValidatorFunc, error) {
	return func(ctx *validation.ValidationContext) *validation.ValidationResult {
		month := extractMonth(ctx.FieldValue())
		if month >= 1 && month <= 12 {
			return validation.ValidResult()
		}
		result := validation.AcquireResult()
		result.Valid = false
		result.ValidatorID = "dateMonthIsValid"
		result.Category = ctx.Category
		result.Record = ctx.Record
		return result
	}, nil
}

// DateDayIsValidFactory creates a validator that checks if a date's day is valid for its month.
func DateDayIsValidFactory(params map[string]any) (validation.ValidatorFunc, error) {
	return func(ctx *validation.ValidationContext) *validation.ValidationResult {
		year := extractYear(ctx.FieldValue())
		month := extractMonth(ctx.FieldValue())
		day := extractDay(ctx.FieldValue())

		if isValidDay(year, month, day) {
			return validation.ValidResult()
		}
		result := validation.AcquireResult()
		result.Valid = false
		result.ValidatorID = "dateDayIsValid"
		result.Category = ctx.Category
		result.Record = ctx.Record
		return result
	}, nil
}

// DateIsValidFactory creates a validator that checks if the entire date is valid.
// Validates year, month, and day components.
func DateIsValidFactory(params map[string]any) (validation.ValidatorFunc, error) {
	return func(ctx *validation.ValidationContext) *validation.ValidationResult {
		value := ctx.FieldValue()
		year := extractYear(value)
		month := extractMonth(value)
		day := extractDay(value)

		// For YYYYMM format (no day), only validate year and month
		if day == 0 {
			if year > 0 && month >= 1 && month <= 12 {
				return validation.ValidResult()
			}
		} else {
			// Full date validation
			if year > 0 && isValidDay(year, month, day) {
				return validation.ValidResult()
			}
		}

		result := validation.AcquireResult()
		result.Valid = false
		result.ValidatorID = "dateIsValid"
		result.Category = ctx.Category
		result.Record = ctx.Record
		return result
	}, nil
}

// DateIsInPastFactory creates a validator that checks if a date is in the past.
func DateIsInPastFactory(params map[string]any) (validation.ValidatorFunc, error) {
	return func(ctx *validation.ValidationContext) *validation.ValidationResult {
		value := ctx.FieldValue()
		year := extractYear(value)
		month := extractMonth(value)
		day := extractDay(value)
		if day == 0 {
			day = 1 // Default to first of month for YYYYMM format
		}

		date := time.Date(year, time.Month(month), day, 0, 0, 0, 0, time.UTC)
		if date.Before(time.Now()) {
			return validation.ValidResult()
		}

		result := validation.AcquireResult()
		result.Valid = false
		result.ValidatorID = "dateIsInPast"
		result.Category = ctx.Category
		result.Record = ctx.Record
		return result
	}, nil
}

// DateIsInFutureFactory creates a validator that checks if a date is in the future.
func DateIsInFutureFactory(params map[string]any) (validation.ValidatorFunc, error) {
	return func(ctx *validation.ValidationContext) *validation.ValidationResult {
		value := ctx.FieldValue()
		year := extractYear(value)
		month := extractMonth(value)
		day := extractDay(value)
		if day == 0 {
			day = 1
		}

		date := time.Date(year, time.Month(month), day, 0, 0, 0, 0, time.UTC)
		if date.After(time.Now()) {
			return validation.ValidResult()
		}

		result := validation.AcquireResult()
		result.Valid = false
		result.ValidatorID = "dateIsInFuture"
		result.Category = ctx.Category
		result.Record = ctx.Record
		return result
	}, nil
}

// QuarterIsValidFactory creates a validator that checks if a quarter value is valid (1-4).
func QuarterIsValidFactory(params map[string]any) (validation.ValidatorFunc, error) {
	return func(ctx *validation.ValidationContext) *validation.ValidationResult {
		quarter := extractQuarter(ctx.FieldValue())
		if quarter >= 1 && quarter <= 4 {
			return validation.ValidResult()
		}
		result := validation.AcquireResult()
		result.Valid = false
		result.ValidatorID = "quarterIsValid"
		result.Category = ctx.Category
		result.Record = ctx.Record
		return result
	}, nil
}

// extractYear extracts the year from a date value.
// Supports formats: YYYYMM (int or string), YYYYMMDD (int or string)
func extractYear(v any) int {
	switch val := v.(type) {
	case int:
		if val >= 10000000 { // YYYYMMDD
			return val / 10000
		}
		if val >= 100000 { // YYYYMM
			return val / 100
		}
		return val // Assume it's just a year
	case string:
		if len(val) >= 4 {
			year, _ := strconv.Atoi(val[:4])
			return year
		}
	}
	return 0
}

// extractMonth extracts the month from a date value.
func extractMonth(v any) int {
	switch val := v.(type) {
	case int:
		if val >= 10000000 { // YYYYMMDD
			return (val / 100) % 100
		}
		if val >= 100000 { // YYYYMM
			return val % 100
		}
		return 0
	case string:
		if len(val) >= 6 {
			month, _ := strconv.Atoi(val[4:6])
			return month
		}
	}
	return 0
}

// extractDay extracts the day from a date value.
// Returns 0 if the value doesn't include a day component.
func extractDay(v any) int {
	switch val := v.(type) {
	case int:
		if val >= 10000000 { // YYYYMMDD
			return val % 100
		}
		return 0 // YYYYMM format has no day
	case string:
		if len(val) >= 8 {
			day, _ := strconv.Atoi(val[6:8])
			return day
		}
	}
	return 0
}

// extractQuarter extracts a quarter from a value.
// Handles YYYYQ format or standalone quarter values.
func extractQuarter(v any) int {
	switch val := v.(type) {
	case int:
		if val >= 10000 && val <= 99999 { // YYYYQ format
			return val % 10
		}
		if val >= 1 && val <= 4 {
			return val
		}
		return 0
	case string:
		if len(val) == 5 {
			q, _ := strconv.Atoi(val[4:5])
			return q
		}
		if len(val) == 1 {
			q, _ := strconv.Atoi(val)
			return q
		}
	}
	return 0
}

// isValidDay checks if a day is valid for a given year and month.
func isValidDay(year, month, day int) bool {
	if month < 1 || month > 12 {
		return false
	}
	if day < 1 {
		return false
	}

	daysInMonth := 31
	switch month {
	case 4, 6, 9, 11:
		daysInMonth = 30
	case 2:
		if isLeapYear(year) {
			daysInMonth = 29
		} else {
			daysInMonth = 28
		}
	}

	return day <= daysInMonth
}

// isLeapYear checks if a year is a leap year.
func isLeapYear(year int) bool {
	return year%4 == 0 && (year%100 != 0 || year%400 == 0)
}
