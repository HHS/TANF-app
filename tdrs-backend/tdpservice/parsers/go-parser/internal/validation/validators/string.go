package validators

import (
	"fmt"
	"regexp"
	"strings"

	"go-parser/internal/validation"
	"go-parser/internal/validation/registry"
)

// RegisterString registers all string validators with the registry.
func RegisterString(r *registry.ValidatorRegistry) {
	r.Register("isEmpty", IsEmptyFactory)
	r.Register("isNotEmpty", IsNotEmptyFactory)
	r.Register("hasLength", HasLengthFactory)
	r.Register("hasMinLength", HasMinLengthFactory)
	r.Register("hasMaxLength", HasMaxLengthFactory)
	r.Register("hasLengthBetween", HasLengthBetweenFactory)
	r.Register("matchesPattern", MatchesPatternFactory)
	r.Register("startsWith", StartsWithFactory)
	r.Register("endsWith", EndsWithFactory)
	r.Register("contains", ContainsFactory)
	r.Register("isAlphanumeric", IsAlphanumericFactory)
	r.Register("isNumeric", IsNumericFactory)
	r.Register("isAlphabetic", IsAlphabeticFactory)
}

// IsEmptyFactory creates a validator that checks if a value is empty.
func IsEmptyFactory(params map[string]any) (validation.ValidatorFunc, error) {
	return func(ctx *validation.ValidationContext) *validation.ValidationResult {
		value := ctx.FieldValue()
		if isEmptyValue(value) {
			return validation.ValidResult()
		}
		result := validation.AcquireResult()
		result.Valid = false
		result.ValidatorID = "isEmpty"
		result.Category = ctx.Category
		result.FieldIndex = ctx.FieldIndex
		result.Record = ctx.Record
		result.Schema = ctx.Schema
		return result
	}, nil
}

// IsNotEmptyFactory creates a validator that checks if a value is not empty.
func IsNotEmptyFactory(params map[string]any) (validation.ValidatorFunc, error) {
	return func(ctx *validation.ValidationContext) *validation.ValidationResult {
		value := ctx.FieldValue()
		if !isEmptyValue(value) {
			return validation.ValidResult()
		}
		result := validation.AcquireResult()
		result.Valid = false
		result.ValidatorID = "isNotEmpty"
		result.Category = ctx.Category
		result.FieldIndex = ctx.FieldIndex
		result.Record = ctx.Record
		result.Schema = ctx.Schema
		return result
	}, nil
}

// HasLengthFactory creates a validator that checks if a string has exact length.
// Params:
//   - length: required exact length
func HasLengthFactory(params map[string]any) (validation.ValidatorFunc, error) {
	length, err := getIntParam(params, "length")
	if err != nil {
		return nil, fmt.Errorf("hasLength: %w", err)
	}

	return func(ctx *validation.ValidationContext) *validation.ValidationResult {
		value := toString(ctx.FieldValue())
		if len(value) == length {
			return validation.ValidResult()
		}
		result := validation.AcquireResult()
		result.Valid = false
		result.ValidatorID = "hasLength"
		result.Category = ctx.Category
		result.FieldIndex = ctx.FieldIndex
		result.Record = ctx.Record
		result.Schema = ctx.Schema
		return result
	}, nil
}

// HasMinLengthFactory creates a validator that checks if a string has minimum length.
func HasMinLengthFactory(params map[string]any) (validation.ValidatorFunc, error) {
	min, err := getIntParam(params, "min")
	if err != nil {
		return nil, fmt.Errorf("hasMinLength: %w", err)
	}

	return func(ctx *validation.ValidationContext) *validation.ValidationResult {
		value := toString(ctx.FieldValue())
		if len(value) >= min {
			return validation.ValidResult()
		}
		result := validation.AcquireResult()
		result.Valid = false
		result.ValidatorID = "hasMinLength"
		result.Category = ctx.Category
		result.FieldIndex = ctx.FieldIndex
		result.Record = ctx.Record
		result.Schema = ctx.Schema
		return result
	}, nil
}

// HasMaxLengthFactory creates a validator that checks if a string has maximum length.
func HasMaxLengthFactory(params map[string]any) (validation.ValidatorFunc, error) {
	max, err := getIntParam(params, "max")
	if err != nil {
		return nil, fmt.Errorf("hasMaxLength: %w", err)
	}

	return func(ctx *validation.ValidationContext) *validation.ValidationResult {
		value := toString(ctx.FieldValue())
		if len(value) <= max {
			return validation.ValidResult()
		}
		result := validation.AcquireResult()
		result.Valid = false
		result.ValidatorID = "hasMaxLength"
		result.Category = ctx.Category
		result.FieldIndex = ctx.FieldIndex
		result.Record = ctx.Record
		result.Schema = ctx.Schema
		return result
	}, nil
}

// HasLengthBetweenFactory creates a validator that checks if string length is within range.
func HasLengthBetweenFactory(params map[string]any) (validation.ValidatorFunc, error) {
	min, err := getIntParam(params, "min")
	if err != nil {
		return nil, fmt.Errorf("hasLengthBetween: %w", err)
	}
	max, err := getIntParam(params, "max")
	if err != nil {
		return nil, fmt.Errorf("hasLengthBetween: %w", err)
	}

	return func(ctx *validation.ValidationContext) *validation.ValidationResult {
		value := toString(ctx.FieldValue())
		length := len(value)
		if length >= min && length <= max {
			return validation.ValidResult()
		}
		result := validation.AcquireResult()
		result.Valid = false
		result.ValidatorID = "hasLengthBetween"
		result.Category = ctx.Category
		result.FieldIndex = ctx.FieldIndex
		result.Record = ctx.Record
		result.Schema = ctx.Schema
		return result
	}, nil
}

// MatchesPatternFactory creates a validator that checks if a value matches a regex pattern.
// Params:
//   - pattern: regex pattern to match
func MatchesPatternFactory(params map[string]any) (validation.ValidatorFunc, error) {
	patternStr, ok := params["pattern"].(string)
	if !ok {
		return nil, fmt.Errorf("matchesPattern requires 'pattern' parameter as string")
	}

	pattern, err := regexp.Compile(patternStr)
	if err != nil {
		return nil, fmt.Errorf("matchesPattern: invalid pattern %q: %w", patternStr, err)
	}

	return func(ctx *validation.ValidationContext) *validation.ValidationResult {
		value := toString(ctx.FieldValue())
		if pattern.MatchString(value) {
			return validation.ValidResult()
		}
		result := validation.AcquireResult()
		result.Valid = false
		result.ValidatorID = "matchesPattern"
		result.Category = ctx.Category
		result.FieldIndex = ctx.FieldIndex
		result.Record = ctx.Record
		result.Schema = ctx.Schema
		return result
	}, nil
}

// StartsWithFactory creates a validator that checks if a value starts with a prefix.
func StartsWithFactory(params map[string]any) (validation.ValidatorFunc, error) {
	prefix, ok := params["prefix"].(string)
	if !ok {
		return nil, fmt.Errorf("startsWith requires 'prefix' parameter as string")
	}

	return func(ctx *validation.ValidationContext) *validation.ValidationResult {
		value := toString(ctx.FieldValue())
		if strings.HasPrefix(value, prefix) {
			return validation.ValidResult()
		}
		result := validation.AcquireResult()
		result.Valid = false
		result.ValidatorID = "startsWith"
		result.Category = ctx.Category
		result.FieldIndex = ctx.FieldIndex
		result.Record = ctx.Record
		result.Schema = ctx.Schema
		return result
	}, nil
}

// EndsWithFactory creates a validator that checks if a value ends with a suffix.
func EndsWithFactory(params map[string]any) (validation.ValidatorFunc, error) {
	suffix, ok := params["suffix"].(string)
	if !ok {
		return nil, fmt.Errorf("endsWith requires 'suffix' parameter as string")
	}

	return func(ctx *validation.ValidationContext) *validation.ValidationResult {
		value := toString(ctx.FieldValue())
		if strings.HasSuffix(value, suffix) {
			return validation.ValidResult()
		}
		result := validation.AcquireResult()
		result.Valid = false
		result.ValidatorID = "endsWith"
		result.Category = ctx.Category
		result.FieldIndex = ctx.FieldIndex
		result.Record = ctx.Record
		result.Schema = ctx.Schema
		return result
	}, nil
}

// ContainsFactory creates a validator that checks if a value contains a substring.
func ContainsFactory(params map[string]any) (validation.ValidatorFunc, error) {
	substr, ok := params["substring"].(string)
	if !ok {
		return nil, fmt.Errorf("contains requires 'substring' parameter as string")
	}

	return func(ctx *validation.ValidationContext) *validation.ValidationResult {
		value := toString(ctx.FieldValue())
		if strings.Contains(value, substr) {
			return validation.ValidResult()
		}
		result := validation.AcquireResult()
		result.Valid = false
		result.ValidatorID = "contains"
		result.Category = ctx.Category
		result.FieldIndex = ctx.FieldIndex
		result.Record = ctx.Record
		result.Schema = ctx.Schema
		return result
	}, nil
}

// IsAlphanumericFactory creates a validator that checks if a value contains only letters and digits.
func IsAlphanumericFactory(params map[string]any) (validation.ValidatorFunc, error) {
	return func(ctx *validation.ValidationContext) *validation.ValidationResult {
		value := toString(ctx.FieldValue())
		for _, r := range value {
			if !isAlphanumeric(r) {
				result := validation.AcquireResult()
				result.Valid = false
				result.ValidatorID = "isAlphanumeric"
				result.Category = ctx.Category
				result.FieldIndex = ctx.FieldIndex
				result.Record = ctx.Record
				result.Schema = ctx.Schema
				return result
			}
		}
		return validation.ValidResult()
	}, nil
}

// IsNumericFactory creates a validator that checks if a value contains only digits.
func IsNumericFactory(params map[string]any) (validation.ValidatorFunc, error) {
	return func(ctx *validation.ValidationContext) *validation.ValidationResult {
		value := toString(ctx.FieldValue())
		for _, r := range value {
			if r < '0' || r > '9' {
				result := validation.AcquireResult()
				result.Valid = false
				result.ValidatorID = "isNumeric"
				result.Category = ctx.Category
				result.FieldIndex = ctx.FieldIndex
				result.Record = ctx.Record
				result.Schema = ctx.Schema
				return result
			}
		}
		return validation.ValidResult()
	}, nil
}

// IsAlphabeticFactory creates a validator that checks if a value contains only letters.
func IsAlphabeticFactory(params map[string]any) (validation.ValidatorFunc, error) {
	return func(ctx *validation.ValidationContext) *validation.ValidationResult {
		value := toString(ctx.FieldValue())
		for _, r := range value {
			if !isLetter(r) {
				result := validation.AcquireResult()
				result.Valid = false
				result.ValidatorID = "isAlphabetic"
				result.Category = ctx.Category
				result.FieldIndex = ctx.FieldIndex
				result.Record = ctx.Record
				result.Schema = ctx.Schema
				return result
			}
		}
		return validation.ValidResult()
	}, nil
}

// isEmptyValue checks if a value is considered empty.
func isEmptyValue(v any) bool {
	if v == nil {
		return true
	}
	switch val := v.(type) {
	case string:
		return strings.TrimSpace(val) == ""
	case int:
		return false // 0 is not considered empty for integers
	case int64:
		return false
	case float64:
		return false
	default:
		return false
	}
}

// toString converts a value to string.
func toString(v any) string {
	if v == nil {
		return ""
	}
	switch val := v.(type) {
	case string:
		return val
	default:
		return fmt.Sprintf("%v", v)
	}
}

// getIntParam extracts an integer parameter from params.
func getIntParam(params map[string]any, name string) (int, error) {
	v, ok := params[name]
	if !ok {
		return 0, fmt.Errorf("requires '%s' parameter", name)
	}
	switch n := v.(type) {
	case int:
		return n, nil
	case int64:
		return int(n), nil
	case float64:
		return int(n), nil
	default:
		return 0, fmt.Errorf("'%s' parameter must be an integer", name)
	}
}

// isAlphanumeric checks if a rune is a letter or digit.
func isAlphanumeric(r rune) bool {
	return isLetter(r) || (r >= '0' && r <= '9')
}

// isLetter checks if a rune is a letter.
func isLetter(r rune) bool {
	return (r >= 'a' && r <= 'z') || (r >= 'A' && r <= 'Z')
}
