"""Tests for shared admin-console authorization helpers."""

from types import SimpleNamespace

import pytest

from tdpservice.users.authorization import is_authorized_admin_user
from tdpservice.users.models import AccountApprovalStatusChoices


def _admin_user(**overrides):
    """Return a minimal approved and active Django staff superuser."""
    attributes = {
        "is_staff": True,
        "is_superuser": True,
        "is_active": True,
        "account_approval_status": AccountApprovalStatusChoices.APPROVED,
    }
    attributes.update(overrides)
    return SimpleNamespace(**attributes)


def test_admin_authorization_does_not_depend_on_group_assignment():
    """A Django staff superuser remains authorized after a role change."""
    user = _admin_user(is_ofa_sys_admin=False)

    assert is_authorized_admin_user(user) is True


@pytest.mark.parametrize("missing_flag", ["is_staff", "is_superuser"])
def test_admin_authorization_requires_both_django_admin_flags(missing_flag):
    """Staff and superuser status are both required for admin-console access."""
    user = _admin_user(**{missing_flag: False})

    assert is_authorized_admin_user(user) is False


def test_admin_authorization_does_not_accept_group_membership_alone():
    """The OFA System Admin role does not replace Django admin flags."""
    user = _admin_user(
        is_ofa_sys_admin=True,
        is_staff=False,
        is_superuser=False,
    )

    assert is_authorized_admin_user(user) is False
