package validation

import (
	"strconv"
	"strings"
)

var nativeRecordValidators = map[string]validationRule{
	"record_length_range":                         recordLengthRangeValidator{},
	"record_length_min":                           recordLengthMinValidator{},
	"record_has_valid_type":                       recordHasValidTypeValidator{},
	"case_number_not_empty":                       caseNumberNotEmptyValidator{},
	"rpt_month_year_is_valid":                     rptMonthYearValidator{},
	"calendar_quarter_is_valid":                   recordCalendarQuarterValidator{},
	"rpt_month_year_matches_header_year_quarter":  rptMonthYearMatchesHeaderYearQuarterValidator{},
	"exit_date_matches_fiscal_period":             exitDateMatchesFiscalPeriodValidator{},
	"amount_requires_positive":                    amountRequiresPositiveValidator{},
	"amount_requires_value_in":                    amountRequiresValueInValidator{},
	"start_before_end":                            startBeforeEndValidator{},
	"t1_sum_assistance_positive":                  t1SumAssistancePositiveValidator{},
	"ifthenalso_range_to_range":                   rangeToRangeSpec{},
	"ifthenalso_range_to_values":                  rangeToValuesSpec{valuesKey: "values"},
	"ifthenalso_range_to_not_values":              rangeToValuesSpec{valuesKey: "excluded_values", excludeValues: true},
	"t2_family_affil_2_3_education_level":         t2FamilyAffil23EducationLevelValidator{},
	"t2_family_affil_1_2_work_eligible":           t2FamilyAffil12WorkEligibleValidator{},
	"t2_family_affil_1_2_work_part_status":        t2FamilyAffil12WorkPartStatusValidator{},
	"tribal_t2_family_affil_1_2_work_part_status": tribalT2FamilyAffil12WorkPartStatusValidator{},
	"t2_work_eligible_1_5_work_part_not_99":       t2WorkEligible15WorkPartNot99Validator{},
	"t2_work_eligible_1_5_ssn_valid":              t2WorkEligible15SSNValidator{},
	"t2_work_eligible_11_age_relationship_hoh":    t2WorkEligible11AgeRelationshipHOHValidator{},
	"m1_sum_assistance_positive":                  m1SumAssistancePositiveValidator{},
	"m2_family_affil_1_2_work_part_status":        m2FamilyAffil12WorkPartStatusValidator{},
	"m2_family_affil_2_3_education_level":         m2FamilyAffil23EducationLevelValidator{},
	"m5_family_affil_1_3_education_level":         m5FamilyAffil13EducationLevelValidator{},
	"t5_age_oasdi":                                t5AgeOASDIValidator{},
	"sum_equals":                                  sumEqualsValidator{},
	"header_record_length":                        headerRecordLengthValidator{},
	"trailer_record_length":                       trailerRecordLengthValidator{},
	"header_tribe_fips_program_agree":             headerTribeFIPSProgramAgreeValidator{},
	"header_program_type_match":                   headerProgramTypeMatchValidator{},
	"header_section_match":                        headerSectionMatchValidator{},
	"header_fiscal_period_match":                  headerFiscalPeriodMatchValidator{},
}

type recordLengthRangeValidator struct {
	min int
	max int
}

func (v recordLengthRangeValidator) Compile(params validationParams) (ValidatorExecutor, error) {
	min, max, err := requiredIntRangeParams(params, "min", "max")
	return recordLengthRangeValidator{min: min, max: max}, err
}

func (v recordLengthRangeValidator) Execute(state *ValidationState) (ValidationOutcome, error) {
	return boolOutcome(state.RecordLength() >= v.min && state.RecordLength() <= v.max), nil
}

type recordLengthMinValidator struct {
	min int
}

func (v recordLengthMinValidator) Compile(params validationParams) (ValidatorExecutor, error) {
	min, err := requiredIntParam(params, "min")
	return recordLengthMinValidator{min: min}, err
}

func (v recordLengthMinValidator) Execute(state *ValidationState) (ValidationOutcome, error) {
	return boolOutcome(state.RecordLength() >= v.min), nil
}

type amountRequiresPositiveValidator struct {
	amountField   string
	requiredField string
}

func (v amountRequiresPositiveValidator) Compile(params validationParams) (ValidatorExecutor, error) {
	amountField, requiredField, err := requiredStringPairParams(params, "amount_field", "required_field")
	return amountRequiresPositiveValidator{amountField: amountField, requiredField: requiredField}, err
}

func (v amountRequiresPositiveValidator) Execute(state *ValidationState) (ValidationOutcome, error) {
	return boolOutcome(state.GetInt(v.amountField) <= 0 || state.GetInt(v.requiredField) > 0), nil
}

type amountRequiresValueInValidator struct {
	amountField   string
	requiredField string
	values        []any
}

func (v amountRequiresValueInValidator) Compile(params validationParams) (ValidatorExecutor, error) {
	amountField, requiredField, fieldErr := requiredStringPairParams(params, "amount_field", "required_field")
	values, valuesErr := requiredAnySliceParam(params, "values")
	return amountRequiresValueInValidator{
		amountField:   amountField,
		requiredField: requiredField,
		values:        values,
	}, firstError(fieldErr, valuesErr)
}

func (v amountRequiresValueInValidator) Execute(state *ValidationState) (ValidationOutcome, error) {
	return boolOutcome(state.GetInt(v.amountField) <= 0 || valueInAny(state.GetInt(v.requiredField), v.values)), nil
}

type sumEqualsValidator struct {
	totalField      string
	componentFields []any
}

func (v sumEqualsValidator) Compile(params validationParams) (ValidatorExecutor, error) {
	totalField, totalErr := requiredStringParam(params, "total_field")
	componentFields, fieldsErr := requiredAnySliceParam(params, "component_fields")
	return sumEqualsValidator{totalField: totalField, componentFields: componentFields}, firstError(totalErr, fieldsErr)
}

func (v sumEqualsValidator) Execute(state *ValidationState) (ValidationOutcome, error) {
	return boolOutcome(state.GetInt(v.totalField) == state.SumFields(v.componentFields)), nil
}

type recordHasValidTypeValidator struct{}

func (v recordHasValidTypeValidator) Compile(validationParams) (ValidatorExecutor, error) {
	return v, nil
}

func (v recordHasValidTypeValidator) Execute(state *ValidationState) (ValidationOutcome, error) {
	return boolOutcome(isNotBlank(state.Get("RecordType"))), nil
}

type caseNumberNotEmptyValidator struct{}

func (v caseNumberNotEmptyValidator) Compile(validationParams) (ValidatorExecutor, error) {
	return v, nil
}

func (v caseNumberNotEmptyValidator) Execute(state *ValidationState) (ValidationOutcome, error) {
	return boolOutcome(isNotBlank(state.GetString("CASE_NUMBER"))), nil
}

type startBeforeEndValidator struct{}

func (v startBeforeEndValidator) Compile(validationParams) (ValidatorExecutor, error) { return v, nil }

func (v startBeforeEndValidator) Execute(state *ValidationState) (ValidationOutcome, error) {
	end := state.GetString("END_DATE")
	return boolOutcome(state.GetString("START_DATE") <= end || isEmpty(end)), nil
}

type rptMonthYearValidator struct{}

func (v rptMonthYearValidator) Compile(validationParams) (ValidatorExecutor, error) { return v, nil }

func (v rptMonthYearValidator) Execute(state *ValidationState) (ValidationOutcome, error) {
	rptMonthYear := state.GetString("RPT_MONTH_YEAR")
	if len(rptMonthYear) < 6 {
		return boolOutcome(false), nil
	}
	year, yearOK := intFromAny(rptMonthYear[0:4])
	month, monthOK := intFromAny(strings.TrimPrefix(rptMonthYear[4:], "0"))
	return boolOutcome(yearOK && monthOK && year > 1900 && month > 0 && month < 13), nil
}

type recordCalendarQuarterValidator struct{}

func (v recordCalendarQuarterValidator) Compile(validationParams) (ValidatorExecutor, error) {
	return v, nil
}

func (v recordCalendarQuarterValidator) Execute(state *ValidationState) (ValidationOutcome, error) {
	calendarQuarter := state.GetString("CALENDAR_QUARTER")
	if len(calendarQuarter) != 5 || !isNumeric(calendarQuarter) {
		return boolOutcome(false), nil
	}
	year, yearOK := intFromAny(calendarQuarter[0:4])
	quarter, quarterOK := intFromAny(calendarQuarter[4:5])
	return boolOutcome(yearOK && quarterOK && year >= 2020 && quarter > 0 && quarter < 5), nil
}

type rptMonthYearMatchesHeaderYearQuarterValidator struct{}

func (v rptMonthYearMatchesHeaderYearQuarterValidator) Compile(validationParams) (ValidatorExecutor, error) {
	return v, nil
}

func (v rptMonthYearMatchesHeaderYearQuarterValidator) Execute(state *ValidationState) (ValidationOutcome, error) {
	if state == nil || state.DataFileContext == nil {
		return boolOutcome(false), nil
	}
	value := state.GetString("RPT_MONTH_YEAR")
	return boolOutcome(extractYear(value) == fiscalToCalendarYear(state.DataFileContext.FiscalYear, state.DataFileContext.FiscalQuarter) &&
		strconv.Itoa(extractQuarter(value)) == fiscalToCalendarQuarter(state.DataFileContext.FiscalYear, state.DataFileContext.FiscalQuarter)), nil
}

type exitDateMatchesFiscalPeriodValidator struct{}

func (v exitDateMatchesFiscalPeriodValidator) Compile(validationParams) (ValidatorExecutor, error) {
	return v, nil
}

func (v exitDateMatchesFiscalPeriodValidator) Execute(state *ValidationState) (ValidationOutcome, error) {
	if state == nil || state.DataFileContext == nil {
		return boolOutcome(false), nil
	}
	value := state.GetString("EXIT_DATE")
	return boolOutcome(extractYear(value) == fiscalToCalendarYear(state.DataFileContext.FiscalYear, state.DataFileContext.FiscalQuarter) &&
		strconv.Itoa(extractQuarter(value)) == fiscalToCalendarQuarter(state.DataFileContext.FiscalYear, state.DataFileContext.FiscalQuarter)), nil
}

type t1SumAssistancePositiveValidator struct{}

func (v t1SumAssistancePositiveValidator) Compile(validationParams) (ValidatorExecutor, error) {
	return v, nil
}

func (v t1SumAssistancePositiveValidator) Execute(state *ValidationState) (ValidationOutcome, error) {
	return boolOutcome(state.GetInt("AMT_FOOD_STAMP_ASSISTANCE")+
		state.GetInt("AMT_SUB_CC")+
		state.GetInt("CASH_AMOUNT")+
		state.GetInt("CC_AMOUNT")+
		state.GetInt("TRANSP_AMOUNT") > 0), nil
}

type t2FamilyAffil23EducationLevelValidator struct{}

func (v t2FamilyAffil23EducationLevelValidator) Compile(validationParams) (ValidatorExecutor, error) {
	return v, nil
}

func (v t2FamilyAffil23EducationLevelValidator) Execute(state *ValidationState) (ValidationOutcome, error) {
	if !intIn(state.GetInt("FAMILY_AFFILIATION"), 2, 3) {
		return boolOutcome(true), nil
	}
	educationLevel := state.GetInt("EDUCATION_LEVEL")
	return boolOutcome(intInRange(educationLevel, 0, 16) || intInRange(educationLevel, 98, 99)), nil
}

type t2FamilyAffil12WorkEligibleValidator struct{}

func (v t2FamilyAffil12WorkEligibleValidator) Compile(validationParams) (ValidatorExecutor, error) {
	return v, nil
}

func (v t2FamilyAffil12WorkEligibleValidator) Execute(state *ValidationState) (ValidationOutcome, error) {
	if !intIn(state.GetInt("FAMILY_AFFILIATION"), 1, 2) {
		return boolOutcome(true), nil
	}
	workEligibleIndicator := state.GetInt("WORK_ELIGIBLE_INDICATOR")
	return boolOutcome(intInRange(workEligibleIndicator, 1, 9) || intInRange(workEligibleIndicator, 11, 12)), nil
}

type t2FamilyAffil12WorkPartStatusValidator struct{}

func (v t2FamilyAffil12WorkPartStatusValidator) Compile(validationParams) (ValidatorExecutor, error) {
	return v, nil
}

func (v t2FamilyAffil12WorkPartStatusValidator) Execute(state *ValidationState) (ValidationOutcome, error) {
	return boolOutcome(!intIn(state.GetInt("FAMILY_AFFILIATION"), 1, 2) ||
		stringIn(state.GetString("WORK_PART_STATUS"), "01", "02", "05", "07", "09", "15", "17", "18", "19", "99")), nil
}

type tribalT2FamilyAffil12WorkPartStatusValidator struct{}

func (v tribalT2FamilyAffil12WorkPartStatusValidator) Compile(validationParams) (ValidatorExecutor, error) {
	return v, nil
}

func (v tribalT2FamilyAffil12WorkPartStatusValidator) Execute(state *ValidationState) (ValidationOutcome, error) {
	if !intIn(state.GetInt("FAMILY_AFFILIATION"), 1, 2) {
		return boolOutcome(true), nil
	}
	status := state.GetInt("WORK_PART_STATUS")
	return boolOutcome(intInRange(status, 1, 3) ||
		intInRange(status, 5, 9) ||
		intInRange(status, 11, 19) ||
		state.GetString("WORK_PART_STATUS") == "99"), nil
}

type t2WorkEligible15WorkPartNot99Validator struct{}

func (v t2WorkEligible15WorkPartNot99Validator) Compile(validationParams) (ValidatorExecutor, error) {
	return v, nil
}

func (v t2WorkEligible15WorkPartNot99Validator) Execute(state *ValidationState) (ValidationOutcome, error) {
	return boolOutcome(!intInRange(state.GetInt("WORK_ELIGIBLE_INDICATOR"), 1, 5) || state.GetString("WORK_PART_STATUS") != "99"), nil
}

type t2WorkEligible15SSNValidator struct{}

func (v t2WorkEligible15SSNValidator) Compile(validationParams) (ValidatorExecutor, error) {
	return v, nil
}

func (v t2WorkEligible15SSNValidator) Execute(state *ValidationState) (ValidationOutcome, error) {
	return boolOutcome(!intInRange(state.GetInt("WORK_ELIGIBLE_INDICATOR"), 1, 5) ||
		!stringIn(state.GetString("SSN"),
			"000000000", "111111111", "222222222", "333333333", "444444444",
			"555555555", "666666666", "777777777", "888888888", "999999999")), nil
}

type t2WorkEligible11AgeRelationshipHOHValidator struct{}

func (v t2WorkEligible11AgeRelationshipHOHValidator) Compile(validationParams) (ValidatorExecutor, error) {
	return v, nil
}

func (v t2WorkEligible11AgeRelationshipHOHValidator) Execute(state *ValidationState) (ValidationOutcome, error) {
	age := calculateAge(state.GetString("DATE_OF_BIRTH"), state.GetString("RPT_MONTH_YEAR"))
	return boolOutcome(state.GetString("WORK_ELIGIBLE_INDICATOR") != "11" ||
		age < 0 ||
		age >= 19 ||
		state.GetInt("RELATIONSHIP_HOH") != 1), nil
}

type m1SumAssistancePositiveValidator struct{}

func (v m1SumAssistancePositiveValidator) Compile(validationParams) (ValidatorExecutor, error) {
	return v, nil
}

func (v m1SumAssistancePositiveValidator) Execute(state *ValidationState) (ValidationOutcome, error) {
	return boolOutcome(state.GetInt("AMT_FOOD_STAMP_ASSISTANCE")+
		state.GetInt("AMT_SUB_CC")+
		state.GetInt("CASH_AMOUNT")+
		state.GetInt("CC_AMOUNT")+
		state.GetInt("CC_NBR_MONTHS") > 0), nil
}

type m2FamilyAffil12WorkPartStatusValidator struct{}

func (v m2FamilyAffil12WorkPartStatusValidator) Compile(validationParams) (ValidatorExecutor, error) {
	return v, nil
}

func (v m2FamilyAffil12WorkPartStatusValidator) Execute(state *ValidationState) (ValidationOutcome, error) {
	return boolOutcome(!intIn(state.GetInt("FAMILY_AFFILIATION"), 1, 2) ||
		stringIn(state.GetString("WORK_PART_STATUS"), "01", "02", "05", "07", "09", "15", "16", "17", "18", "99")), nil
}

type m2FamilyAffil23EducationLevelValidator struct{}

func (v m2FamilyAffil23EducationLevelValidator) Compile(validationParams) (ValidatorExecutor, error) {
	return v, nil
}

func (v m2FamilyAffil23EducationLevelValidator) Execute(state *ValidationState) (ValidationOutcome, error) {
	if !intIn(state.GetInt("FAMILY_AFFILIATION"), 2, 3) {
		return boolOutcome(true), nil
	}
	educationLevel := state.GetInt("EDUCATION_LEVEL")
	return boolOutcome(intInRange(educationLevel, 1, 16) || intInRange(educationLevel, 98, 99)), nil
}

type m5FamilyAffil13EducationLevelValidator struct{}

func (v m5FamilyAffil13EducationLevelValidator) Compile(validationParams) (ValidatorExecutor, error) {
	return v, nil
}

func (v m5FamilyAffil13EducationLevelValidator) Execute(state *ValidationState) (ValidationOutcome, error) {
	if !intInRange(state.GetInt("FAMILY_AFFILIATION"), 1, 3) {
		return boolOutcome(true), nil
	}
	educationLevel := state.GetInt("EDUCATION_LEVEL")
	return boolOutcome(intInRange(educationLevel, 1, 16) || intInRange(educationLevel, 98, 99)), nil
}

type t5AgeOASDIValidator struct{}

func (v t5AgeOASDIValidator) Compile(validationParams) (ValidatorExecutor, error) { return v, nil }

func (v t5AgeOASDIValidator) Execute(state *ValidationState) (ValidationOutcome, error) {
	return boolOutcome(calculateAge(state.GetString("DATE_OF_BIRTH"), state.GetString("RPT_MONTH_YEAR")) <= 18 ||
		intIn(state.GetInt("REC_OASDI_INSURANCE"), 1, 2)), nil
}

type headerRecordLengthValidator struct{}

func (v headerRecordLengthValidator) Compile(validationParams) (ValidatorExecutor, error) {
	return v, nil
}

func (v headerRecordLengthValidator) Execute(state *ValidationState) (ValidationOutcome, error) {
	return boolOutcome(state.RecordLength() == 23), nil
}

type trailerRecordLengthValidator struct{}

func (v trailerRecordLengthValidator) Compile(validationParams) (ValidatorExecutor, error) {
	return v, nil
}

func (v trailerRecordLengthValidator) Execute(state *ValidationState) (ValidationOutcome, error) {
	return boolOutcome(state.RecordLength() == 23), nil
}

type headerTribeFIPSProgramAgreeValidator struct{}

func (v headerTribeFIPSProgramAgreeValidator) Compile(validationParams) (ValidatorExecutor, error) {
	return v, nil
}

func (v headerTribeFIPSProgramAgreeValidator) Execute(state *ValidationState) (ValidationOutcome, error) {
	isTANWithEmptyFIPS := state.GetString("program_type") == "TAN" &&
		(isEmpty(state.GetString("state_fips")) || state.GetString("state_fips") == "00")
	hasTribeCode := !isTribeCodeEmpty(state.GetString("tribe_code"))
	return boolOutcome(isTANWithEmptyFIPS == hasTribeCode), nil
}

type headerProgramTypeMatchValidator struct{}

func (v headerProgramTypeMatchValidator) Compile(validationParams) (ValidatorExecutor, error) {
	return v, nil
}

func (v headerProgramTypeMatchValidator) Execute(state *ValidationState) (ValidationOutcome, error) {
	if state == nil || state.DataFileContext == nil {
		return boolOutcome(false), nil
	}
	tribeCodeEmpty := isTribeCodeEmpty(state.GetString("tribe_code"))
	return boolOutcome((!tribeCodeEmpty && state.DataFileContext.Program == "TRIBAL") ||
		(tribeCodeEmpty && state.DataFileContext.Program == state.GetString("program_type"))), nil
}

type headerSectionMatchValidator struct{}

func (v headerSectionMatchValidator) Compile(validationParams) (ValidatorExecutor, error) {
	return v, nil
}

func (v headerSectionMatchValidator) Execute(state *ValidationState) (ValidationOutcome, error) {
	if state == nil || state.DataFileContext == nil {
		return boolOutcome(false), nil
	}
	switch state.GetString("type") {
	case "A":
		return boolOutcome(state.DataFileContext.SectionName == "Active Case Data"), nil
	case "C":
		return boolOutcome(state.DataFileContext.SectionName == "Closed Case Data"), nil
	case "G":
		return boolOutcome(state.DataFileContext.SectionName == "Aggregate Data"), nil
	case "S":
		return boolOutcome(state.DataFileContext.SectionName == "Stratum Data"), nil
	default:
		return boolOutcome(false), nil
	}
}

type headerFiscalPeriodMatchValidator struct{}

func (v headerFiscalPeriodMatchValidator) Compile(validationParams) (ValidatorExecutor, error) {
	return v, nil
}

func (v headerFiscalPeriodMatchValidator) Execute(state *ValidationState) (ValidationOutcome, error) {
	if state == nil || state.DataFileContext == nil {
		return boolOutcome(false), nil
	}
	return boolOutcome(state.GetInt("year") == fiscalToCalendarYear(state.DataFileContext.FiscalYear, state.DataFileContext.FiscalQuarter) &&
		state.GetString("quarter") == fiscalToCalendarQuarter(state.DataFileContext.FiscalYear, state.DataFileContext.FiscalQuarter)), nil
}
