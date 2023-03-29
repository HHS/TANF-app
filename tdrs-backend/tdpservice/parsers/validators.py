"""Generic parser validator functions for use in schema definitions."""


# higher order validator func

def make_validator(validator_func, error_func):
    """Return a function accepting a value input and returning (bool, string) to represent validation state."""
    return lambda value: (True, None) if validator_func(value) else (False, error_func(value))


# generic validators

def matches(option):
    """Validate that value is equal to option."""
    return make_validator(
        lambda value: value == option,
        lambda value: f'{value} does not match {option}.'
    )


def oneOf(options=[]):
    """Validate that value exists in the provided options array."""
    return make_validator(
        lambda value: value in options,
        lambda value: f'{value} is not in {options}.'
    )


def between(min, max):
    """Validate value, when casted to int, is greater than min and less than max."""
    return make_validator(
        lambda value: int(value) > min and int(value) < max,
        lambda value: f'{value} is not between {min} and {max}.'
    )


def hasLength(length):
    """Validate that value (string or array) has a length matching length param."""
    return make_validator(
        lambda value: len(value) == length,
        lambda value: f'Value length {len(value)} does not match {length}.'
    )


def contains(substring):
    """Validate that string value contains the given substring param."""
    return make_validator(
        lambda value: value.find(substring) != -1,
        lambda value: f'{value} does not contain {substring}.'
    )


def startsWith(substring):
    """Validate that string value starts with the given substring param."""
    return make_validator(
        lambda value: value.startswith(substring),
        lambda value: f'{value} does not start with {substring}.'
    )


# custom validators

def validate_single_header_trailer(file):
    """Validate that a raw datafile has one trailer and one footer."""
    headers = 0
    # trailers = 0

    for rawline in file:
        line = rawline.decode()

        if line.startswith('HEADER'):
            headers += 1
        # elif line.startswith('TRAILER'):
        #     trailers += 1

        if headers > 1:
            return (False, 'Multiple headers found.')

        # if trailers > 1:
        #     return (False, 'Multiple trailers found.')

    if headers == 0:
        return (False, 'No headers found.')

    # if trailers == 0:
    #     return (False, 'No trailers found.')

    return (True, None)
