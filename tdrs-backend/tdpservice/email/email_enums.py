"""Enum for email types that map to email templates."""
from enum import Enum


class EmailType(Enum):
    """Email type enum."""

    ACCESS_REQUEST_COUNT = "access-request-count.html"
    ACCESS_REQUEST_SUBMITTED = "access-request-submitted.html"
    DATA_SUBMITTED = "data-submitted.html"
    DATA_SUBMISSION_FAILED = "data-submitted-failed.html"
    FRA_SUBMITTED = "fra-data-submitted.html"
    REQUEST_APPROVED = "request-approved.html"
    REQUEST_DENIED = "request-denied.html"
    DEACTIVATION_WARNING = "account-deactivation-warning.html"
    ACCOUNT_DEACTIVATED = "account-deactivated.html"
    ACCOUNT_DEACTIVATED_ADMIN = "account-deactivated-admin.html"
    UPCOMING_SUBMISSION_DEADLINE = "upcoming-submission-deadline.html"
    STUCK_FILE_LIST = "stuck-file-list.html"
    SYSTEM_ADMIN_ROLE_CHANGED = "system-admin-role-changed.html"
    PROFILE_CHANGE_REQUEST_APPROVED = "profile-change-request-approved.html"
    PROFILE_CHANGE_REQUEST_REJECTED = "profile-change-request-rejected.html"
