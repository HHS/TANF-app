"""Validation helper functions and data classes."""


import functools
import logging
from dataclasses import dataclass
from typing import Any

logger = logging.getLogger(__name__)


def make_validator(validator_func, error_func):
    """
    Return a function accepting a value input and returning (bool, string) to represent validation state.

    @param validator_func: a function accepting a val and returning a bool
    @param error_func: a function accepting a ValidationErrorArguments obj and returning a string
    @return: a function returning (True, None) for success or (False, string) for failure,
    with the string representing the error message
    """
    def validator(value, eargs):
        try:
            if validator_func(value):
                return (True, None)
        except Exception:
            logger.exception("Caught exception in validator.")
        return (False, error_func(eargs))

    return validator


# decorator helper
# outer function wraps the decorator to handle arguments to the decorator itself
def validator(baseValidator):
    """
    Wrap error generation func to create a validator with baseValidator.

    @param baseValidator: a function from parsers.validators.base
    @param errorFunc: a function returning an error generator for make_validator
    @return: make_validator with the results of baseValidator and errorFunc both evaluated
    """
    # inner decorator wraps the given function and returns a function
    # that gives us our final make_validator
    def _decorator(errorFunc):
        @functools.wraps(errorFunc)
        def _validator(*args, **kwargs):
            validator_func = baseValidator(*args, **kwargs)
            error_func = errorFunc(*args, **kwargs)
            return make_validator(validator_func, error_func)
        return _validator
    return _decorator


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


@dataclass
class ValidationErrorArgs:
    """Dataclass for args to `make_validator` `error_func`s."""

    value: Any
    row_schema: object  # RowSchema causes circular import
    friendly_name: str
    item_num: str
