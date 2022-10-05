"""Module for testing the automated account emails."""

import pytest
import tdpservice
from tdpservice.users.models import User


@pytest.mark.django_db
def test_access_request_sends_email(user, mocker):
    """Test that an email is sent when an access request is requested."""
    mocker.patch(
        'tdpservice.email.email.mail.delay',
        return_value=True
    )
    user = User.objects.get(username=user.username)
    user.account_approval_status = 'Access request'
    user.save()

    assert user.account_approval_status == 'Access request'
    tdpservice.email.email.mail.delay.assert_called_once()


@pytest.mark.django_db
def test_access_request_approved_sends_email(user, mocker):
    """Test that an email is sent when an access request is approved."""
    mocker.patch(
        'tdpservice.email.email.mail.delay',
        return_value=True
    )
    user = User.objects.get(username=user.username)
    user.account_approval_status = 'Approved'
    user.save()

    assert user.account_approval_status == 'Approved'
    tdpservice.email.email.mail.delay.assert_called_once()

@pytest.mark.django_db
def test_access_denied_sends_email(user, mocker):
    """Test that an email is sent when an access request is denied."""
    mocker.patch(
        'tdpservice.email.email.mail.delay',
        return_value=True
    )
    user = User.objects.get(username=user.username)
    user.account_approval_status = 'Denied'
    user.save()

    assert user.account_approval_status == 'Denied'
    tdpservice.email.email.mail.delay.assert_called_once()

@pytest.mark.django_db
def test_deactivating_user_sends_email(user, mocker):
    """Test that an email is sent when an account is deactivated."""
    mocker.patch(
        'tdpservice.email.email.mail.delay',
        return_value=True
    )
    user = User.objects.get(username=user.username)
    user.account_approval_status = 'Deactivated'
    user.save()

    assert user.account_approval_status == 'Deactivated'
    tdpservice.email.email.mail.delay.assert_called_once()
