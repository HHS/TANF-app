package validation

import (
	"reflect"
	"strconv"
	"strings"
)

// intFromAny coerces supported numeric/string values to int.
func intFromAny(value any) (int, bool) {
	switch typed := value.(type) {
	case int:
		return typed, true
	case int8:
		return int(typed), true
	case int16:
		return int(typed), true
	case int32:
		return int(typed), true
	case int64:
		return int(typed), true
	case uint:
		return int(typed), true
	case uint8:
		return int(typed), true
	case uint16:
		return int(typed), true
	case uint32:
		return int(typed), true
	case uint64:
		return int(typed), true
	case float64:
		return int(typed), typed == float64(int(typed))
	case string:
		trimmed := strings.TrimSpace(typed)
		if trimmed == "" {
			return 0, false
		}
		parsed, err := strconv.Atoi(trimmed)
		return parsed, err == nil
	default:
		return 0, false
	}
}

// valueInAny checks equality against a heterogeneous value list.
func valueInAny(value any, values []any) bool {
	for _, candidate := range values {
		if anyEqual(value, candidate) {
			return true
		}
	}
	return false
}

// anyEqual compares values only when Go can do so safely.
func anyEqual(left any, right any) bool {
	if reflect.TypeOf(left) == nil || reflect.TypeOf(right) == nil {
		return left == right
	}
	if reflect.TypeOf(left) == reflect.TypeOf(right) && reflect.TypeOf(left).Comparable() {
		return left == right
	}
	return false
}

// intIn checks whether an integer matches one of the candidates.
func intIn(value int, values ...int) bool {
	for _, candidate := range values {
		if value == candidate {
			return true
		}
	}
	return false
}

// intInRange checks inclusive integer bounds.
func intInRange(value int, min int, max int) bool {
	return value >= min && value <= max
}

// stringIn checks whether a string matches one of the candidates.
func stringIn(value string, values ...string) bool {
	for _, candidate := range values {
		if value == candidate {
			return true
		}
	}
	return false
}
