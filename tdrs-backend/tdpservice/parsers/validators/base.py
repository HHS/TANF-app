"""Base functions to be overloaded and composed from within the other validator classes."""

import functools
from .util import _is_empty


def _handle_cast(val, cast):
    return cast(val)


def _handle_kwargs(val, **kwargs):
    if 'cast' in kwargs and kwargs['cast'] is not None:
        val = _handle_cast(val, kwargs['cast'])

    return val


def base_validator(makeValidator):
    """Wrap validator funcs to handle kwargs."""
    @functools.wraps(makeValidator)
    def _validator(*args, **kwargs):
        validator = makeValidator(*args, **kwargs)

        def _validate(val):
            val = _handle_kwargs(val, **kwargs)
            return validator(val)

        return _validate

    return _validator


@base_validator
def isEqual(option, **kwargs):
    """Return a function that tests if an input param is equal to option."""
    return lambda val: val == option


@base_validator
def isNotEqual(option, **kwargs):
    """Return a function that tests if an input param is not equal to option."""
    return lambda val: val != option


@base_validator
def isOneOf(options, **kwargs):
    """Return a function that tests if an input param is one of options."""
    def check_option(value):
        # split the option if it is a range and append the range to the options
        for option in options:
            if "-" in str(option):
                start, end = option.split("-")
                options.extend([i for i in range(int(start), int(end) + 1)])
                options.remove(option)
        return value in options

    return lambda val: check_option(val)


@base_validator
def isNotOneOf(options, **kwargs):
    """Return a function that tests if an input param is not one of options."""
    return lambda val: val not in options


@base_validator
def isGreaterThan(option, inclusive=False, **kwargs):
    """Return a function that tests if an input param is greater than option."""
    return lambda val: val > option if not inclusive else val >= option


@base_validator
def isLessThan(option, inclusive=False, **kwargs):
    """Return a function that tests if an input param is less than option."""
    return lambda val: val < option if not inclusive else val <= option


@base_validator
def isBetween(min, max, inclusive=False, **kwargs):
    """Return a function that tests if an input param is between min and max."""
    return lambda val: min < val < max if not inclusive else min <= val <= max


@base_validator
def startsWith(substr, **kwargs):
    """Return a function that tests if an input param starts with substr."""
    return lambda val: str(val).startswith(substr)


@base_validator
def contains(substr, **kwargs):
    """Return a function that tests if an input param contains substr."""
    return lambda val: str(val).find(substr) != -1


@base_validator
def isNumber(**kwargs):
    """Return a function that tests if an input param is numeric."""
    return lambda val: str(val).strip().isnumeric()


@base_validator
def isAlphaNumeric(**kwargs):
    """Return a function that tests if an input param is alphanumeric."""
    return lambda val: val.isalnum()


@base_validator
def isEmpty(start=0, end=None, **kwargs):
    """Return a function that tests if an input param is empty or all fill chars."""
    return lambda val: _is_empty(val, start, end)


@base_validator
def isNotEmpty(start=0, end=None, **kwargs):
    """Return a function that tests if an input param is not empty or all fill chars."""
    return lambda val: not _is_empty(val, start, end)


@base_validator
def isBlank(**kwargs):
    """Return a function that tests if an input param is all space."""
    return lambda val: val.isspace()


@base_validator
def hasLength(length, **kwargs):
    """Return a function that tests if an input param has length equal to length."""
    return lambda val: len(val) == length


@base_validator
def hasLengthGreaterThan(length, inclusive=False, **kwargs):
    """Return a function that tests if an input param has length greater than length."""
    return lambda val: len(val) > length if not inclusive else len(val) >= length


@base_validator
def intHasLength(length, **kwargs):
    """Return a function that tests if an integer input param has a number of digits equal to length."""
    return lambda val: sum(c.isdigit() for c in str(val)) == length


@base_validator
def isNotZero(number_of_zeros=1, **kwargs):
    """Return a function that tests if an input param is zero or all zeros."""
    return lambda val: val != "0" * number_of_zeros


@base_validator
def dateYearIsLargerThan(year, **kwargs):
    """Return a function that tests that an input date has a year value larger than the given year."""
    return lambda val: int(val) > year


@base_validator
def dateMonthIsValid(**kwargs):
    """Return a function that tests that an input date has a month value that is valid."""
    return lambda val: int(val) in range(1, 13)


@base_validator
def dateDayIsValid(**kwargs):
    """Return a function that tests that an input date has a day value that is valid."""
    return lambda val: int(val) in range(1, 32)


@base_validator
def quarterIsValid(**kwargs):
    """Return a function that tests that an input date has a quarter value that is valid."""
    return lambda val: int(val) > 0 and int(val) < 5
