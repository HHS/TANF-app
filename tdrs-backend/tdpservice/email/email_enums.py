"""Enum for email types that map to email templates."""

from enum import Enum

# class EmailType(Enum):
#     """Email type enum."""

# ACCESS_REQUEST_COUNT = "access-request-count.html"
# ACCESS_REQUEST_SUBMITTED = "access-request-submitted.html"
# DATA_SUBMITTED = "data-submitted.html"
# DATA_SUBMISSION_FAILED = "data-submitted-failed.html"
# FRA_SUBMITTED = "fra-data-submitted.html"
# REQUEST_APPROVED = "request-approved.html"
# REQUEST_DENIED = "request-denied.html"
# DEACTIVATION_WARNING = "account-deactivation-warning.html"
# ACCOUNT_DEACTIVATED = "account-deactivated.html"
# ACCOUNT_DEACTIVATED_ADMIN = "account-deactivated-admin.html"
# UPCOMING_SUBMISSION_DEADLINE = "upcoming-submission-deadline.html"
# STUCK_FILE_LIST = "stuck-file-list.html"
# SYSTEM_ADMIN_ROLE_CHANGED = "system-admin-role-changed.html"
# PROFILE_CHANGE_REQUEST_APPROVED = "profile-change-request-approved.html"
# PROFILE_CHANGE_REQUEST_REJECTED = "profile-change-request-rejected.html"


class UserAccountEmail(Enum):
    """Email templates related to user accounts."""

    ACCESS_REQUEST_SUBMITTED = "user_account/access-request-submitted.html"
    ACCESS_REQUEST_APPROVED = "user_account/request-approved.html"
    ACCESS_REQUEST_DENIED = "user_account/request-denied.html"
    DEACTIVATION_WARNING = "user_account/account-deactivation-warning.html"
    ACCOUNT_DEACTIVATED = "user_account/account-deactivated.html"
    PROFILE_CHANGE_REQUEST_APPROVED = (
        "user_account/profile-change-request-approved.html"
    )
    PROFILE_CHANGE_REQUEST_REJECTED = (
        "user_account/profile-change-request-rejected.html"
    )


class DataFileEmail(Enum):
    """Email templates related to data file submissions."""

    # DATA_SUBMITTED = "data-submitted.html"
    # FRA_SUBMITTED = "fra-data-submitted.html"
    UPCOMING_SUBMISSION_DEADLINE = "upcoming-submission-deadline.html"

    class TANF(Enum):
        ACCEPTED = "tanf/accepted.html"
        ACCEPTED_WITH_ERRORS = "tanf/accepted_with_errors.html"
        PARTIALLY_ACCEPTED = "tanf/partially_accepted.html"
        REJECTED = "tanf/rejected.html"

    class FRA(Enum):
        ACCEPTED = "fra/accepted.html"
        ACCEPTED_WITH_ERRORS = "fra/accepted_with_errors.html"
        PARTIALLY_ACCEPTED = "fra/partially_accepted.html"
        REJECTED = "fra/rejected.html"


class AdminEmail(Enum):
    """Email templates related to admin actions and reminders"""

    ACCESS_REQUEST_COUNT = "admin/access-request-count.html"
    ACCOUNT_DEACTIVATED_ADMIN = "admin/account-deactivated-admin.html"
    STUCK_FILE_LIST = "admin/stuck-file-list.html"
    SYSTEM_ADMIN_ROLE_CHANGED = "admin/system-admin-role-changed.html"
