"""Test cases for feedback report email helper."""

from datetime import date

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
    report_file.date_extracted_on = date(2025, 1, 31)
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
        assert "01/31/2025" in mail.outbox[0].body

    def test_uses_correct_email_template(self, mock_report_file):
        """Test that the correct email template is referenced."""
        recipients = ["user@example.com"]

        with patch("tdpservice.email.helpers.feedback_report.automated_email") as mock_email:
            send_feedback_report_available_email(mock_report_file, recipients)

            mock_email.assert_called_once()
            call_kwargs = mock_email.call_args[1]
            assert call_kwargs["email_path"] == "feedback/report-available.html"

    def test_email_context_contains_required_fields(self, mock_report_file):
        """Test that email context contains all required template variables."""
        recipients = ["user@example.com"]

        with patch("tdpservice.email.helpers.feedback_report.automated_email") as mock_email:
            send_feedback_report_available_email(mock_report_file, recipients)

            call_kwargs = mock_email.call_args[1]
            context = call_kwargs["email_context"]

            assert "stt_name" in context
            assert "fiscal_year" in context
            assert "date_extracted_on" in context
            assert "report_date" in context
            assert "url" in context
            assert "subject" in context

            assert context["stt_name"] == mock_report_file.stt.name
            assert context["fiscal_year"] == 2025
            assert context["date_extracted_on"] == "01/31/2025"

    def test_handles_report_file_without_user(self, stt):
        """Test that email is sent even if report_file.user is None."""
        report_file = MagicMock()
        report_file.id = 1
        report_file.stt = stt
        report_file.year = 2025
        report_file.date_extracted_on = date(2025, 1, 31)
        report_file.created_at = timezone.now()
        report_file.user = None

        recipients = ["user@example.com"]

        send_feedback_report_available_email(report_file, recipients)

        assert len(mail.outbox) == 1

    def test_handles_report_file_without_date_extracted_on(self, stt, user):
        """Test that email is sent even if date_extracted_on is None."""
        report_file = MagicMock()
        report_file.id = 1
        report_file.stt = stt
        report_file.year = 2025
        report_file.date_extracted_on = None
        report_file.created_at = timezone.now()
        report_file.user = user

        recipients = ["user@example.com"]

        send_feedback_report_available_email(report_file, recipients)

        assert len(mail.outbox) == 1
        assert "N/A" in mail.outbox[0].body

    def test_fra_report_type_uses_fra_label_in_subject(self, mock_report_file):
        """Test that FRA report type produces 'FRA' label in subject and body."""
        mock_report_file.report_type = "FRA"
        recipients = ["user@example.com"]

        send_feedback_report_available_email(mock_report_file, recipients)

        assert len(mail.outbox) == 1
        assert "FRA Feedback Report Available" in mail.outbox[0].subject
        assert "FRA feedback report" in mail.outbox[0].body

    def test_tribal_tanf_report_type_uses_tribal_tanf_label_in_subject(
        self, mock_report_file
    ):
        """Test that TRIBAL_TANF report type produces 'Tribal TANF' label in subject and body."""
        mock_report_file.report_type = "TRIBAL_TANF"
        recipients = ["user@example.com"]

        send_feedback_report_available_email(mock_report_file, recipients)

        assert len(mail.outbox) == 1
        assert "Tribal TANF Feedback Report Available" in mail.outbox[0].subject
        assert "Tribal TANF feedback report" in mail.outbox[0].body

    def test_unknown_report_type_uses_tanf_ssp_label_in_subject(self, mock_report_file):
        """Test that unknown report types fall back to 'TANF/SSP' label in subject and body."""
        mock_report_file.report_type = "TANF"
        recipients = ["user@example.com"]

        send_feedback_report_available_email(mock_report_file, recipients)

        assert len(mail.outbox) == 1
        assert "TANF/SSP Feedback Report Available" in mail.outbox[0].subject
        assert "TANF/SSP feedback report" in mail.outbox[0].body

    def test_report_type_none_uses_tanf_ssp_label(self, mock_report_file):
        """Test that report_type=None defaults to 'TANF/SSP' label."""
        mock_report_file.report_type = None
        recipients = ["user@example.com"]

        send_feedback_report_available_email(mock_report_file, recipients)

        assert len(mail.outbox) == 1
        assert "TANF/SSP Feedback Report Available" in mail.outbox[0].subject

    def test_fra_email_context_includes_report_type(self, mock_report_file):
        """Test that FRA report type is correctly passed in email context."""
        mock_report_file.report_type = "FRA"
        recipients = ["user@example.com"]

        with patch("tdpservice.email.helpers.feedback_report.automated_email") as mock_email:
            send_feedback_report_available_email(mock_report_file, recipients)

            call_kwargs = mock_email.call_args[1]
            context = call_kwargs["email_context"]
            assert context["report_type"] == "FRA"
            assert context["report_type_label"] == "FRA"

    def test_tribal_tanf_email_context_includes_report_type(self, mock_report_file):
        """Test that TRIBAL_TANF report type is correctly passed in email context."""
        mock_report_file.report_type = "TRIBAL_TANF"
        recipients = ["user@example.com"]

        with patch("tdpservice.email.helpers.feedback_report.automated_email") as mock_email:
            send_feedback_report_available_email(mock_report_file, recipients)

            call_kwargs = mock_email.call_args[1]
            context = call_kwargs["email_context"]
            assert context["report_type"] == "TRIBAL_TANF"
            assert context["report_type_label"] == "Tribal TANF"
