"""Enum for email types that map to email templates."""
from enum import Enum


class EmailType(Enum):
    """Email type enum."""

    ACCESS_REQUEST_COUNT = 'access-request-count.html'
    ACCESS_REQUEST_SUBMITTED = 'access-request-submitted.html'
    DATA_SUBMITTED = 'data-submitted.html'
    DATA_SUBMISSION_FAILED = 'data-submitted-failed.html'
    REQUEST_APPROVED = 'request-approved.html'
    REQUEST_DENIED = 'request-denied.html'
    DEACTIVATION_WARNING = 'account-deactivation-warning.html'
    ACCOUNT_DEACTIVATED = 'account-deactivated.html'
