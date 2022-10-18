"""Enum for email types that map to email templates."""
from enum import Enum


class EmailType(Enum):
    """Email type enum."""

    ACCESS_REQUEST_SUBMITTED = 'access-request-submitted.html'
    DATA_SUBMITTED = 'data-submitted.html'
    REQUEST_APPROVED = 'request-approved.html'
    REQUEST_DENIED = 'request-denied.html'
    INACTIVE_ACCOUNT_10_DAYS = 'inactive-account-10-days.html'
    INACTIVE_ACCOUNT_3_DAYS = 'inactive-account-3-days.html'
    INACTIVE_ACCOUNT_1_DAYS = 'inactive-account-1-days.html'
    ACCOUNT_DEACTIVATED = 'account-deactivated.html'
