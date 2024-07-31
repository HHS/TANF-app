"""Overloaded base validators and custom validators for category 2 validation (field validation)."""

from tdpservice.parsers.util import clean_options_string
from .base import ValidatorFunctions
from .util import ValidationErrorArgs, make_validator


def format_error_context(eargs: ValidationErrorArgs):
    """Format the error message for consistency across cat2 validators."""
    return f'{eargs.row_schema.record_type} Item {eargs.item_num} ({eargs.friendly_name}):'


class FieldValidators():
    """Base validator message overloads for field validation."""

    @staticmethod
    def isEqual(option, **kwargs):
        """Return a custom message for the isEqual validator."""
        return make_validator(
            ValidatorFunctions.isEqual(option, **kwargs),
            lambda eargs: f"{format_error_context(eargs)} {eargs.value} does not match {option}."
        )

    @staticmethod
    def isNotEqual(option, **kwargs):
        """Return a custom message for the isNotEqual validator."""
        return make_validator(
            ValidatorFunctions.isNotEqual(option, **kwargs),
            lambda eargs: f"{format_error_context(eargs)} {eargs.value} matches {option}."
        )

    @staticmethod
    def isOneOf(options, **kwargs):
        """Return a custom message for the isOneOf validator."""
        return make_validator(
            ValidatorFunctions.isOneOf(options, **kwargs),
            lambda eargs: f"{format_error_context(eargs)} {eargs.value} is not in {clean_options_string(options)}."
        )

    @staticmethod
    def isNotOneOf(options, **kwargs):
        """Return a custom message for the isNotOneOf validator."""
        return make_validator(
            ValidatorFunctions.isNotOneOf(options, **kwargs),
            lambda eargs: f"{format_error_context(eargs)} {eargs.value} is in {clean_options_string(options)}."
        )

    @staticmethod
    def isGreaterThan(option, inclusive=False, **kwargs):
        """Return a custom message for the isGreaterThan validator."""
        return make_validator(
            ValidatorFunctions.isGreaterThan(option, inclusive, **kwargs),
            lambda eargs: f"{format_error_context(eargs)} {eargs.value} is not larger than {option}."
        )

    @staticmethod
    def isLessThan(option, inclusive=False, **kwargs):
        """Return a custom message for the isLessThan validator."""
        return make_validator(
            ValidatorFunctions.isLessThan(option, inclusive, **kwargs),
            lambda eargs: f"{format_error_context(eargs)} {eargs.value} is not smaller than {option}."
        )

    @staticmethod
    def isBetween(min, max, inclusive=False, **kwargs):
        """Return a custom message for the isBetween validator."""
        def inclusive_err(eargs):
            return f"{format_error_context(eargs)} {eargs.value} is not in range [{min}, {max}]."

        def exclusive_err(eargs):
            return f"{format_error_context(eargs)} {eargs.value} is not between {min} and {max}."

        return make_validator(
            ValidatorFunctions.isBetween(min, max, inclusive, **kwargs),
            inclusive_err if inclusive else exclusive_err
        )

    @staticmethod
    def startsWith(substr, **kwargs):
        """Return a custom message for the startsWith validator."""
        return make_validator(
            ValidatorFunctions.startsWith(substr, **kwargs),
            lambda eargs: f"{format_error_context(eargs)} {eargs.value} does not start with {substr}."
        )

    @staticmethod
    def contains(substr, **kwargs):
        """Return a custom message for the contains validator."""
        return make_validator(
            ValidatorFunctions.contains(substr, **kwargs),
            lambda eargs: f"{format_error_context(eargs)} {eargs.value} does not contain {substr}."
        )

    @staticmethod
    def isNumber(**kwargs):
        """Return a custom message for the isNumber validator."""
        return make_validator(
            ValidatorFunctions.isNumber(**kwargs),
            lambda eargs: f"{format_error_context(eargs)} {eargs.value} is not a number."
        )

    @staticmethod
    def isAlphaNumeric(**kwargs):
        """Return a custom message for the isAlphaNumeric validator."""
        return make_validator(
            ValidatorFunctions.isAlphaNumeric(**kwargs),
            lambda eargs: f"{format_error_context(eargs)} {eargs.value} is not alphanumeric."
        )

    @staticmethod
    def isEmpty(start=0, end=None, **kwargs):
        """Return a custom message for the isEmpty validator."""
        return make_validator(
            ValidatorFunctions.isEmpty(**kwargs),
            lambda eargs: f'{format_error_context(eargs)} {eargs.value} is not blank '
            f'between positions {start} and {end if end else len(eargs.value)}.'
        )

    @staticmethod
    def isNotEmpty(start=0, end=None, **kwargs):
        """Return a custom message for the isNotEmpty validator."""
        return make_validator(
            ValidatorFunctions.isNotEmpty(**kwargs),
            lambda eargs: f'{format_error_context(eargs)} {str(eargs.value)} contains blanks '
            f'between positions {start} and {end if end else len(str(eargs.value))}.'
        )

    @staticmethod
    def isBlank(**kwargs):
        """Return a custom message for the isBlank validator."""
        return make_validator(
            ValidatorFunctions.isBlank(**kwargs),
            lambda eargs: f"{format_error_context(eargs)} {eargs.value} is not blank."
        )

    @staticmethod
    def hasLength(length, **kwargs):
        """Return a custom message for the hasLength validator."""
        return make_validator(
            ValidatorFunctions.hasLength(length, **kwargs),
            lambda eargs: f"{format_error_context(eargs)} field length "
            f"is {len(eargs.value)} characters but must be {length}.",
        )

    @staticmethod
    def hasLengthGreaterThan(length, inclusive=False, **kwargs):
        """Return a custom message for the hasLengthGreaterThan validator."""
        return make_validator(
            ValidatorFunctions.hasLengthGreaterThan(length, inclusive, **kwargs),
            lambda eargs: f"{format_error_context(eargs)} Value length {len(eargs.value)} is not greater than {length}."
        )

    @staticmethod
    def intHasLength(length, **kwargs):
        """Return a custom message for the intHasLength validator."""
        return make_validator(
            ValidatorFunctions.intHasLength(length, **kwargs),
            lambda eargs: f"{format_error_context(eargs)} {eargs.value} does not have exactly {length} digits.",
        )

    @staticmethod
    def isNotZero(number_of_zeros=1, **kwargs):
        """Return a custom message for the isNotZero validator."""
        return make_validator(
            ValidatorFunctions.isNotZero(number_of_zeros, **kwargs),
            lambda eargs: f"{format_error_context(eargs)} {eargs.value} is zero."
        )

    # the remaining can be written using the previous validator functions
    @staticmethod
    def dateYearIsLargerThan(year, **kwargs):
        """Validate that in a monthyear combination, the year is larger than the given year."""
        _validator = ValidatorFunctions.dateYearIsLargerThan(year, **kwargs)
        return make_validator(
            lambda value: _validator(int(str(value)[:4])),
            lambda eargs: f"{format_error_context(eargs)} Year {str(eargs.value)[:4]} must be larger than {year}.",
        )

    @staticmethod
    def dateMonthIsValid(**kwargs):
        """Validate that in a monthyear combination, the month is a valid month."""
        _validator = ValidatorFunctions.dateMonthIsValid(**kwargs)
        return make_validator(
            lambda val: _validator(int(str(val)[4:6])),
            lambda eargs: f"{format_error_context(eargs)} {str(eargs.value)[4:6]} is not a valid month.",
        )

    @staticmethod
    def dateDayIsValid(**kwargs):
        """Validate that in a monthyearday combination, the day is a valid day."""
        _validator = ValidatorFunctions.dateDayIsValid(**kwargs)
        return make_validator(
            lambda value: _validator(int(str(value)[6:])),
            lambda eargs: f"{format_error_context(eargs)} {str(eargs.value)[6:]} is not a valid day.",
        )

    @staticmethod
    def quarterIsValid(**kwargs):
        """Validate in a year quarter combination, the quarter is valid."""
        _validator = ValidatorFunctions.quarterIsValid(**kwargs)
        return make_validator(
            lambda value: _validator(int(str(value)[-1])),
            lambda eargs: f"{format_error_context(eargs)} {str(eargs.value)[-1]} is not a valid quarter.",
        )

    @staticmethod
    def validateRace():
        """Validate race."""
        return make_validator(
            ValidatorFunctions.isBetween(0, 2, inclusive=True),
            lambda eargs:
                f"{format_error_context(eargs)} {eargs.value} is not in range [0, 2]."
        )

    @staticmethod
    def validateHeaderUpdateIndicator():
        """Validate the header update indicator."""
        return make_validator(
            ValidatorFunctions.isEqual('D'),
            lambda eargs:
                f"HEADER Update Indicator must be set to D instead of {eargs.value}. "
                "Please review Exporting Complete Data Using FTANF in the Knowledge Center."
        )