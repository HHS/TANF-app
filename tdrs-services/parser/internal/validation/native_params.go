package validation

import "fmt"

// requiredAnyParam reads a required validator parameter.
func requiredAnyParam(params map[string]any, key string) (any, error) {
	value, ok := params[key]
	if !ok {
		return nil, fmt.Errorf("missing required param %q", key)
	}
	return value, nil
}

// requiredStringParam reads a required non-empty string parameter.
func requiredStringParam(params map[string]any, key string) (string, error) {
	value, err := requiredAnyParam(params, key)
	if err != nil {
		return "", err
	}
	stringValue, ok := value.(string)
	if !ok || stringValue == "" {
		return "", fmt.Errorf("param %q must be a non-empty string, got %T", key, value)
	}
	return stringValue, nil
}

// requiredStringPairParams reads two required string parameters.
func requiredStringPairParams(params map[string]any, firstKey string, secondKey string) (string, string, error) {
	first, firstErr := requiredStringParam(params, firstKey)
	second, secondErr := requiredStringParam(params, secondKey)
	return first, second, firstError(firstErr, secondErr)
}

// requiredIntParam reads a required integer-compatible parameter.
func requiredIntParam(params map[string]any, key string) (int, error) {
	value, err := requiredAnyParam(params, key)
	if err != nil {
		return 0, err
	}
	intValue, ok := intFromAny(value)
	if !ok {
		return 0, fmt.Errorf("param %q must be an integer, got %T", key, value)
	}
	return intValue, nil
}

// requiredIntRangeParams reads required minimum and maximum integer parameters.
func requiredIntRangeParams(params map[string]any, minKey string, maxKey string) (int, int, error) {
	min, minErr := requiredIntParam(params, minKey)
	max, maxErr := requiredIntParam(params, maxKey)
	return min, max, firstError(minErr, maxErr)
}

// requiredAnySliceParam reads a required array-like parameter.
func requiredAnySliceParam(params map[string]any, key string) ([]any, error) {
	value, err := requiredAnyParam(params, key)
	if err != nil {
		return nil, err
	}
	switch typed := value.(type) {
	case []any:
		return typed, nil
	case []string:
		values := make([]any, len(typed))
		for i, item := range typed {
			values[i] = item
		}
		return values, nil
	case []int:
		values := make([]any, len(typed))
		for i, item := range typed {
			values[i] = item
		}
		return values, nil
	default:
		return nil, fmt.Errorf("param %q must be an array, got %T", key, value)
	}
}

// requiredStringSliceParam reads a required string array parameter.
func requiredStringSliceParam(params map[string]any, key string) ([]string, error) {
	values, err := requiredAnySliceParam(params, key)
	if err != nil {
		return nil, err
	}
	result := make([]string, 0, len(values))
	for _, value := range values {
		stringValue, ok := value.(string)
		if !ok || stringValue == "" {
			return nil, fmt.Errorf("param %q must contain only non-empty strings, got %T", key, value)
		}
		result = append(result, stringValue)
	}
	return result, nil
}

// firstError returns the first non-nil error in order.
func firstError(errs ...error) error {
	for _, err := range errs {
		if err != nil {
			return err
		}
	}
	return nil
}
