package validators

import (
	"fmt"
	"strings"

	"go-parser/internal/validation"
	"go-parser/internal/validation/registry"
)

// RegisterCrossField registers all cross-field (Cat 3) validators with the registry.
// These validators operate on multiple fields within a single record.
func RegisterCrossField(r *registry.ValidatorRegistry) {
	r.Register("sumIsGreaterThan", SumIsGreaterThanFactory)
	r.Register("sumIsLessThan", SumIsLessThanFactory)
	r.Register("sumEquals", SumEqualsFactory)
	r.Register("atLeastOneOf", AtLeastOneOfFactory)
	r.Register("exactlyOneOf", ExactlyOneOfFactory)
	r.Register("allOrNone", AllOrNoneFactory)
	r.Register("fieldsAreEqual", FieldsAreEqualFactory)
	r.Register("fieldIsGreaterThanField", FieldIsGreaterThanFieldFactory)
	r.Register("fieldIsLessThanField", FieldIsLessThanFieldFactory)
}

// SumIsGreaterThanFactory creates a validator that checks if the sum of fields is greater than a value.
// Params:
//   - fields: slice of field names to sum
//   - value: threshold value
func SumIsGreaterThanFactory(params map[string]any) (validation.ValidatorFunc, error) {
	fields, err := getStringSliceParam(params, "fields")
	if err != nil {
		return nil, fmt.Errorf("sumIsGreaterThan: %w", err)
	}
	threshold, err := getNumericParam(params, "value")
	if err != nil {
		return nil, fmt.Errorf("sumIsGreaterThan: %w", err)
	}

	return func(ctx *validation.ValidationContext) *validation.ValidationResult {
		sum := sumFields(ctx, fields)
		if sum > threshold {
			return validation.ValidResult()
		}
		result := validation.AcquireResult()
		result.Valid = false
		result.ValidatorID = "sumIsGreaterThan"
		result.Category = ctx.Category
		result.Record = ctx.Record
		result.Schema = ctx.Schema
		result.FieldName = strings.Join(fields, ", ")
		return result
	}, nil
}

// SumIsLessThanFactory creates a validator that checks if the sum of fields is less than a value.
func SumIsLessThanFactory(params map[string]any) (validation.ValidatorFunc, error) {
	fields, err := getStringSliceParam(params, "fields")
	if err != nil {
		return nil, fmt.Errorf("sumIsLessThan: %w", err)
	}
	threshold, err := getNumericParam(params, "value")
	if err != nil {
		return nil, fmt.Errorf("sumIsLessThan: %w", err)
	}

	return func(ctx *validation.ValidationContext) *validation.ValidationResult {
		sum := sumFields(ctx, fields)
		if sum < threshold {
			return validation.ValidResult()
		}
		result := validation.AcquireResult()
		result.Valid = false
		result.ValidatorID = "sumIsLessThan"
		result.Category = ctx.Category
		result.Record = ctx.Record
		result.Schema = ctx.Schema
		result.FieldName = strings.Join(fields, ", ")
		return result
	}, nil
}

// SumEqualsFactory creates a validator that checks if the sum of fields equals a value.
func SumEqualsFactory(params map[string]any) (validation.ValidatorFunc, error) {
	fields, err := getStringSliceParam(params, "fields")
	if err != nil {
		return nil, fmt.Errorf("sumEquals: %w", err)
	}
	expected, err := getNumericParam(params, "value")
	if err != nil {
		return nil, fmt.Errorf("sumEquals: %w", err)
	}

	return func(ctx *validation.ValidationContext) *validation.ValidationResult {
		sum := sumFields(ctx, fields)
		if sum == expected {
			return validation.ValidResult()
		}
		result := validation.AcquireResult()
		result.Valid = false
		result.ValidatorID = "sumEquals"
		result.Category = ctx.Category
		result.Record = ctx.Record
		result.Schema = ctx.Schema
		result.FieldName = strings.Join(fields, ", ")
		return result
	}, nil
}

// AtLeastOneOfFactory creates a validator that checks if at least one of the fields has a value.
// Params:
//   - fields: slice of field names
func AtLeastOneOfFactory(params map[string]any) (validation.ValidatorFunc, error) {
	fields, err := getStringSliceParam(params, "fields")
	if err != nil {
		return nil, fmt.Errorf("atLeastOneOf: %w", err)
	}

	return func(ctx *validation.ValidationContext) *validation.ValidationResult {
		for _, fieldName := range fields {
			value := ctx.GetField(fieldName)
			if !isEmptyValue(value) {
				return validation.ValidResult()
			}
		}
		result := validation.AcquireResult()
		result.Valid = false
		result.ValidatorID = "atLeastOneOf"
		result.Category = ctx.Category
		result.Record = ctx.Record
		result.Schema = ctx.Schema
		result.FieldName = strings.Join(fields, ", ")
		return result
	}, nil
}

// ExactlyOneOfFactory creates a validator that checks if exactly one of the fields has a value.
func ExactlyOneOfFactory(params map[string]any) (validation.ValidatorFunc, error) {
	fields, err := getStringSliceParam(params, "fields")
	if err != nil {
		return nil, fmt.Errorf("exactlyOneOf: %w", err)
	}

	return func(ctx *validation.ValidationContext) *validation.ValidationResult {
		count := 0
		for _, fieldName := range fields {
			value := ctx.GetField(fieldName)
			if !isEmptyValue(value) {
				count++
			}
		}
		if count == 1 {
			return validation.ValidResult()
		}
		result := validation.AcquireResult()
		result.Valid = false
		result.ValidatorID = "exactlyOneOf"
		result.Category = ctx.Category
		result.Record = ctx.Record
		result.Schema = ctx.Schema
		result.FieldName = strings.Join(fields, ", ")
		return result
	}, nil
}

// AllOrNoneFactory creates a validator that checks if all fields have values or none do.
func AllOrNoneFactory(params map[string]any) (validation.ValidatorFunc, error) {
	fields, err := getStringSliceParam(params, "fields")
	if err != nil {
		return nil, fmt.Errorf("allOrNone: %w", err)
	}

	return func(ctx *validation.ValidationContext) *validation.ValidationResult {
		hasValue := 0
		isEmpty := 0
		for _, fieldName := range fields {
			value := ctx.GetField(fieldName)
			if isEmptyValue(value) {
				isEmpty++
			} else {
				hasValue++
			}
		}
		// Valid if all have values or all are empty
		if hasValue == 0 || isEmpty == 0 {
			return validation.ValidResult()
		}
		result := validation.AcquireResult()
		result.Valid = false
		result.ValidatorID = "allOrNone"
		result.Category = ctx.Category
		result.Record = ctx.Record
		result.Schema = ctx.Schema
		result.FieldName = strings.Join(fields, ", ")
		return result
	}, nil
}

// FieldsAreEqualFactory creates a validator that checks if two fields have equal values.
// Params:
//   - field1: first field name
//   - field2: second field name
func FieldsAreEqualFactory(params map[string]any) (validation.ValidatorFunc, error) {
	field1, ok := params["field1"].(string)
	if !ok {
		return nil, fmt.Errorf("fieldsAreEqual requires 'field1' parameter as string")
	}
	field2, ok := params["field2"].(string)
	if !ok {
		return nil, fmt.Errorf("fieldsAreEqual requires 'field2' parameter as string")
	}

	return func(ctx *validation.ValidationContext) *validation.ValidationResult {
		value1 := ctx.GetField(field1)
		value2 := ctx.GetField(field2)
		if compareValues(value1, value2) == 0 {
			return validation.ValidResult()
		}
		result := validation.AcquireResult()
		result.Valid = false
		result.ValidatorID = "fieldsAreEqual"
		result.Category = ctx.Category
		result.Record = ctx.Record
		result.Schema = ctx.Schema
		result.FieldName = field1 + ", " + field2
		return result
	}, nil
}

// FieldIsGreaterThanFieldFactory creates a validator that checks if one field is greater than another.
// Params:
//   - field1: field that should be greater
//   - field2: field to compare against
func FieldIsGreaterThanFieldFactory(params map[string]any) (validation.ValidatorFunc, error) {
	field1, ok := params["field1"].(string)
	if !ok {
		return nil, fmt.Errorf("fieldIsGreaterThanField requires 'field1' parameter as string")
	}
	field2, ok := params["field2"].(string)
	if !ok {
		return nil, fmt.Errorf("fieldIsGreaterThanField requires 'field2' parameter as string")
	}

	return func(ctx *validation.ValidationContext) *validation.ValidationResult {
		value1 := ctx.GetField(field1)
		value2 := ctx.GetField(field2)
		if compareValues(value1, value2) > 0 {
			return validation.ValidResult()
		}
		result := validation.AcquireResult()
		result.Valid = false
		result.ValidatorID = "fieldIsGreaterThanField"
		result.Category = ctx.Category
		result.Record = ctx.Record
		result.Schema = ctx.Schema
		result.FieldName = field1
		return result
	}, nil
}

// FieldIsLessThanFieldFactory creates a validator that checks if one field is less than another.
func FieldIsLessThanFieldFactory(params map[string]any) (validation.ValidatorFunc, error) {
	field1, ok := params["field1"].(string)
	if !ok {
		return nil, fmt.Errorf("fieldIsLessThanField requires 'field1' parameter as string")
	}
	field2, ok := params["field2"].(string)
	if !ok {
		return nil, fmt.Errorf("fieldIsLessThanField requires 'field2' parameter as string")
	}

	return func(ctx *validation.ValidationContext) *validation.ValidationResult {
		value1 := ctx.GetField(field1)
		value2 := ctx.GetField(field2)
		if compareValues(value1, value2) < 0 {
			return validation.ValidResult()
		}
		result := validation.AcquireResult()
		result.Valid = false
		result.ValidatorID = "fieldIsLessThanField"
		result.Category = ctx.Category
		result.Record = ctx.Record
		result.Schema = ctx.Schema
		result.FieldName = field1
		return result
	}, nil
}

// sumFields sums the numeric values of the given fields.
func sumFields(ctx *validation.ValidationContext, fields []string) float64 {
	var sum float64
	for _, fieldName := range fields {
		value := ctx.GetField(fieldName)
		if num, ok := toFloat64(value); ok {
			sum += num
		}
	}
	return sum
}

// getStringSliceParam extracts a string slice parameter from params.
func getStringSliceParam(params map[string]any, name string) ([]string, error) {
	v, ok := params[name]
	if !ok {
		return nil, fmt.Errorf("requires '%s' parameter", name)
	}

	switch val := v.(type) {
	case []string:
		return val, nil
	case []any:
		result := make([]string, len(val))
		for i, item := range val {
			s, ok := item.(string)
			if !ok {
				return nil, fmt.Errorf("'%s' must be a slice of strings", name)
			}
			result[i] = s
		}
		return result, nil
	default:
		return nil, fmt.Errorf("'%s' must be a slice of strings", name)
	}
}

// getNumericParam extracts a numeric parameter from params as float64.
func getNumericParam(params map[string]any, name string) (float64, error) {
	v, ok := params[name]
	if !ok {
		return 0, fmt.Errorf("requires '%s' parameter", name)
	}

	switch n := v.(type) {
	case int:
		return float64(n), nil
	case int64:
		return float64(n), nil
	case float64:
		return n, nil
	default:
		return 0, fmt.Errorf("'%s' must be a number", name)
	}
}
