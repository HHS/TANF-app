"""Test cases for feedback report email helper."""

import pytest
from unittest.mock import patch, MagicMock
from django.core import mail
from django.utils import timezone

from tdpservice.email.helpers.feedback_report import send_feedback_report_available_email


@pytest.fixture
def mock_report_file(stt, user):
    """Create a mock ReportFile for testing."""
    report_file = MagicMock()
    report_file.id = 1
    report_file.stt = stt
    report_file.year = 2025
    report_file.quarter = "Q1"
    report_file.created_at = timezone.now()
    report_file.user = user
    return report_file


@pytest.mark.django_db
class TestSendFeedbackReportAvailableEmail:
    """Tests for send_feedback_report_available_email function."""

    def test_sends_email_to_recipients(self, mock_report_file):
        """Test that email is sent to provided recipients."""
        recipients = ["user1@example.com", "user2@example.com"]

        send_feedback_report_available_email(mock_report_file, recipients)

        assert len(mail.outbox) == 1
        assert mock_report_file.stt.name in mail.outbox[0].subject
        assert "2025" in mail.outbox[0].subject
        assert "Q1" in mail.outbox[0].subject

    def test_does_not_send_email_when_no_recipients(self, mock_report_file):
        """Test that no email is sent when recipients list is empty."""
        send_feedback_report_available_email(mock_report_file, [])

        assert len(mail.outbox) == 0

    def test_does_not_send_email_when_recipients_is_none(self, mock_report_file):
        """Test that no email is sent when recipients is None."""
        send_feedback_report_available_email(mock_report_file, None)

        assert len(mail.outbox) == 0

    def test_email_contains_expected_text_message(self, mock_report_file):
        """Test that email body contains expected text."""
        recipients = ["user@example.com"]

        send_feedback_report_available_email(mock_report_file, recipients)

        assert len(mail.outbox) == 1
        assert mock_report_file.stt.name in mail.outbox[0].body
        assert "2025" in mail.outbox[0].body
        assert "Q1" in mail.outbox[0].body

    def test_uses_correct_email_template(self, mock_report_file):
        """Test that the correct email template is referenced."""
        recipients = ["user@example.com"]

        with patch("tdpservice.email.helpers.feedback_report.automated_email") as mock_email:
            send_feedback_report_available_email(mock_report_file, recipients)

            mock_email.assert_called_once()
            call_kwargs = mock_email.call_args[1]
            assert call_kwargs["email_path"] == "feedback-report-available.html"

    def test_email_context_contains_required_fields(self, mock_report_file):
        """Test that email context contains all required template variables."""
        recipients = ["user@example.com"]

        with patch("tdpservice.email.helpers.feedback_report.automated_email") as mock_email:
            send_feedback_report_available_email(mock_report_file, recipients)

            call_kwargs = mock_email.call_args[1]
            context = call_kwargs["email_context"]

            assert "stt_name" in context
            assert "fiscal_year" in context
            assert "quarter" in context
            assert "report_date" in context
            assert "url" in context
            assert "subject" in context

            assert context["stt_name"] == mock_report_file.stt.name
            assert context["fiscal_year"] == 2025
            assert context["quarter"] == "Q1"

    def test_handles_report_file_without_user(self, stt):
        """Test that email is sent even if report_file.user is None."""
        report_file = MagicMock()
        report_file.id = 1
        report_file.stt = stt
        report_file.year = 2025
        report_file.quarter = "Q1"
        report_file.created_at = timezone.now()
        report_file.user = None

        recipients = ["user@example.com"]

        send_feedback_report_available_email(report_file, recipients)

        assert len(mail.outbox) == 1
