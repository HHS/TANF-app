package validation

import (
	"fmt"
	"reflect"
	"strconv"
	"strings"

	"go-parser/internal/parser"
)

type nativeFactory func(params map[string]any) (ValidatorExecutor, error)

var nativeFieldValidators = map[string]nativeFactory{
	"length":             compileFieldLength,
	"in_range_int":       compileFieldInRangeInt,
	"in_values":          compileFieldInValues,
	"equals":             compileFieldEquals,
	"not_empty":          fieldPredicate(isNotEmpty),
	"not_blank":          fieldPredicate(isNotBlank),
	"positive_value":     fieldPredicate(func(value any) bool { v, ok := intFromAny(value); return ok && v > 0 }),
	"not_negative":       fieldPredicate(func(value any) bool { v, ok := intFromAny(value); return ok && v >= 0 }),
	"valid_year":         fieldPredicate(func(value any) bool { return extractYear(value) >= 1900 }),
	"year_after_1998":    fieldPredicate(func(value any) bool { return extractYear(value) > 1998 }),
	"valid_day":          fieldPredicate(func(value any) bool { day := extractDay(value); return day >= 1 && day <= 31 }),
	"valid_month":        fieldPredicate(func(value any) bool { month := extractMonth(value); return month >= 1 && month <= 12 }),
	"valid_date":         fieldPredicate(isValidDate),
	"is_numeric":         fieldPredicate(func(value any) bool { return isNumeric(toString(value)) }),
	"is_alphanumeric":    fieldPredicate(func(value any) bool { return isAlphaNumeric(toString(value)) }),
	"in_values_or_blank": compileFieldInValuesOrBlank,
	"education_level": fieldPredicate(func(value any) bool {
		v, ok := intFromAny(value)
		return ok && (intInRange(v, 0, 16) || intInRange(v, 98, 99))
	}),
	"work_eligible_indicator": fieldPredicate(func(value any) bool {
		v, ok := intFromAny(value)
		return (ok && intInRange(v, 0, 9)) || toString(value) == "11" || toString(value) == "12"
	}),
	"validate_race":             fieldPredicate(func(value any) bool { v, ok := intFromAny(value); return isBlank(value) || (ok && intInRange(v, 0, 2)) }),
	"year_after_2019":           fieldPredicate(func(value any) bool { return extractYear(value) > 2019 }),
	"quarter_is_valid":          fieldPredicate(func(value any) bool { q := extractQuarter(value); return intInRange(q, 1, 4) }),
	"calendar_quarter_is_valid": fieldPredicate(validCalendarQuarterValue),
	"closure_reason":            fieldPredicate(func(value any) bool { v, ok := intFromAny(value); return ok && (intInRange(v, 1, 19) || v == 99) }),
	"education_level_no_zero": fieldPredicate(func(value any) bool {
		v, ok := intFromAny(value)
		return ok && (intInRange(v, 1, 16) || intInRange(v, 98, 99))
	}),
	"fra_ssn":                     fieldPredicate(isValidFRASSNValue),
	"tribal_closure_reason":       fieldPredicate(func(value any) bool { v, ok := intFromAny(value); return ok && (intInRange(v, 1, 18) || v == 99) }),
	"header_year_range":           fieldPredicate(func(value any) bool { v, ok := intFromAny(value); return ok && intInRange(v, 2000, 2099) }),
	"header_quarter":              fieldStringIn("1", "2", "3", "4"),
	"header_section_type":         fieldStringIn("A", "C", "G", "S"),
	"header_fips_code":            fieldPredicate(func(value any) bool { return isEmpty(value) || isValidFIPS(toString(value)) }),
	"header_tribe_code_range":     fieldPredicate(validHeaderTribeCodeRange),
	"header_program_type":         fieldStringIn("TAN", "SSP"),
	"header_edit_indicator":       fieldStringIn("1", "2"),
	"header_encryption_indicator": fieldStringIn(" ", "E", ""),
	"header_update_indicator":     fieldPredicate(func(value any) bool { return toString(value) == "D" }),
	"is_alphanumeric_or_space":    fieldPredicate(func(value any) bool { return isAlphaNumeric(toString(value)) || toString(value) == " " }),
}

var nativeRecordValidators = map[string]nativeFactory{
	"record_length_range":                        compileRecordLengthRange,
	"record_length_min":                          compileRecordLengthMin,
	"record_has_valid_type":                      recordPredicate(func(state *ValidationState) bool { return isNotBlank(state.Get("RecordType")) }),
	"case_number_not_empty":                      recordPredicate(func(state *ValidationState) bool { return isNotBlank(state.GetString("CASE_NUMBER")) }),
	"rpt_month_year_is_valid":                    recordPredicate(validRptMonthYear),
	"calendar_quarter_is_valid":                  recordPredicate(validRecordCalendarQuarter),
	"rpt_month_year_matches_header_year_quarter": recordPredicate(rptMonthYearMatchesHeaderYearQuarter),
	"exit_date_matches_fiscal_period":            recordPredicate(exitDateMatchesFiscalPeriod),
	"amount_requires_positive":                   compileAmountRequiresPositive,
	"amount_requires_value_in":                   compileAmountRequiresValueIn,
	"start_before_end": recordPredicate(func(state *ValidationState) bool {
		end := state.GetString("END_DATE")
		return state.GetString("START_DATE") <= end || isEmpty(end)
	}),
	"t1_sum_assistance_positive":                  recordPredicate(t1SumAssistancePositive),
	"ifthenalso_range_to_range":                   compileRangeToRange,
	"ifthenalso_range_to_values":                  compileRangeToValues,
	"ifthenalso_range_to_not_values":              compileRangeToNotValues,
	"t2_family_affil_2_3_education_level":         recordPredicate(t2FamilyAffil23EducationLevel),
	"t2_family_affil_1_2_work_eligible":           recordPredicate(t2FamilyAffil12WorkEligible),
	"t2_family_affil_1_2_work_part_status":        recordPredicate(t2FamilyAffil12WorkPartStatus),
	"tribal_t2_family_affil_1_2_work_part_status": recordPredicate(tribalT2FamilyAffil12WorkPartStatus),
	"t2_work_eligible_1_5_work_part_not_99": recordPredicate(func(state *ValidationState) bool {
		return !intInRange(state.GetInt("WORK_ELIGIBLE_INDICATOR"), 1, 5) || state.GetString("WORK_PART_STATUS") != "99"
	}),
	"t2_work_eligible_1_5_ssn_valid":           recordPredicate(t2WorkEligible15SSNValid),
	"t2_work_eligible_11_age_relationship_hoh": recordPredicate(t2WorkEligible11AgeRelationshipHOH),
	"m1_sum_assistance_positive":               recordPredicate(m1SumAssistancePositive),
	"m2_family_affil_1_2_work_part_status":     recordPredicate(m2FamilyAffil12WorkPartStatus),
	"m2_family_affil_2_3_education_level":      recordPredicate(m2FamilyAffil23EducationLevel),
	"m5_family_affil_1_3_education_level":      recordPredicate(m5FamilyAffil13EducationLevel),
	"t5_age_oasdi":                             recordPredicate(t5AgeOASDI),
	"sum_equals":                               compileSumEquals,
	"header_record_length":                     recordPredicate(func(state *ValidationState) bool { return state.RecordLength() == 23 }),
	"trailer_record_length":                    recordPredicate(func(state *ValidationState) bool { return state.RecordLength() == 23 }),
	"header_tribe_fips_program_agree":          recordPredicate(headerTribeFIPSProgramAgree),
	"header_program_type_match":                recordPredicate(headerProgramTypeMatch),
	"header_section_match":                     recordPredicate(headerSectionMatch),
	"header_fiscal_period_match":               recordPredicate(headerFiscalPeriodMatch),
}

var nativeGroupValidators = map[string]nativeFactory{
	"max_records_per_case":                   compileMaxRecordsPerCase,
	"exact_duplicates":                       compileExactDuplicates,
	"partial_duplicates":                     compilePartialDuplicates,
	"partial_duplicates_excluding":           compilePartialDuplicatesExcluding,
	"federally_funded_ssn":                   compileFederallyFundedSSN,
	"requires_related_record":                compileRequiresRelatedRecord,
	"requires_related_record_with_int_value": compileRequiresRelatedRecordWithIntValue,
}

// nativeExecutorFor resolves a native executor factory by validator scope and ID.
func nativeExecutorFor(scope string, id string, params map[string]any) (ValidatorExecutor, bool, error) {
	switch scope {
	case ScopeField:
		return nativeExecutorFromMap(nativeFieldValidators, id, params)
	case ScopeRecord:
		return nativeExecutorFromMap(nativeRecordValidators, id, params)
	case ScopeGroup:
		return nativeExecutorFromMap(nativeGroupValidators, id, params)
	default:
		return nil, false, nil
	}
}

// nativeExecutorFromMap compiles a mapped native factory with validator params.
func nativeExecutorFromMap(validators map[string]nativeFactory, id string, params map[string]any) (ValidatorExecutor, bool, error) {
	factory, ok := validators[id]
	if !ok {
		return nil, false, nil
	}
	executor, err := factory(params)
	return executor, true, err
}

// fieldPredicate adapts a field-value predicate into a native validator factory.
func fieldPredicate(fn func(value any) bool) nativeFactory {
	return func(map[string]any) (ValidatorExecutor, error) {
		return fieldPredicateExecutor(fn), nil
	}
}

// fieldStringIn builds a field validator that accepts only the provided strings.
func fieldStringIn(values ...string) nativeFactory {
	return fieldPredicate(func(value any) bool {
		return stringIn(toString(value), values...)
	})
}

// fieldPredicateExecutor runs a field predicate against ValidationState.Value.
func fieldPredicateExecutor(fn func(value any) bool) ValidatorExecutor {
	return ValidatorExecutorFunc(func(state *ValidationState) (ValidationOutcome, error) {
		if state == nil {
			return boolOutcome(fn(nil)), nil
		}
		return boolOutcome(fn(state.Value)), nil
	})
}

// recordPredicate adapts a record-state predicate into a native validator factory.
func recordPredicate(fn func(state *ValidationState) bool) nativeFactory {
	return func(map[string]any) (ValidatorExecutor, error) {
		return recordPredicateExecutor(fn), nil
	}
}

// recordPredicateExecutor normalizes a record predicate into a bool outcome.
func recordPredicateExecutor(fn func(state *ValidationState) bool) ValidatorExecutor {
	return ValidatorExecutorFunc(func(state *ValidationState) (ValidationOutcome, error) {
		return boolOutcome(fn(state)), nil
	})
}

// groupPredicateExecutor normalizes a group predicate into a bool outcome.
func groupPredicateExecutor(fn func(state *ValidationState) bool) ValidatorExecutor {
	return ValidatorExecutorFunc(func(state *ValidationState) (ValidationOutcome, error) {
		return boolOutcome(fn(state)), nil
	})
}

// groupRecordsExecutor converts invalid records into a per-record outcome.
func groupRecordsExecutor(fn func(state *ValidationState) []*parser.ParsedRecord) ValidatorExecutor {
	return ValidatorExecutorFunc(func(state *ValidationState) (ValidationOutcome, error) {
		return recordsOutcome(fn(state)), nil
	})
}

// groupDuplicateMatchesExecutor converts duplicate matches into a per-record outcome.
func groupDuplicateMatchesExecutor(fn func(state *ValidationState) []*DuplicateMatch) ValidatorExecutor {
	return ValidatorExecutorFunc(func(state *ValidationState) (ValidationOutcome, error) {
		return duplicateMatchesOutcome(fn(state)), nil
	})
}

// compileFieldLength validates that a field's string form has the configured length.
func compileFieldLength(params map[string]any) (ValidatorExecutor, error) {
	n, err := requiredIntParam(params, "n")
	return fieldPredicateExecutor(func(value any) bool { return len(toString(value)) == n }), err
}

// compileFieldInRangeInt validates that a field parses inside an integer range.
func compileFieldInRangeInt(params map[string]any) (ValidatorExecutor, error) {
	min, max, err := requiredIntRangeParams(params, "min", "max")
	return fieldPredicateExecutor(func(value any) bool {
		v, ok := intFromAny(value)
		return ok && v >= min && v <= max
	}), err
}

// compileFieldInValues validates that a field matches one configured value.
func compileFieldInValues(params map[string]any) (ValidatorExecutor, error) {
	values, err := requiredAnySliceParam(params, "values")
	return fieldPredicateExecutor(func(value any) bool { return valueInAny(value, values) }), err
}

// compileFieldEquals validates that a field equals the configured value.
func compileFieldEquals(params map[string]any) (ValidatorExecutor, error) {
	expected, err := requiredAnyParam(params, "value")
	return fieldPredicateExecutor(func(value any) bool { return anyEqual(value, expected) }), err
}

// compileFieldInValuesOrBlank allows blanks or one configured value.
func compileFieldInValuesOrBlank(params map[string]any) (ValidatorExecutor, error) {
	values, err := requiredAnySliceParam(params, "values")
	return fieldPredicateExecutor(func(value any) bool { return isBlank(value) || valueInAny(value, values) }), err
}

// compileRecordLengthRange validates decoded record length bounds.
func compileRecordLengthRange(params map[string]any) (ValidatorExecutor, error) {
	min, max, err := requiredIntRangeParams(params, "min", "max")
	return recordPredicateExecutor(func(state *ValidationState) bool { return state.RecordLength() >= min && state.RecordLength() <= max }), err
}

// compileRecordLengthMin validates a decoded record length minimum.
func compileRecordLengthMin(params map[string]any) (ValidatorExecutor, error) {
	min, err := requiredIntParam(params, "min")
	return recordPredicateExecutor(func(state *ValidationState) bool { return state.RecordLength() >= min }), err
}

// compileAmountRequiresPositive requires a related field when an amount is positive.
func compileAmountRequiresPositive(params map[string]any) (ValidatorExecutor, error) {
	amountField, requiredField, err := requiredStringPairParams(params, "amount_field", "required_field")
	return recordPredicateExecutor(func(state *ValidationState) bool {
		return state.GetInt(amountField) <= 0 || state.GetInt(requiredField) > 0
	}), err
}

// compileAmountRequiresValueIn restricts a related field when an amount is positive.
func compileAmountRequiresValueIn(params map[string]any) (ValidatorExecutor, error) {
	amountField, requiredField, fieldErr := requiredStringPairParams(params, "amount_field", "required_field")
	values, valuesErr := requiredAnySliceParam(params, "values")
	return recordPredicateExecutor(func(state *ValidationState) bool {
		return state.GetInt(amountField) <= 0 || valueInAny(state.GetInt(requiredField), values)
	}), firstError(fieldErr, valuesErr)
}

// compileRangeToRange builds an if-then validator from one range to another.
func compileRangeToRange(params map[string]any) (ValidatorExecutor, error) {
	spec, err := rangeToRangeSpecFromParams(params)
	return recordPredicateExecutor(spec.Valid), err
}

// compileRangeToValues builds an if-then validator from a range to allowed values.
func compileRangeToValues(params map[string]any) (ValidatorExecutor, error) {
	spec, err := rangeToValuesSpecFromParams(params, "values")
	return recordPredicateExecutor(spec.Valid), err
}

// compileRangeToNotValues builds an if-then validator from a range to disallowed values.
func compileRangeToNotValues(params map[string]any) (ValidatorExecutor, error) {
	spec, err := rangeToValuesSpecFromParams(params, "excluded_values")
	return recordPredicateExecutor(spec.ValidNot), err
}

// compileSumEquals validates that a total field equals configured component fields.
func compileSumEquals(params map[string]any) (ValidatorExecutor, error) {
	totalField, totalErr := requiredStringParam(params, "total_field")
	componentFields, fieldsErr := requiredAnySliceParam(params, "component_fields")
	return recordPredicateExecutor(func(state *ValidationState) bool {
		return state.GetInt(totalField) == state.SumFields(componentFields)
	}), firstError(totalErr, fieldsErr)
}

// compileMaxRecordsPerCase enforces the maximum records allowed in a group.
func compileMaxRecordsPerCase(params map[string]any) (ValidatorExecutor, error) {
	maxRecords, err := requiredIntParam(params, "max")
	return groupPredicateExecutor(func(state *ValidationState) bool {
		return groupStatsFromState(state).TotalRecords <= maxRecords
	}), err
}

// compileExactDuplicates reports exact duplicate records for a record type.
func compileExactDuplicates(params map[string]any) (ValidatorExecutor, error) {
	recordType, err := requiredStringParam(params, "record_type")
	return groupDuplicateMatchesExecutor(func(state *ValidationState) []*DuplicateMatch {
		if state == nil || state.Group == nil {
			return nil
		}
		return getExactDuplicates(state.Group, recordType)
	}), err
}

// compilePartialDuplicates reports duplicates across selected fields.
func compilePartialDuplicates(params map[string]any) (ValidatorExecutor, error) {
	recordType, recordErr := requiredStringParam(params, "record_type")
	fields, fieldsErr := requiredAnySliceParam(params, "fields")
	return groupDuplicateMatchesExecutor(func(state *ValidationState) []*DuplicateMatch {
		if state == nil || state.Group == nil {
			return nil
		}
		return getPartialDuplicates(state.Group, recordType, fields)
	}), firstError(recordErr, fieldsErr)
}

// compilePartialDuplicatesExcluding reports partial duplicates after exclusions.
func compilePartialDuplicatesExcluding(params map[string]any) (ValidatorExecutor, error) {
	recordType, recordErr := requiredStringParam(params, "record_type")
	fields, fieldsErr := requiredAnySliceParam(params, "fields")
	excludeField, excludeFieldErr := requiredStringParam(params, "exclude_field")
	excludeValues, excludeErr := requiredAnySliceParam(params, "exclude_values")
	return groupDuplicateMatchesExecutor(func(state *ValidationState) []*DuplicateMatch {
		if state == nil || state.Group == nil {
			return nil
		}
		return getPartialDuplicatesExcluding(state.Group, recordType, fields, excludeField, excludeValues)
	}), firstError(recordErr, fieldsErr, excludeFieldErr, excludeErr)
}

// compileFederallyFundedSSN reports federally funded records with invalid SSNs.
func compileFederallyFundedSSN(params map[string]any) (ValidatorExecutor, error) {
	spec, err := federallyFundedSSNSpecFromParams(params)
	return groupRecordsExecutor(spec.InvalidRecords), err
}

// compileRequiresRelatedRecord reports records missing any required related type.
func compileRequiresRelatedRecord(params map[string]any) (ValidatorExecutor, error) {
	recordType, recordErr := requiredStringParam(params, "record_type")
	relatedRecordTypes, relatedErr := requiredStringSliceParam(params, "related_record_types")
	return groupRecordsExecutor(func(state *ValidationState) []*parser.ParsedRecord {
		stats := groupStatsFromState(state)
		for _, relatedRecordType := range relatedRecordTypes {
			if stats.RecordCounts[relatedRecordType] > 0 {
				return nil
			}
		}
		var records []*parser.ParsedRecord
		for _, rec := range recordsFromState(state) {
			if rec.GetRecordType() == recordType {
				records = append(records, rec)
			}
		}
		return records
	}), firstError(recordErr, relatedErr)
}

// compileRequiresRelatedRecordWithIntValue reports records missing a typed related value.
func compileRequiresRelatedRecordWithIntValue(params map[string]any) (ValidatorExecutor, error) {
	recordType, recordErr := requiredStringParam(params, "record_type")
	relatedRecordTypes, relatedErr := requiredStringSliceParam(params, "related_record_types")
	fieldName, fieldErr := requiredStringParam(params, "field_name")
	expectedValue, expectedErr := requiredIntParam(params, "expected_value")
	return groupRecordsExecutor(func(state *ValidationState) []*parser.ParsedRecord {
		var records []*parser.ParsedRecord
		for _, rec := range recordsFromState(state) {
			if rec.GetRecordType() != recordType {
				continue
			}
			if !state.HasRelatedRecordWithInt(relatedRecordTypes, fieldName, expectedValue) {
				records = append(records, rec)
			}
		}
		return records
	}), firstError(recordErr, relatedErr, fieldErr, expectedErr)
}

// recordsFromState safely returns the group's records from validation state.
func recordsFromState(state *ValidationState) []*parser.ParsedRecord {
	if state == nil || state.Group == nil {
		return nil
	}
	return state.Group.Records
}

// validCalendarQuarterValue validates a compact year-quarter field value.
func validCalendarQuarterValue(value any) bool {
	s := toString(value)
	if len(s) != 5 {
		return false
	}
	q, ok := intFromAny(s[4:5])
	return ok && intInRange(q, 1, 4)
}

// isValidFRASSNValue validates FRA SSN formatting and blocked values.
func isValidFRASSNValue(value any) bool {
	s := toString(value)
	return isNumeric(s) &&
		len(s) == 9 &&
		s[0:3] != "000" &&
		s[0:3] != "666" &&
		s[3:5] != "00" &&
		s[5:9] != "0000"
}

// validHeaderTribeCodeRange accepts empty tribe codes or the configured range.
func validHeaderTribeCodeRange(value any) bool {
	if isTribeCodeEmpty(toString(value)) {
		return true
	}
	v, ok := intFromAny(value)
	return ok && intInRange(v, 0, 999)
}

// validRptMonthYear validates reporting month/year shape and bounds.
func validRptMonthYear(state *ValidationState) bool {
	rptMonthYear := state.GetString("RPT_MONTH_YEAR")
	if len(rptMonthYear) < 6 {
		return false
	}
	year, yearOK := intFromAny(rptMonthYear[0:4])
	month, monthOK := intFromAny(strings.TrimPrefix(rptMonthYear[4:], "0"))
	return yearOK && monthOK && year > 1900 && month > 0 && month < 13
}

// validRecordCalendarQuarter validates record-level calendar quarter values.
func validRecordCalendarQuarter(state *ValidationState) bool {
	calendarQuarter := state.GetString("CALENDAR_QUARTER")
	if len(calendarQuarter) != 5 || !isNumeric(calendarQuarter) {
		return false
	}
	year, yearOK := intFromAny(calendarQuarter[0:4])
	quarter, quarterOK := intFromAny(calendarQuarter[4:5])
	return yearOK && quarterOK && year >= 2020 && quarter > 0 && quarter < 5
}

// rptMonthYearMatchesHeaderYearQuarter compares reporting period to file context.
func rptMonthYearMatchesHeaderYearQuarter(state *ValidationState) bool {
	if state == nil || state.DataFileContext == nil {
		return false
	}
	value := state.GetString("RPT_MONTH_YEAR")
	return extractYear(value) == fiscalToCalendarYear(state.DataFileContext.FiscalYear, state.DataFileContext.FiscalQuarter) &&
		strconv.Itoa(extractQuarter(value)) == fiscalToCalendarQuarter(state.DataFileContext.FiscalYear, state.DataFileContext.FiscalQuarter)
}

// exitDateMatchesFiscalPeriod compares exit date to the file fiscal period.
func exitDateMatchesFiscalPeriod(state *ValidationState) bool {
	if state == nil || state.DataFileContext == nil {
		return false
	}
	value := state.GetString("EXIT_DATE")
	return extractYear(value) == fiscalToCalendarYear(state.DataFileContext.FiscalYear, state.DataFileContext.FiscalQuarter) &&
		strconv.Itoa(extractQuarter(value)) == fiscalToCalendarQuarter(state.DataFileContext.FiscalYear, state.DataFileContext.FiscalQuarter)
}

// t1SumAssistancePositive checks that T1 assistance components sum positive.
func t1SumAssistancePositive(state *ValidationState) bool {
	return state.GetInt("AMT_FOOD_STAMP_ASSISTANCE")+
		state.GetInt("AMT_SUB_CC")+
		state.GetInt("CASH_AMOUNT")+
		state.GetInt("CC_AMOUNT")+
		state.GetInt("TRANSP_AMOUNT") > 0
}

// t2FamilyAffil23EducationLevel validates education for T2 affiliation 2 or 3.
func t2FamilyAffil23EducationLevel(state *ValidationState) bool {
	if !intIn(state.GetInt("FAMILY_AFFILIATION"), 2, 3) {
		return true
	}
	educationLevel := state.GetInt("EDUCATION_LEVEL")
	return intInRange(educationLevel, 0, 16) || intInRange(educationLevel, 98, 99)
}

// t2FamilyAffil12WorkEligible validates work eligibility for T2 affiliation 1 or 2.
func t2FamilyAffil12WorkEligible(state *ValidationState) bool {
	if !intIn(state.GetInt("FAMILY_AFFILIATION"), 1, 2) {
		return true
	}
	wei := state.GetInt("WORK_ELIGIBLE_INDICATOR")
	return intInRange(wei, 1, 9) || intInRange(wei, 11, 12)
}

// t2FamilyAffil12WorkPartStatus validates T2 work participation status values.
func t2FamilyAffil12WorkPartStatus(state *ValidationState) bool {
	return !intIn(state.GetInt("FAMILY_AFFILIATION"), 1, 2) ||
		stringIn(state.GetString("WORK_PART_STATUS"), "01", "02", "05", "07", "09", "15", "17", "18", "19", "99")
}

// tribalT2FamilyAffil12WorkPartStatus validates tribal T2 work status values.
func tribalT2FamilyAffil12WorkPartStatus(state *ValidationState) bool {
	if !intIn(state.GetInt("FAMILY_AFFILIATION"), 1, 2) {
		return true
	}
	status := state.GetInt("WORK_PART_STATUS")
	return intInRange(status, 1, 3) || intInRange(status, 5, 9) || intInRange(status, 11, 19) || state.GetString("WORK_PART_STATUS") == "99"
}

// t2WorkEligible15SSNValid rejects blocked SSNs for work eligible values 1-5.
func t2WorkEligible15SSNValid(state *ValidationState) bool {
	return !intInRange(state.GetInt("WORK_ELIGIBLE_INDICATOR"), 1, 5) ||
		!stringIn(state.GetString("SSN"),
			"000000000", "111111111", "222222222", "333333333", "444444444",
			"555555555", "666666666", "777777777", "888888888", "999999999")
}

// t2WorkEligible11AgeRelationshipHOH validates age and relationship for code 11.
func t2WorkEligible11AgeRelationshipHOH(state *ValidationState) bool {
	age := calculateAge(state.GetString("DATE_OF_BIRTH"), state.GetString("RPT_MONTH_YEAR"))
	return state.GetString("WORK_ELIGIBLE_INDICATOR") != "11" || age < 0 || age >= 19 || state.GetInt("RELATIONSHIP_HOH") != 1
}

// m1SumAssistancePositive checks that M1 assistance components sum positive.
func m1SumAssistancePositive(state *ValidationState) bool {
	return state.GetInt("AMT_FOOD_STAMP_ASSISTANCE")+
		state.GetInt("AMT_SUB_CC")+
		state.GetInt("CASH_AMOUNT")+
		state.GetInt("CC_AMOUNT")+
		state.GetInt("CC_NBR_MONTHS") > 0
}

// m2FamilyAffil12WorkPartStatus validates M2 work participation status values.
func m2FamilyAffil12WorkPartStatus(state *ValidationState) bool {
	return !intIn(state.GetInt("FAMILY_AFFILIATION"), 1, 2) ||
		stringIn(state.GetString("WORK_PART_STATUS"), "01", "02", "05", "07", "09", "15", "16", "17", "18", "99")
}

// m2FamilyAffil23EducationLevel validates education for M2 affiliation 2 or 3.
func m2FamilyAffil23EducationLevel(state *ValidationState) bool {
	if !intIn(state.GetInt("FAMILY_AFFILIATION"), 2, 3) {
		return true
	}
	educationLevel := state.GetInt("EDUCATION_LEVEL")
	return intInRange(educationLevel, 1, 16) || intInRange(educationLevel, 98, 99)
}

// m5FamilyAffil13EducationLevel validates education for M5 affiliation 1-3.
func m5FamilyAffil13EducationLevel(state *ValidationState) bool {
	if !intInRange(state.GetInt("FAMILY_AFFILIATION"), 1, 3) {
		return true
	}
	educationLevel := state.GetInt("EDUCATION_LEVEL")
	return intInRange(educationLevel, 1, 16) || intInRange(educationLevel, 98, 99)
}

// t5AgeOASDI validates age-based OASDI insurance requirements.
func t5AgeOASDI(state *ValidationState) bool {
	return calculateAge(state.GetString("DATE_OF_BIRTH"), state.GetString("RPT_MONTH_YEAR")) <= 18 ||
		intIn(state.GetInt("REC_OASDI_INSURANCE"), 1, 2)
}

// headerTribeFIPSProgramAgree validates header tribe/FIPS/program consistency.
func headerTribeFIPSProgramAgree(state *ValidationState) bool {
	isTANWithEmptyFIPS := state.GetString("program_type") == "TAN" &&
		(isEmpty(state.GetString("state_fips")) || state.GetString("state_fips") == "00")
	hasTribeCode := !isTribeCodeEmpty(state.GetString("tribe_code"))
	return isTANWithEmptyFIPS == hasTribeCode
}

// headerProgramTypeMatch compares header program type to file context.
func headerProgramTypeMatch(state *ValidationState) bool {
	if state == nil || state.DataFileContext == nil {
		return false
	}
	tribeCodeEmpty := isTribeCodeEmpty(state.GetString("tribe_code"))
	return (!tribeCodeEmpty && state.DataFileContext.Program == "TRIBAL") ||
		(tribeCodeEmpty && state.DataFileContext.Program == state.GetString("program_type"))
}

// headerSectionMatch compares header section type to file context.
func headerSectionMatch(state *ValidationState) bool {
	if state == nil || state.DataFileContext == nil {
		return false
	}
	switch state.GetString("type") {
	case "A":
		return state.DataFileContext.SectionName == "Active Case Data"
	case "C":
		return state.DataFileContext.SectionName == "Closed Case Data"
	case "G":
		return state.DataFileContext.SectionName == "Aggregate Data"
	case "S":
		return state.DataFileContext.SectionName == "Stratum Data"
	default:
		return false
	}
}

// headerFiscalPeriodMatch compares header fiscal values to file context.
func headerFiscalPeriodMatch(state *ValidationState) bool {
	if state == nil || state.DataFileContext == nil {
		return false
	}
	return state.GetInt("year") == fiscalToCalendarYear(state.DataFileContext.FiscalYear, state.DataFileContext.FiscalQuarter) &&
		state.GetString("quarter") == fiscalToCalendarQuarter(state.DataFileContext.FiscalYear, state.DataFileContext.FiscalQuarter)
}

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
}

// rangeToValuesSpecFromParams extracts if-then value comparison settings.
func rangeToValuesSpecFromParams(params map[string]any, valuesKey string) (rangeToValuesSpec, error) {
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
	}, firstError(conditionFieldErr, conditionMinErr, conditionMaxErr, targetFieldErr, valuesErr)
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

// firstError returns the first non-nil error in order.
func firstError(errs ...error) error {
	for _, err := range errs {
		if err != nil {
			return err
		}
	}
	return nil
}
