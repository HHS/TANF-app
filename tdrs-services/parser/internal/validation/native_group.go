package validation

import "go-parser/internal/parser"

var nativeGroupValidators = map[string]validationRule{
	"max_records_per_case":                   maxRecordsPerCaseValidator{},
	"exact_duplicates":                       exactDuplicatesValidator{},
	"partial_duplicates":                     partialDuplicatesValidator{},
	"partial_duplicates_excluding":           partialDuplicatesExcludingValidator{},
	"federally_funded_ssn":                   federallyFundedSSNSpec{},
	"requires_related_record":                requiresRelatedRecordValidator{},
	"requires_related_record_with_int_value": requiresRelatedRecordWithIntValueValidator{},
}

type maxRecordsPerCaseValidator struct {
	maxRecords int
}

func (v maxRecordsPerCaseValidator) Compile(params validationParams) (ValidatorExecutor, error) {
	maxRecords, err := requiredIntParam(params, "max")
	return maxRecordsPerCaseValidator{maxRecords: maxRecords}, err
}

func (v maxRecordsPerCaseValidator) Execute(state *ValidationState) (ValidationOutcome, error) {
	return boolOutcome(groupStatsFromState(state).TotalRecords <= v.maxRecords), nil
}

type exactDuplicatesValidator struct {
	recordType string
}

func (v exactDuplicatesValidator) Compile(params validationParams) (ValidatorExecutor, error) {
	recordType, err := requiredStringParam(params, "record_type")
	return exactDuplicatesValidator{recordType: recordType}, err
}

func (v exactDuplicatesValidator) Execute(state *ValidationState) (ValidationOutcome, error) {
	if state == nil || state.Group == nil {
		return duplicateMatchesOutcome(nil), nil
	}
	return duplicateMatchesOutcome(getExactDuplicates(state.Group, v.recordType)), nil
}

type partialDuplicatesValidator struct {
	recordType string
	fields     []any
}

func (v partialDuplicatesValidator) Compile(params validationParams) (ValidatorExecutor, error) {
	recordType, recordErr := requiredStringParam(params, "record_type")
	fields, fieldsErr := requiredAnySliceParam(params, "fields")
	return partialDuplicatesValidator{recordType: recordType, fields: fields}, firstError(recordErr, fieldsErr)
}

func (v partialDuplicatesValidator) Execute(state *ValidationState) (ValidationOutcome, error) {
	if state == nil || state.Group == nil {
		return duplicateMatchesOutcome(nil), nil
	}
	return duplicateMatchesOutcome(getPartialDuplicates(state.Group, v.recordType, v.fields)), nil
}

type partialDuplicatesExcludingValidator struct {
	recordType    string
	fields        []any
	excludeField  string
	excludeValues []any
}

func (v partialDuplicatesExcludingValidator) Compile(params validationParams) (ValidatorExecutor, error) {
	recordType, recordErr := requiredStringParam(params, "record_type")
	fields, fieldsErr := requiredAnySliceParam(params, "fields")
	excludeField, excludeFieldErr := requiredStringParam(params, "exclude_field")
	excludeValues, excludeErr := requiredAnySliceParam(params, "exclude_values")
	return partialDuplicatesExcludingValidator{
		recordType:    recordType,
		fields:        fields,
		excludeField:  excludeField,
		excludeValues: excludeValues,
	}, firstError(recordErr, fieldsErr, excludeFieldErr, excludeErr)
}

func (v partialDuplicatesExcludingValidator) Execute(state *ValidationState) (ValidationOutcome, error) {
	if state == nil || state.Group == nil {
		return duplicateMatchesOutcome(nil), nil
	}
	return duplicateMatchesOutcome(getPartialDuplicatesExcluding(state.Group, v.recordType, v.fields, v.excludeField, v.excludeValues)), nil
}

type requiresRelatedRecordValidator struct {
	recordType         string
	relatedRecordTypes []string
}

func (v requiresRelatedRecordValidator) Compile(params validationParams) (ValidatorExecutor, error) {
	recordType, recordErr := requiredStringParam(params, "record_type")
	relatedRecordTypes, relatedErr := requiredStringSliceParam(params, "related_record_types")
	return requiresRelatedRecordValidator{
		recordType:         recordType,
		relatedRecordTypes: relatedRecordTypes,
	}, firstError(recordErr, relatedErr)
}

func (v requiresRelatedRecordValidator) Execute(state *ValidationState) (ValidationOutcome, error) {
	stats := groupStatsFromState(state)
	for _, relatedRecordType := range v.relatedRecordTypes {
		if stats.RecordCounts[relatedRecordType] > 0 {
			return recordsOutcome(nil), nil
		}
	}

	var records []*parser.ParsedRecord
	for _, rec := range recordsFromState(state) {
		if rec.GetRecordType() == v.recordType {
			records = append(records, rec)
		}
	}
	return recordsOutcome(records), nil
}

type requiresRelatedRecordWithIntValueValidator struct {
	recordType         string
	relatedRecordTypes []string
	fieldName          string
	expectedValue      int
}

func (v requiresRelatedRecordWithIntValueValidator) Compile(params validationParams) (ValidatorExecutor, error) {
	recordType, recordErr := requiredStringParam(params, "record_type")
	relatedRecordTypes, relatedErr := requiredStringSliceParam(params, "related_record_types")
	fieldName, fieldErr := requiredStringParam(params, "field_name")
	expectedValue, expectedErr := requiredIntParam(params, "expected_value")
	return requiresRelatedRecordWithIntValueValidator{
		recordType:         recordType,
		relatedRecordTypes: relatedRecordTypes,
		fieldName:          fieldName,
		expectedValue:      expectedValue,
	}, firstError(recordErr, relatedErr, fieldErr, expectedErr)
}

func (v requiresRelatedRecordWithIntValueValidator) Execute(state *ValidationState) (ValidationOutcome, error) {
	var records []*parser.ParsedRecord
	for _, rec := range recordsFromState(state) {
		if rec.GetRecordType() != v.recordType {
			continue
		}
		if !state.HasRelatedRecordWithInt(v.relatedRecordTypes, v.fieldName, v.expectedValue) {
			records = append(records, rec)
		}
	}
	return recordsOutcome(records), nil
}

// recordsFromState safely returns the group's records from validation state.
func recordsFromState(state *ValidationState) []*parser.ParsedRecord {
	if state == nil || state.Group == nil {
		return nil
	}
	return state.Group.Records
}

// groupHasRelatedRecordWithInt checks related records for a field integer value.
func groupHasRelatedRecordWithInt(group *parser.ParsedGroup, relatedRecordTypes []string, fieldName string, expectedValue int) bool {
	if group == nil {
		return false
	}
	for _, rec := range group.Records {
		if stringIn(rec.GetRecordType(), relatedRecordTypes...) && rec.GetInt(fieldName) == expectedValue {
			return true
		}
	}
	return false
}
