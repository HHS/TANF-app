"""Shared user authorization helpers."""

from typing import Any

from tdpservice.users.models import AccountApprovalStatusChoices


def is_authorized_admin_user(user: Any) -> bool:
    """Return whether an approved Django superuser may access the admin console."""
    return (
        getattr(user, "is_staff", False)
        and getattr(user, "is_superuser", False)
        and getattr(user, "is_active", False)
        and getattr(user, "account_approval_status", None)
        == AccountApprovalStatusChoices.APPROVED
    )
