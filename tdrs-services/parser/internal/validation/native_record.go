package validation

import (
	"strconv"
	"strings"
)

var nativeRecordValidators = map[string]nativeFactory{
	"record_length_range":                         compileRecordLengthRange,
	"record_length_min":                           compileRecordLengthMin,
	"record_has_valid_type":                       recordPredicate(recordHasValidType),
	"case_number_not_empty":                       recordPredicate(caseNumberNotEmpty),
	"rpt_month_year_is_valid":                     recordPredicate(validRptMonthYear),
	"calendar_quarter_is_valid":                   recordPredicate(validRecordCalendarQuarter),
	"rpt_month_year_matches_header_year_quarter":  recordPredicate(rptMonthYearMatchesHeaderYearQuarter),
	"exit_date_matches_fiscal_period":             recordPredicate(exitDateMatchesFiscalPeriod),
	"amount_requires_positive":                    compileAmountRequiresPositive,
	"amount_requires_value_in":                    compileAmountRequiresValueIn,
	"start_before_end":                            recordPredicate(startBeforeEnd),
	"t1_sum_assistance_positive":                  recordPredicate(t1SumAssistancePositive),
	"ifthenalso_range_to_range":                   compileRangeToRange,
	"ifthenalso_range_to_values":                  compileRangeToValues,
	"ifthenalso_range_to_not_values":              compileRangeToNotValues,
	"t2_family_affil_2_3_education_level":         recordPredicate(t2FamilyAffil23EducationLevel),
	"t2_family_affil_1_2_work_eligible":           recordPredicate(t2FamilyAffil12WorkEligible),
	"t2_family_affil_1_2_work_part_status":        recordPredicate(t2FamilyAffil12WorkPartStatus),
	"tribal_t2_family_affil_1_2_work_part_status": recordPredicate(tribalT2FamilyAffil12WorkPartStatus),
	"t2_work_eligible_1_5_work_part_not_99":       recordPredicate(t2WorkEligible15WorkPartNot99),
	"t2_work_eligible_1_5_ssn_valid":              recordPredicate(t2WorkEligible15SSNValid),
	"t2_work_eligible_11_age_relationship_hoh":    recordPredicate(t2WorkEligible11AgeRelationshipHOH),
	"m1_sum_assistance_positive":                  recordPredicate(m1SumAssistancePositive),
	"m2_family_affil_1_2_work_part_status":        recordPredicate(m2FamilyAffil12WorkPartStatus),
	"m2_family_affil_2_3_education_level":         recordPredicate(m2FamilyAffil23EducationLevel),
	"m5_family_affil_1_3_education_level":         recordPredicate(m5FamilyAffil13EducationLevel),
	"t5_age_oasdi":                                recordPredicate(t5AgeOASDI),
	"sum_equals":                                  compileSumEquals,
	"header_record_length":                        recordPredicate(headerRecordLength),
	"trailer_record_length":                       recordPredicate(trailerRecordLength),
	"header_tribe_fips_program_agree":             recordPredicate(headerTribeFIPSProgramAgree),
	"header_program_type_match":                   recordPredicate(headerProgramTypeMatch),
	"header_section_match":                        recordPredicate(headerSectionMatch),
	"header_fiscal_period_match":                  recordPredicate(headerFiscalPeriodMatch),
}

type recordLengthRangeValidator struct {
	min int
	max int
}

func (v recordLengthRangeValidator) Execute(state *ValidationState) (ValidationOutcome, error) {
	return boolOutcome(state.RecordLength() >= v.min && state.RecordLength() <= v.max), nil
}

// compileRecordLengthRange validates decoded record length bounds.
func compileRecordLengthRange(params map[string]any) (ValidatorExecutor, error) {
	min, max, err := requiredIntRangeParams(params, "min", "max")
	return recordLengthRangeValidator{min: min, max: max}, err
}

type recordLengthMinValidator struct {
	min int
}

func (v recordLengthMinValidator) Execute(state *ValidationState) (ValidationOutcome, error) {
	return boolOutcome(state.RecordLength() >= v.min), nil
}

// compileRecordLengthMin validates a decoded record length minimum.
func compileRecordLengthMin(params map[string]any) (ValidatorExecutor, error) {
	min, err := requiredIntParam(params, "min")
	return recordLengthMinValidator{min: min}, err
}

type amountRequiresPositiveValidator struct {
	amountField   string
	requiredField string
}

func (v amountRequiresPositiveValidator) Execute(state *ValidationState) (ValidationOutcome, error) {
	return boolOutcome(state.GetInt(v.amountField) <= 0 || state.GetInt(v.requiredField) > 0), nil
}

// compileAmountRequiresPositive requires a related field when an amount is positive.
func compileAmountRequiresPositive(params map[string]any) (ValidatorExecutor, error) {
	amountField, requiredField, err := requiredStringPairParams(params, "amount_field", "required_field")
	return amountRequiresPositiveValidator{amountField: amountField, requiredField: requiredField}, err
}

type amountRequiresValueInValidator struct {
	amountField   string
	requiredField string
	values        []any
}

func (v amountRequiresValueInValidator) Execute(state *ValidationState) (ValidationOutcome, error) {
	return boolOutcome(state.GetInt(v.amountField) <= 0 || valueInAny(state.GetInt(v.requiredField), v.values)), nil
}

// compileAmountRequiresValueIn restricts a related field when an amount is positive.
func compileAmountRequiresValueIn(params map[string]any) (ValidatorExecutor, error) {
	amountField, requiredField, fieldErr := requiredStringPairParams(params, "amount_field", "required_field")
	values, valuesErr := requiredAnySliceParam(params, "values")
	return amountRequiresValueInValidator{
		amountField:   amountField,
		requiredField: requiredField,
		values:        values,
	}, firstError(fieldErr, valuesErr)
}

type sumEqualsValidator struct {
	totalField      string
	componentFields []any
}

func (v sumEqualsValidator) Execute(state *ValidationState) (ValidationOutcome, error) {
	return boolOutcome(state.GetInt(v.totalField) == state.SumFields(v.componentFields)), nil
}

// compileSumEquals validates that a total field equals configured component fields.
func compileSumEquals(params map[string]any) (ValidatorExecutor, error) {
	totalField, totalErr := requiredStringParam(params, "total_field")
	componentFields, fieldsErr := requiredAnySliceParam(params, "component_fields")
	return sumEqualsValidator{totalField: totalField, componentFields: componentFields}, firstError(totalErr, fieldsErr)
}

// compileRangeToRange builds an if-then validator from one range to another.
func compileRangeToRange(params map[string]any) (ValidatorExecutor, error) {
	return rangeToRangeSpecFromParams(params)
}

// compileRangeToValues builds an if-then validator from a range to allowed values.
func compileRangeToValues(params map[string]any) (ValidatorExecutor, error) {
	return rangeToValuesSpecFromParams(params, "values", false)
}

// compileRangeToNotValues builds an if-then validator from a range to disallowed values.
func compileRangeToNotValues(params map[string]any) (ValidatorExecutor, error) {
	return rangeToValuesSpecFromParams(params, "excluded_values", true)
}

// recordHasValidType checks the parsed record type field is present.
func recordHasValidType(state *ValidationState) bool {
	return isNotBlank(state.Get("RecordType"))
}

// caseNumberNotEmpty checks that a record has a case number.
func caseNumberNotEmpty(state *ValidationState) bool {
	return isNotBlank(state.GetString("CASE_NUMBER"))
}

// startBeforeEnd permits empty end dates or start dates before the end date.
func startBeforeEnd(state *ValidationState) bool {
	end := state.GetString("END_DATE")
	return state.GetString("START_DATE") <= end || isEmpty(end)
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

// t2WorkEligible15WorkPartNot99 rejects work participation status 99 for eligibility 1 through 5.
func t2WorkEligible15WorkPartNot99(state *ValidationState) bool {
	return !intInRange(state.GetInt("WORK_ELIGIBLE_INDICATOR"), 1, 5) || state.GetString("WORK_PART_STATUS") != "99"
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

// headerRecordLength validates the fixed decoded header length.
func headerRecordLength(state *ValidationState) bool {
	return state.RecordLength() == 23
}

// trailerRecordLength validates the fixed decoded trailer length.
func trailerRecordLength(state *ValidationState) bool {
	return state.RecordLength() == 23
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
