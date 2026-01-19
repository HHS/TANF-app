// Package validators provides built-in validator implementations.
package validators

import (
	"fmt"

	"go-parser/internal/validation"
	"go-parser/internal/validation/registry"
)

// RegisterComparison registers all comparison validators with the registry.
func RegisterComparison(r *registry.ValidatorRegistry) {
	r.Register("isEqual", IsEqualFactory)
	r.Register("isNotEqual", IsNotEqualFactory)
	r.Register("isGreaterThan", IsGreaterThanFactory)
	r.Register("isGreaterThanOrEqual", IsGreaterThanOrEqualFactory)
	r.Register("isLessThan", IsLessThanFactory)
	r.Register("isLessThanOrEqual", IsLessThanOrEqualFactory)
	r.Register("isBetween", IsBetweenFactory)
	r.Register("isOneOf", IsOneOfFactory)
}

// IsEqualFactory creates a validator that checks if a value equals a target.
// Params:
//   - value: the target value to compare against
func IsEqualFactory(params map[string]any) (validation.ValidatorFunc, error) {
	target, ok := params["value"]
	if !ok {
		return nil, fmt.Errorf("isEqual requires 'value' parameter")
	}

	return func(ctx *validation.ValidationContext) *validation.ValidationResult {
		value := ctx.FieldValue()
		if compareValues(value, target) == 0 {
			return validation.ValidResult()
		}
		result := validation.AcquireResult()
		result.Valid = false
		result.ValidatorID = "isEqual"
		result.Category = ctx.Category
		result.Record = ctx.Record
		return result
	}, nil
}

// IsNotEqualFactory creates a validator that checks if a value does not equal a target.
func IsNotEqualFactory(params map[string]any) (validation.ValidatorFunc, error) {
	target, ok := params["value"]
	if !ok {
		return nil, fmt.Errorf("isNotEqual requires 'value' parameter")
	}

	return func(ctx *validation.ValidationContext) *validation.ValidationResult {
		value := ctx.FieldValue()
		if compareValues(value, target) != 0 {
			return validation.ValidResult()
		}
		result := validation.AcquireResult()
		result.Valid = false
		result.ValidatorID = "isNotEqual"
		result.Category = ctx.Category
		result.Record = ctx.Record
		return result
	}, nil
}

// IsGreaterThanFactory creates a validator that checks if a value is greater than a target.
func IsGreaterThanFactory(params map[string]any) (validation.ValidatorFunc, error) {
	target, ok := params["value"]
	if !ok {
		return nil, fmt.Errorf("isGreaterThan requires 'value' parameter")
	}

	return func(ctx *validation.ValidationContext) *validation.ValidationResult {
		value := ctx.FieldValue()
		if compareValues(value, target) > 0 {
			return validation.ValidResult()
		}
		result := validation.AcquireResult()
		result.Valid = false
		result.ValidatorID = "isGreaterThan"
		result.Category = ctx.Category
		result.Record = ctx.Record
		return result
	}, nil
}

// IsGreaterThanOrEqualFactory creates a validator that checks if a value is >= a target.
func IsGreaterThanOrEqualFactory(params map[string]any) (validation.ValidatorFunc, error) {
	target, ok := params["value"]
	if !ok {
		return nil, fmt.Errorf("isGreaterThanOrEqual requires 'value' parameter")
	}

	return func(ctx *validation.ValidationContext) *validation.ValidationResult {
		value := ctx.FieldValue()
		if compareValues(value, target) >= 0 {
			return validation.ValidResult()
		}
		result := validation.AcquireResult()
		result.Valid = false
		result.ValidatorID = "isGreaterThanOrEqual"
		result.Category = ctx.Category
		result.Record = ctx.Record
		return result
	}, nil
}

// IsLessThanFactory creates a validator that checks if a value is less than a target.
func IsLessThanFactory(params map[string]any) (validation.ValidatorFunc, error) {
	target, ok := params["value"]
	if !ok {
		return nil, fmt.Errorf("isLessThan requires 'value' parameter")
	}

	return func(ctx *validation.ValidationContext) *validation.ValidationResult {
		value := ctx.FieldValue()
		if compareValues(value, target) < 0 {
			return validation.ValidResult()
		}
		result := validation.AcquireResult()
		result.Valid = false
		result.ValidatorID = "isLessThan"
		result.Category = ctx.Category
		result.Record = ctx.Record
		return result
	}, nil
}

// IsLessThanOrEqualFactory creates a validator that checks if a value is <= a target.
func IsLessThanOrEqualFactory(params map[string]any) (validation.ValidatorFunc, error) {
	target, ok := params["value"]
	if !ok {
		return nil, fmt.Errorf("isLessThanOrEqual requires 'value' parameter")
	}

	return func(ctx *validation.ValidationContext) *validation.ValidationResult {
		value := ctx.FieldValue()
		if compareValues(value, target) <= 0 {
			return validation.ValidResult()
		}
		result := validation.AcquireResult()
		result.Valid = false
		result.ValidatorID = "isLessThanOrEqual"
		result.Category = ctx.Category
		result.Record = ctx.Record
		return result
	}, nil
}

// IsBetweenFactory creates a validator that checks if a value is between min and max.
// Params:
//   - min: minimum value (inclusive by default)
//   - max: maximum value (inclusive by default)
//   - inclusive: whether bounds are inclusive (default: true)
func IsBetweenFactory(params map[string]any) (validation.ValidatorFunc, error) {
	min, ok := params["min"]
	if !ok {
		return nil, fmt.Errorf("isBetween requires 'min' parameter")
	}
	max, ok := params["max"]
	if !ok {
		return nil, fmt.Errorf("isBetween requires 'max' parameter")
	}

	// Default to inclusive
	inclusive := true
	if v, ok := params["inclusive"].(bool); ok {
		inclusive = v
	}

	return func(ctx *validation.ValidationContext) *validation.ValidationResult {
		value := ctx.FieldValue()
		cmpMin := compareValues(value, min)
		cmpMax := compareValues(value, max)

		valid := false
		if inclusive {
			valid = cmpMin >= 0 && cmpMax <= 0
		} else {
			valid = cmpMin > 0 && cmpMax < 0
		}

		if valid {
			return validation.ValidResult()
		}
		result := validation.AcquireResult()
		result.Valid = false
		result.ValidatorID = "isBetween"
		result.Category = ctx.Category
		result.Record = ctx.Record
		return result
	}, nil
}

// IsOneOfFactory creates a validator that checks if a value is in a list of allowed values.
// Params:
//   - values: slice of allowed values
func IsOneOfFactory(params map[string]any) (validation.ValidatorFunc, error) {
	rawValues, ok := params["values"]
	if !ok {
		return nil, fmt.Errorf("isOneOf requires 'values' parameter")
	}

	// Convert to a lookup map for O(1) checks
	// Handle different types that might come from YAML
	values := make(map[any]bool)
	switch v := rawValues.(type) {
	case []any:
		for _, val := range v {
			values[normalizeValue(val)] = true
		}
	case []int:
		for _, val := range v {
			values[val] = true
		}
	case []string:
		for _, val := range v {
			values[val] = true
		}
	default:
		return nil, fmt.Errorf("isOneOf 'values' must be a slice, got %T", rawValues)
	}

	return func(ctx *validation.ValidationContext) *validation.ValidationResult {
		value := normalizeValue(ctx.FieldValue())
		if values[value] {
			return validation.ValidResult()
		}
		result := validation.AcquireResult()
		result.Valid = false
		result.ValidatorID = "isOneOf"
		result.Category = ctx.Category
		result.Record = ctx.Record
		return result
	}, nil
}

// compareValues compares two values of potentially different types.
// Returns -1 if a < b, 0 if a == b, 1 if a > b.
// Handles int, int64, float64, string comparisons.
func compareValues(a, b any) int {
	// Handle nil cases
	if a == nil && b == nil {
		return 0
	}
	if a == nil {
		return -1
	}
	if b == nil {
		return 1
	}

	// Normalize both to comparable types
	aNum, aIsNum := toFloat64(a)
	bNum, bIsNum := toFloat64(b)

	if aIsNum && bIsNum {
		if aNum < bNum {
			return -1
		}
		if aNum > bNum {
			return 1
		}
		return 0
	}

	// Fall back to string comparison
	aStr := fmt.Sprintf("%v", a)
	bStr := fmt.Sprintf("%v", b)
	if aStr < bStr {
		return -1
	}
	if aStr > bStr {
		return 1
	}
	return 0
}

// toFloat64 converts a value to float64 if possible.
func toFloat64(v any) (float64, bool) {
	switch n := v.(type) {
	case int:
		return float64(n), true
	case int64:
		return float64(n), true
	case int32:
		return float64(n), true
	case float64:
		return n, true
	case float32:
		return float64(n), true
	default:
		return 0, false
	}
}

// normalizeValue normalizes a value for comparison/lookup.
// Converts numeric types to int when possible for consistent comparisons.
func normalizeValue(v any) any {
	switch n := v.(type) {
	case int:
		return n
	case int64:
		return int(n)
	case int32:
		return int(n)
	case float64:
		if n == float64(int(n)) {
			return int(n)
		}
		return n
	case float32:
		if n == float32(int(n)) {
			return int(n)
		}
		return float64(n)
	default:
		return v
	}
}
