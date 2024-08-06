"""Overloaded base validators and custom validators for category 2 validation (field validation)."""

from tdpservice.parsers.util import clean_options_string
from . import base
from .util import ValidationErrorArgs, make_validator


def format_error_context(eargs: ValidationErrorArgs):
    """Format the error message for consistency across cat2 validators."""
    return f'{eargs.row_schema.record_type} Item {eargs.item_num} ({eargs.friendly_name}):'


def isEqual(option, **kwargs):
    """Return a custom message for the isEqual validator."""
    return make_validator(
        base.isEqual(option, **kwargs),
        lambda eargs: f"{format_error_context(eargs)} {eargs.value} does not match {option}."
    )


def isNotEqual(option, **kwargs):
    """Return a custom message for the isNotEqual validator."""
    return make_validator(
        base.isNotEqual(option, **kwargs),
        lambda eargs: f"{format_error_context(eargs)} {eargs.value} matches {option}."
    )


def isOneOf(options, **kwargs):
    """Return a custom message for the isOneOf validator."""
    return make_validator(
        base.isOneOf(options, **kwargs),
        lambda eargs: f"{format_error_context(eargs)} {eargs.value} is not in {clean_options_string(options)}."
    )


def isNotOneOf(options, **kwargs):
    """Return a custom message for the isNotOneOf validator."""
    return make_validator(
        base.isNotOneOf(options, **kwargs),
        lambda eargs: f"{format_error_context(eargs)} {eargs.value} is in {clean_options_string(options)}."
    )


def isGreaterThan(option, inclusive=False, **kwargs):
    """Return a custom message for the isGreaterThan validator."""
    return make_validator(
        base.isGreaterThan(option, inclusive, **kwargs),
        lambda eargs: f"{format_error_context(eargs)} {eargs.value} is not larger than {option}."
    )


def isLessThan(option, inclusive=False, **kwargs):
    """Return a custom message for the isLessThan validator."""
    return make_validator(
        base.isLessThan(option, inclusive, **kwargs),
        lambda eargs: f"{format_error_context(eargs)} {eargs.value} is not smaller than {option}."
    )


def isBetween(min, max, inclusive=False, **kwargs):
    """Return a custom message for the isBetween validator."""
    def inclusive_err(eargs):
        return f"{format_error_context(eargs)} {eargs.value} is not in range [{min}, {max}]."

    def exclusive_err(eargs):
        return f"{format_error_context(eargs)} {eargs.value} is not between {min} and {max}."

    return make_validator(
        base.isBetween(min, max, inclusive, **kwargs),
        inclusive_err if inclusive else exclusive_err
    )


def startsWith(substr, **kwargs):
    """Return a custom message for the startsWith validator."""
    return make_validator(
        base.startsWith(substr, **kwargs),
        lambda eargs: f"{format_error_context(eargs)} {eargs.value} does not start with {substr}."
    )


def contains(substr, **kwargs):
    """Return a custom message for the contains validator."""
    return make_validator(
        base.contains(substr, **kwargs),
        lambda eargs: f"{format_error_context(eargs)} {eargs.value} does not contain {substr}."
    )


def isNumber(**kwargs):
    """Return a custom message for the isNumber validator."""
    return make_validator(
        base.isNumber(**kwargs),
        lambda eargs: f"{format_error_context(eargs)} {eargs.value} is not a number."
    )


def isAlphaNumeric(**kwargs):
    """Return a custom message for the isAlphaNumeric validator."""
    return make_validator(
        base.isAlphaNumeric(**kwargs),
        lambda eargs: f"{format_error_context(eargs)} {eargs.value} is not alphanumeric."
    )


def isEmpty(start=0, end=None, **kwargs):
    """Return a custom message for the isEmpty validator."""
    return make_validator(
        base.isEmpty(**kwargs),
        lambda eargs: f'{format_error_context(eargs)} {eargs.value} is not blank '
        f'between positions {start} and {end if end else len(eargs.value)}.'
    )


def isNotEmpty(start=0, end=None, **kwargs):
    """Return a custom message for the isNotEmpty validator."""
    return make_validator(
        base.isNotEmpty(**kwargs),
        lambda eargs: f'{format_error_context(eargs)} {str(eargs.value)} contains blanks '
        f'between positions {start} and {end if end else len(str(eargs.value))}.'
    )


def isBlank(**kwargs):
    """Return a custom message for the isBlank validator."""
    return make_validator(
        base.isBlank(**kwargs),
        lambda eargs: f"{format_error_context(eargs)} {eargs.value} is not blank."
    )


def hasLength(length, **kwargs):
    """Return a custom message for the hasLength validator."""
    return make_validator(
        base.hasLength(length, **kwargs),
        lambda eargs: f"{format_error_context(eargs)} field length "
        f"is {len(eargs.value)} characters but must be {length}.",
    )


def hasLengthGreaterThan(length, inclusive=False, **kwargs):
    """Return a custom message for the hasLengthGreaterThan validator."""
    return make_validator(
        base.hasLengthGreaterThan(length, inclusive, **kwargs),
        lambda eargs: f"{format_error_context(eargs)} Value length {len(eargs.value)} is not greater than {length}."
    )


def intHasLength(length, **kwargs):
    """Return a custom message for the intHasLength validator."""
    return make_validator(
        base.intHasLength(length, **kwargs),
        lambda eargs: f"{format_error_context(eargs)} {eargs.value} does not have exactly {length} digits.",
    )


def isNotZero(number_of_zeros=1, **kwargs):
    """Return a custom message for the isNotZero validator."""
    return make_validator(
        base.isNotZero(number_of_zeros, **kwargs),
        lambda eargs: f"{format_error_context(eargs)} {eargs.value} is zero."
    )


# the remaining can be written using the previous validator functions
def dateYearIsLargerThan(year, **kwargs):
    """Validate that in a monthyear combination, the year is larger than the given year."""
    _validator = base.dateYearIsLargerThan(year, **kwargs)
    return make_validator(
        lambda value: _validator(int(str(value)[:4])),
        lambda eargs: f"{format_error_context(eargs)} Year {str(eargs.value)[:4]} must be larger than {year}.",
    )


def dateMonthIsValid(**kwargs):
    """Validate that in a monthyear combination, the month is a valid month."""
    _validator = base.dateMonthIsValid(**kwargs)
    return make_validator(
        lambda val: _validator(int(str(val)[4:6])),
        lambda eargs: f"{format_error_context(eargs)} {str(eargs.value)[4:6]} is not a valid month.",
    )


def dateDayIsValid(**kwargs):
    """Validate that in a monthyearday combination, the day is a valid day."""
    _validator = base.dateDayIsValid(**kwargs)
    return make_validator(
        lambda value: _validator(int(str(value)[6:])),
        lambda eargs: f"{format_error_context(eargs)} {str(eargs.value)[6:]} is not a valid day.",
    )


def quarterIsValid(**kwargs):
    """Validate in a year quarter combination, the quarter is valid."""
    _validator = base.quarterIsValid(**kwargs)
    return make_validator(
        lambda value: _validator(int(str(value)[-1])),
        lambda eargs: f"{format_error_context(eargs)} {str(eargs.value)[-1]} is not a valid quarter.",
    )


def validateRace():
    """Validate race."""
    return make_validator(
        base.isBetween(0, 2, inclusive=True),
        lambda eargs:
            f"{format_error_context(eargs)} {eargs.value} is not in range [0, 2]."
    )


def validateHeaderUpdateIndicator():
    """Validate the header update indicator."""
    return make_validator(
        base.isEqual('D'),
        lambda eargs:
            f"HEADER Update Indicator must be set to D instead of {eargs.value}. "
            "Please review Exporting Complete Data Using FTANF in the Knowledge Center."
    )
