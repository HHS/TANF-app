import logging
from dataclasses import dataclass
from typing import Any
from tdpservice.parsers.models import ParserErrorCategoryChoices
from tdpservice.parsers.util import fiscal_to_calendar

logger = logging.getLogger(__name__)


def make_validator(validator_func, error_func):
    """Return a function accepting a value input and returning (bool, string) to represent validation state."""
    def validator(value, eargs):
        try:
            if validator_func(value):
                return (True, None)
        except Exception:
            logger.exception("Caught exception in validator.")
        return (False, error_func(eargs))

    return validator


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


def _is_empty(value, start, end):
    end = end if end else len(str(value))
    vlen = end - start
    subv = str(value)[start:end]
    return value_is_empty(subv, vlen) or len(subv) < vlen


def _is_all_zeros(value, start, end):
    """Check if a value is all zeros."""
    return value[start:end] == "0" * (end - start)


def evaluate_all(validators, value, eargs):
    """Evaluate all validators in the list and compose the result tuples in an array."""
    return [
        validator(value, eargs)
        for validator in validators
    ]


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


@dataclass
class ValidationErrorArgs:
    """Dataclass for args to `make_validator` `error_func`s."""

    value: Any
    row_schema: object  # RowSchema causes circular import
    friendly_name: str
    item_num: str
    # error_context_format: str = 'prefix'
