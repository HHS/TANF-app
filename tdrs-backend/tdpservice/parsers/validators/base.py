"""Base functions to be overloaded and composed from within the other validator classes."""

from .util import _is_empty


def _handle_cast(val, cast):
    return cast(val)


def _handle_kwargs(val, **kwargs):
    if 'cast' in kwargs and kwargs['cast'] is not None:
        val = _handle_cast(val, kwargs['cast'])

    return val


def _make_base_validator(func, **kwargs):
    def _validate(val):
        val = _handle_kwargs(val, **kwargs)
        return func(val)
    return _validate


def isEqual(option, **kwargs):
    """Return a function that tests if an input param is equal to option."""
    return _make_base_validator(
        lambda val: val == option,
        **kwargs
    )


def isNotEqual(option, **kwargs):
    """Return a function that tests if an input param is not equal to option."""
    return _make_base_validator(
        lambda val: val != option,
        **kwargs
    )


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

    return _make_base_validator(
        lambda val: check_option(val),
        **kwargs
    )


def isNotOneOf(options, **kwargs):
    """Return a function that tests if an input param is not one of options."""
    return _make_base_validator(
        lambda val: val not in options,
        **kwargs
    )


def isGreaterThan(option, inclusive=False, **kwargs):
    """Return a function that tests if an input param is greater than option."""
    return _make_base_validator(
        lambda val: val > option if not inclusive else val >= option,
        **kwargs
    )


def isLessThan(option, inclusive=False, **kwargs):
    """Return a function that tests if an input param is less than option."""
    return _make_base_validator(
        lambda val: val < option if not inclusive else val <= option,
        **kwargs
    )


def isBetween(min, max, inclusive=False, **kwargs):
    """Return a function that tests if an input param is between min and max."""
    return _make_base_validator(
        lambda val: min < val < max if not inclusive else min <= val <= max,
        **kwargs
    )


def startsWith(substr, **kwargs):
    """Return a function that tests if an input param starts with substr."""
    return _make_base_validator(
        lambda val: str(val).startswith(substr),
        **kwargs
    )


def contains(substr, **kwargs):
    """Return a function that tests if an input param contains substr."""
    return _make_base_validator(
        lambda val: str(val).find(substr) != -1,
        **kwargs
    )


def isNumber(**kwargs):
    """Return a function that tests if an input param is numeric."""
    return _make_base_validator(
        lambda val: str(val).strip().isnumeric(),
        **kwargs
    )


def isAlphaNumeric(**kwargs):
    """Return a function that tests if an input param is alphanumeric."""
    return _make_base_validator(
        lambda val: val.isalnum(),
        **kwargs
    )


def isEmpty(start=0, end=None, **kwargs):
    """Return a function that tests if an input param is empty or all fill chars."""
    return _make_base_validator(
        lambda val: _is_empty(val, start, end),
        **kwargs
    )


def isNotEmpty(start=0, end=None, **kwargs):
    """Return a function that tests if an input param is not empty or all fill chars."""
    return _make_base_validator(
        lambda val: not _is_empty(val, start, end),
        **kwargs
    )


def isBlank(**kwargs):
    """Return a function that tests if an input param is all space."""
    return _make_base_validator(
        lambda val: val.isspace(),
        **kwargs
    )


def hasLength(length, **kwargs):
    """Return a function that tests if an input param has length equal to length."""
    return _make_base_validator(
        lambda val: len(val) == length,
        **kwargs
    )


def hasLengthGreaterThan(length, inclusive=False, **kwargs):
    """Return a function that tests if an input param has length greater than length."""
    return _make_base_validator(
        lambda val: len(val) > length if not inclusive else len(val) >= length,
        **kwargs
    )


def intHasLength(length, **kwargs):
    """Return a function that tests if an integer input param has a number of digits equal to length."""
    return _make_base_validator(
        lambda val: sum(c.isdigit() for c in str(val)) == length,
        **kwargs
    )


def isNotZero(number_of_zeros=1, **kwargs):
    """Return a function that tests if an input param is zero or all zeros."""
    return _make_base_validator(
        lambda val: val != "0" * number_of_zeros,
        **kwargs
    )


def dateYearIsLargerThan(year, **kwargs):
    """Return a function that tests that an input date has a year value larger than the given year."""
    return _make_base_validator(
        lambda val: int(val) > year,
        **kwargs
    )


def dateMonthIsValid(**kwargs):
    """Return a function that tests that an input date has a month value that is valid."""
    return _make_base_validator(
        lambda val: int(val) in range(1, 13),
        **kwargs
    )


def dateDayIsValid(**kwargs):
    """Return a function that tests that an input date has a day value that is valid."""
    return _make_base_validator(
        lambda val: int(val) in range(1, 32),
        **kwargs
    )


def quarterIsValid(**kwargs):
    """Return a function that tests that an input date has a quarter value that is valid."""
    return _make_base_validator(
        lambda val: int(val) > 0 and int(val) < 5,
        **kwargs
    )
