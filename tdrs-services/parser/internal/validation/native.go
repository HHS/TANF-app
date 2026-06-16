package validation

import (
	"fmt"
	"reflect"
	"strconv"
	"strings"

	"go-parser/internal/parser"
)

func nativeExecutorFor(scope string, id string, params map[string]any) (NativeExecutor, bool, error) {
	switch scope {
	case ScopeField:
		return nativeFieldExecutor(id, params)
	case ScopeRecord:
		return nativeRecordExecutor(id, params)
	case ScopeGroup:
		return nativeGroupExecutor(id, params)
	default:
		return nil, false, nil
	}
}

func nativeFieldExecutor(id string, params map[string]any) (NativeExecutor, bool, error) {
	switch id {
	case "length":
		n, err := requiredIntParam(params, "n")
		return fieldBoolExecutor(func(value any) bool { return len(toString(value)) == n }), true, err
	case "in_range_int":
		min, max, err := requiredIntRangeParams(params, "min", "max")
		return fieldBoolExecutor(func(value any) bool {
			v, ok := intFromAny(value)
			return ok && v >= min && v <= max
		}), true, err
	case "in_values":
		values, err := requiredAnySliceParam(params, "values")
		return fieldBoolExecutor(func(value any) bool { return valueInAny(value, values) }), true, err
	case "equals":
		expected, err := requiredAnyParam(params, "value")
		return fieldBoolExecutor(func(value any) bool { return anyEqual(value, expected) }), true, err
	case "not_empty":
		return fieldBoolExecutor(isNotEmpty), true, nil
	case "not_blank":
		return fieldBoolExecutor(isNotBlank), true, nil
	case "positive_value":
		return fieldBoolExecutor(func(value any) bool {
			v, ok := intFromAny(value)
			return ok && v > 0
		}), true, nil
	case "not_negative":
		return fieldBoolExecutor(func(value any) bool {
			v, ok := intFromAny(value)
			return ok && v >= 0
		}), true, nil
	case "valid_year":
		return fieldBoolExecutor(func(value any) bool { return extractYear(value) >= 1900 }), true, nil
	case "year_after_1998":
		return fieldBoolExecutor(func(value any) bool { return extractYear(value) > 1998 }), true, nil
	case "valid_day":
		return fieldBoolExecutor(func(value any) bool {
			day := extractDay(value)
			return day >= 1 && day <= 31
		}), true, nil
	case "valid_month":
		return fieldBoolExecutor(func(value any) bool {
			month := extractMonth(value)
			return month >= 1 && month <= 12
		}), true, nil
	case "valid_date":
		return fieldBoolExecutor(isValidDate), true, nil
	case "is_numeric":
		return fieldBoolExecutor(func(value any) bool { return isNumeric(toString(value)) }), true, nil
	case "is_alphanumeric":
		return fieldBoolExecutor(func(value any) bool { return isAlphaNumeric(toString(value)) }), true, nil
	case "in_values_or_blank":
		values, err := requiredAnySliceParam(params, "values")
		return fieldBoolExecutor(func(value any) bool { return isBlank(value) || valueInAny(value, values) }), true, err
	case "education_level":
		return fieldBoolExecutor(func(value any) bool {
			v, ok := intFromAny(value)
			return ok && ((v >= 0 && v <= 16) || (v >= 98 && v <= 99))
		}), true, nil
	case "work_eligible_indicator":
		return fieldBoolExecutor(func(value any) bool {
			v, ok := intFromAny(value)
			return (ok && v >= 0 && v <= 9) || toString(value) == "11" || toString(value) == "12"
		}), true, nil
	case "validate_race":
		return fieldBoolExecutor(func(value any) bool {
			if isBlank(value) {
				return true
			}
			v, ok := intFromAny(value)
			return ok && v >= 0 && v <= 2
		}), true, nil
	case "year_after_2019":
		return fieldBoolExecutor(func(value any) bool { return extractYear(value) > 2019 }), true, nil
	case "quarter_is_valid":
		return fieldBoolExecutor(func(value any) bool {
			q := extractQuarter(value)
			return q >= 1 && q <= 4
		}), true, nil
	case "calendar_quarter_is_valid":
		return fieldBoolExecutor(func(value any) bool {
			s := toString(value)
			if len(s) != 5 {
				return false
			}
			q, ok := intFromAny(s[4:5])
			return ok && q >= 1 && q <= 4
		}), true, nil
	case "closure_reason":
		return fieldBoolExecutor(func(value any) bool {
			v, ok := intFromAny(value)
			return ok && ((v >= 1 && v <= 19) || v == 99)
		}), true, nil
	case "education_level_no_zero":
		return fieldBoolExecutor(func(value any) bool {
			v, ok := intFromAny(value)
			return ok && ((v >= 1 && v <= 16) || (v >= 98 && v <= 99))
		}), true, nil
	case "fra_ssn":
		return fieldBoolExecutor(func(value any) bool {
			s := toString(value)
			return isNumeric(s) &&
				len(s) == 9 &&
				s[0:3] != "000" &&
				s[0:3] != "666" &&
				s[3:5] != "00" &&
				s[5:9] != "0000"
		}), true, nil
	case "tribal_closure_reason":
		return fieldBoolExecutor(func(value any) bool {
			v, ok := intFromAny(value)
			return ok && ((v >= 1 && v <= 18) || v == 99)
		}), true, nil
	case "header_year_range":
		return fieldBoolExecutor(func(value any) bool {
			v, ok := intFromAny(value)
			return ok && v >= 2000 && v <= 2099
		}), true, nil
	case "header_quarter":
		return fieldStringInExecutor("1", "2", "3", "4"), true, nil
	case "header_section_type":
		return fieldStringInExecutor("A", "C", "G", "S"), true, nil
	case "header_fips_code":
		return fieldBoolExecutor(func(value any) bool { return isEmpty(value) || isValidFIPS(toString(value)) }), true, nil
	case "header_tribe_code_range":
		return fieldBoolExecutor(func(value any) bool {
			if isTribeCodeEmpty(toString(value)) {
				return true
			}
			v, ok := intFromAny(value)
			return ok && v >= 0 && v <= 999
		}), true, nil
	case "header_program_type":
		return fieldStringInExecutor("TAN", "SSP"), true, nil
	case "header_edit_indicator":
		return fieldStringInExecutor("1", "2"), true, nil
	case "header_encryption_indicator":
		return fieldStringInExecutor(" ", "E", ""), true, nil
	case "header_update_indicator":
		return fieldBoolExecutor(func(value any) bool { return toString(value) == "D" }), true, nil
	case "is_alphanumeric_or_space":
		return fieldBoolExecutor(func(value any) bool {
			return isAlphaNumeric(toString(value)) || toString(value) == " "
		}), true, nil
	default:
		return nil, false, nil
	}
}

func nativeRecordExecutor(id string, params map[string]any) (NativeExecutor, bool, error) {
	switch id {
	case "record_length_range":
		min, max, err := requiredIntRangeParams(params, "min", "max")
		return recordBoolExecutor(func(env *RecordEnv) bool { return env.RecordLength >= min && env.RecordLength <= max }), true, err
	case "record_length_min":
		min, err := requiredIntParam(params, "min")
		return recordBoolExecutor(func(env *RecordEnv) bool { return env.RecordLength >= min }), true, err
	case "record_has_valid_type":
		return recordBoolExecutor(func(env *RecordEnv) bool { return isNotBlank(env.Get("RecordType")) }), true, nil
	case "case_number_not_empty":
		return recordBoolExecutor(func(env *RecordEnv) bool { return isNotBlank(env.GetString("CASE_NUMBER")) }), true, nil
	case "rpt_month_year_is_valid":
		return recordBoolExecutor(func(env *RecordEnv) bool {
			rptMonthYear := env.GetString("RPT_MONTH_YEAR")
			if len(rptMonthYear) < 6 {
				return false
			}
			year, yearOK := intFromAny(rptMonthYear[0:4])
			month, monthOK := intFromAny(strings.TrimPrefix(rptMonthYear[4:], "0"))
			return yearOK && monthOK && year > 1900 && month > 0 && month < 13
		}), true, nil
	case "calendar_quarter_is_valid":
		return recordBoolExecutor(func(env *RecordEnv) bool {
			calendarQuarter := env.GetString("CALENDAR_QUARTER")
			if len(calendarQuarter) != 5 || !isNumeric(calendarQuarter) {
				return false
			}
			year, yearOK := intFromAny(calendarQuarter[0:4])
			quarter, quarterOK := intFromAny(calendarQuarter[4:5])
			return yearOK && quarterOK && year >= 2020 && quarter > 0 && quarter < 5
		}), true, nil
	case "rpt_month_year_matches_header_year_quarter":
		return recordBoolExecutor(func(env *RecordEnv) bool {
			if env.DataFileContext == nil {
				return false
			}
			value := env.GetString("RPT_MONTH_YEAR")
			return extractYear(value) == fiscalToCalendarYear(env.DataFileContext.FiscalYear, env.DataFileContext.FiscalQuarter) &&
				strconv.Itoa(extractQuarter(value)) == fiscalToCalendarQuarter(env.DataFileContext.FiscalYear, env.DataFileContext.FiscalQuarter)
		}), true, nil
	case "exit_date_matches_fiscal_period":
		return recordBoolExecutor(func(env *RecordEnv) bool {
			if env.DataFileContext == nil {
				return false
			}
			value := env.GetString("EXIT_DATE")
			return extractYear(value) == fiscalToCalendarYear(env.DataFileContext.FiscalYear, env.DataFileContext.FiscalQuarter) &&
				strconv.Itoa(extractQuarter(value)) == fiscalToCalendarQuarter(env.DataFileContext.FiscalYear, env.DataFileContext.FiscalQuarter)
		}), true, nil
	case "amount_requires_positive":
		amountField, requiredField, err := requiredStringPairParams(params, "amount_field", "required_field")
		return recordBoolExecutor(func(env *RecordEnv) bool {
			return env.GetInt(amountField) <= 0 || env.GetInt(requiredField) > 0
		}), true, err
	case "amount_requires_value_in":
		amountField, requiredField, err := requiredStringPairParams(params, "amount_field", "required_field")
		values, valuesErr := requiredAnySliceParam(params, "values")
		return recordBoolExecutor(func(env *RecordEnv) bool {
			return env.GetInt(amountField) <= 0 || valueInAny(env.GetInt(requiredField), values)
		}), true, firstError(err, valuesErr)
	case "start_before_end":
		return recordBoolExecutor(func(env *RecordEnv) bool {
			end := env.GetString("END_DATE")
			return env.GetString("START_DATE") <= end || isEmpty(end)
		}), true, nil
	case "t1_sum_assistance_positive":
		return recordBoolExecutor(func(env *RecordEnv) bool {
			return env.GetInt("AMT_FOOD_STAMP_ASSISTANCE")+
				env.GetInt("AMT_SUB_CC")+
				env.GetInt("CASH_AMOUNT")+
				env.GetInt("CC_AMOUNT")+
				env.GetInt("TRANSP_AMOUNT") > 0
		}), true, nil
	case "ifthenalso_range_to_range":
		spec, err := rangeToRangeSpecFromParams(params)
		return recordBoolExecutor(func(env *RecordEnv) bool {
			condition := env.GetInt(spec.conditionField)
			if condition < spec.conditionMin || condition > spec.conditionMax {
				return true
			}
			target := env.GetInt(spec.targetField)
			return target >= spec.targetMin && target <= spec.targetMax
		}), true, err
	case "ifthenalso_range_to_values":
		spec, err := rangeToValuesSpecFromParams(params, "values")
		return recordBoolExecutor(func(env *RecordEnv) bool {
			condition := env.GetInt(spec.conditionField)
			return condition < spec.conditionMin || condition > spec.conditionMax || valueInAny(env.GetInt(spec.targetField), spec.values)
		}), true, err
	case "ifthenalso_range_to_not_values":
		spec, err := rangeToValuesSpecFromParams(params, "excluded_values")
		return recordBoolExecutor(func(env *RecordEnv) bool {
			condition := env.GetInt(spec.conditionField)
			return condition < spec.conditionMin || condition > spec.conditionMax || !valueInAny(env.GetInt(spec.targetField), spec.values)
		}), true, err
	case "t2_family_affil_2_3_education_level":
		return recordBoolExecutor(func(env *RecordEnv) bool {
			if !intIn(env.GetInt("FAMILY_AFFILIATION"), 2, 3) {
				return true
			}
			educationLevel := env.GetInt("EDUCATION_LEVEL")
			return intInRange(educationLevel, 0, 16) || intInRange(educationLevel, 98, 99)
		}), true, nil
	case "t2_family_affil_1_2_work_eligible":
		return recordBoolExecutor(func(env *RecordEnv) bool {
			if !intIn(env.GetInt("FAMILY_AFFILIATION"), 1, 2) {
				return true
			}
			wei := env.GetInt("WORK_ELIGIBLE_INDICATOR")
			return intInRange(wei, 1, 9) || intInRange(wei, 11, 12)
		}), true, nil
	case "t2_family_affil_1_2_work_part_status":
		return recordBoolExecutor(func(env *RecordEnv) bool {
			return !intIn(env.GetInt("FAMILY_AFFILIATION"), 1, 2) ||
				stringIn(env.GetString("WORK_PART_STATUS"), "01", "02", "05", "07", "09", "15", "17", "18", "19", "99")
		}), true, nil
	case "tribal_t2_family_affil_1_2_work_part_status":
		return recordBoolExecutor(func(env *RecordEnv) bool {
			if !intIn(env.GetInt("FAMILY_AFFILIATION"), 1, 2) {
				return true
			}
			status := env.GetInt("WORK_PART_STATUS")
			return intInRange(status, 1, 3) || intInRange(status, 5, 9) || intInRange(status, 11, 19) || env.GetString("WORK_PART_STATUS") == "99"
		}), true, nil
	case "t2_work_eligible_1_5_work_part_not_99":
		return recordBoolExecutor(func(env *RecordEnv) bool {
			return !intInRange(env.GetInt("WORK_ELIGIBLE_INDICATOR"), 1, 5) || env.GetString("WORK_PART_STATUS") != "99"
		}), true, nil
	case "t2_work_eligible_1_5_ssn_valid":
		return recordBoolExecutor(func(env *RecordEnv) bool {
			return !intInRange(env.GetInt("WORK_ELIGIBLE_INDICATOR"), 1, 5) ||
				!stringIn(env.GetString("SSN"),
					"000000000", "111111111", "222222222", "333333333", "444444444",
					"555555555", "666666666", "777777777", "888888888", "999999999")
		}), true, nil
	case "t2_work_eligible_11_age_relationship_hoh":
		return recordBoolExecutor(func(env *RecordEnv) bool {
			age := calculateAge(env.GetString("DATE_OF_BIRTH"), env.GetString("RPT_MONTH_YEAR"))
			return env.GetString("WORK_ELIGIBLE_INDICATOR") != "11" || age < 0 || age >= 19 || env.GetInt("RELATIONSHIP_HOH") != 1
		}), true, nil
	case "m1_sum_assistance_positive":
		return recordBoolExecutor(func(env *RecordEnv) bool {
			return env.GetInt("AMT_FOOD_STAMP_ASSISTANCE")+
				env.GetInt("AMT_SUB_CC")+
				env.GetInt("CASH_AMOUNT")+
				env.GetInt("CC_AMOUNT")+
				env.GetInt("CC_NBR_MONTHS") > 0
		}), true, nil
	case "m2_family_affil_1_2_work_part_status":
		return recordBoolExecutor(func(env *RecordEnv) bool {
			return !intIn(env.GetInt("FAMILY_AFFILIATION"), 1, 2) ||
				stringIn(env.GetString("WORK_PART_STATUS"), "01", "02", "05", "07", "09", "15", "16", "17", "18", "99")
		}), true, nil
	case "m2_family_affil_2_3_education_level":
		return recordBoolExecutor(func(env *RecordEnv) bool {
			if !intIn(env.GetInt("FAMILY_AFFILIATION"), 2, 3) {
				return true
			}
			educationLevel := env.GetInt("EDUCATION_LEVEL")
			return intInRange(educationLevel, 1, 16) || intInRange(educationLevel, 98, 99)
		}), true, nil
	case "m5_family_affil_1_3_education_level":
		return recordBoolExecutor(func(env *RecordEnv) bool {
			if !intInRange(env.GetInt("FAMILY_AFFILIATION"), 1, 3) {
				return true
			}
			educationLevel := env.GetInt("EDUCATION_LEVEL")
			return intInRange(educationLevel, 1, 16) || intInRange(educationLevel, 98, 99)
		}), true, nil
	case "t5_age_oasdi":
		return recordBoolExecutor(func(env *RecordEnv) bool {
			return calculateAge(env.GetString("DATE_OF_BIRTH"), env.GetString("RPT_MONTH_YEAR")) <= 18 ||
				intIn(env.GetInt("REC_OASDI_INSURANCE"), 1, 2)
		}), true, nil
	case "sum_equals":
		totalField, err := requiredStringParam(params, "total_field")
		componentFields, fieldsErr := requiredAnySliceParam(params, "component_fields")
		return recordBoolExecutor(func(env *RecordEnv) bool {
			return env.GetInt(totalField) == env.SumFields(componentFields)
		}), true, firstError(err, fieldsErr)
	case "header_record_length", "trailer_record_length":
		return recordBoolExecutor(func(env *RecordEnv) bool { return env.RecordLength == 23 }), true, nil
	case "header_tribe_fips_program_agree":
		return recordBoolExecutor(func(env *RecordEnv) bool {
			isTANWithEmptyFIPS := env.GetString("program_type") == "TAN" &&
				(isEmpty(env.GetString("state_fips")) || env.GetString("state_fips") == "00")
			hasTribeCode := !isTribeCodeEmpty(env.GetString("tribe_code"))
			return isTANWithEmptyFIPS == hasTribeCode
		}), true, nil
	case "header_program_type_match":
		return recordBoolExecutor(func(env *RecordEnv) bool {
			if env.DataFileContext == nil {
				return false
			}
			tribeCodeEmpty := isTribeCodeEmpty(env.GetString("tribe_code"))
			return (!tribeCodeEmpty && env.DataFileContext.Program == "TRIBAL") ||
				(tribeCodeEmpty && env.DataFileContext.Program == env.GetString("program_type"))
		}), true, nil
	case "header_section_match":
		return recordBoolExecutor(func(env *RecordEnv) bool {
			if env.DataFileContext == nil {
				return false
			}
			switch env.GetString("type") {
			case "A":
				return env.DataFileContext.SectionName == "Active Case Data"
			case "C":
				return env.DataFileContext.SectionName == "Closed Case Data"
			case "G":
				return env.DataFileContext.SectionName == "Aggregate Data"
			case "S":
				return env.DataFileContext.SectionName == "Stratum Data"
			default:
				return false
			}
		}), true, nil
	case "header_fiscal_period_match":
		return recordBoolExecutor(func(env *RecordEnv) bool {
			if env.DataFileContext == nil {
				return false
			}
			return env.GetInt("year") == fiscalToCalendarYear(env.DataFileContext.FiscalYear, env.DataFileContext.FiscalQuarter) &&
				env.GetString("quarter") == fiscalToCalendarQuarter(env.DataFileContext.FiscalYear, env.DataFileContext.FiscalQuarter)
		}), true, nil
	default:
		return nil, false, nil
	}
}

func nativeGroupExecutor(id string, params map[string]any) (NativeExecutor, bool, error) {
	switch id {
	case "max_records_per_case":
		maxRecords, err := requiredIntParam(params, "max")
		return groupExecutor(func(env *GroupEnv) (any, error) { return env.TotalRecords <= maxRecords, nil }), true, err
	case "exact_duplicates":
		recordType, err := requiredStringParam(params, "record_type")
		return groupExecutor(func(env *GroupEnv) (any, error) { return getExactDuplicates(env.Group, recordType), nil }), true, err
	case "partial_duplicates":
		recordType, err := requiredStringParam(params, "record_type")
		fields, fieldsErr := requiredAnySliceParam(params, "fields")
		return groupExecutor(func(env *GroupEnv) (any, error) { return getPartialDuplicates(env.Group, recordType, fields), nil }), true, firstError(err, fieldsErr)
	case "partial_duplicates_excluding":
		recordType, err := requiredStringParam(params, "record_type")
		fields, fieldsErr := requiredAnySliceParam(params, "fields")
		excludeField, excludeFieldErr := requiredStringParam(params, "exclude_field")
		excludeValues, excludeErr := requiredAnySliceParam(params, "exclude_values")
		return groupExecutor(func(env *GroupEnv) (any, error) {
			return getPartialDuplicatesExcluding(env.Group, recordType, fields, excludeField, excludeValues), nil
		}), true, firstError(err, fieldsErr, excludeFieldErr, excludeErr)
	case "federally_funded_ssn":
		spec, err := federallyFundedSSNSpecFromParams(params)
		return groupExecutor(func(env *GroupEnv) (any, error) {
			var records []*parser.ParsedRecord
			if !hasAnyRecordOfTypeWithInt(env.Group, spec.fundingRecordType, spec.fundingField, spec.fundingValue) {
				return records, nil
			}
			for _, rec := range getRecordsOfType(env.Group, spec.recipientRecordType) {
				if rec.GetInt(spec.familyAffiliationField) == spec.familyAffiliationValue && !isValidSSN(rec.GetString(spec.ssnField)) {
					records = append(records, rec)
				}
			}
			return records, nil
		}), true, err
	case "requires_related_record":
		recordType, err := requiredStringParam(params, "record_type")
		relatedRecordTypes, relatedErr := requiredStringSliceParam(params, "related_record_types")
		return groupExecutor(func(env *GroupEnv) (any, error) {
			var records []*parser.ParsedRecord
			hasRelated := false
			for _, relatedRecordType := range relatedRecordTypes {
				if env.RecordCounts[relatedRecordType] > 0 {
					hasRelated = true
					break
				}
			}
			if hasRelated {
				return records, nil
			}
			for _, rec := range env.Group.Records {
				if rec.GetRecordType() == recordType {
					records = append(records, rec)
				}
			}
			return records, nil
		}), true, firstError(err, relatedErr)
	case "requires_related_record_with_int_value":
		recordType, err := requiredStringParam(params, "record_type")
		relatedRecordTypes, relatedErr := requiredStringSliceParam(params, "related_record_types")
		fieldName, fieldErr := requiredStringParam(params, "field_name")
		expectedValue, expectedErr := requiredIntParam(params, "expected_value")
		return groupExecutor(func(env *GroupEnv) (any, error) {
			var records []*parser.ParsedRecord
			for _, rec := range env.Group.Records {
				if rec.GetRecordType() != recordType {
					continue
				}
				if !groupHasRelatedRecordWithInt(env.Group, relatedRecordTypes, fieldName, expectedValue) {
					records = append(records, rec)
				}
			}
			return records, nil
		}), true, firstError(err, relatedErr, fieldErr, expectedErr)
	default:
		return nil, false, nil
	}
}

func fieldBoolExecutor(fn func(value any) bool) NativeExecutor {
	return func(env any) (any, error) {
		fieldEnv, ok := env.(*FieldEnv)
		if !ok {
			return nil, fmt.Errorf("expected *FieldEnv, got %T", env)
		}
		return fn(fieldEnv.Value), nil
	}
}

func fieldStringInExecutor(values ...string) NativeExecutor {
	return fieldBoolExecutor(func(value any) bool {
		return stringIn(toString(value), values...)
	})
}

func recordBoolExecutor(fn func(env *RecordEnv) bool) NativeExecutor {
	return func(env any) (any, error) {
		recordEnv, ok := env.(*RecordEnv)
		if !ok {
			return nil, fmt.Errorf("expected *RecordEnv, got %T", env)
		}
		return fn(recordEnv), nil
	}
}

func groupExecutor(fn func(env *GroupEnv) (any, error)) NativeExecutor {
	return func(env any) (any, error) {
		groupEnv, ok := env.(*GroupEnv)
		if !ok {
			return nil, fmt.Errorf("expected *GroupEnv, got %T", env)
		}
		return fn(groupEnv)
	}
}

type rangeToRangeSpec struct {
	conditionField string
	conditionMin   int
	conditionMax   int
	targetField    string
	targetMin      int
	targetMax      int
}

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

type rangeToValuesSpec struct {
	conditionField string
	conditionMin   int
	conditionMax   int
	targetField    string
	values         []any
}

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

type federallyFundedSSNSpec struct {
	recipientRecordType    string
	familyAffiliationField string
	familyAffiliationValue int
	fundingRecordType      string
	fundingField           string
	fundingValue           int
	ssnField               string
}

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

func groupHasRelatedRecordWithInt(group *parser.ParsedGroup, relatedRecordTypes []string, fieldName string, expectedValue int) bool {
	for _, rec := range group.Records {
		if stringIn(rec.GetRecordType(), relatedRecordTypes...) && rec.GetInt(fieldName) == expectedValue {
			return true
		}
	}
	return false
}

func requiredAnyParam(params map[string]any, key string) (any, error) {
	value, ok := params[key]
	if !ok {
		return nil, fmt.Errorf("missing required param %q", key)
	}
	return value, nil
}

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

func requiredStringPairParams(params map[string]any, firstKey string, secondKey string) (string, string, error) {
	first, firstErr := requiredStringParam(params, firstKey)
	second, secondErr := requiredStringParam(params, secondKey)
	return first, second, firstError(firstErr, secondErr)
}

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

func requiredIntRangeParams(params map[string]any, minKey string, maxKey string) (int, int, error) {
	min, minErr := requiredIntParam(params, minKey)
	max, maxErr := requiredIntParam(params, maxKey)
	return min, max, firstError(minErr, maxErr)
}

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

func valueInAny(value any, values []any) bool {
	for _, candidate := range values {
		if anyEqual(value, candidate) {
			return true
		}
	}
	return false
}

func anyEqual(left any, right any) bool {
	if reflect.TypeOf(left) == nil || reflect.TypeOf(right) == nil {
		return left == right
	}
	if reflect.TypeOf(left) == reflect.TypeOf(right) && reflect.TypeOf(left).Comparable() {
		return left == right
	}
	return false
}

func intIn(value int, values ...int) bool {
	for _, candidate := range values {
		if value == candidate {
			return true
		}
	}
	return false
}

func intInRange(value int, min int, max int) bool {
	return value >= min && value <= max
}

func stringIn(value string, values ...string) bool {
	for _, candidate := range values {
		if value == candidate {
			return true
		}
	}
	return false
}

func firstError(errs ...error) error {
	for _, err := range errs {
		if err != nil {
			return err
		}
	}
	return nil
}
