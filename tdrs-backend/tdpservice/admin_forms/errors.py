"""Normalized error responses for generic admin forms."""

from typing import Any

from django.forms.forms import NON_FIELD_ERRORS
from django.forms.utils import ErrorDict


def normalize_form_errors(errors: ErrorDict) -> dict[str, Any]:
    """Return normalized field and non-field errors from a Django form."""
    field_errors = {}
    non_field_errors = []

    for field_name, error_list in errors.as_data().items():
        messages = [
            str(message)
            for validation_error in error_list
            for message in validation_error.messages
        ]

        if field_name == NON_FIELD_ERRORS:
            non_field_errors.extend(messages)
        else:
            field_errors[field_name] = messages

    return {
        "field_errors": field_errors,
        "non_field_errors": non_field_errors,
    }
