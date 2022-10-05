"""Django test case that tests the send_email function in the email.py file."""

from django.core import mail
from django.test import TestCase
from django.core.exceptions import ValidationError
from django.template import TemplateDoesNotExist

from tdpservice.email.email import (
    send_email,
    filter_valid_emails,
    construct_email
)

class EmailTest(TestCase):
    """Email test class."""

    def test_send_email(self):
        """Test email."""
        subject = "Test email"
        message = "This is a test email."
        html_message = "<DOCTYPE html><html><body><h1>This is a test email.</h1></body></html>"
        recipient_list = ["test_user@hhs.gov"]

        mail.outbox.clear()

        send_email(subject=subject, message=message, html_message=html_message, recipient_list=recipient_list)

        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, subject)

    def test_send_email_fails_with_invalid_email(self):
        """Test email failure. Expect a failure because the recipient email is invalid."""
        subject = "Test email"
        message = "This is a test email."
        html_message = "<DOCTYPE html><html><body><h1>This is a test email.</h1></body></html>"
        recipient_list = ["test_user"]

        mail.outbox.clear()

        with self.assertRaises(ValidationError):
            send_email(subject=subject, message=message, html_message=html_message, recipient_list=recipient_list)
        self.assertEqual(len(mail.outbox), 0)

    def test_filter_valid_emails(self):
        """Test validate emails."""
        emails = ["test_user@hhs.gov", "foo", "bar"]

        self.assertEqual(filter_valid_emails(emails), ["test_user@hhs.gov"])

    def test_filter_valid_emails_fails(self):
        """Test validate emails raised ValidationError ."""
        emails = ["foo", "bar"]

        with self.assertRaises(ValidationError):
            filter_valid_emails(emails)

    def test_construct_email_fails_with_no_template(self):
        """Test get email template failure. Expect a failure because the template does not exist."""
        email_type = "test"
        context = {}

        with self.assertRaises(TemplateDoesNotExist):
            construct_email(email_type, context)
