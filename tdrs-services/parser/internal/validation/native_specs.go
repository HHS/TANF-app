package validation

import "go-parser/internal/parser"

type rangeToRangeSpec struct {
	conditionField string
	conditionMin   int
	conditionMax   int
	targetField    string
	targetMin      int
	targetMax      int
}

// rangeToRangeSpecFromParams extracts if-then range comparison settings.
func rangeToRangeSpecFromParams(params map[string]any) (rangeToRangeSpec, error) {
	conditionField, conditionFieldErr := requiredStringParam(params, "condition_field")
	conditionMin, conditionMinErr := requiredIntParam(params, "condition_min")
	conditionMax, conditionMaxErr := requiredIntParam(params, "condition_max")
	targetField, targetFieldErr := requiredStringParam(params, "target_field")
	targetMin, targetMinErr := requiredIntParam(params, "target_min")
	targetMax, targetMaxErr := requiredIntParam(params, "target_max")
	return rangeToRangeSpec{
		conditionField: conditionField,
		conditionMin:   conditionMin,
		conditionMax:   conditionMax,
		targetField:    targetField,
		targetMin:      targetMin,
		targetMax:      targetMax,
	}, firstError(conditionFieldErr, conditionMinErr, conditionMaxErr, targetFieldErr, targetMinErr, targetMaxErr)
}

func (s rangeToRangeSpec) Execute(state *ValidationState) (ValidationOutcome, error) {
	return boolOutcome(s.Valid(state)), nil
}

// Valid applies a conditional range requirement to the target field.
func (s rangeToRangeSpec) Valid(state *ValidationState) bool {
	condition := state.GetInt(s.conditionField)
	if condition < s.conditionMin || condition > s.conditionMax {
		return true
	}
	target := state.GetInt(s.targetField)
	return target >= s.targetMin && target <= s.targetMax
}

type rangeToValuesSpec struct {
	conditionField string
	conditionMin   int
	conditionMax   int
	targetField    string
	values         []any
	excludeValues  bool
}

// rangeToValuesSpecFromParams extracts if-then value comparison settings.
func rangeToValuesSpecFromParams(params map[string]any, valuesKey string, excludeValues bool) (rangeToValuesSpec, error) {
	conditionField, conditionFieldErr := requiredStringParam(params, "condition_field")
	conditionMin, conditionMinErr := requiredIntParam(params, "condition_min")
	conditionMax, conditionMaxErr := requiredIntParam(params, "condition_max")
	targetField, targetFieldErr := requiredStringParam(params, "target_field")
	values, valuesErr := requiredAnySliceParam(params, valuesKey)
	return rangeToValuesSpec{
		conditionField: conditionField,
		conditionMin:   conditionMin,
		conditionMax:   conditionMax,
		targetField:    targetField,
		values:         values,
		excludeValues:  excludeValues,
	}, firstError(conditionFieldErr, conditionMinErr, conditionMaxErr, targetFieldErr, valuesErr)
}

func (s rangeToValuesSpec) Execute(state *ValidationState) (ValidationOutcome, error) {
	if s.excludeValues {
		return boolOutcome(s.ValidNot(state)), nil
	}
	return boolOutcome(s.Valid(state)), nil
}

// Valid applies a conditional allowed-values requirement.
func (s rangeToValuesSpec) Valid(state *ValidationState) bool {
	condition := state.GetInt(s.conditionField)
	return condition < s.conditionMin || condition > s.conditionMax || valueInAny(state.GetInt(s.targetField), s.values)
}

// ValidNot applies a conditional disallowed-values requirement.
func (s rangeToValuesSpec) ValidNot(state *ValidationState) bool {
	condition := state.GetInt(s.conditionField)
	return condition < s.conditionMin || condition > s.conditionMax || !valueInAny(state.GetInt(s.targetField), s.values)
}

type federallyFundedSSNSpec struct {
	recipientRecordType    string
	familyAffiliationField string
	familyAffiliationValue int
	fundingRecordType      string
	fundingField           string
	fundingValue           int
	ssnField               string
}

// federallyFundedSSNSpecFromParams extracts federally funded SSN settings.
func federallyFundedSSNSpecFromParams(params map[string]any) (federallyFundedSSNSpec, error) {
	recipientRecordType, recipientErr := requiredStringParam(params, "recipient_record_type")
	familyAffiliationField, familyFieldErr := requiredStringParam(params, "family_affiliation_field")
	familyAffiliationValue, familyValueErr := requiredIntParam(params, "family_affiliation_value")
	fundingRecordType, fundingRecordErr := requiredStringParam(params, "funding_record_type")
	fundingField, fundingFieldErr := requiredStringParam(params, "funding_field")
	fundingValue, fundingValueErr := requiredIntParam(params, "funding_value")
	ssnField, ssnErr := requiredStringParam(params, "ssn_field")
	return federallyFundedSSNSpec{
		recipientRecordType:    recipientRecordType,
		familyAffiliationField: familyAffiliationField,
		familyAffiliationValue: familyAffiliationValue,
		fundingRecordType:      fundingRecordType,
		fundingField:           fundingField,
		fundingValue:           fundingValue,
		ssnField:               ssnField,
	}, firstError(recipientErr, familyFieldErr, familyValueErr, fundingRecordErr, fundingFieldErr, fundingValueErr, ssnErr)
}

func (s federallyFundedSSNSpec) Execute(state *ValidationState) (ValidationOutcome, error) {
	return recordsOutcome(s.InvalidRecords(state)), nil
}

// InvalidRecords returns recipient records with invalid federally funded SSNs.
func (s federallyFundedSSNSpec) InvalidRecords(state *ValidationState) []*parser.ParsedRecord {
	var records []*parser.ParsedRecord
	if state == nil || !state.HasAnyRecordOfTypeWithInt(s.fundingRecordType, s.fundingField, s.fundingValue) {
		return records
	}
	for _, rec := range state.RecordsOfType(s.recipientRecordType) {
		if rec.GetInt(s.familyAffiliationField) == s.familyAffiliationValue && !isValidSSN(rec.GetString(s.ssnField)) {
			records = append(records, rec)
		}
	}
	return records
}
