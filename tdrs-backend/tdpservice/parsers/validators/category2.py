from tdpservice.parsers.util import clean_options_string
from .base import ValidatorFunctions
from .util import ValidationErrorArgs, make_validator, evaluate_all


def format_error_context(eargs: ValidationErrorArgs):
    """Format the error message for consistency across cat2 validators."""
    return f'{eargs.row_schema.record_type} Item {eargs.item_num} ({eargs.friendly_name}):'


class FieldValidators():
    # @staticmethod
    # @make_validator(ValidatorFunctions.isEqual)
    # def isEqual():
    #     return lambda eargs: f'stuff'

    @staticmethod
    def isEqual(option, **kwargs):
        return make_validator(
            ValidatorFunctions.isEqual(option, **kwargs),
            lambda eargs: f"{format_error_context(eargs)} {eargs.value} does not match {option}."
        )

    @staticmethod
    def isNotEqual(option, **kwargs):
        return make_validator(
            ValidatorFunctions.isNotEqual(option, **kwargs),
            lambda eargs: f"{format_error_context(eargs)} {eargs.value} matches {option}."
        )

    @staticmethod
    def isOneOf(options, **kwargs):
        return make_validator(
            ValidatorFunctions.isOneOf(options, **kwargs),
            lambda eargs: f"{format_error_context(eargs)} {eargs.value} is not in {clean_options_string(options)}."
        )

    @staticmethod
    def isNotOneOf(options, **kwargs):
        return make_validator(
            ValidatorFunctions.isNotOneOf(options, **kwargs),
            lambda eargs: f"{format_error_context(eargs)} {eargs.value} is in {clean_options_string(options)}."
        )

    @staticmethod
    def isGreaterThan(option, inclusive=False, **kwargs):
        return make_validator(
            ValidatorFunctions.isGreaterThan(option, inclusive, **kwargs),
            lambda eargs: f"{format_error_context(eargs)} {eargs.value} is not larger than {option}."
        )

    @staticmethod
    def isLessThan(option, inclusive=False, **kwargs):
        return make_validator(
            ValidatorFunctions.isLessThan(option, inclusive, **kwargs),
            lambda eargs: f"{format_error_context(eargs)} {eargs.value} is not smaller than {option}."
        )

    @staticmethod
    def isBetween(min, max, inclusive=False, **kwargs):
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
        return make_validator(
            ValidatorFunctions.startsWith(substr, **kwargs),
            lambda eargs: f"{format_error_context(eargs)} {eargs.value} does not start with {substr}."
        )

    @staticmethod
    def contains(substr, **kwargs):
        return make_validator(
            ValidatorFunctions.contains(substr, **kwargs),
            lambda eargs: f"{format_error_context(eargs)} {eargs.value} does not contain {substr}."
        )

    @staticmethod
    def isNumber(**kwargs):
        return make_validator(
            ValidatorFunctions.isNumber(**kwargs),
            lambda eargs: f"{format_error_context(eargs)} {eargs.value} is not a number."
        )

    @staticmethod
    def isAlphaNumeric(**kwargs):
        return make_validator(
            ValidatorFunctions.isAlphaNumeric(**kwargs),
            lambda eargs: f"{format_error_context(eargs)} {eargs.value} is not alphanumeric."
        )

    @staticmethod
    def isEmpty(start=0, end=None, **kwargs):
        return make_validator(
            ValidatorFunctions.isEmpty(**kwargs),
            lambda eargs: f'{format_error_context(eargs)} {eargs.value} is not blank '
            f'between positions {start} and {end if end else len(eargs.value)}.'
        )

    @staticmethod
    def isNotEmpty(start=0, end=None, **kwargs):
        return make_validator(
            ValidatorFunctions.isNotEmpty(**kwargs),
            lambda eargs: f'{format_error_context(eargs)} {str(eargs.value)} contains blanks '
            f'between positions {start} and {end if end else len(str(eargs.value))}.'
        )

    @staticmethod
    def isBlank(**kwargs):
        return make_validator(
            ValidatorFunctions.isBlank(**kwargs),
            lambda eargs: f"{format_error_context(eargs)} {eargs.value} is not blank."
        )

    @staticmethod
    def hasLength(length, **kwargs):
        return make_validator(
            ValidatorFunctions.hasLength(length, **kwargs),
            lambda eargs: f"{format_error_context(eargs)} field length "
            f"is {len(eargs.value)} characters but must be {length}.",
        )

    @staticmethod
    def hasLengthGreaterThan(length, inclusive=False, **kwargs):
        return make_validator(
            ValidatorFunctions.hasLengthGreaterThan(length, inclusive, **kwargs),
            lambda eargs: f"{format_error_context(eargs)} Value length {len(eargs.value)} is not greater than {length}."
        )

    @staticmethod
    def intHasLength(length, **kwargs):
        return make_validator(
            ValidatorFunctions.intHasLength(length, **kwargs),
            lambda eargs: f"{format_error_context(eargs)} {eargs.value} does not have exactly {length} digits.",
        )

    @staticmethod
    def isNotZero(number_of_zeros=1, **kwargs):
        return make_validator(
            ValidatorFunctions.isNotZero(number_of_zeros, **kwargs),
            lambda eargs: f"{format_error_context(eargs)} {eargs.value} is zero."
        )

    @staticmethod
    def orValidators(validators, **kwargs):
        """Return a validator that is true only if one of the validators is true."""
        def _validate(value, eargs):
            validator_results = evaluate_all(validators, value, eargs)

            if not any(result[0] for result in validator_results):
                return (False, " or ".join([result[1] for result in validator_results]))
            return (True, None)

        return _validate

    @staticmethod
    def dateYearIsLargerThan(year):
        """Validate that in a monthyear combination, the year is larger than the given year."""
        return make_validator(
            lambda value: int(str(value)[:4]) > year,
            lambda eargs: f"{format_error_context(eargs)} Year {str(eargs.value)[:4]} must be larger than {year}.",
        )

    @staticmethod
    def dateMonthIsValid():
        """Validate that in a monthyear combination, the month is a valid month."""
        return make_validator(
            lambda value: int(str(value)[4:6]) in range(1, 13),
            lambda eargs: f"{format_error_context(eargs)} {str(eargs.value)[4:6]} is not a valid month.",
        )

    @staticmethod
    def dateDayIsValid():
        """Validate that in a monthyearday combination, the day is a valid day."""
        return make_validator(
            lambda value: int(str(value)[6:]) in range(1, 32),
            lambda eargs: f"{format_error_context(eargs)} {str(eargs.value)[6:]} is not a valid day.",
        )

    @staticmethod
    def validateRace():
        """Validate race."""
        return make_validator(
            lambda value: value >= 0 and value <= 2,
            lambda eargs:
                f"{format_error_context(eargs)} {eargs.value} is not greater than or equal to 0 "
                "or smaller than or equal to 2."
        )

    @staticmethod
    def quarterIsValid():
        """Validate in a year quarter combination, the quarter is valid."""
        return make_validator(
            lambda value: int(str(value)[-1]) > 0 and int(str(value)[-1]) < 5,
            lambda eargs: f"{format_error_context(eargs)} {str(eargs.value)[-1]} is not a valid quarter.",
        )
