"""Validator functions which may be assigned to model fields."""
import logging

from django.core.exceptions import ValidationError
from inflection import pluralize

logger = logging.getLogger(__name__)

# The default set of Extensions allowed for an uploaded file
ALLOWED_FILE_EXTENSIONS = [
    None,  # files with no extensions are allowed
    'txt',  # plain text files
]

# The default set of Content Types allowed for an uploaded file
ALLOWED_FILE_CONTENT_TYPES = [
    'text/plain',
]

# https://github.com/raft-tech/clamav-rest#status-codes
AV_SCAN_CODES = {
    'CLEAN': [200],
    'INFECTED': [406],
    'ERROR': [400, 412, 500, 501]
}


def _get_unsupported_msg(_type, value, supported_options):
    """Constructs a message to convey an unsupported operation."""
    return (
        f'Unsupported {_type}: {value}, supported {pluralize(_type)} '
        f'are: {supported_options}'
    )


def validate_file_content_type(file):
    file_content_type = file.file.content_type

    if file_content_type not in ALLOWED_FILE_CONTENT_TYPES:
        msg = _get_unsupported_msg(
            'file content type',
            file_content_type,
            ALLOWED_FILE_CONTENT_TYPES
        )
        raise ValidationError(msg)


def validate_file_extension(file):
    file_extension = (
        file.name.split('.')[-1].lower() if '.' in file.name else None
    )

    if file_extension not in ALLOWED_FILE_EXTENSIONS:
        msg = _get_unsupported_msg(
            'file extension',
            file_extension,
            ALLOWED_FILE_EXTENSIONS
        )
        raise ValidationError(msg)


def validate_file_infection(file):
    pass


def validate_data_file(file):
    validate_file_extension(file)
    validate_file_content_type(file)
    validate_file_infection(file)
