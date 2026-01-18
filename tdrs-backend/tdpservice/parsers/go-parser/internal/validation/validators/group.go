package validators

import (
	"fmt"
	"strings"

	"go-parser/internal/validation"
	"go-parser/internal/validation/registry"
	"go-parser/internal/worker"
)

// RegisterGroup registers all group-level (Cat 4) validators with the registry.
// These validators operate on groups of related records (e.g., a case with multiple record types).
func RegisterGroup(r *registry.ValidatorRegistry) {
	r.Register("recordTypePresent", RecordTypePresentFactory)
	r.Register("recordCountEquals", RecordCountEqualsFactory)
	r.Register("recordCountInRange", RecordCountInRangeFactory)
	r.Register("recordCountAtLeast", RecordCountAtLeastFactory)
	r.Register("recordCountAtMost", RecordCountAtMostFactory)
	r.Register("t1HasMatchingChildren", T1HasMatchingChildrenFactory)
	r.Register("parentRecordExists", ParentRecordExistsFactory)
	r.Register("childRecordsExist", ChildRecordsExistFactory)
	r.Register("uniqueFieldAcrossRecords", UniqueFieldAcrossRecordsFactory)
}

// RecordTypePresentFactory creates a validator that checks if a specific record type is present in the group.
// Params:
//   - record_type: the record type that must be present (e.g., "T1", "T2")
//   - required: whether the record type is required (default: true)
func RecordTypePresentFactory(params map[string]any) (validation.ValidatorFunc, error) {
	recordType, ok := params["record_type"].(string)
	if !ok {
		return nil, fmt.Errorf("recordTypePresent requires 'record_type' parameter as string")
	}

	required := true
	if v, ok := params["required"].(bool); ok {
		required = v
	}

	return func(ctx *validation.ValidationContext) *validation.ValidationResult {
		if ctx.Group == nil {
			if required {
				result := validation.AcquireResult()
				result.Valid = false
				result.ValidatorID = "recordTypePresent"
				result.Category = ctx.Category
				result.Group = ctx.Group
				return result
			}
			return validation.ValidResult()
		}

		// Check if record type exists in group
		for _, record := range ctx.Group.Records {
			if record.Schema != nil && record.Schema.RecordType == recordType {
				return validation.ValidResult()
			}
		}

		if !required {
			return validation.ValidResult()
		}

		result := validation.AcquireResult()
		result.Valid = false
		result.ValidatorID = "recordTypePresent"
		result.Category = ctx.Category
		result.Group = ctx.Group
		return result
	}, nil
}

// RecordCountEqualsFactory creates a validator that checks if the count of a record type equals a value.
// Params:
//   - record_type: the record type to count
//   - count: expected count
func RecordCountEqualsFactory(params map[string]any) (validation.ValidatorFunc, error) {
	recordType, ok := params["record_type"].(string)
	if !ok {
		return nil, fmt.Errorf("recordCountEquals requires 'record_type' parameter as string")
	}
	expectedCount, err := getIntParam(params, "count")
	if err != nil {
		return nil, fmt.Errorf("recordCountEquals: %w", err)
	}

	return func(ctx *validation.ValidationContext) *validation.ValidationResult {
		count := countRecordType(ctx.Group, recordType)
		if count == expectedCount {
			return validation.ValidResult()
		}
		result := validation.AcquireResult()
		result.Valid = false
		result.ValidatorID = "recordCountEquals"
		result.Category = ctx.Category
		result.Group = ctx.Group
		return result
	}, nil
}

// RecordCountInRangeFactory creates a validator that checks if the count of a record type is within a range.
// Params:
//   - record_type: the record type to count
//   - min: minimum count (inclusive)
//   - max: maximum count (inclusive)
func RecordCountInRangeFactory(params map[string]any) (validation.ValidatorFunc, error) {
	recordType, ok := params["record_type"].(string)
	if !ok {
		return nil, fmt.Errorf("recordCountInRange requires 'record_type' parameter as string")
	}
	min, err := getIntParam(params, "min")
	if err != nil {
		return nil, fmt.Errorf("recordCountInRange: %w", err)
	}
	max, err := getIntParam(params, "max")
	if err != nil {
		return nil, fmt.Errorf("recordCountInRange: %w", err)
	}

	return func(ctx *validation.ValidationContext) *validation.ValidationResult {
		count := countRecordType(ctx.Group, recordType)
		if count >= min && count <= max {
			return validation.ValidResult()
		}
		result := validation.AcquireResult()
		result.Valid = false
		result.ValidatorID = "recordCountInRange"
		result.Category = ctx.Category
		result.Group = ctx.Group
		return result
	}, nil
}

// RecordCountAtLeastFactory creates a validator that checks if the count of a record type is at least a value.
func RecordCountAtLeastFactory(params map[string]any) (validation.ValidatorFunc, error) {
	recordType, ok := params["record_type"].(string)
	if !ok {
		return nil, fmt.Errorf("recordCountAtLeast requires 'record_type' parameter as string")
	}
	min, err := getIntParam(params, "min")
	if err != nil {
		return nil, fmt.Errorf("recordCountAtLeast: %w", err)
	}

	return func(ctx *validation.ValidationContext) *validation.ValidationResult {
		count := countRecordType(ctx.Group, recordType)
		if count >= min {
			return validation.ValidResult()
		}
		result := validation.AcquireResult()
		result.Valid = false
		result.ValidatorID = "recordCountAtLeast"
		result.Category = ctx.Category
		result.Group = ctx.Group
		return result
	}, nil
}

// RecordCountAtMostFactory creates a validator that checks if the count of a record type is at most a value.
func RecordCountAtMostFactory(params map[string]any) (validation.ValidatorFunc, error) {
	recordType, ok := params["record_type"].(string)
	if !ok {
		return nil, fmt.Errorf("recordCountAtMost requires 'record_type' parameter as string")
	}
	max, err := getIntParam(params, "max")
	if err != nil {
		return nil, fmt.Errorf("recordCountAtMost: %w", err)
	}

	return func(ctx *validation.ValidationContext) *validation.ValidationResult {
		count := countRecordType(ctx.Group, recordType)
		if count <= max {
			return validation.ValidResult()
		}
		result := validation.AcquireResult()
		result.Valid = false
		result.ValidatorID = "recordCountAtMost"
		result.Category = ctx.Category
		result.Group = ctx.Group
		return result
	}, nil
}

// T1HasMatchingChildrenFactory creates a validator that checks if T1 records have matching child records.
// This is a TANF-specific validator for case consistency.
// Params:
//   - child_types: slice of child record types (e.g., ["T2", "T3"])
func T1HasMatchingChildrenFactory(params map[string]any) (validation.ValidatorFunc, error) {
	childTypes, err := getStringSliceParam(params, "child_types")
	if err != nil {
		return nil, fmt.Errorf("t1HasMatchingChildren: %w", err)
	}

	return func(ctx *validation.ValidationContext) *validation.ValidationResult {
		if ctx.Group == nil {
			result := validation.AcquireResult()
			result.Valid = false
			result.ValidatorID = "t1HasMatchingChildren"
			result.Category = ctx.Category
			result.Group = ctx.Group
			return result
		}

		// Check if there are any child records of the specified types
		hasChild := false
		for _, record := range ctx.Group.Records {
			if record.Schema == nil {
				continue
			}
			for _, childType := range childTypes {
				if record.Schema.RecordType == childType {
					hasChild = true
					break
				}
			}
			if hasChild {
				break
			}
		}

		if hasChild {
			return validation.ValidResult()
		}

		result := validation.AcquireResult()
		result.Valid = false
		result.ValidatorID = "t1HasMatchingChildren"
		result.Category = ctx.Category
		result.Group = ctx.Group
		return result
	}, nil
}

// ParentRecordExistsFactory creates a validator that checks if a parent record type exists for each child.
// Params:
//   - parent_type: the parent record type (e.g., "T1")
//   - child_type: the child record type (e.g., "T2")
func ParentRecordExistsFactory(params map[string]any) (validation.ValidatorFunc, error) {
	parentType, ok := params["parent_type"].(string)
	if !ok {
		return nil, fmt.Errorf("parentRecordExists requires 'parent_type' parameter as string")
	}
	childType, ok := params["child_type"].(string)
	if !ok {
		return nil, fmt.Errorf("parentRecordExists requires 'child_type' parameter as string")
	}

	return func(ctx *validation.ValidationContext) *validation.ValidationResult {
		if ctx.Group == nil {
			return validation.ValidResult()
		}

		hasParent := false
		hasChild := false

		for _, record := range ctx.Group.Records {
			if record.Schema == nil {
				continue
			}
			if record.Schema.RecordType == parentType {
				hasParent = true
			}
			if record.Schema.RecordType == childType {
				hasChild = true
			}
		}

		// If there are children, there must be a parent
		if hasChild && !hasParent {
			result := validation.AcquireResult()
			result.Valid = false
			result.ValidatorID = "parentRecordExists"
			result.Category = ctx.Category
			result.Group = ctx.Group
			return result
		}

		return validation.ValidResult()
	}, nil
}

// ChildRecordsExistFactory creates a validator that checks if child records exist for a parent.
// Params:
//   - parent_type: the parent record type
//   - child_types: slice of valid child record types
//   - required: whether at least one child is required (default: true)
func ChildRecordsExistFactory(params map[string]any) (validation.ValidatorFunc, error) {
	parentType, ok := params["parent_type"].(string)
	if !ok {
		return nil, fmt.Errorf("childRecordsExist requires 'parent_type' parameter as string")
	}
	childTypes, err := getStringSliceParam(params, "child_types")
	if err != nil {
		return nil, fmt.Errorf("childRecordsExist: %w", err)
	}

	required := true
	if v, ok := params["required"].(bool); ok {
		required = v
	}

	childTypeSet := make(map[string]bool)
	for _, t := range childTypes {
		childTypeSet[t] = true
	}

	return func(ctx *validation.ValidationContext) *validation.ValidationResult {
		if ctx.Group == nil {
			return validation.ValidResult()
		}

		hasParent := false
		hasChild := false

		for _, record := range ctx.Group.Records {
			if record.Schema == nil {
				continue
			}
			if record.Schema.RecordType == parentType {
				hasParent = true
			}
			if childTypeSet[record.Schema.RecordType] {
				hasChild = true
			}
		}

		// If there's a parent and it requires children
		if hasParent && required && !hasChild {
			result := validation.AcquireResult()
			result.Valid = false
			result.ValidatorID = "childRecordsExist"
			result.Category = ctx.Category
			result.Group = ctx.Group
			result.FieldName = strings.Join(childTypes, ", ")
			return result
		}

		return validation.ValidResult()
	}, nil
}

// UniqueFieldAcrossRecordsFactory creates a validator that checks if a field is unique across records.
// Params:
//   - record_type: the record type to check
//   - field: the field name that must be unique
func UniqueFieldAcrossRecordsFactory(params map[string]any) (validation.ValidatorFunc, error) {
	recordType, ok := params["record_type"].(string)
	if !ok {
		return nil, fmt.Errorf("uniqueFieldAcrossRecords requires 'record_type' parameter as string")
	}
	fieldName, ok := params["field"].(string)
	if !ok {
		return nil, fmt.Errorf("uniqueFieldAcrossRecords requires 'field' parameter as string")
	}

	return func(ctx *validation.ValidationContext) *validation.ValidationResult {
		if ctx.Group == nil {
			return validation.ValidResult()
		}

		seen := make(map[any]bool)
		for _, record := range ctx.Group.Records {
			if record.Schema == nil || record.Schema.RecordType != recordType {
				continue
			}
			value := record.Get(fieldName)
			if value == nil {
				continue
			}
			if seen[value] {
				result := validation.AcquireResult()
				result.Valid = false
				result.ValidatorID = "uniqueFieldAcrossRecords"
				result.Category = ctx.Category
				result.Group = ctx.Group
				result.FieldName = fieldName
				result.Record = record // The duplicate record
				return result
			}
			seen[value] = true
		}

		return validation.ValidResult()
	}, nil
}

// countRecordType counts records of a specific type in a group.
func countRecordType(group *worker.ParsedGroup, recordType string) int {
	if group == nil {
		return 0
	}
	count := 0
	for _, record := range group.Records {
		if record.Schema != nil && record.Schema.RecordType == recordType {
			count++
		}
	}
	return count
}
