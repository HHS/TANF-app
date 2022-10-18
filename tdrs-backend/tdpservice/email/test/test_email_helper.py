"""Test functions for email helper."""
import pytest

import tdpservice
from tdpservice.email.email_helper import send_deactivation_warning_email, send_data_submitted_email


@pytest.mark.django_db
def test_send_deactivation_warning_email(mocker, user):
    """Test that the send_deactivation_warning_email function runs."""
    mocker.patch(
        'tdpservice.email.email_helper.automated_email.delay',
        return_value=None
    )
    send_deactivation_warning_email([user], 10)

    assert tdpservice.email.email.automated_email.delay.called_once_with(
        recipient_email=user.email,
        subject='Account Deactivation Warning: 10 days remaining',
    )

@pytest.mark.django_db
def test_send_data_submitted_email(mocker):
    """Test that the send_data_submitted_email function runs."""
    mocker.patch(
        'tdpservice.email.email_helper.automated_email.delay',
        return_value=None
    )
    context = {
        'stt_name': 'foo_stt',
        'submission_date': 'foo_date',
        'submitted_by': 'foo_user',
    }
    send_data_submitted_email(context)

    assert tdpservice.email.email.automated_email.delay.called_once_with(
        email_context=context,
    )
