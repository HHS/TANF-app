"""Test functions for email helper."""
import pytest
from django.core import mail
from tdpservice.email.helpers.account_deactivation_warning import send_deactivation_warning_email


@pytest.mark.django_db
def test_send_deactivation_warning_email(mocker, user):
    """Test that the send_deactivation_warning_email function runs."""
    send_deactivation_warning_email([user], 10)

    assert len(mail.outbox) == 1
    assert mail.outbox[0].subject == "Account Deactivation Warning: 10 days remaining"
