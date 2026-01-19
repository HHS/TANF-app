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
		if ctx.Record.DecodedSize == length {
			return validation.ValidResult()
		}
		result := validation.AcquireResult()
		result.Valid = false
		result.ValidatorID = "recordHasLength"
		result.Category = ctx.Category
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
		if ctx.Record.DecodedSize >= min && ctx.Record.DecodedSize <= max {
			return validation.ValidResult()
		}
		result := validation.AcquireResult()
		result.Valid = false
		result.ValidatorID = "recordHasLengthBetween"
		result.Category = ctx.Category
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
		if ctx.Record.DecodedSize >= min {
			return validation.ValidResult()
		}
		result := validation.AcquireResult()
		result.Valid = false
		result.ValidatorID = "recordHasMinLength"
		result.Category = ctx.Category
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
		if ctx.Record.DecodedSize <= max {
			return validation.ValidResult()
		}
		result := validation.AcquireResult()
		result.Valid = false
		result.ValidatorID = "recordHasMaxLength"
		result.Category = ctx.Category
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
		if strings.HasPrefix(ctx.Record.Schema.RecordType, prefix) {
			return validation.ValidResult()
		}
		result := validation.AcquireResult()
		result.Valid = false
		result.ValidatorID = "recordStartsWith"
		result.Category = ctx.Category
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
		if strings.HasSuffix(ctx.Record.Schema.RecordType, suffix) {
			return validation.ValidResult()
		}
		result := validation.AcquireResult()
		result.Valid = false
		result.ValidatorID = "recordEndsWith"
		result.Category = ctx.Category
		return result
	}, nil
}

// CaseNumberNotEmptyFactory creates a validator that checks if the case number field is not empty.
// This is a common Cat 1 validation for records.
func CaseNumberNotEmptyFactory(params map[string]any) (validation.ValidatorFunc, error) {
	return func(ctx *validation.ValidationContext) *validation.ValidationResult {
		result := validation.AcquireResult()
		result.Valid = false
		result.ValidatorID = "caseNumberNotEmpty"
		result.Category = ctx.Category

		caseIdx, ok := ctx.Record.Schema.FieldIndex["CASE_NUMBER"]
		if !ok {
			return result
		}

		caseNumber := ctx.Record.Fields[caseIdx].Value.(string)
		trimmed := strings.TrimSpace(caseNumber)
		if trimmed != "" {
			return validation.ValidResult()
		}

		return result
	}, nil
}
