"""Module for testing the automated account emails."""

import pytest
from django.core import mail
from tdpservice.users.models import User


@pytest.mark.django_db
def test_access_request_sends_email(user, mocker):
    """Test that an email is sent when an access request is requested."""
    user = User.objects.get(username=user.username)
    user.account_approval_status = 'Access request'
    user.save()

    assert user.account_approval_status == 'Access request'
    assert len(mail.outbox) == 1
    assert mail.outbox[0].subject == "Access Request Submitted"


@pytest.mark.django_db
def test_access_request_approved_sends_email(user, mocker):
    """Test that an email is sent when an access request is approved."""
    user = User.objects.get(username=user.username)
    user.account_approval_status = 'Approved'
    user.save()

    assert user.account_approval_status == 'Approved'
    assert len(mail.outbox) == 1
    assert mail.outbox[0].subject == "Access Request Approved"

@pytest.mark.django_db
def test_access_denied_sends_email(user, mocker):
    """Test that an email is sent when an access request is denied."""
    user = User.objects.get(username=user.username)
    user.account_approval_status = 'Denied'
    user.save()

    assert user.account_approval_status == 'Denied'
    assert len(mail.outbox) == 1
    assert mail.outbox[0].subject == "Access Request Denied"

@pytest.mark.django_db
def test_deactivating_user_sends_email(user, mocker):
    """Test that an email is sent when an account is deactivated."""
    user = User.objects.get(username=user.username)
    user.account_approval_status = 'Deactivated'
    user.save()

    assert user.account_approval_status == 'Deactivated'
    assert len(mail.outbox) == 1
    assert mail.outbox[0].subject == "Account is Deactivated"
