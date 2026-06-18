package validation

var nativeFieldValidators = map[string]nativeFactory{
	"length":                      compileFieldLength,
	"in_range_int":                compileFieldInRangeInt,
	"in_values":                   compileFieldInValues,
	"equals":                      compileFieldEquals,
	"not_empty":                   fieldPredicate(isNotEmpty),
	"not_blank":                   fieldPredicate(isNotBlank),
	"positive_value":              fieldPredicate(validPositiveValue),
	"not_negative":                fieldPredicate(validNotNegative),
	"valid_year":                  fieldPredicate(validYearValue),
	"year_after_1998":             fieldPredicate(yearAfter1998),
	"valid_day":                   fieldPredicate(validDayValue),
	"valid_month":                 fieldPredicate(validMonthValue),
	"valid_date":                  fieldPredicate(isValidDate),
	"is_numeric":                  fieldPredicate(numericValue),
	"is_alphanumeric":             fieldPredicate(alphanumericValue),
	"in_values_or_blank":          compileFieldInValuesOrBlank,
	"education_level":             fieldPredicate(validEducationLevel),
	"work_eligible_indicator":     fieldPredicate(validWorkEligibleIndicator),
	"validate_race":               fieldPredicate(validRaceValue),
	"year_after_2019":             fieldPredicate(yearAfter2019),
	"quarter_is_valid":            fieldPredicate(validQuarterValue),
	"calendar_quarter_is_valid":   fieldPredicate(validCalendarQuarterValue),
	"closure_reason":              fieldPredicate(validClosureReason),
	"education_level_no_zero":     fieldPredicate(validEducationLevelNoZero),
	"fra_ssn":                     fieldPredicate(isValidFRASSNValue),
	"tribal_closure_reason":       fieldPredicate(validTribalClosureReason),
	"header_year_range":           fieldPredicate(validHeaderYearRange),
	"header_quarter":              fieldStringIn("1", "2", "3", "4"),
	"header_section_type":         fieldStringIn("A", "C", "G", "S"),
	"header_fips_code":            fieldPredicate(validHeaderFIPSCode),
	"header_tribe_code_range":     fieldPredicate(validHeaderTribeCodeRange),
	"header_program_type":         fieldStringIn("TAN", "SSP"),
	"header_edit_indicator":       fieldStringIn("1", "2"),
	"header_encryption_indicator": fieldStringIn(" ", "E", ""),
	"header_update_indicator":     fieldPredicate(validHeaderUpdateIndicator),
	"is_alphanumeric_or_space":    fieldPredicate(alphanumericOrSpaceValue),
}

// fieldStringIn builds a field validator that accepts only the provided strings.
func fieldStringIn(values ...string) nativeFactory {
	allowedValues := append([]string(nil), values...)
	return func(map[string]any) (ValidatorExecutor, error) {
		return fieldStringSetValidator{allowedValues: allowedValues}, nil
	}
}

type fieldStringSetValidator struct {
	allowedValues []string
}

func (v fieldStringSetValidator) Execute(state *ValidationState) (ValidationOutcome, error) {
	return boolOutcome(stringIn(toString(fieldValueFromState(state)), v.allowedValues...)), nil
}

type fieldLengthValidator struct {
	n int
}

func (v fieldLengthValidator) Execute(state *ValidationState) (ValidationOutcome, error) {
	return boolOutcome(len(toString(fieldValueFromState(state))) == v.n), nil
}

// compileFieldLength validates that a field's string form has the configured length.
func compileFieldLength(params map[string]any) (ValidatorExecutor, error) {
	n, err := requiredIntParam(params, "n")
	return fieldLengthValidator{n: n}, err
}

type fieldInRangeIntValidator struct {
	min int
	max int
}

func (v fieldInRangeIntValidator) Execute(state *ValidationState) (ValidationOutcome, error) {
	value, ok := intFromAny(fieldValueFromState(state))
	return boolOutcome(ok && value >= v.min && value <= v.max), nil
}

// compileFieldInRangeInt validates that a field parses inside an integer range.
func compileFieldInRangeInt(params map[string]any) (ValidatorExecutor, error) {
	min, max, err := requiredIntRangeParams(params, "min", "max")
	return fieldInRangeIntValidator{min: min, max: max}, err
}

type fieldInValuesValidator struct {
	values []any
}

func (v fieldInValuesValidator) Execute(state *ValidationState) (ValidationOutcome, error) {
	return boolOutcome(valueInAny(fieldValueFromState(state), v.values)), nil
}

// compileFieldInValues validates that a field matches one configured value.
func compileFieldInValues(params map[string]any) (ValidatorExecutor, error) {
	values, err := requiredAnySliceParam(params, "values")
	return fieldInValuesValidator{values: values}, err
}

type fieldEqualsValidator struct {
	expected any
}

func (v fieldEqualsValidator) Execute(state *ValidationState) (ValidationOutcome, error) {
	return boolOutcome(anyEqual(fieldValueFromState(state), v.expected)), nil
}

// compileFieldEquals validates that a field equals the configured value.
func compileFieldEquals(params map[string]any) (ValidatorExecutor, error) {
	expected, err := requiredAnyParam(params, "value")
	return fieldEqualsValidator{expected: expected}, err
}

type fieldInValuesOrBlankValidator struct {
	values []any
}

func (v fieldInValuesOrBlankValidator) Execute(state *ValidationState) (ValidationOutcome, error) {
	value := fieldValueFromState(state)
	return boolOutcome(isBlank(value) || valueInAny(value, v.values)), nil
}

// compileFieldInValuesOrBlank allows blanks or one configured value.
func compileFieldInValuesOrBlank(params map[string]any) (ValidatorExecutor, error) {
	values, err := requiredAnySliceParam(params, "values")
	return fieldInValuesOrBlankValidator{values: values}, err
}

// fieldValueFromState safely returns the field value from validation state.
func fieldValueFromState(state *ValidationState) any {
	if state == nil {
		return nil
	}
	return state.Value
}

// validPositiveValue accepts integer-compatible values greater than zero.
func validPositiveValue(value any) bool {
	v, ok := intFromAny(value)
	return ok && v > 0
}

// validNotNegative accepts integer-compatible values at or above zero.
func validNotNegative(value any) bool {
	v, ok := intFromAny(value)
	return ok && v >= 0
}

// validYearValue accepts date-like values whose extracted year is at least 1900.
func validYearValue(value any) bool {
	return extractYear(value) >= 1900
}

// yearAfter1998 accepts date-like values after calendar year 1998.
func yearAfter1998(value any) bool {
	return extractYear(value) > 1998
}

// validDayValue accepts date-like values with day 1 through 31.
func validDayValue(value any) bool {
	day := extractDay(value)
	return day >= 1 && day <= 31
}

// validMonthValue accepts date-like values with month 1 through 12.
func validMonthValue(value any) bool {
	month := extractMonth(value)
	return month >= 1 && month <= 12
}

// numericValue accepts string forms containing only digits.
func numericValue(value any) bool {
	return isNumeric(toString(value))
}

// alphanumericValue accepts string forms containing only letters and digits.
func alphanumericValue(value any) bool {
	return isAlphaNumeric(toString(value))
}

// validEducationLevel accepts TANF education-level code ranges.
func validEducationLevel(value any) bool {
	v, ok := intFromAny(value)
	return ok && (intInRange(v, 0, 16) || intInRange(v, 98, 99))
}

// validWorkEligibleIndicator accepts work eligibility indicator code ranges.
func validWorkEligibleIndicator(value any) bool {
	v, ok := intFromAny(value)
	return (ok && intInRange(v, 0, 9)) || toString(value) == "11" || toString(value) == "12"
}

// validRaceValue accepts blank or race indicator values 0 through 2.
func validRaceValue(value any) bool {
	v, ok := intFromAny(value)
	return isBlank(value) || (ok && intInRange(v, 0, 2))
}

// yearAfter2019 accepts date-like values after calendar year 2019.
func yearAfter2019(value any) bool {
	return extractYear(value) > 2019
}

// validQuarterValue accepts date-like values whose quarter is 1 through 4.
func validQuarterValue(value any) bool {
	quarter := extractQuarter(value)
	return intInRange(quarter, 1, 4)
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

// validClosureReason accepts closure reason code ranges.
func validClosureReason(value any) bool {
	v, ok := intFromAny(value)
	return ok && (intInRange(v, 1, 19) || v == 99)
}

// validEducationLevelNoZero accepts education-level code ranges excluding zero.
func validEducationLevelNoZero(value any) bool {
	v, ok := intFromAny(value)
	return ok && (intInRange(v, 1, 16) || intInRange(v, 98, 99))
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

// validTribalClosureReason accepts tribal closure reason code ranges.
func validTribalClosureReason(value any) bool {
	v, ok := intFromAny(value)
	return ok && (intInRange(v, 1, 18) || v == 99)
}

// validHeaderYearRange accepts header years in the supported parser range.
func validHeaderYearRange(value any) bool {
	v, ok := intFromAny(value)
	return ok && intInRange(v, 2000, 2099)
}

// validHeaderFIPSCode accepts empty or configured FIPS codes.
func validHeaderFIPSCode(value any) bool {
	return isEmpty(value) || isValidFIPS(toString(value))
}

// validHeaderTribeCodeRange accepts empty tribe codes or the configured range.
func validHeaderTribeCodeRange(value any) bool {
	if isTribeCodeEmpty(toString(value)) {
		return true
	}
	v, ok := intFromAny(value)
	return ok && intInRange(v, 0, 999)
}

// validHeaderUpdateIndicator accepts the deletion update indicator.
func validHeaderUpdateIndicator(value any) bool {
	return toString(value) == "D"
}

// alphanumericOrSpaceValue accepts alphanumeric values or a single space.
func alphanumericOrSpaceValue(value any) bool {
	return isAlphaNumeric(toString(value)) || toString(value) == " "
}
