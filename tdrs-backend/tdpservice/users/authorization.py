"""Shared user authorization helpers."""

from tdpservice.users.models import AccountApprovalStatusChoices


def is_authorized_admin_user(user):
    """Return whether a user may access the admin console."""
    return (
        getattr(user, "is_ofa_sys_admin", False)
        and getattr(user, "is_active", False)
        and getattr(user, "account_approval_status", None)
        == AccountApprovalStatusChoices.APPROVED
    )
