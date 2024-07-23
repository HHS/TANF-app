"""Django test case that tests the send_email function in the email.py file."""

from django.core import mail
from django.test import TestCase
from django.core.exceptions import ValidationError

from tdpservice.email.email import (
    automated_email,
    send_email,
    filter_valid_emails
)


class EmailTest(TestCase):
    """Email test class."""

    def test_automated_email(self):
        """Test automated_email."""
        email_path = "access-request-submitted.html"
        recipient_email = "test@email.com"
        subject = "Test email"
        email_context = {}
        text_message = "This is a test email."

        automated_email(email_path, recipient_email, subject, email_context, text_message)

        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, subject)

    def test_send_email(self):
        """Test email."""
        subject = "Test email"
        message = "This is a test email."
        html_message = "<DOCTYPE html><html><body><h1>This is a test email.</h1></body></html>"
        recipient_list = ["test_user@hhs.gov"]

        send_email(subject=subject, message=message, html_message=html_message, recipient_list=recipient_list)

        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, subject)

    def test_automated_email_fails_with_invalid_email(self):
        """Test email failure. Expect a failure because the recipient email is invalid."""
        email_path = "access-request-submitted.html"
        recipient_email = "fak-e"
        subject = "Test email"
        email_context = {}
        text_message = "This is a test email."
        subject = "Test email"

        mail.outbox.clear()

        automated_email(email_path, recipient_email, subject, email_context, text_message)
        self.assertEqual(len(mail.outbox), 0)

    def test_filter_valid_emails(self):
        """Test validate emails."""
        emails = ["test_user@hhs.gov", "foo", "bar"]

        self.assertEqual(filter_valid_emails(emails), ["test_user@hhs.gov"])

    def test_filter_valid_emails_fails(self):
        """Test validate emails raised ValidationError ."""
        emails = ["foo", "bar"]

        assert len(filter_valid_emails(emails)) == 0
