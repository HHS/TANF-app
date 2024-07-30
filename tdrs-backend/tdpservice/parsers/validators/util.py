import logging
from dataclasses import dataclass
from typing import Any

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


@dataclass
class ValidationErrorArgs:
    """Dataclass for args to `make_validator` `error_func`s."""

    value: Any
    row_schema: object  # RowSchema causes circular import
    friendly_name: str
    item_num: str
    # error_context_format: str = 'prefix'
