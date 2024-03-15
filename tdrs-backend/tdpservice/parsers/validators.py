"""Generic parser validator functions for use in schema definitions."""

from .models import ParserErrorCategoryChoices
from .util import fiscal_to_calendar
from datetime import date
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

# higher order validator func


def make_validator(validator_func, error_func):
    """Return a function accepting a value input and returning (bool, string) to represent validation state."""
    def validator(value):
        try:
            if validator_func(value):
                return (True, None)
            return (False, error_func(value))
        except Exception as e:
            logger.debug(f"Caught exception in validator. Exception: {e}")
            return (False, error_func(value))
    return validator


def or_validators(*args, **kwargs):
    """Return a validator that is true only if one of the validators is true."""
    return (
        lambda value: (True, None)
        if any([validator(value)[0] for validator in args])
        else (False, " or ".join([validator(value)[1] for validator in args]))
    )


def and_validators(validator1, validator2):
    """Return a validator that is true only if both validators are true."""
    return (
        lambda value: (True, None)
        if (validator1(value)[0] and validator2(value)[0])
        else (
            False,
            (validator1(value)[1])
            if validator1(value)[1] is not None
            else "" + " and " + validator2(value)[1]
            if validator2(value)[1] is not None
            else "",
        )
    )


def extended_and_validators(*args, **kwargs):
    """Return a validator that is true only if all validators are true."""
    def returned_func(value):
        if all([validator(value)[0] for validator in args]):
            return (True, None)
        else:
            return (False, "".join(
                [
                    " and " + validator(value)[1] if validator(value)[0] else ""
                    for validator in args
                ]
            ))
    return returned_func


def if_then_validator(
    condition_field, condition_function, result_field, result_function
):
    """Return second validation if the first validator is true.

    :param condition_field: function that returns (bool, string) to represent validation state
    :param condition_function: function that returns (bool, string) to represent validation state
    :param result_field: function that returns (bool, string) to represent validation state
    :param result_function: function that returns (bool, string) to represent validation state
    """

    def if_then_validator_func(value):
        value1 = (
            value[condition_field]
            if type(value) is dict
            else getattr(value, condition_field)
        )
        value2 = (
            value[result_field] if type(value) is dict else getattr(value, result_field)
        )

        validator1_result = condition_function(value1)
        validator2_result = result_function(value2)

        if not validator1_result[0]:
            returned_value = (True, None, [condition_field, result_field])
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

                error_message = f"if {condition_field} " + (center_error) + f" then {result_field} " + ending_error
            else:
                error_message = None

            returned_value = (validator2_result[0], error_message, [condition_field, result_field])

        return returned_value

    return lambda value: if_then_validator_func(value)


def sumIsEqual(condition_field, sum_fields=[]):
    """Validate that the sum of the sum_fields equals the condition_field."""

    def sumIsEqualFunc(value):
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
                f"The sum of {sum_fields} does not equal {condition_field}.",
                fields,
            )
        )

    return lambda value: sumIsEqualFunc(value)


def sumIsLarger(fields, val):
    """Validate that the sum of the fields is larger than val."""

    def sumIsLargerFunc(value):
        sum = 0
        for field in fields:
            temp_val = value[field] if type(value) is dict else getattr(value, field)
            sum += 0 if temp_val is None else temp_val

        return (
            (True, None, [field for field in fields])
            if sum > val
            else (
                False,
                f"The sum of {fields} is not larger than {val}.",
                [field for field in fields],
            )
        )

    return lambda value: sumIsLargerFunc(value)


# generic validators


def matches(option):
    """Validate that value is equal to option."""
    return make_validator(
        lambda value: value == option, lambda value: f"{value} does not match {option}."
    )


def notMatches(option):
    """Validate that value is not equal to option."""
    return make_validator(
        lambda value: value != option, lambda value: f"{value} matches {option}."
    )


def oneOf(options=[]):
    """Validate that value does not exist in the provided options array."""
    return make_validator(
        lambda value: value in options, lambda value: f"{value} is not in {options}."
    )


def notOneOf(options=[]):
    """Validate that value exists in the provided options array."""
    return make_validator(
        lambda value: value not in options, lambda value: f"{value} is in {options}."
    )


def between(min, max):
    """Validate value, when casted to int, is greater than min and less than max."""
    return make_validator(
        lambda value: int(value) > min and int(value) < max,
        lambda value: f"{value} is not between {min} and {max}.",
    )


def hasLength(length, error_func=None):
    """Validate that value (string or array) has a length matching length param."""
    return make_validator(
        lambda value: len(value) == length,
        lambda value: error_func(value, length)
        if error_func
        else f"Value length {len(value)} does not match {length}.",
    )


def contains(substring):
    """Validate that string value contains the given substring param."""
    return make_validator(
        lambda value: value.find(substring) != -1,
        lambda value: f"{value} does not contain {substring}.",
    )


def startsWith(substring):
    """Validate that string value starts with the given substring param."""
    return make_validator(
        lambda value: value.startswith(substring),
        lambda value: f"{value} does not start with {substring}.",
    )


def isNumber():
    """Validate that value can be casted to a number."""
    return make_validator(
        lambda value: value.isnumeric(), lambda value: f"{value} is not a number."
    )


def isAlphaNumeric():
    """Validate that value is alphanumeric."""
    return make_validator(
        lambda value: value.isalnum(), lambda value: f"{value} is not alphanumeric."
    )


def isBlank():
    """Validate that string value is blank."""
    return make_validator(
        lambda value: value.isspace(), lambda value: f"{value} is not blank."
    )


def isInStringRange(lower, upper):
    """Validate that string value is in a specific range."""
    return make_validator(
        lambda value: int(value) >= lower and int(value) <= upper,
        lambda value: f"{value} is not in range [{lower}, {upper}].",
    )


def isStringLargerThan(val):
    """Validate that string value is larger than val."""
    return make_validator(
        lambda value: int(value) > val,
        lambda value: f"{value} is not larger than {val}.",
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
        lambda value: f'{str(value)} contains blanks between positions {start} and {end if end else len(str(value))}.'
    )


def isEmpty(start=0, end=None):
    """Validate that string value is only blanks."""
    return make_validator(
        lambda value: _is_empty(value, start, end),
        lambda value: f'{value} is not blank between positions {start} and {end if end else len(value)}.'
    )


def notZero(number_of_zeros=1):
    """Validate that value is not zero."""
    return make_validator(
        lambda value: value != "0" * number_of_zeros, lambda value: f"{value} is zero."
    )


def isLargerThan(LowerBound):
    """Validate that value is larger than the given value."""
    return make_validator(
        lambda value: float(value) > LowerBound if value is not None else False,
        lambda value: f"{value} is not larger than {LowerBound}.",
    )


def isSmallerThan(UpperBound):
    """Validate that value is smaller than the given value."""
    return make_validator(
        lambda value: value < UpperBound,
        lambda value: f"{value} is not smaller than {UpperBound}.",
    )


def isLargerThanOrEqualTo(LowerBound):
    """Validate that value is larger than the given value."""
    return make_validator(
        lambda value: value >= LowerBound,
        lambda value: f"{value} is not larger than {LowerBound}.",
    )


def isSmallerThanOrEqualTo(UpperBound):
    """Validate that value is smaller than the given value."""
    return make_validator(
        lambda value: value <= UpperBound,
        lambda value: f"{value} is not smaller than {UpperBound}.",
    )


def isInLimits(LowerBound, UpperBound):
    """Validate that value is in a range including the limits."""
    return make_validator(
        lambda value: value >= LowerBound and value <= UpperBound,
        lambda value: f"{value} is not larger or equal to {LowerBound} and smaller or equal to {UpperBound}.",
    )


# custom validators


def dateMonthIsValid():
    """Validate that in a monthyear combination, the month is a valid month."""
    return make_validator(
        lambda value: int(str(value)[4:6]) in range(1, 13),
        lambda value: f"{str(value)[4:6]} is not a valid month.",
    )


def olderThan(min_age):
    """Validate that value is larger than min_age."""
    return make_validator(
        lambda value: date.today().year - int(str(value)[:4]) > min_age,
        lambda value: f"{date.today().year - int(str(value)[:4])} is not larger than {min_age}.",
    )


def dateYearIsLargerThan(year):
    """Validate that in a monthyear combination, the year is larger than the given year."""
    return make_validator(
        lambda value: int(str(value)[:4]) > year,
        lambda value: f"{str(value)[:4]} year must be larger than {year}.",
    )


def quarterIsValid():
    """Validate in a year quarter combination, the quarter is valid."""
    return make_validator(
        lambda value: int(str(value)[-1]) > 0 and int(str(value)[-1]) < 5,
        lambda value: f"{str(value)[-1]} is not a valid quarter.",
    )


def validateSSN():
    """Validate that SSN value is not a repeating digit."""
    options = [str(i) * 9 for i in range(0, 10)]
    return make_validator(
        lambda value: value not in options, lambda value: f"{value} is in {options}."
    )


def validateRace():
    """Validate race."""
    return make_validator(
        lambda value: value >= 0 and value <= 2,
        lambda value: f"{value} is not greater than or equal to 0 or smaller than or equal to 1.",
    )


# outlier validators
def validate__FAM_AFF__SSN():
    """
    Validate social security number provided.

    If item FAMILY_AFFILIATION ==2 and item CITIZENSHIP_STATUS ==1 or 2,
    then item SSN != 000000000 -- 999999999.
    """
    # value is instance
    def validate(instance):
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
                    "If FAMILY_AFFILIATION ==2 and CITIZENSHIP_STATUS==1 or 2, then SSN != 000000000 -- 999999999.",
                    ["FAMILY_AFFILIATION", "CITIZENSHIP_STATUS", "SSN"],
                )
            else:
                return (True, None, ["FAMILY_AFFILIATION", "CITIZENSHIP_STATUS", "SSN"])
        else:
            return (True, None, ["FAMILY_AFFILIATION", "CITIZENSHIP_STATUS", "SSN"])

    return lambda instance: validate(instance)


def validate__FAM_AFF__HOH__Fed_Time():
    """If FAMILY_AFFILIATION == 1 and RELATIONSHIP_HOH== 1 or 2, then MONTHS_FED_TIME_LIMIT >= 1."""
    # value is instance
    def validate(instance):
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
                return (False,
                        "If FAMILY_AFFILIATION == 2 and MONTHS_FED_TIME_LIMIT== 1 or 2,"
                        + " then MONTHS_FED_TIME_LIMIT > 1.",
                        ['FAMILY_AFFILIATION', 'MONTHS_FED_TIME_LIMIT']
                        )
            else:
                return (
                    True,
                    None,
                    ["FAMILY_AFFILIATION", "RELATIONSHIP_HOH", "MONTHS_FED_TIME_LIMIT"],
                )
        else:
            return (
                True,
                None,
                ["FAMILY_AFFILIATION", "RELATIONSHIP_HOH", "MONTHS_FED_TIME_LIMIT"],
            )

    return lambda instance: validate(instance)


def validate__FAM_AFF__HOH__Count_Fed_Time():
    """If FAMILY_AFFILIATION == 1 and RELATIONSHIP_HOH== 1 or 2, then COUNTABLE_MONTH_FED_TIME >= 1."""
    # value is instance
    def validate(instance):
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
                return (
                    False,
                    "If FAMILY_AFFILIATION == 2 and COUNTABLE_MONTH_FED_TIME== 1 or 2, then "
                    + "COUNTABLE_MONTH_FED_TIME > 1.",
                    [
                        "FAMILY_AFFILIATION",
                        "RELATIONSHIP_HOH",
                        "COUNTABLE_MONTH_FED_TIME",
                    ],
                )
            else:
                return (
                    True,
                    None,
                    [
                        "FAMILY_AFFILIATION",
                        "RELATIONSHIP_HOH",
                        "COUNTABLE_MONTH_FED_TIME",
                    ],
                )
        else:
            return (
                True,
                None,
                ["FAMILY_AFFILIATION", "RELATIONSHIP_HOH", "COUNTABLE_MONTH_FED_TIME"],
            )

    return lambda instance: validate(instance)


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
