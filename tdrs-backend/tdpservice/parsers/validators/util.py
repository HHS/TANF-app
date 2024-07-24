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


def evaluate_all(validators, value, eargs):
    """Evaluate all validators in the list and compose the result tuples in an array."""
    return [
        validator(value, eargs)
        for validator in validators
    ]


@dataclass
class ValidationErrorArgs:
    """Dataclass for args to `make_validator` `error_func`s."""

    value: Any
    validation_option: Any
    row_schema: object  # RowSchema causes circular import
    friendly_name: str
    item_num: str
    # error_context_format: str = 'prefix'
