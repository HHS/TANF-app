package validators

import (
	"fmt"
	"strings"

	"go-parser/internal/validation"
	"go-parser/internal/validation/registry"
)

// RegisterRecord registers all record-level (Cat 1) validators with the registry.
// These validators operate on raw row data before field parsing.
func RegisterRecord(r *registry.ValidatorRegistry) {
	r.Register("recordHasLength", RecordHasLengthFactory)
	r.Register("recordHasLengthBetween", RecordHasLengthBetweenFactory)
	r.Register("recordHasMinLength", RecordHasMinLengthFactory)
	r.Register("recordHasMaxLength", RecordHasMaxLengthFactory)
	r.Register("recordStartsWith", RecordStartsWithFactory)
	r.Register("recordEndsWith", RecordEndsWithFactory)
	r.Register("caseNumberNotEmpty", CaseNumberNotEmptyFactory)
	r.Register("fieldAtPositionIsNotEmpty", FieldAtPositionIsNotEmptyFactory)
	r.Register("fieldAtPositionEquals", FieldAtPositionEqualsFactory)
	r.Register("fieldAtPositionIsOneOf", FieldAtPositionIsOneOfFactory)
}

// RecordHasLengthFactory creates a validator that checks if a record has exact length.
// Params:
//   - length: required exact length
func RecordHasLengthFactory(params map[string]any) (validation.ValidatorFunc, error) {
	length, err := getIntParam(params, "length")
	if err != nil {
		return nil, fmt.Errorf("recordHasLength: %w", err)
	}

	return func(ctx *validation.ValidationContext) *validation.ValidationResult {
		rowData := ctx.RawRowData()
		if len(rowData) == length {
			return validation.ValidResult()
		}
		result := validation.AcquireResult()
		result.Valid = false
		result.ValidatorID = "recordHasLength"
		result.Category = ctx.Category
		result.Row = ctx.Row
		result.Schema = ctx.Schema
		return result
	}, nil
}

// RecordHasLengthBetweenFactory creates a validator that checks if record length is within range.
// Params:
//   - min: minimum length (inclusive)
//   - max: maximum length (inclusive)
func RecordHasLengthBetweenFactory(params map[string]any) (validation.ValidatorFunc, error) {
	min, err := getIntParam(params, "min")
	if err != nil {
		return nil, fmt.Errorf("recordHasLengthBetween: %w", err)
	}
	max, err := getIntParam(params, "max")
	if err != nil {
		return nil, fmt.Errorf("recordHasLengthBetween: %w", err)
	}

	return func(ctx *validation.ValidationContext) *validation.ValidationResult {
		rowData := ctx.RawRowData()
		length := len(rowData)
		if length >= min && length <= max {
			return validation.ValidResult()
		}
		result := validation.AcquireResult()
		result.Valid = false
		result.ValidatorID = "recordHasLengthBetween"
		result.Category = ctx.Category
		result.Row = ctx.Row
		result.Schema = ctx.Schema
		return result
	}, nil
}

// RecordHasMinLengthFactory creates a validator that checks if record has minimum length.
func RecordHasMinLengthFactory(params map[string]any) (validation.ValidatorFunc, error) {
	min, err := getIntParam(params, "min")
	if err != nil {
		return nil, fmt.Errorf("recordHasMinLength: %w", err)
	}

	return func(ctx *validation.ValidationContext) *validation.ValidationResult {
		rowData := ctx.RawRowData()
		if len(rowData) >= min {
			return validation.ValidResult()
		}
		result := validation.AcquireResult()
		result.Valid = false
		result.ValidatorID = "recordHasMinLength"
		result.Category = ctx.Category
		result.Row = ctx.Row
		result.Schema = ctx.Schema
		return result
	}, nil
}

// RecordHasMaxLengthFactory creates a validator that checks if record has maximum length.
func RecordHasMaxLengthFactory(params map[string]any) (validation.ValidatorFunc, error) {
	max, err := getIntParam(params, "max")
	if err != nil {
		return nil, fmt.Errorf("recordHasMaxLength: %w", err)
	}

	return func(ctx *validation.ValidationContext) *validation.ValidationResult {
		rowData := ctx.RawRowData()
		if len(rowData) <= max {
			return validation.ValidResult()
		}
		result := validation.AcquireResult()
		result.Valid = false
		result.ValidatorID = "recordHasMaxLength"
		result.Category = ctx.Category
		result.Row = ctx.Row
		result.Schema = ctx.Schema
		return result
	}, nil
}

// RecordStartsWithFactory creates a validator that checks if record starts with a prefix.
// Params:
//   - prefix: required prefix string
func RecordStartsWithFactory(params map[string]any) (validation.ValidatorFunc, error) {
	prefix, ok := params["prefix"].(string)
	if !ok {
		return nil, fmt.Errorf("recordStartsWith requires 'prefix' parameter as string")
	}

	return func(ctx *validation.ValidationContext) *validation.ValidationResult {
		rowData := ctx.RawRowData()
		if strings.HasPrefix(rowData, prefix) {
			return validation.ValidResult()
		}
		result := validation.AcquireResult()
		result.Valid = false
		result.ValidatorID = "recordStartsWith"
		result.Category = ctx.Category
		result.Row = ctx.Row
		result.Schema = ctx.Schema
		return result
	}, nil
}

// RecordEndsWithFactory creates a validator that checks if record ends with a suffix.
func RecordEndsWithFactory(params map[string]any) (validation.ValidatorFunc, error) {
	suffix, ok := params["suffix"].(string)
	if !ok {
		return nil, fmt.Errorf("recordEndsWith requires 'suffix' parameter as string")
	}

	return func(ctx *validation.ValidationContext) *validation.ValidationResult {
		rowData := ctx.RawRowData()
		if strings.HasSuffix(rowData, suffix) {
			return validation.ValidResult()
		}
		result := validation.AcquireResult()
		result.Valid = false
		result.ValidatorID = "recordEndsWith"
		result.Category = ctx.Category
		result.Row = ctx.Row
		result.Schema = ctx.Schema
		return result
	}, nil
}

// CaseNumberNotEmptyFactory creates a validator that checks if the case number field is not empty.
// This is a common Cat 1 validation for records.
// Params:
//   - start: starting byte position (0-indexed, inclusive)
//   - end: ending byte position (0-indexed, exclusive)
func CaseNumberNotEmptyFactory(params map[string]any) (validation.ValidatorFunc, error) {
	start, err := getIntParam(params, "start")
	if err != nil {
		return nil, fmt.Errorf("caseNumberNotEmpty: %w", err)
	}
	end, err := getIntParam(params, "end")
	if err != nil {
		return nil, fmt.Errorf("caseNumberNotEmpty: %w", err)
	}

	return func(ctx *validation.ValidationContext) *validation.ValidationResult {
		caseNumber := ctx.RawRowSlice(start, end)
		trimmed := strings.TrimSpace(caseNumber)
		if trimmed != "" {
			return validation.ValidResult()
		}
		result := validation.AcquireResult()
		result.Valid = false
		result.ValidatorID = "caseNumberNotEmpty"
		result.Category = ctx.Category
		result.Row = ctx.Row
		result.Schema = ctx.Schema
		return result
	}, nil
}

// FieldAtPositionIsNotEmptyFactory creates a validator that checks if a field at a position is not empty.
// Params:
//   - start: starting byte position (0-indexed, inclusive)
//   - end: ending byte position (0-indexed, exclusive)
func FieldAtPositionIsNotEmptyFactory(params map[string]any) (validation.ValidatorFunc, error) {
	start, err := getIntParam(params, "start")
	if err != nil {
		return nil, fmt.Errorf("fieldAtPositionIsNotEmpty: %w", err)
	}
	end, err := getIntParam(params, "end")
	if err != nil {
		return nil, fmt.Errorf("fieldAtPositionIsNotEmpty: %w", err)
	}

	return func(ctx *validation.ValidationContext) *validation.ValidationResult {
		value := ctx.RawRowSlice(start, end)
		trimmed := strings.TrimSpace(value)
		if trimmed != "" {
			return validation.ValidResult()
		}
		result := validation.AcquireResult()
		result.Valid = false
		result.ValidatorID = "fieldAtPositionIsNotEmpty"
		result.Category = ctx.Category
		result.Row = ctx.Row
		result.Schema = ctx.Schema
		return result
	}, nil
}

// FieldAtPositionEqualsFactory creates a validator that checks if a field at a position equals a value.
// Params:
//   - start: starting byte position (0-indexed, inclusive)
//   - end: ending byte position (0-indexed, exclusive)
//   - value: expected value (will be trimmed before comparison)
//   - trim: whether to trim the extracted value (default: true)
func FieldAtPositionEqualsFactory(params map[string]any) (validation.ValidatorFunc, error) {
	start, err := getIntParam(params, "start")
	if err != nil {
		return nil, fmt.Errorf("fieldAtPositionEquals: %w", err)
	}
	end, err := getIntParam(params, "end")
	if err != nil {
		return nil, fmt.Errorf("fieldAtPositionEquals: %w", err)
	}
	expected := fmt.Sprintf("%v", params["value"])

	// Default trim to true
	trim := true
	if v, ok := params["trim"].(bool); ok {
		trim = v
	}

	return func(ctx *validation.ValidationContext) *validation.ValidationResult {
		value := ctx.RawRowSlice(start, end)
		if trim {
			value = strings.TrimSpace(value)
		}
		if value == expected {
			return validation.ValidResult()
		}
		result := validation.AcquireResult()
		result.Valid = false
		result.ValidatorID = "fieldAtPositionEquals"
		result.Category = ctx.Category
		result.Row = ctx.Row
		result.Schema = ctx.Schema
		return result
	}, nil
}

// FieldAtPositionIsOneOfFactory creates a validator that checks if a field at a position is one of allowed values.
// Params:
//   - start: starting byte position (0-indexed, inclusive)
//   - end: ending byte position (0-indexed, exclusive)
//   - values: slice of allowed values
//   - trim: whether to trim the extracted value (default: true)
func FieldAtPositionIsOneOfFactory(params map[string]any) (validation.ValidatorFunc, error) {
	start, err := getIntParam(params, "start")
	if err != nil {
		return nil, fmt.Errorf("fieldAtPositionIsOneOf: %w", err)
	}
	end, err := getIntParam(params, "end")
	if err != nil {
		return nil, fmt.Errorf("fieldAtPositionIsOneOf: %w", err)
	}

	rawValues, ok := params["values"]
	if !ok {
		return nil, fmt.Errorf("fieldAtPositionIsOneOf requires 'values' parameter")
	}

	// Build lookup set
	allowedValues := make(map[string]bool)
	switch v := rawValues.(type) {
	case []any:
		for _, val := range v {
			allowedValues[fmt.Sprintf("%v", val)] = true
		}
	case []string:
		for _, val := range v {
			allowedValues[val] = true
		}
	default:
		return nil, fmt.Errorf("fieldAtPositionIsOneOf 'values' must be a slice")
	}

	// Default trim to true
	trim := true
	if v, ok := params["trim"].(bool); ok {
		trim = v
	}

	return func(ctx *validation.ValidationContext) *validation.ValidationResult {
		value := ctx.RawRowSlice(start, end)
		if trim {
			value = strings.TrimSpace(value)
		}
		if allowedValues[value] {
			return validation.ValidResult()
		}
		result := validation.AcquireResult()
		result.Valid = false
		result.ValidatorID = "fieldAtPositionIsOneOf"
		result.Category = ctx.Category
		result.Row = ctx.Row
		result.Schema = ctx.Schema
		return result
	}, nil
}
