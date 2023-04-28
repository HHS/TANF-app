"""Generic parser validator functions for use in schema definitions."""

from .util import generate_parser_error


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


def notEmpty(start=0, end=None):
    """Validate that string value isn't only blanks."""
    return make_validator(
        lambda value: not value[start:end if end else len(value)].isspace(),
        lambda value: f'{value} contains blanks between positions {start} and {end if end else len(value)}.'
    )


# custom validators

def validate_single_header_trailer(datafile):
    """Validate that a raw datafile has one trailer and one footer."""
    line_number = 0
    headers = 0
    trailers = 0
    is_valid = True
    error_message = None

    for rawline in datafile.file:
        line = rawline.decode()
        line_number += 1

        if line.startswith('HEADER'):
            headers += 1
        elif line.startswith('TRAILER'):
            trailers += 1

        if headers > 1:
            is_valid = False
            error_message = 'Multiple headers found.'
            break

        if trailers > 1:
            is_valid = False
            error_message = 'Multiple trailers found.'
            break

    if headers == 0:
        is_valid = False
        error_message = 'No headers found.'

    error = None
    if not is_valid:
        error = generate_parser_error(
            datafile=datafile,
            line_number=line_number,
            schema=None,
            error_category="1",
            error_message=error_message,
            record=None,
            field=None
        )

    return is_valid, error


def validate_header_section_matches_submission(datafile, section):
    """Validate header section matches submission section."""
    is_valid = datafile.section == section

    error = None
    if not is_valid:
        error = generate_parser_error(
            datafile=datafile,
            line_number=1,
            schema=None,
            error_category="1",
            error_message="Section does not match.",
            record=None,
            field=None
        )

    return is_valid, error
