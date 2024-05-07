"""Test functions for deactivated account warnings."""
import pytest
import tdpservice
from datetime import datetime, timedelta, timezone
from tdpservice.email.tasks import check_for_accounts_needing_deactivation_warning
from tdpservice.users.models import AccountApprovalStatusChoices

import logging
logger = logging.getLogger(__name__)


@pytest.mark.django_db
def test_deactivation_email_10_days(user, mocker):
    """Test that the check_for_accounts_needing_deactivation_warning task runs."""
    mocker.patch(
        'tdpservice.email.helpers.account_deactivation_warning.send_deactivation_warning_email',
        return_value=None
    )
    mocker.patch(
        'tdpservice.email.tasks.users_to_deactivate',
        return_value=[user]
    )

    user.last_login = datetime.now(tz=timezone.utc) - timedelta(days=170)
    user.first_name = 'UniqueName'
    user.save()
    check_for_accounts_needing_deactivation_warning()
    assert tdpservice.email.helpers.account_deactivation_warning.send_deactivation_warning_email.called_once_with(
        users=[user], days=10)

@pytest.mark.django_db
def test_deactivation_email_3_days(user, mocker):
    """Test that the check_for_accounts_needing_deactivation_warning task runs."""
    mocker.patch(
        'tdpservice.email.helpers.account_deactivation_warning.send_deactivation_warning_email',
        return_value=None
    )
    mocker.patch(
        'tdpservice.email.tasks.users_to_deactivate',
        return_value=[user]
    )

    user.last_login = datetime.now(tz=timezone.utc) - timedelta(days=177)
    user.first_name = 'UniqueName'
    user.save()
    check_for_accounts_needing_deactivation_warning()
    assert tdpservice.email.helpers.account_deactivation_warning.send_deactivation_warning_email.called_once_with(
        users=[user], days=3)

@pytest.mark.django_db
def test_deactivation_email_1_days(user, mocker):
    """Test that the check_for_accounts_needing_deactivation_warning task runs."""
    mocker.patch(
        'tdpservice.email.helpers.account_deactivation_warning.send_deactivation_warning_email',
        return_value=None
    )
    mocker.patch(
        'tdpservice.email.tasks.users_to_deactivate',
        return_value=[user]
    )

    user.last_login = datetime.now(tz=timezone.utc) - timedelta(days=179)
    user.first_name = 'UniqueName'
    user.save()
    check_for_accounts_needing_deactivation_warning()
    assert tdpservice.email.helpers.account_deactivation_warning.send_deactivation_warning_email.called_once_with(
        users=[user], days=1)


@pytest.mark.django_db
def test_no_users_to_warn(user, mocker):
    """Test that the check_for_accounts_needing_deactivation_warning task runs."""
    mocker.patch(
        'tdpservice.email.helpers.account_deactivation_warning.send_deactivation_warning_email',
        return_value=None
    )
    mocker.patch(
        'tdpservice.email.tasks.users_to_deactivate',
        return_value=[user]
    )

    user.last_login = datetime.now() - timedelta(days=169)
    user.first_name = 'UniqueName'
    user.save()
    check_for_accounts_needing_deactivation_warning()
    tdpservice.email.helpers.account_deactivation_warning.send_deactivation_warning_email.assert_not_called()

@pytest.mark.django_db
def test_users_to_deactivate(user):
    """Test that the users_to_deactivate function returns the correct users."""
    user.last_login = datetime.now() - timedelta(days=170)
    user.first_name = 'UniqueName'
    user.account_approval_status = AccountApprovalStatusChoices.APPROVED
    user.save()
    users = tdpservice.email.tasks.users_to_deactivate(10)
    assert users[0].first_name == user.first_name
