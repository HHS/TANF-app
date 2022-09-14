"""Enum fot email types that map to email templates."""
from enum import Enum


class EmailType(Enum):
    """Email type enum."""

    ACCESS_REQUEST_SUBMITTED = 'access-request-submitted'
    DATA_SUBMITTED = 'data-submitted'
    REQUEST_APPROVED = 'request-approved'
    REQUEST_DENIED = 'request-denied'
    INACTIVE_ACCOUNT_10_DAYS = 'inactive-account-10-days'
    INACTIVE_ACCOUNT_3_DAYS = 'inactive-account-3-days'
    INACTIVE_ACCOUNT_1_DAYS = 'inactive-account-1-days'
    ACCOUNT_DEACTIVATED = 'account-deactivated'
