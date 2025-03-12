"""Overloads and custom validators for category 1 (preparsing)."""

from tdpservice.parsers.dataclasses import RawRow
from tdpservice.parsers.models import ParserErrorCategoryChoices
from tdpservice.parsers.util import fiscal_to_calendar, year_month_to_year_quarter
from tdpservice.parsers.validators import base
from tdpservice.parsers.validators.util import Result, make_validator, _is_all_zeros, _is_empty, value_is_empty
from tdpservice.parsers.dataclasses import ValidationErrorArgs


def format_error_context(eargs: ValidationErrorArgs):
    """Format the error message for consistency across cat1 validators."""
    return f'{eargs.row_schema.record_type} Item {eargs.item_num} ({eargs.friendly_name}):'


def recordIsNotEmpty(start=0, end=None, **kwargs):
    """Return a function that tests that a record/row is not empty."""
    return make_validator(
        base.isNotEmpty(start, end, **kwargs),
        lambda eargs: f'{format_error_context(eargs)} {str(eargs.value)} contains blanks '
        f'between positions {start} and {end if end else len(str(eargs.value))}.'
    )


def recordHasLength(length, **kwargs):
    """Return a function that tests that a record/row has the specified length."""
    return make_validator(
        base.hasLength(length, **kwargs),
        lambda eargs:
            f"{eargs.row_schema.record_type}: record length is {len(eargs.value)} characters but must be {length}.",
    )


def recordHasLengthBetween(min, max, **kwargs):
    """Return a function that tests that a record/row has a length between min and max."""
    _validator = base.isBetween(min, max, inclusive=True, **kwargs)
    return make_validator(
        lambda record: _validator(len(record)),
        lambda eargs:
            f"{eargs.row_schema.record_type}: record length of {len(eargs.value)} "
            f"characters is not in the range [{min}, {max}].",
    )


def recordStartsWith(substr, func=None, **kwargs):
    """Return a function that tests that a record/row starts with a specified substr."""
    return make_validator(
        base.startsWith(substr, **kwargs),
        func if func else lambda eargs: f'{eargs.value} must start with {substr}.'
    )


def caseNumberNotEmpty(start=0, end=None, **kwargs):
    """Return a function that tests that a record/row is not blank between the Case Number indices."""
    return make_validator(
        base.isNotEmpty(start, end, **kwargs),
        lambda eargs: f'{eargs.row_schema.record_type}: Case number {str(eargs.value)} cannot contain blanks.'
    )


def or_priority_validators(validators=[]):
    """Return a validator that is true based on a priority of validators.

    validators: ordered list of validators to be checked
    """
    def or_priority_validators_func(value, eargs):
        for validator in validators:
            result = validator(value, eargs)
            if not result.valid:
                return result
        return Result()

    return or_priority_validators_func


def validate_fieldYearMonth_with_headerYearQuarter():
    """Validate that the field year and month match the header year and quarter."""
    def validate_reporting_month_year_fields_header(row: RawRow, eargs):
        row_schema = eargs.row_schema
        field_month_year = row_schema.get_field_values_by_names(
            row, ['RPT_MONTH_YEAR']).get('RPT_MONTH_YEAR')
        df_quarter = row_schema.datafile.quarter
        df_year = row_schema.datafile.year

        # get reporting month year from header
        field_year, field_quarter = year_month_to_year_quarter(f"{field_month_year}")
        file_calendar_year, file_calendar_qtr = fiscal_to_calendar(df_year, f"{df_quarter}")

        if str(file_calendar_year) == str(field_year) and file_calendar_qtr == field_quarter:
            return Result()

        return Result(
            valid=False,
            error=(f"{row_schema.record_type}: Reporting month year {field_month_year} "
                   f"does not match file reporting year:{df_year}, quarter:{df_quarter}."),
        )

    return validate_reporting_month_year_fields_header


def validateRptMonthYear():
    """Validate RPT_MONTH_YEAR."""
    return make_validator(
        lambda value: value[2:8].isdigit() and int(value[2:6]) > 1900 and value[6:8] in {
            "01", "02", "03", "04", "05", "06", "07", "08", "09", "10", "11", "12"
        },
        lambda eargs:
            f"{format_error_context(eargs)} The value: {eargs.value[2:8]}, "
            "does not follow the YYYYMM format for Reporting Year and Month.",
    )


def t3_m3_child_validator(which_child):
    """T3 child validator."""
    def t3_first_child_validator_func(row: RawRow, eargs):
        if not _is_empty(row, 1, 60) and len(row) >= 60:
            return Result()
        elif not len(row) >= 60:
            return Result(valid=False, error=f"The first child record is too short at {len(row)} "
                          "characters and must be at least 60 characters.")
        else:
            return Result(valid=False, error="The first child record is empty.")

    def t3_second_child_validator_func(row: RawRow, eargs):
        if not _is_empty(row, 60, 101) and len(row) >= 101 and \
                not _is_empty(row, 8, 19) and \
                not _is_all_zeros(row, 60, 101):
            return Result()
        elif not len(row) >= 101:
            return Result(valid=False, error=(f"The second child record is too short at {len(row)} "
                                              "characters and must be at least 101 characters."))
        else:
            return Result(valid=False, error="The second child record is empty.")

    return t3_first_child_validator_func if which_child == 1 else t3_second_child_validator_func


def calendarQuarterIsValid(start=0, end=None):
    """Validate that the calendar quarter value is valid."""
    return make_validator(
        lambda value: value[start:end].isnumeric() and int(value[start:end - 1]) >= 2020
        and int(value[end - 1:end]) > 0 and int(value[end - 1:end]) < 5,
        lambda eargs: f"{eargs.row_schema.record_type}: {eargs.value[start:end]} is invalid. "
        "Calendar Quarter must be a numeric representing the Calendar Year and Quarter formatted as YYYYQ",
    )


# file pre-check validators
# TODO: the validators below are called explicitly with the ability to generate an error. They need a different method
# to deprecate themselves if we ever choose to.
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

    return Result(valid=is_valid, error=error)


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

    return Result(valid=is_valid, error=error)


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
    return Result(valid=is_valid, error=error)
