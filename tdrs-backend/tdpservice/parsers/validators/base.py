"""Base functions to be overloaded and composed from within the other validator classes."""

from .util import _is_empty


class ValidatorFunctions:
    """Base higher-order validator functions that can be composed and customized."""

    @staticmethod
    def _handle_cast(val, cast):
        return cast(val)

    @staticmethod
    def _handle_kwargs(val, **kwargs):
        if 'cast' in kwargs and kwargs['cast'] is not None:
            val = ValidatorFunctions._handle_cast(val, kwargs['cast'])

        return val

    @staticmethod
    def _make_validator(func, **kwargs):
        def _validate(val):
            val = ValidatorFunctions._handle_kwargs(val, **kwargs)
            return func(val)
        return _validate

    @staticmethod
    def isEqual(option, **kwargs):
        """Return a function that tests if an input param is equal to option."""
        return ValidatorFunctions._make_validator(
            lambda val: val == option,
            **kwargs
        )

    @staticmethod
    def isNotEqual(option, **kwargs):
        """Return a function that tests if an input param is not equal to option."""
        return ValidatorFunctions._make_validator(
            lambda val: val != option,
            **kwargs
        )

    @staticmethod
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

        return ValidatorFunctions._make_validator(
            lambda val: check_option(val),
            **kwargs
        )

    @staticmethod
    def isNotOneOf(options, **kwargs):
        """Return a function that tests if an input param is not one of options."""
        return ValidatorFunctions._make_validator(
            lambda val: val not in options,
            **kwargs
        )

    @staticmethod
    def isGreaterThan(option, inclusive=False, **kwargs):
        """Return a function that tests if an input param is greater than option."""
        return ValidatorFunctions._make_validator(
            lambda val: val > option if not inclusive else val >= option,
            **kwargs
        )

    @staticmethod
    def isLessThan(option, inclusive=False, **kwargs):
        """Return a function that tests if an input param is less than option."""
        return ValidatorFunctions._make_validator(
            lambda val: val < option if not inclusive else val <= option,
            **kwargs
        )

    @staticmethod
    def isBetween(min, max, inclusive=False, **kwargs):
        """Return a function that tests if an input param is between min and max."""
        return ValidatorFunctions._make_validator(
            lambda val: min < val < max if not inclusive else min <= val <= max,
            **kwargs
        )

    @staticmethod
    def startsWith(substr, **kwargs):
        """Return a function that tests if an input param starts with substr."""
        return ValidatorFunctions._make_validator(
            lambda val: str(val).startswith(substr),
            **kwargs
        )

    @staticmethod
    def contains(substr, **kwargs):
        """Return a function that tests if an input param contains substr."""
        return ValidatorFunctions._make_validator(
            lambda val: str(val).find(substr) != -1,
            **kwargs
        )

    @staticmethod
    def isNumber(**kwargs):
        """Return a function that tests if an input param is numeric."""
        return ValidatorFunctions._make_validator(
            lambda val: str(val).strip().isnumeric(),
            **kwargs
        )

    @staticmethod
    def isAlphaNumeric(**kwargs):
        """Return a function that tests if an input param is alphanumeric."""
        return ValidatorFunctions._make_validator(
            lambda val: val.isalnum(),
            **kwargs
        )

    @staticmethod
    def isEmpty(start=0, end=None, **kwargs):
        """Return a function that tests if an input param is empty or all fill chars."""
        return ValidatorFunctions._make_validator(
            lambda val: _is_empty(val, start, end),
            **kwargs
        )

    @staticmethod
    def isNotEmpty(start=0, end=None, **kwargs):
        """Return a function that tests if an input param is not empty or all fill chars."""
        return ValidatorFunctions._make_validator(
            lambda val: not _is_empty(val, start, end),
            **kwargs
        )

    @staticmethod
    def isBlank(**kwargs):
        """Return a function that tests if an input param is all space."""
        return ValidatorFunctions._make_validator(
            lambda val: val.isspace(),
            **kwargs
        )

    @staticmethod
    def hasLength(length, **kwargs):
        """Return a function that tests if an input param has length equal to length."""
        return ValidatorFunctions._make_validator(
            lambda val: len(val) == length,
            **kwargs
        )

    @staticmethod
    def hasLengthGreaterThan(length, inclusive=False, **kwargs):
        """Return a function that tests if an input param has length greater than length."""
        return ValidatorFunctions._make_validator(
            lambda val: len(val) > length if not inclusive else len(val) >= length,
            **kwargs
        )

    @staticmethod
    def intHasLength(length, **kwargs):
        """Return a function that tests if an integer input param has a number of digits equal to length."""
        return ValidatorFunctions._make_validator(
            lambda val: sum(c.isdigit() for c in str(val)) == length,
            **kwargs
        )

    @staticmethod
    def isNotZero(number_of_zeros=1, **kwargs):
        """Return a function that tests if an input param is zero or all zeros."""
        return ValidatorFunctions._make_validator(
            lambda val: val != "0" * number_of_zeros,
            **kwargs
        )

    @staticmethod
    def dateYearIsLargerThan(year, **kwargs):
        """Return a function that tests that an input date has a year value larger than the given year."""
        return ValidatorFunctions._make_validator(
            lambda val: int(val) > year,
            **kwargs
        )

    @staticmethod
    def dateMonthIsValid(**kwargs):
        """Return a function that tests that an input date has a month value that is valid."""
        return ValidatorFunctions._make_validator(
            lambda val: int(val) in range(1, 13),
            **kwargs
        )

    @staticmethod
    def dateDayIsValid(**kwargs):
        """Return a function that tests that an input date has a day value that is valid."""
        return ValidatorFunctions._make_validator(
            lambda val: int(val) in range(1, 32),
            **kwargs
        )

    @staticmethod
    def quarterIsValid(**kwargs):
        """Return a function that tests that an input date has a quarter value that is valid."""
        return ValidatorFunctions._make_validator(
            lambda val: int(val) > 0 and int(val) < 5,
            **kwargs
        )
