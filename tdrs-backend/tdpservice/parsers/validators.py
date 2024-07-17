"""Generic parser validator functions for use in schema definitions."""

import datetime
import logging
from dataclasses import dataclass
from typing import Any
# from tdpservice.parsers.row_schema import RowSchema
from tdpservice.parsers.models import ParserErrorCategoryChoices
from tdpservice.parsers.util import fiscal_to_calendar, year_month_to_year_quarter, clean_options_string

logger = logging.getLogger(__name__)


def value_is_empty(value, length, extra_vals={}):
    """Handle 'empty' values as field inputs."""
    # TODO: have to build mixed type handling for value
    empty_values = {
        '',
        ' '*length,  # '     '
        '#'*length,  # '#####'
        '_'*length,  # '_____'
    }

    empty_values = empty_values.union(extra_vals)

    return value is None or value in empty_values


@dataclass
class ValidationErrorArgs:
    """Dataclass for args to `make_validator` `error_func`s."""

    value: Any
    row_schema: object  # RowSchema causes circular import
    friendly_name: str
    item_num: str
    error_context_format: str = 'prefix'


def format_error_context(eargs: ValidationErrorArgs):
    """Format the error message for consistency across cat2 validators."""
    match eargs.error_context_format:
        case 'inline':
            return f'Item {eargs.item_num} ({eargs.friendly_name})'

        case 'prefix' | _:
            return f'{eargs.row_schema.record_type} Item {eargs.item_num} ({eargs.friendly_name}):'


# higher order validator functions


def make_validator(validator_func, error_func):
    """Return a function accepting a value input and returning (bool, string) to represent validation state."""
    def validator(value, row_schema=None, friendly_name=None, item_num=None, error_context_format='prefix'):
        eargs = ValidationErrorArgs(
            value=value,
            row_schema=row_schema,
            friendly_name=friendly_name,
            item_num=item_num,
            error_context_format=error_context_format
        )

        try:
            if validator_func(value):
                return (True, None)
            return (False, error_func(eargs))
        except Exception as e:
            logger.debug(f"Caught exception in validator. Exception: {e}")
            return (False, error_func(eargs))
    return validator


def or_validators(*args, **kwargs):
    """Return a validator that is true only if one of the validators is true."""
    return (
        lambda value, row_schema, friendly_name,
        item_num, error_context_format='inline': (True, None)
        if any([
            validator(value, row_schema, friendly_name, item_num, error_context_format)[0] for validator in args
        ])
        else (False, " or ".join([
            validator(value, row_schema, friendly_name, item_num, error_context_format)[1] for validator in args
        ]))
    )


def and_validators(validator1, validator2):
    """Return a validator that is true only if both validators are true."""
    return (
        lambda value, row_schema, friendly_name, item_num: (True, None)
        if (validator1(value, row_schema, friendly_name, item_num, 'inline')[0]
            and validator2(value, row_schema, friendly_name, item_num, 'inline')[0])
        else (
            False,
            (validator1(value, row_schema, friendly_name, item_num, 'inline')[1])
            if validator1(value, row_schema, friendly_name, item_num, 'inline')[1] is not None
            else "" + " and " + validator2(value)[1]
            if validator2(value, row_schema, friendly_name, item_num, 'inline')[1] is not None
            else "",
        )
    )

def or_priority_validators(validators=[]):
    """Return a validator that is true based on a priority of validators.

    validators: ordered list of validators to be checked
    """
    def or_priority_validators_func(value, rows_schema, friendly_name=None, item_num=None):
        for validator in validators:
            if not validator(value, rows_schema, friendly_name, item_num, 'inline')[0]:
                return (False, validator(value, rows_schema,
                                         friendly_name, item_num, 'inline')[1])
        return (True, None)

    return or_priority_validators_func


def extended_and_validators(*args, **kwargs):
    """Return a validator that is true only if all validators are true."""
    def returned_func(value, row_schema, friendly_name, item_num):
        if all([validator(value, row_schema, friendly_name, item_num, 'inline')[0] for validator in args]):
            return (True, None)
        else:
            return (False, "".join(
                [
                    " and " + validator(value, row_schema, friendly_name, item_num, 'inline')[1]
                    if validator(value, row_schema, friendly_name, item_num, 'inline')[0] else ""
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

        condition_field = row_schema.get_field_by_name(condition_field_name)
        result_field = row_schema.get_field_by_name(result_field_name)

        validator1_result = condition_function(
            value1,
            row_schema,
            condition_field.friendly_name,
            condition_field.item,
            'inline'
        )
        validator2_result = result_function(
            value2,
            row_schema,
            result_field.friendly_name,
            result_field.item,
            'inline'
        )

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
                                 " then " + ending_error)
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
    def validate_reporting_month_year_fields_header(
            line, row_schema, friendly_name, item_num, error_context_format=None):

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


def recordHasLength(length):
    """Validate that value (string or array) has a length matching length param."""
    return make_validator(
        lambda value: len(value) == length,
        lambda eargs: f"{eargs.row_schema.record_type}: record length is "
        f"{len(eargs.value)} characters but must be {length}.",
    )


def recordHasLengthBetween(lower, upper, error_func=None):
    """Validate that value (string or array) has a length matching length param."""
    return make_validator(
        lambda value: len(value) >= lower and len(value) <= upper,
        lambda eargs: error_func(eargs.value, lower, upper)
        if error_func
        else
        f"{eargs.row_schema.record_type}: record length of {len(eargs.value)} "
        f"characters is not in the range [{lower}, {upper}].",
    )


def caseNumberNotEmpty(start=0, end=None):
    """Validate that string value isn't only blanks."""
    return make_validator(
        lambda value: not _is_empty(value, start, end),
        lambda eargs: f'{eargs.row_schema.record_type}: Case number {str(eargs.value)} cannot contain blanks.'
    )


def calendarQuarterIsValid(start=0, end=None):
    """Validate that the calendar quarter value is valid."""
    return make_validator(
        lambda value: value[start:end].isnumeric() and int(value[start:end - 1]) >= 2020
        and int(value[end - 1:end]) > 0 and int(value[end - 1:end]) < 5,
        lambda eargs: f"{eargs.row_schema.record_type}: {eargs.value[start:end]} is invalid. "
        "Calendar Quarter must be a numeric representing the Calendar Year and Quarter formatted as YYYYQ",
    )


# generic validators


def matches(option, error_func=None):
    """Validate that value is equal to option."""
    return make_validator(
        lambda value: value == option,
        lambda eargs: error_func(option)
        if error_func
        else f"{format_error_context(eargs)} {eargs.value} does not match {option}.",
    )


def notMatches(option):
    """Validate that value is not equal to option."""
    return make_validator(
        lambda value: value != option,
        lambda eargs: f"{format_error_context(eargs)} {eargs.value} matches {option}."
    )


def oneOf(options=[]):
    """Validate that value does not exist in the provided options array."""
    """
    accepts options as list of: string, int or string range ("3-20")
    """

    def check_option(value, options):
        # split the option if it is a range and append the range to the options
        for option in options:
            if "-" in str(option):
                start, end = option.split("-")
                options.extend([i for i in range(int(start), int(end) + 1)])
                options.remove(option)
        return value in options

    return make_validator(
        lambda value: check_option(value, options),
        lambda eargs:
            f"{format_error_context(eargs)} {eargs.value} is not in {clean_options_string(options)}."
    )


def notOneOf(options=[]):
    """Validate that value exists in the provided options array."""
    return make_validator(
        lambda value: value not in options,
        lambda eargs:
            f"{format_error_context(eargs)} {eargs.value} is in {clean_options_string(options)}."
    )


def between(min, max):
    """Validate value, when casted to int, is greater than min and less than max."""
    return make_validator(
        lambda value: int(value) > min and int(value) < max,
        lambda eargs:
            f"{format_error_context(eargs)} {eargs.value} is not between {min} and {max}.",
    )


def fieldHasLength(length):
    """Validate that the field value (string or array) has a length matching length param."""
    return make_validator(
        lambda value: len(value) == length,
        lambda eargs:
            f"{eargs.row_schema.record_type} field length is {len(eargs.value)} characters but must be {length}.",
    )


def hasLengthGreaterThan(val, error_func=None):
    """Validate that value (string or array) has a length greater than val."""
    return make_validator(
        lambda value: len(value) >= val,
        lambda eargs:
            f"Value length {len(eargs.value)} is not greater than {val}.",
    )


def intHasLength(num_digits):
    """Validate the number of digits in an integer."""
    return make_validator(
        lambda value: sum(c.isdigit() for c in str(value)) == num_digits,
        lambda eargs:
            f"{format_error_context(eargs)} {eargs.value} does not have exactly {num_digits} digits.",
    )


def contains(substring):
    """Validate that string value contains the given substring param."""
    return make_validator(
        lambda value: value.find(substring) != -1,
        lambda eargs: f"{format_error_context(eargs)} {eargs.value} does not contain {substring}.",
    )


def startsWith(substring, error_func=None):
    """Validate that string value starts with the given substring param."""
    return make_validator(
        lambda value: value.startswith(substring),
        lambda eargs: error_func(substring)
        if error_func
        else f"{format_error_context(eargs)} {eargs.value} does not start with {substring}.",
    )


def isNumber():
    """Validate that value can be casted to a number."""
    return make_validator(
        lambda value: str(value).strip().isnumeric(),
        lambda eargs: f"{format_error_context(eargs)} {eargs.value} is not a number."
    )


def isAlphaNumeric():
    """Validate that value is alphanumeric."""
    return make_validator(
        lambda value: value.isalnum(),
        lambda eargs: f"{format_error_context(eargs)} {eargs.value} is not alphanumeric."
    )


def isBlank():
    """Validate that string value is blank."""
    return make_validator(
        lambda value: value.isspace(),
        lambda eargs: f"{format_error_context(eargs)} {eargs.value} is not blank."
    )


def isInStringRange(lower, upper):
    """Validate that string value is in a specific range."""
    return make_validator(
        lambda value: int(value) >= lower and int(value) <= upper,
        lambda eargs: f"{format_error_context(eargs)} {eargs.value} is not in range [{lower}, {upper}].",
    )


def isStringLargerThan(val):
    """Validate that string value is larger than val."""
    return make_validator(
        lambda value: int(value) > val,
        lambda eargs: f"{format_error_context(eargs)} {eargs.value} is not larger than {val}.",
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
        lambda eargs:
            f'{format_error_context(eargs)} {str(eargs.value)} contains blanks '
            f'between positions {start} and {end if end else len(str(eargs.value))}.'
    )


def isEmpty(start=0, end=None):
    """Validate that string value is only blanks."""
    return make_validator(
        lambda value: _is_empty(value, start, end),
        lambda eargs:
            f'{format_error_context(eargs)} {eargs.value} is not blank '
            f'between positions {start} and {end if end else len(eargs.value)}.'
    )


def notZero(number_of_zeros=1):
    """Validate that value is not zero."""
    return make_validator(
        lambda value: value != "0" * number_of_zeros,
        lambda eargs: f"{format_error_context(eargs)} {eargs.value} is zero."
    )


def isLargerThan(LowerBound):
    """Validate that value is larger than the given value."""
    return make_validator(
        lambda value: float(value) > LowerBound if value is not None else False,
        lambda eargs: f"{format_error_context(eargs)} {eargs.value} is not larger than {LowerBound}.",
    )


def isSmallerThan(UpperBound):
    """Validate that value is smaller than the given value."""
    return make_validator(
        lambda value: value < UpperBound,
        lambda eargs: f"{format_error_context(eargs)} {eargs.value} is not smaller than {UpperBound}.",
    )


def isLargerThanOrEqualTo(LowerBound):
    """Validate that value is larger than the given value."""
    return make_validator(
        lambda value: value >= LowerBound,
        lambda eargs: f"{format_error_context(eargs)} {eargs.value} is not larger than {LowerBound}.",
    )


def isSmallerThanOrEqualTo(UpperBound):
    """Validate that value is smaller than the given value."""
    return make_validator(
        lambda value: value <= UpperBound,
        lambda eargs: f"{format_error_context(eargs)} {eargs.value} is not smaller than {UpperBound}.",
    )


def isInLimits(LowerBound, UpperBound):
    """Validate that value is in a range including the limits."""
    return make_validator(
        lambda value: int(value) >= LowerBound and int(value) <= UpperBound,
        lambda eargs:
            f"{format_error_context(eargs)} {eargs.value} is not larger or equal "
            f"to {LowerBound} and smaller or equal to {UpperBound}."
    )

# custom validators

def dateMonthIsValid():
    """Validate that in a monthyear combination, the month is a valid month."""
    return make_validator(
        lambda value: int(str(value)[4:6]) in range(1, 13),
        lambda eargs: f"{format_error_context(eargs)} {str(eargs.value)[4:6]} is not a valid month.",
    )

def dateDayIsValid():
    """Validate that in a monthyearday combination, the day is a valid day."""
    return make_validator(
        lambda value: int(str(value)[6:]) in range(1, 32),
        lambda eargs: f"{format_error_context(eargs)} {str(eargs.value)[6:]} is not a valid day.",
    )


def olderThan(min_age):
    """Validate that value is larger than min_age."""
    return make_validator(
        lambda value: datetime.date.today().year - int(str(value)[:4]) > min_age,
        lambda eargs:
            f"{format_error_context(eargs)} {str(eargs.value)[:4]} must be less "
            f"than or equal to {datetime.date.today().year - min_age} to meet the minimum age requirement."
    )


def dateYearIsLargerThan(year):
    """Validate that in a monthyear combination, the year is larger than the given year."""
    return make_validator(
        lambda value: int(str(value)[:4]) > year,
        lambda eargs: f"{format_error_context(eargs)} Year {str(eargs.value)[:4]} must be larger than {year}.",
    )


def quarterIsValid():
    """Validate in a year quarter combination, the quarter is valid."""
    return make_validator(
        lambda value: int(str(value)[-1]) > 0 and int(str(value)[-1]) < 5,
        lambda eargs: f"{format_error_context(eargs)} {str(eargs.value)[-1]} is not a valid quarter.",
    )


def validateSSN():
    """Validate that SSN value is not a repeating digit."""
    options = [str(i) * 9 for i in range(0, 10)]
    return make_validator(
        lambda value: value not in options,
        lambda eargs: f"{format_error_context(eargs)} {eargs.value} is in {options}."
    )


def validateRace():
    """Validate race."""
    return make_validator(
        lambda value: value >= 0 and value <= 2,
        lambda eargs:
            f"{format_error_context(eargs)} {eargs.value} is not greater than or equal to 0 "
            "or smaller than or equal to 2."
    )


def validateRptMonthYear():
    """Validate RPT_MONTH_YEAR."""
    return make_validator(
        lambda value: value[2:8].isdigit() and int(value[2:6]) > 1900 and value[6:8] in {"01", "02", "03", "04", "05",
                                                                                         "06", "07", "08", "09", "10",
                                                                                         "11", "12"},
        lambda eargs:
            f"{format_error_context(eargs)} The value: {eargs.value[2:8]}, "
            "does not follow the YYYYMM format for Reporting Year and Month.",
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


def _is_all_zeros(value, start, end):
    """Check if a value is all zeros."""
    return value[start:end] == "0" * (end - start)


def t3_m3_child_validator(which_child):
    """T3 child validator."""
    def t3_first_child_validator_func(value, temp, friendly_name, item_num):
        if not _is_empty(value, 1, 60) and len(value) >= 60:
            return (True, None)
        elif not len(value) >= 60:
            return (False, f"The first child record is too short at {len(value)} "
                    "characters and must be at least 60 characters.")
        else:
            return (False, "The first child record is empty.")

    def t3_second_child_validator_func(value, temp, friendly_name, item_num):
        if not _is_empty(value, 60, 101) and len(value) >= 101 and \
                not _is_empty(value, 8, 19) and \
                not _is_all_zeros(value, 60, 101):
            return (True, None)
        elif not len(value) >= 101:
            return (False, f"The second child record is too short at {len(value)} "
                    "characters and must be at least 101 characters.")
        else:
            return (False, "The second child record is empty.")

    return t3_first_child_validator_func if which_child == 1 else t3_second_child_validator_func


def is_quiet_preparser_errors(min_length, empty_from=61, empty_to=101):
    """Return a function that checks if the length is valid and if the value is empty."""
    def return_value(value):
        is_length_valid = len(value) >= min_length
        is_empty = value_is_empty(
            value[empty_from:empty_to],
            len(value[empty_from:empty_to])
            )
        return not (is_length_valid and not is_empty and not _is_all_zeros(value, empty_from, empty_to))
    return return_value


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
