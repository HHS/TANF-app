"""Generic parser validator functions for use in schema definitions."""

from .models import ParserErrorCategoryChoices
from .util import fiscal_to_calendar, year_month_to_year_quarter
import datetime
import logging

logger = logging.getLogger(__name__)


def value_is_empty(value, length, extra_vals={}):
    """Handle 'empty' values as field inputs."""
    empty_values = {
        '',
        ' '*length,  # '     '
        '#'*length,  # '#####'
        '_'*length,  # '_____'
    }

    empty_values = empty_values.union(extra_vals)

    return value is None or value in empty_values

# higher order validator functions

def make_validator(validator_func, error_func):
    """Return a function accepting a value input and returning (bool, string) to represent validation state."""
    def validator(value, row_schema=None, friendly_name=None, item_num=None):
        try:
            if validator_func(value):
                return (True, None)
            return (False, error_func(value, row_schema, friendly_name, item_num))
        except Exception as e:
            logger.debug(f"Caught exception in validator. Exception: {e}")
            return (False, error_func(value, row_schema, friendly_name, item_num))
    return validator


def or_validators(*args, **kwargs):
    """Return a validator that is true only if one of the validators is true."""
    return (
        lambda value, row_schema, friendly_name, item_num: (True, None)
        if any([validator(value, row_schema, friendly_name, item_num)[0] for validator in args])
        else (False, " or ".join([validator(value, row_schema, friendly_name, item_num)[1] for validator in args]))
    )


def and_validators(validator1, validator2):
    """Return a validator that is true only if both validators are true."""
    return (
        lambda value, row_schema, friendly_name, item_num: (True, None)
        if (validator1(value, row_schema, friendly_name, item_num)[0] and validator2(value, row_schema,
                                                                                     friendly_name, item_num)[0])
        else (
            False,
            (validator1(value, row_schema, friendly_name, item_num)[1])
            if validator1(value, row_schema, friendly_name, item_num)[1] is not None
            else "" + " and " + validator2(value)[1]
            if validator2(value, row_schema, friendly_name, item_num)[1] is not None
            else "",
        )
    )

def or_priority_validators(validators=[]):
    """Return a validator that is true based on a priority of validators.

    validators: ordered list of validators to be checked
    """
    def or_priority_validators_func(value, rows_schema, friendly_name=None, item_num=None):
        for validator in validators:
            if not validator(value, rows_schema, friendly_name, item_num)[0]:
                return (False, validator(value, rows_schema,
                                         friendly_name, item_num)[1])
        return (True, None)

    return or_priority_validators_func


def extended_and_validators(*args, **kwargs):
    """Return a validator that is true only if all validators are true."""
    def returned_func(value, row_schema, friendly_name, item_num):
        if all([validator(value, row_schema, friendly_name, item_num)[0] for validator in args]):
            return (True, None)
        else:
            return (False, "".join(
                [
                    " and " + validator(value, row_schema,
                                        friendly_name, item_num)[1] if validator(value, row_schema,
                                                                                 friendly_name, item_num)[0] else ""
                    for validator in args
                ]
            ))
    return returned_func


def if_then_validator(
    condition_field_name, condition_function, result_field_name, result_function
):
    """Return second validation if the first validator is true.

    :param condition_field: function that returns (bool, string) to represent validation state
    :param condition_function: function that returns (bool, string) to represent validation state
    :param result_field: function that returns (bool, string) to represent validation state
    :param result_function: function that returns (bool, string) to represent validation state
    """

    def if_then_validator_func(value, row_schema):
        value1 = (
            value[condition_field_name]
            if type(value) is dict
            else getattr(value, condition_field_name)
        )
        value2 = (
            value[result_field_name] if type(value) is dict else getattr(value, result_field_name)
        )

        # TODO: There is some work to be done here to get the actual friendly name and item numbers of the fields
        validator1_result = condition_function(value1, row_schema, condition_field_name, "-1")
        validator2_result = result_function(value2, row_schema, result_field_name, "-1")

        if not validator1_result[0]:
            returned_value = (True, None, [condition_field_name, result_field_name])
        else:
            if not validator2_result[0]:

                # center of error message
                if validator1_result[1] is not None:
                    center_error = validator1_result[1]
                else:
                    center_error = f":{value1} validator1 passed"

                # ending of error message
                if validator2_result[1] is not None:
                    ending_error = validator2_result[1]
                else:
                    ending_error = "validator2 passed"

                error_message = (f"if {condition_field_name} " + (center_error) +
                                 f" then {result_field_name} " + ending_error)
            else:
                error_message = None

            returned_value = (validator2_result[0], error_message, [condition_field_name, result_field_name])

        return returned_value

    return lambda value, row_schema: if_then_validator_func(value, row_schema)


def sumIsEqual(condition_field, sum_fields=[]):
    """Validate that the sum of the sum_fields equals the condition_field."""

    def sumIsEqualFunc(value, row_schema):
        sum = 0
        for field in sum_fields:
            val = value[field] if type(value) is dict else getattr(value, field)
            sum += 0 if val is None else val

        condition_val = (
            value[condition_field]
            if type(value) is dict
            else getattr(value, condition_field)
        )
        fields = [condition_field]
        fields.extend(sum_fields)
        return (
            (True, None, fields)
            if sum == condition_val
            else (
                False,
                f"{row_schema.record_type}: The sum of {sum_fields} does not equal {condition_field}.",
                fields,
            )
        )

    return sumIsEqualFunc


def field_year_month_with_header_year_quarter():
    """Validate that the field year and month match the header year and quarter."""
    def validate_reporting_month_year_fields_header(line, row_schema, friendly_name, item_num):

        field_month_year = row_schema.get_field_values_by_names(line, ['RPT_MONTH_YEAR']).get('RPT_MONTH_YEAR')
        df_quarter = row_schema.datafile.quarter
        df_year = row_schema.datafile.year

        # get reporting month year from header
        field_year, field_quarter = year_month_to_year_quarter(f"{field_month_year}")
        file_calendar_year, file_calendar_qtr = fiscal_to_calendar(df_year, f"{df_quarter}")
        return (True, None) if str(file_calendar_year) == str(field_year) and file_calendar_qtr == field_quarter else (
            False, f"{row_schema.record_type}: Reporting month year {field_month_year} " +
            f"does not match file reporting year:{df_year}, quarter:{df_quarter}.",
            )

    return validate_reporting_month_year_fields_header


def sumIsLarger(fields, val):
    """Validate that the sum of the fields is larger than val."""

    def sumIsLargerFunc(value, row_schema):
        sum = 0
        for field in fields:
            temp_val = value[field] if type(value) is dict else getattr(value, field)
            sum += 0 if temp_val is None else temp_val

        return (
            (True, None, [field for field in fields])
            if sum > val
            else (
                False,
                f"{row_schema.record_type}: The sum of {fields} is not larger than {val}.",
                [field for field in fields],
            )
        )

    return sumIsLargerFunc


# generic validators


def matches(option, error_func=None):
    """Validate that value is equal to option."""
    return make_validator(
        lambda value: value == option,
        lambda value, row_schema, friendly_name, item_num: error_func(option)
        if error_func
        else f"{row_schema.record_type} {friendly_name}: {value} does not match {option}.",
    )


def notMatches(option):
    """Validate that value is not equal to option."""
    return make_validator(
        lambda value: value != option,
        lambda value, row_schema, friendly_name, item_num: f"{row_schema.record_type}: {value} matches {option}."
    )


def oneOf(options=[]):
    """Validate that value does not exist in the provided options array."""
    return make_validator(
        lambda value: value in options,
        lambda value, row_schema, friendly_name, item_num: f"{row_schema.record_type}: {value} is not in {options}."
    )


def notOneOf(options=[]):
    """Validate that value exists in the provided options array."""
    return make_validator(
        lambda value: value not in options,
        lambda value, row_schema, friendly_name, item_num: f"{row_schema.record_type}: {value} is in {options}."
    )


def between(min, max):
    """Validate value, when casted to int, is greater than min and less than max."""
    return make_validator(
        lambda value: int(value) > min and int(value) < max,
        lambda value, row_schema,
        friendly_name, item_num: f"{row_schema.record_type}: {value} is not between {min} and {max}.",
    )


def recordHasLength(length):
    """Validate that value (string or array) has a length matching length param."""
    return make_validator(
        lambda value: len(value) == length,
        lambda value,
        row_schema,
        friendly_name,
        item_num: f"{row_schema.record_type} record length is {len(value)} characters but must be {length}.",
    )


def intHasLength(num_digits):
    """Validate the number of digits in an integer."""
    return make_validator(
        lambda value: sum(c.isdigit() for c in str(value)) == num_digits,
        lambda value, row_schema,
        friendly_name, item_num: f"{row_schema.record_type}: {value} does not have exactly {num_digits} digits.",
    )


def contains(substring):
    """Validate that string value contains the given substring param."""
    return make_validator(
        lambda value: value.find(substring) != -1,
        lambda value, row_schema,
        friendly_name, item_num: f"{row_schema.record_type}: {value} does not contain {substring}.",
    )


def startsWith(substring, error_func=None):
    """Validate that string value starts with the given substring param."""
    return make_validator(
        lambda value: value.startswith(substring),
        lambda value, row_schema, friendly_name, item_num: error_func(substring)
        if error_func
        else f"{row_schema.record_type}: {value} does not start with {substring}.",
    )


def isNumber():
    """Validate that value can be casted to a number."""
    return make_validator(
        lambda value: value.isnumeric(),
        lambda value, row_schema, friendly_name, item_num: f"{row_schema.record_type}: {value} is not a number."
    )


def isAlphaNumeric():
    """Validate that value is alphanumeric."""
    return make_validator(
        lambda value: value.isalnum(),
        lambda value, row_schema, friendly_name, item_num: f"{row_schema.record_type}: {value} is not alphanumeric."
    )


def isBlank():
    """Validate that string value is blank."""
    return make_validator(
        lambda value: value.isspace(),
        lambda value, row_schema, friendly_name, item_num: f"{row_schema.record_type}: {value} is not blank."
    )


def isInStringRange(lower, upper):
    """Validate that string value is in a specific range."""
    return make_validator(
        lambda value: int(value) >= lower and int(value) <= upper,
        lambda value, row_schema,
        friendly_name, item_num: f"{row_schema.record_type}: {value} is not in range [{lower}, {upper}].",
    )


def isStringLargerThan(val):
    """Validate that string value is larger than val."""
    return make_validator(
        lambda value: int(value) > val,
        lambda value, row_schema,
        friendly_name, item_num: f"{row_schema.record_type}: {value} is not larger than {val}.",
    )


def _is_empty(value, start, end):
    end = end if end else len(str(value))
    vlen = end - start
    subv = str(value)[start:end]
    return value_is_empty(subv, vlen) or len(subv) < vlen


def notEmpty(start=0, end=None):
    """Validate that string value isn't only blanks."""
    return make_validator(
        lambda value: not _is_empty(value, start, end),
        lambda value, row_schema,
        friendly_name, item_num: f'{row_schema.record_type}: {str(value)} contains blanks between positions {start} '
                                 f'and {end if end else len(str(value))}.'
    )


def caseNumberNotEmpty(start=0, end=None):
    """Validate that string value isn't only blanks."""
    return make_validator(
        lambda value: not _is_empty(value, start, end),
        lambda value, row_schema,
        friendly_name, item_num: f'{row_schema.record_type}: Case number {str(value)} cannot contain blanks.'
    )


def calendarQuarterIsValid(start=0, end=None):
    """Validate that the calendar quarter value is valid."""
    return make_validator(
        lambda value: value[start:end].isnumeric() and int(value[start:end - 1]) >= 2020
        and int(value[end - 1:end]) > 0 and int(value[end - 1:end]) < 5,
        lambda value,
        row_schema,
        friendly_name,
        item_num: f"{row_schema.record_type}: {value[start:end]} is invalid. Calendar Quarter must be a numeric "
        "representing the Calendar Year and Quarter formatted as YYYYQ",
    )


def isEmpty(start=0, end=None):
    """Validate that string value is only blanks."""
    return make_validator(
        lambda value: _is_empty(value, start, end),
        lambda value, row_schema,
        friendly_name, item_num: f'{value} is not blank between positions {start} and {end if end else len(value)}.'
    )


def notZero(number_of_zeros=1):
    """Validate that value is not zero."""
    return make_validator(
        lambda value: value != "0" * number_of_zeros,
        lambda value, row_schema, friendly_name, item_num: f"{row_schema.record_type}: {value} is zero."
    )


def isLargerThan(LowerBound):
    """Validate that value is larger than the given value."""
    return make_validator(
        lambda value: float(value) > LowerBound if value is not None else False,
        lambda value, row_schema,
        friendly_name, item_num: f"{row_schema.record_type}: {value} is not larger than {LowerBound}.",
    )


def isSmallerThan(UpperBound):
    """Validate that value is smaller than the given value."""
    return make_validator(
        lambda value: value < UpperBound,
        lambda value, row_schema,
        friendly_name, item_num: f"{row_schema.record_type}: {value} is not smaller than {UpperBound}.",
    )


def isLargerThanOrEqualTo(LowerBound):
    """Validate that value is larger than the given value."""
    return make_validator(
        lambda value: value >= LowerBound,
        lambda value, row_schema,
        friendly_name, item_num: f"{row_schema.record_type}: {value} is not larger than {LowerBound}.",
    )


def isSmallerThanOrEqualTo(UpperBound):
    """Validate that value is smaller than the given value."""
    return make_validator(
        lambda value: value <= UpperBound,
        lambda value, row_schema,
        friendly_name, item_num: f"{row_schema.record_type}: {value} is not smaller than {UpperBound}.",
    )


def isInLimits(LowerBound, UpperBound):
    """Validate that value is in a range including the limits."""
    return make_validator(
        lambda value: value >= LowerBound and value <= UpperBound,
        lambda value, row_schema,
        friendly_name, item_num: f"{row_schema.record_type}: {value} is not larger or equal to {LowerBound} and "
                                 f"smaller or equal to {UpperBound}."
    )


# custom validators

def dateMonthIsValid():
    """Validate that in a monthyear combination, the month is a valid month."""
    return make_validator(
        lambda value: int(str(value)[4:6]) in range(1, 13),
        lambda value, row_schema,
        friendly_name, item_num: f"{row_schema.record_type}: {str(value)[4:6]} is not a valid month.",
    )

def dateDayIsValid():
    """Validate that in a monthyearday combination, the day is a valid day."""
    return make_validator(
        lambda value: int(str(value)[6:]) in range(1, 32),
        lambda value, row_schema,
        friendly_name, item_num: f"{row_schema.record_type}: {str(value)[6:]} is not a valid day.",
    )


def olderThan(min_age):
    """Validate that value is larger than min_age."""
    return make_validator(
        lambda value: datetime.date.today().year - int(str(value)[:4]) > min_age,
        lambda value, row_schema,
        friendly_name, item_num: (f"{row_schema.record_type}: {str(value)[:4]} must be less than or equal to "
                                  f"{datetime.date.today().year - min_age} to meet the minimum age requirement.")
    )


def dateYearIsLargerThan(year):
    """Validate that in a monthyear combination, the year is larger than the given year."""
    return make_validator(
        lambda value: int(str(value)[:4]) > year,
        lambda value, row_schema,
        friendly_name, item_num: f"{row_schema.record_type}: Year {str(value)[:4]} must be larger than {year}.",
    )


def quarterIsValid():
    """Validate in a year quarter combination, the quarter is valid."""
    return make_validator(
        lambda value: int(str(value)[-1]) > 0 and int(str(value)[-1]) < 5,
        lambda value, row_schema,
        friendly_name, item_num: f"{row_schema.record_type}: {str(value)[-1]} is not a valid quarter.",
    )


def validateSSN():
    """Validate that SSN value is not a repeating digit."""
    options = [str(i) * 9 for i in range(0, 10)]
    return make_validator(
        lambda value: value not in options,
        lambda value, row_schema, friendly_name, item_num: f"{row_schema.record_type}: {value} is in {options}."
    )


def validateRace():
    """Validate race."""
    return make_validator(
        lambda value: value >= 0 and value <= 2,
        lambda value, row_schema,
        friendly_name, item_num: f"{row_schema.record_type}: {value} is not greater than or equal to 0 "
                                 "or smaller than or equal to 2."
    )


def validateRptMonthYear():
    """Validate RPT_MONTH_YEAR."""
    return make_validator(
        lambda value: value[2:8].isdigit() and int(value[2:6]) > 1900 and value[6:8] in {"01", "02", "03", "04", "05",
                                                                                         "06", "07", "08", "09", "10",
                                                                                         "11", "12"},
        lambda value, row_schema,
        friendly_name, item_num: f"{row_schema.record_type}: The value: {value[2:8]}, does not follow the YYYYMM "
                                 "format for Reporting Year and Month.",
    )


# outlier validators
def validate__FAM_AFF__SSN():
    """
    Validate social security number provided.

    If item FAMILY_AFFILIATION ==2 and item CITIZENSHIP_STATUS ==1 or 2,
    then item SSN != 000000000 -- 999999999.
    """
    # value is instance
    def validate(instance, row_schema):
        FAMILY_AFFILIATION = (
            instance["FAMILY_AFFILIATION"]
            if type(instance) is dict
            else getattr(instance, "FAMILY_AFFILIATION")
        )
        CITIZENSHIP_STATUS = (
            instance["CITIZENSHIP_STATUS"]
            if type(instance) is dict
            else getattr(instance, "CITIZENSHIP_STATUS")
        )
        SSN = instance["SSN"] if type(instance) is dict else getattr(instance, "SSN")
        if FAMILY_AFFILIATION == 2 and (
            CITIZENSHIP_STATUS == 1 or CITIZENSHIP_STATUS == 2
        ):
            if SSN in [str(i) * 9 for i in range(10)]:
                return (
                    False,
                    f"{row_schema.record_type}: If FAMILY_AFFILIATION ==2 and CITIZENSHIP_STATUS==1 or 2, "
                    "then SSN != 000000000 -- 999999999.",
                    ["FAMILY_AFFILIATION", "CITIZENSHIP_STATUS", "SSN"],
                )
            else:
                return (True, None, ["FAMILY_AFFILIATION", "CITIZENSHIP_STATUS", "SSN"])
        else:
            return (True, None, ["FAMILY_AFFILIATION", "CITIZENSHIP_STATUS", "SSN"])

    return validate


def validate__FAM_AFF__HOH__Fed_Time():
    """If FAMILY_AFFILIATION == 1 and RELATIONSHIP_HOH == 1 or 2, then MONTHS_FED_TIME_LIMIT >= 1."""
    # value is instance
    def validate(instance, row_schema):
        false_case = (False,
                      f"{row_schema.record_type}: If FAMILY_AFFILIATION == 1 and RELATIONSHIP_HOH == 1 or 2, then "
                      + "MONTHS_FED_TIME_LIMIT >= 1.",
                      ["FAMILY_AFFILIATION", "RELATIONSHIP_HOH", "MONTHS_FED_TIME_LIMIT",],
                      )
        true_case = (True,
                     None,
                     ["FAMILY_AFFILIATION", "RELATIONSHIP_HOH", "MONTHS_FED_TIME_LIMIT",],
                     )
        try:
            FAMILY_AFFILIATION = (
                instance["FAMILY_AFFILIATION"]
                if type(instance) is dict
                else getattr(instance, "FAMILY_AFFILIATION")
            )
            RELATIONSHIP_HOH = (
                instance["RELATIONSHIP_HOH"]
                if type(instance) is dict
                else getattr(instance, "RELATIONSHIP_HOH")
            )
            RELATIONSHIP_HOH = int(RELATIONSHIP_HOH)
            MONTHS_FED_TIME_LIMIT = (
                instance["MONTHS_FED_TIME_LIMIT"]
                if type(instance) is dict
                else getattr(instance, "MONTHS_FED_TIME_LIMIT")
            )
            if FAMILY_AFFILIATION == 1 and (RELATIONSHIP_HOH == 1 or RELATIONSHIP_HOH == 2):
                if MONTHS_FED_TIME_LIMIT is None or int(MONTHS_FED_TIME_LIMIT) < 1:
                    return false_case
                else:
                    return true_case
            else:
                return true_case
        except Exception:
            vals = {"FAMILY_AFFILIATION": FAMILY_AFFILIATION,
                    "RELATIONSHIP_HOH": RELATIONSHIP_HOH,
                    "MONTHS_FED_TIME_LIMIT": MONTHS_FED_TIME_LIMIT}
            logger.debug("Caught exception in validator: validate__FAM_AFF__HOH__Fed_Time. With field values: " +
                         f"{vals}.")
            return false_case

    return validate


def validate__FAM_AFF__HOH__Count_Fed_Time():
    """If FAMILY_AFFILIATION == 1 and RELATIONSHIP_HOH == 1 or 2, then COUNTABLE_MONTH_FED_TIME >= 1."""
    # value is instance
    def validate(instance, row_schema):
        false_case = (False,
                      f"{row_schema.record_type}: If FAMILY_AFFILIATION == 1 and RELATIONSHIP_HOH == 1 or 2, then "
                      + "COUNTABLE_MONTH_FED_TIME >= 1.",
                      ["FAMILY_AFFILIATION", "RELATIONSHIP_HOH", "COUNTABLE_MONTH_FED_TIME",],
                      )
        true_case = (True,
                     None,
                     ["FAMILY_AFFILIATION", "RELATIONSHIP_HOH", "COUNTABLE_MONTH_FED_TIME",],
                     )
        try:
            FAMILY_AFFILIATION = (
                instance["FAMILY_AFFILIATION"]
                if type(instance) is dict
                else getattr(instance, "FAMILY_AFFILIATION")
            )
            RELATIONSHIP_HOH = (
                instance["RELATIONSHIP_HOH"]
                if type(instance) is dict
                else getattr(instance, "RELATIONSHIP_HOH")
            )
            RELATIONSHIP_HOH = int(RELATIONSHIP_HOH)
            COUNTABLE_MONTH_FED_TIME = (
                instance["COUNTABLE_MONTH_FED_TIME"]
                if type(instance) is dict
                else getattr(instance, "COUNTABLE_MONTH_FED_TIME")
            )
            if FAMILY_AFFILIATION == 1 and (RELATIONSHIP_HOH == 1 or RELATIONSHIP_HOH == 2):
                if int(COUNTABLE_MONTH_FED_TIME) < 1:
                    return false_case
                else:
                    return true_case
            else:
                return true_case
        except Exception:
            vals = {"FAMILY_AFFILIATION": FAMILY_AFFILIATION,
                    "RELATIONSHIP_HOH": RELATIONSHIP_HOH,
                    "COUNTABLE_MONTH_FED_TIME": COUNTABLE_MONTH_FED_TIME
                    }
            logger.debug("Caught exception in validator: validate__FAM_AFF__HOH__Count_Fed_Time. With field values: " +
                         f"{vals}.")
            return false_case

    return validate


def validate_header_section_matches_submission(datafile, section, generate_error):
    """Validate header section matches submission section."""
    is_valid = datafile.section == section

    error = None
    if not is_valid:
        error = generate_error(
            schema=None,
            error_category=ParserErrorCategoryChoices.PRE_CHECK,
            error_message=f"Data does not match the expected layout for {datafile.section}.",
            record=None,
            field=None,
        )

    return is_valid, error


def validate_tribe_fips_program_agree(program_type, tribe_code, state_fips_code, generate_error):
    """Validate tribe code, fips code, and program type all agree with eachother."""
    is_valid = False

    if program_type == 'TAN' and value_is_empty(state_fips_code, 2, extra_vals={'0'*2}):
        is_valid = not value_is_empty(tribe_code, 3, extra_vals={'0'*3})
    else:
        is_valid = value_is_empty(tribe_code, 3, extra_vals={'0'*3})

    error = None
    if not is_valid:
        error = generate_error(
            schema=None,
            error_category=ParserErrorCategoryChoices.PRE_CHECK,

            error_message=f"Tribe Code ({tribe_code}) inconsistency with Program Type ({program_type}) and " +
            f"FIPS Code ({state_fips_code}).",
            record=None,
            field=None
        )

    return is_valid, error


def validate_header_rpt_month_year(datafile, header, generate_error):
    """Validate header rpt_month_year."""
    # the header year/quarter represent a calendar period, and frontend year/qtr represents a fiscal period
    header_calendar_qtr = f"Q{header['quarter']}"
    header_calendar_year = header['year']
    file_calendar_year, file_calendar_qtr = fiscal_to_calendar(datafile.year, f"{datafile.quarter}")

    is_valid = file_calendar_year is not None and file_calendar_qtr is not None
    is_valid = is_valid and file_calendar_year == header_calendar_year and file_calendar_qtr == header_calendar_qtr

    error = None
    if not is_valid:
        error = generate_error(
            schema=None,
            error_category=ParserErrorCategoryChoices.PRE_CHECK,
            error_message=f"Submitted reporting year:{header['year']}, quarter:Q{header['quarter']} doesn't match "
            + f"file reporting year:{datafile.year}, quarter:{datafile.quarter}.",
            record=None,
            field=None,
        )
    return is_valid, error

def validate__WORK_ELIGIBLE_INDICATOR__HOH__AGE():
    """If WORK_ELIGIBLE_INDICATOR == 11 and AGE < 19, then RELATIONSHIP_HOH != 1."""
    # value is instance
    def validate(instance, row_schema):
        false_case = (False,
                      f"{row_schema.record_type}: If WORK_ELIGIBLE_INDICATOR == 11 and AGE < 19, "
                      "then RELATIONSHIP_HOH != 1",
                      ['WORK_ELIGIBLE_INDICATOR', 'RELATIONSHIP_HOH', 'DATE_OF_BIRTH']
                      )
        true_case = (True,
                     None,
                     ['WORK_ELIGIBLE_INDICATOR', 'RELATIONSHIP_HOH', 'DATE_OF_BIRTH'],
                     )
        try:
            WORK_ELIGIBLE_INDICATOR = (
                instance["WORK_ELIGIBLE_INDICATOR"]
                if type(instance) is dict
                else getattr(instance, "WORK_ELIGIBLE_INDICATOR")
            )
            RELATIONSHIP_HOH = (
                instance["RELATIONSHIP_HOH"]
                if type(instance) is dict
                else getattr(instance, "RELATIONSHIP_HOH")
            )
            RELATIONSHIP_HOH = int(RELATIONSHIP_HOH)

            DOB = str(
                instance["DATE_OF_BIRTH"]
                if type(instance) is dict
                else getattr(instance, "DATE_OF_BIRTH")
            )

            RPT_MONTH_YEAR = str(
                instance["RPT_MONTH_YEAR"]
                if type(instance) is dict
                else getattr(instance, "RPT_MONTH_YEAR")
            )

            RPT_MONTH_YEAR += "01"

            DOB_datetime = datetime.datetime.strptime(DOB, '%Y%m%d')
            RPT_MONTH_YEAR_datetime = datetime.datetime.strptime(RPT_MONTH_YEAR, '%Y%m%d')
            AGE = (RPT_MONTH_YEAR_datetime - DOB_datetime).days / 365.25

            if WORK_ELIGIBLE_INDICATOR == "11" and AGE < 19:
                if RELATIONSHIP_HOH == 1:
                    return false_case
                else:
                    return true_case
            else:
                return true_case
        except Exception:
            vals = {"WORK_ELIGIBLE_INDICATOR": WORK_ELIGIBLE_INDICATOR,
                    "RELATIONSHIP_HOH": RELATIONSHIP_HOH,
                    "DOB": DOB
                    }
            logger.debug("Caught exception in validator: validate__WORK_ELIGIBLE_INDICATOR__HOH__AGE. " +
                         f"With field values: {vals}.")
            # Per conversation with Alex on 03/26/2024, returning the true case during exception handling to avoid
            # confusing the STTs.
            return true_case

    return validate
