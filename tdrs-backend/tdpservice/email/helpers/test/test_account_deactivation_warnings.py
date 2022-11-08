"""Test functions for email helper."""
import pytest

import tdpservice
from tdpservice.email.helpers.account_deactivation_warning import send_deactivation_warning_email


@pytest.mark.django_db
def test_send_deactivation_warning_email(mocker, user):
    """Test that the send_deactivation_warning_email function runs."""
    mocker.patch(
        'tdpservice.email.helpers.account_deactivation_warning.automated_email.delay',
        return_value=None
    )
    send_deactivation_warning_email([user], 10)

    assert tdpservice.email.email.automated_email.delay.called_once_with(
        recipient_email=user.email,
        subject='Account Deactivation Warning: 10 days remaining',
    )
