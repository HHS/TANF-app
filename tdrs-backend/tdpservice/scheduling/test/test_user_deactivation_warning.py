"""Test functions for deactivated account warnings."""

from datetime import datetime, timedelta, timezone

from django.contrib.auth.models import Group

import pytest

from tdpservice.email.tasks import (
    check_for_accounts_needing_deactivation_warning,
    deactivate_users,
    users_to_deactivate,
)
from tdpservice.users.models import AccountApprovalStatusChoices


@pytest.mark.django_db
@pytest.mark.parametrize("days", [10, 3, 1])
def test_deactivation_email(user, mocker, days: int) -> None:
    """Send one warning for the matching deactivation interval."""
    send_warning = mocker.patch(
        "tdpservice.email.tasks.send_deactivation_warning_email"
    )
    mocker.patch(
        "tdpservice.email.tasks.users_to_deactivate",
        side_effect=lambda warning_days: [user] if warning_days == days else [],
    )

    check_for_accounts_needing_deactivation_warning()

    send_warning.assert_called_once_with([user], days)


@pytest.mark.django_db
def test_deactivate_users(user, mocker) -> None:
    """Deactivate inactive users, remove their groups, and notify admins."""
    send_admin_notification = mocker.patch(
        "tdpservice.email.tasks.email_admin_deactivated_user"
    )
    user.groups.add(Group.objects.create(name="Deactivation test group"))
    user.last_login = datetime.now(tz=timezone.utc) - timedelta(days=181)
    user.account_approval_status = AccountApprovalStatusChoices.APPROVED
    user.save()
    deactivate_users()

    user.refresh_from_db()
    assert user.account_approval_status == AccountApprovalStatusChoices.DEACTIVATED
    assert user.groups.count() == 0
    send_admin_notification.assert_called_once_with(user)


@pytest.mark.django_db
def test_no_users_to_warn(mocker) -> None:
    """Do not send warnings when every deactivation interval is empty."""
    send_warning = mocker.patch(
        "tdpservice.email.tasks.send_deactivation_warning_email"
    )
    mocker.patch("tdpservice.email.tasks.users_to_deactivate", return_value=[])

    check_for_accounts_needing_deactivation_warning()

    send_warning.assert_not_called()


@pytest.mark.django_db
def test_users_to_deactivate(user) -> None:
    """Test that the users_to_deactivate function returns the correct users."""
    user.last_login = datetime.now(tz=timezone.utc) - timedelta(days=170)
    user.first_name = "UniqueName"
    user.account_approval_status = AccountApprovalStatusChoices.APPROVED
    user.save()
    # Reload the factory's string UUID as the database's UUID type.
    user.refresh_from_db()
    users = users_to_deactivate(10)
    assert list(users) == [user]
