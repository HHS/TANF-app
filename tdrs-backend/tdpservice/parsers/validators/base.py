from .util import _is_empty


class ValidatorFunctions:
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
        return ValidatorFunctions._make_validator(
            lambda val: val == option,
            **kwargs
        )

    @staticmethod
    def isNotEqual(option, **kwargs):
        return ValidatorFunctions._make_validator(
            lambda val: val != option,
            **kwargs
        )

    @staticmethod
    def isOneOf(options, **kwargs):
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
        return ValidatorFunctions._make_validator(
            lambda val: val not in options,
            **kwargs
        )

    @staticmethod
    def isGreaterThan(option, inclusive=False, **kwargs):
        return ValidatorFunctions._make_validator(
            lambda val: val > option if not inclusive else val >= option,
            **kwargs
        )

    @staticmethod
    def isLessThan(option, inclusive=False, **kwargs):
        return ValidatorFunctions._make_validator(
            lambda val: val < option if not inclusive else val <= option,
            **kwargs
        )

    @staticmethod
    def isBetween(min, max, inclusive=False, **kwargs):
        return ValidatorFunctions._make_validator(
            lambda val: min < val < max if not inclusive else min <= val <= max,
            **kwargs
        )

    @staticmethod
    def startsWith(substr, **kwargs):
        return ValidatorFunctions._make_validator(
            lambda val: str(val).startswith(substr),
            **kwargs
        )

    @staticmethod
    def contains(substr, **kwargs):
        return ValidatorFunctions._make_validator(
            lambda val: str(val).find(substr) != -1,
            **kwargs
        )

    @staticmethod
    def isNumber(**kwargs):
        return ValidatorFunctions._make_validator(
            lambda val: str(val).strip().isnumeric(),
            **kwargs
        )

    @staticmethod
    def isAlphaNumeric(**kwargs):
        return ValidatorFunctions._make_validator(
            lambda val: val.isalnum(),
            **kwargs
        )

    @staticmethod
    def isEmpty(start=0, end=None, **kwargs):
        return ValidatorFunctions._make_validator(
            lambda val: _is_empty(val, start, end),
            **kwargs
        )

    @staticmethod
    def isNotEmpty(start=0, end=None, **kwargs):
        return ValidatorFunctions._make_validator(
            lambda val: not _is_empty(val, start, end),
            **kwargs
        )

    @staticmethod
    def isBlank(**kwargs):
        return ValidatorFunctions._make_validator(
            lambda val: val.isspace(),
            **kwargs
        )

    @staticmethod
    def hasLength(length, **kwargs):
        return ValidatorFunctions._make_validator(
            lambda val: len(val) == length,
            **kwargs
        )

    @staticmethod
    def hasLengthGreaterThan(length, inclusive=False, **kwargs):
        return ValidatorFunctions._make_validator(
            lambda val: len(val) > length if not inclusive else len(val) >= length,
            **kwargs
        )

    @staticmethod
    def intHasLength(length, **kwargs):
        return ValidatorFunctions._make_validator(
            lambda val: sum(c.isdigit() for c in str(val)) == length,
            **kwargs
        )

    @staticmethod
    def isNotZero(number_of_zeros=1, **kwargs):
        return ValidatorFunctions._make_validator(
            lambda val: val != "0" * number_of_zeros,
            **kwargs
        )
