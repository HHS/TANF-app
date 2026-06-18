package validation

var nativeFieldValidators = map[string]validationRule{
	"length":                      fieldLengthValidator{},
	"in_range_int":                fieldInRangeIntValidator{},
	"in_values":                   fieldInValuesValidator{},
	"equals":                      fieldEqualsValidator{},
	"not_empty":                   notEmptyValidator{},
	"not_blank":                   notBlankValidator{},
	"positive_value":              positiveValueValidator{},
	"not_negative":                notNegativeValidator{},
	"valid_year":                  validYearValidator{},
	"year_after_1998":             yearAfter1998Validator{},
	"valid_day":                   validDayValidator{},
	"valid_month":                 validMonthValidator{},
	"valid_date":                  validDateValidator{},
	"is_numeric":                  numericValidator{},
	"is_alphanumeric":             alphanumericValidator{},
	"in_values_or_blank":          fieldInValuesOrBlankValidator{},
	"education_level":             educationLevelValidator{},
	"work_eligible_indicator":     workEligibleIndicatorValidator{},
	"validate_race":               raceValidator{},
	"year_after_2019":             yearAfter2019Validator{},
	"quarter_is_valid":            quarterValidator{},
	"calendar_quarter_is_valid":   calendarQuarterValidator{},
	"closure_reason":              closureReasonValidator{},
	"education_level_no_zero":     educationLevelNoZeroValidator{},
	"fra_ssn":                     fraSSNValidator{},
	"tribal_closure_reason":       tribalClosureReasonValidator{},
	"header_year_range":           headerYearRangeValidator{},
	"header_quarter":              fieldStringSetValidator{allowedValues: []string{"1", "2", "3", "4"}},
	"header_section_type":         fieldStringSetValidator{allowedValues: []string{"A", "C", "G", "S"}},
	"header_fips_code":            headerFIPSCodeValidator{},
	"header_tribe_code_range":     headerTribeCodeRangeValidator{},
	"header_program_type":         fieldStringSetValidator{allowedValues: []string{"TAN", "SSP"}},
	"header_edit_indicator":       fieldStringSetValidator{allowedValues: []string{"1", "2"}},
	"header_encryption_indicator": fieldStringSetValidator{allowedValues: []string{" ", "E", ""}},
	"header_update_indicator":     headerUpdateIndicatorValidator{},
	"is_alphanumeric_or_space":    alphanumericOrSpaceValidator{},
}

type fieldStringSetValidator struct {
	allowedValues []string
}

func (v fieldStringSetValidator) Compile(validationParams) (ValidatorExecutor, error) {
	return fieldStringSetValidator{allowedValues: append([]string(nil), v.allowedValues...)}, nil
}

func (v fieldStringSetValidator) Execute(state *ValidationState) (ValidationOutcome, error) {
	return boolOutcome(stringIn(toString(fieldValueFromState(state)), v.allowedValues...)), nil
}

type fieldLengthValidator struct {
	n int
}

func (v fieldLengthValidator) Compile(params validationParams) (ValidatorExecutor, error) {
	n, err := requiredIntParam(params, "n")
	return fieldLengthValidator{n: n}, err
}

func (v fieldLengthValidator) Execute(state *ValidationState) (ValidationOutcome, error) {
	return boolOutcome(len(toString(fieldValueFromState(state))) == v.n), nil
}

type fieldInRangeIntValidator struct {
	min int
	max int
}

func (v fieldInRangeIntValidator) Compile(params validationParams) (ValidatorExecutor, error) {
	min, max, err := requiredIntRangeParams(params, "min", "max")
	return fieldInRangeIntValidator{min: min, max: max}, err
}

func (v fieldInRangeIntValidator) Execute(state *ValidationState) (ValidationOutcome, error) {
	value, ok := intFromAny(fieldValueFromState(state))
	return boolOutcome(ok && value >= v.min && value <= v.max), nil
}

type fieldInValuesValidator struct {
	values []any
}

func (v fieldInValuesValidator) Compile(params validationParams) (ValidatorExecutor, error) {
	values, err := requiredAnySliceParam(params, "values")
	return fieldInValuesValidator{values: values}, err
}

func (v fieldInValuesValidator) Execute(state *ValidationState) (ValidationOutcome, error) {
	return boolOutcome(valueInAny(fieldValueFromState(state), v.values)), nil
}

type fieldEqualsValidator struct {
	expected any
}

func (v fieldEqualsValidator) Compile(params validationParams) (ValidatorExecutor, error) {
	expected, err := requiredAnyParam(params, "value")
	return fieldEqualsValidator{expected: expected}, err
}

func (v fieldEqualsValidator) Execute(state *ValidationState) (ValidationOutcome, error) {
	return boolOutcome(anyEqual(fieldValueFromState(state), v.expected)), nil
}

type fieldInValuesOrBlankValidator struct {
	values []any
}

func (v fieldInValuesOrBlankValidator) Compile(params validationParams) (ValidatorExecutor, error) {
	values, err := requiredAnySliceParam(params, "values")
	return fieldInValuesOrBlankValidator{values: values}, err
}

func (v fieldInValuesOrBlankValidator) Execute(state *ValidationState) (ValidationOutcome, error) {
	value := fieldValueFromState(state)
	return boolOutcome(isBlank(value) || valueInAny(value, v.values)), nil
}

type notEmptyValidator struct{}

func (v notEmptyValidator) Compile(validationParams) (ValidatorExecutor, error) { return v, nil }

func (v notEmptyValidator) Execute(state *ValidationState) (ValidationOutcome, error) {
	return boolOutcome(isNotEmpty(fieldValueFromState(state))), nil
}

type notBlankValidator struct{}

func (v notBlankValidator) Compile(validationParams) (ValidatorExecutor, error) { return v, nil }

func (v notBlankValidator) Execute(state *ValidationState) (ValidationOutcome, error) {
	return boolOutcome(isNotBlank(fieldValueFromState(state))), nil
}

type positiveValueValidator struct{}

func (v positiveValueValidator) Compile(validationParams) (ValidatorExecutor, error) { return v, nil }

func (v positiveValueValidator) Execute(state *ValidationState) (ValidationOutcome, error) {
	value, ok := intFromAny(fieldValueFromState(state))
	return boolOutcome(ok && value > 0), nil
}

type notNegativeValidator struct{}

func (v notNegativeValidator) Compile(validationParams) (ValidatorExecutor, error) { return v, nil }

func (v notNegativeValidator) Execute(state *ValidationState) (ValidationOutcome, error) {
	value, ok := intFromAny(fieldValueFromState(state))
	return boolOutcome(ok && value >= 0), nil
}

type validYearValidator struct{}

func (v validYearValidator) Compile(validationParams) (ValidatorExecutor, error) { return v, nil }

func (v validYearValidator) Execute(state *ValidationState) (ValidationOutcome, error) {
	return boolOutcome(extractYear(fieldValueFromState(state)) >= 1900), nil
}

type yearAfter1998Validator struct{}

func (v yearAfter1998Validator) Compile(validationParams) (ValidatorExecutor, error) { return v, nil }

func (v yearAfter1998Validator) Execute(state *ValidationState) (ValidationOutcome, error) {
	return boolOutcome(extractYear(fieldValueFromState(state)) > 1998), nil
}

type validDayValidator struct{}

func (v validDayValidator) Compile(validationParams) (ValidatorExecutor, error) { return v, nil }

func (v validDayValidator) Execute(state *ValidationState) (ValidationOutcome, error) {
	day := extractDay(fieldValueFromState(state))
	return boolOutcome(day >= 1 && day <= 31), nil
}

type validMonthValidator struct{}

func (v validMonthValidator) Compile(validationParams) (ValidatorExecutor, error) { return v, nil }

func (v validMonthValidator) Execute(state *ValidationState) (ValidationOutcome, error) {
	month := extractMonth(fieldValueFromState(state))
	return boolOutcome(month >= 1 && month <= 12), nil
}

type validDateValidator struct{}

func (v validDateValidator) Compile(validationParams) (ValidatorExecutor, error) { return v, nil }

func (v validDateValidator) Execute(state *ValidationState) (ValidationOutcome, error) {
	return boolOutcome(isValidDate(fieldValueFromState(state))), nil
}

type numericValidator struct{}

func (v numericValidator) Compile(validationParams) (ValidatorExecutor, error) { return v, nil }

func (v numericValidator) Execute(state *ValidationState) (ValidationOutcome, error) {
	return boolOutcome(isNumeric(toString(fieldValueFromState(state)))), nil
}

type alphanumericValidator struct{}

func (v alphanumericValidator) Compile(validationParams) (ValidatorExecutor, error) { return v, nil }

func (v alphanumericValidator) Execute(state *ValidationState) (ValidationOutcome, error) {
	return boolOutcome(isAlphaNumeric(toString(fieldValueFromState(state)))), nil
}

type educationLevelValidator struct{}

func (v educationLevelValidator) Compile(validationParams) (ValidatorExecutor, error) { return v, nil }

func (v educationLevelValidator) Execute(state *ValidationState) (ValidationOutcome, error) {
	value, ok := intFromAny(fieldValueFromState(state))
	return boolOutcome(ok && (intInRange(value, 0, 16) || intInRange(value, 98, 99))), nil
}

type workEligibleIndicatorValidator struct{}

func (v workEligibleIndicatorValidator) Compile(validationParams) (ValidatorExecutor, error) {
	return v, nil
}

func (v workEligibleIndicatorValidator) Execute(state *ValidationState) (ValidationOutcome, error) {
	fieldValue := fieldValueFromState(state)
	value, ok := intFromAny(fieldValue)
	return boolOutcome((ok && intInRange(value, 0, 9)) || toString(fieldValue) == "11" || toString(fieldValue) == "12"), nil
}

type raceValidator struct{}

func (v raceValidator) Compile(validationParams) (ValidatorExecutor, error) { return v, nil }

func (v raceValidator) Execute(state *ValidationState) (ValidationOutcome, error) {
	fieldValue := fieldValueFromState(state)
	value, ok := intFromAny(fieldValue)
	return boolOutcome(isBlank(fieldValue) || (ok && intInRange(value, 0, 2))), nil
}

type yearAfter2019Validator struct{}

func (v yearAfter2019Validator) Compile(validationParams) (ValidatorExecutor, error) { return v, nil }

func (v yearAfter2019Validator) Execute(state *ValidationState) (ValidationOutcome, error) {
	return boolOutcome(extractYear(fieldValueFromState(state)) > 2019), nil
}

type quarterValidator struct{}

func (v quarterValidator) Compile(validationParams) (ValidatorExecutor, error) { return v, nil }

func (v quarterValidator) Execute(state *ValidationState) (ValidationOutcome, error) {
	return boolOutcome(intInRange(extractQuarter(fieldValueFromState(state)), 1, 4)), nil
}

type calendarQuarterValidator struct{}

func (v calendarQuarterValidator) Compile(validationParams) (ValidatorExecutor, error) { return v, nil }

func (v calendarQuarterValidator) Execute(state *ValidationState) (ValidationOutcome, error) {
	value := toString(fieldValueFromState(state))
	if len(value) != 5 {
		return boolOutcome(false), nil
	}
	quarter, ok := intFromAny(value[4:5])
	return boolOutcome(ok && intInRange(quarter, 1, 4)), nil
}

type closureReasonValidator struct{}

func (v closureReasonValidator) Compile(validationParams) (ValidatorExecutor, error) { return v, nil }

func (v closureReasonValidator) Execute(state *ValidationState) (ValidationOutcome, error) {
	value, ok := intFromAny(fieldValueFromState(state))
	return boolOutcome(ok && (intInRange(value, 1, 19) || value == 99)), nil
}

type educationLevelNoZeroValidator struct{}

func (v educationLevelNoZeroValidator) Compile(validationParams) (ValidatorExecutor, error) {
	return v, nil
}

func (v educationLevelNoZeroValidator) Execute(state *ValidationState) (ValidationOutcome, error) {
	value, ok := intFromAny(fieldValueFromState(state))
	return boolOutcome(ok && (intInRange(value, 1, 16) || intInRange(value, 98, 99))), nil
}

type fraSSNValidator struct{}

func (v fraSSNValidator) Compile(validationParams) (ValidatorExecutor, error) { return v, nil }

func (v fraSSNValidator) Execute(state *ValidationState) (ValidationOutcome, error) {
	value := toString(fieldValueFromState(state))
	return boolOutcome(isNumeric(value) &&
		len(value) == 9 &&
		value[0:3] != "000" &&
		value[0:3] != "666" &&
		value[3:5] != "00" &&
		value[5:9] != "0000"), nil
}

type tribalClosureReasonValidator struct{}

func (v tribalClosureReasonValidator) Compile(validationParams) (ValidatorExecutor, error) {
	return v, nil
}

func (v tribalClosureReasonValidator) Execute(state *ValidationState) (ValidationOutcome, error) {
	value, ok := intFromAny(fieldValueFromState(state))
	return boolOutcome(ok && (intInRange(value, 1, 18) || value == 99)), nil
}

type headerYearRangeValidator struct{}

func (v headerYearRangeValidator) Compile(validationParams) (ValidatorExecutor, error) { return v, nil }

func (v headerYearRangeValidator) Execute(state *ValidationState) (ValidationOutcome, error) {
	value, ok := intFromAny(fieldValueFromState(state))
	return boolOutcome(ok && intInRange(value, 2000, 2099)), nil
}

type headerFIPSCodeValidator struct{}

func (v headerFIPSCodeValidator) Compile(validationParams) (ValidatorExecutor, error) { return v, nil }

func (v headerFIPSCodeValidator) Execute(state *ValidationState) (ValidationOutcome, error) {
	value := fieldValueFromState(state)
	return boolOutcome(isEmpty(value) || isValidFIPS(toString(value))), nil
}

type headerTribeCodeRangeValidator struct{}

func (v headerTribeCodeRangeValidator) Compile(validationParams) (ValidatorExecutor, error) {
	return v, nil
}

func (v headerTribeCodeRangeValidator) Execute(state *ValidationState) (ValidationOutcome, error) {
	value := fieldValueFromState(state)
	if isTribeCodeEmpty(toString(value)) {
		return boolOutcome(true), nil
	}
	parsed, ok := intFromAny(value)
	return boolOutcome(ok && intInRange(parsed, 0, 999)), nil
}

type headerUpdateIndicatorValidator struct{}

func (v headerUpdateIndicatorValidator) Compile(validationParams) (ValidatorExecutor, error) {
	return v, nil
}

func (v headerUpdateIndicatorValidator) Execute(state *ValidationState) (ValidationOutcome, error) {
	return boolOutcome(toString(fieldValueFromState(state)) == "D"), nil
}

type alphanumericOrSpaceValidator struct{}

func (v alphanumericOrSpaceValidator) Compile(validationParams) (ValidatorExecutor, error) {
	return v, nil
}

func (v alphanumericOrSpaceValidator) Execute(state *ValidationState) (ValidationOutcome, error) {
	value := toString(fieldValueFromState(state))
	return boolOutcome(isAlphaNumeric(value) || value == " "), nil
}

// fieldValueFromState safely returns the field value from validation state.
func fieldValueFromState(state *ValidationState) any {
	if state == nil {
		return nil
	}
	return state.Value
}
