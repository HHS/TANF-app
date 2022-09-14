"""Django test case that tests the send_email function in the email.py file."""

from django.core import mail
from django.test import TestCase
from django.core.exceptions import ValidationError
from django.template import TemplateDoesNotExist

from tdpservice.email.email import send_email, validate_emails, validate_single_email, validate_sender_email, get_email_template

class EmailTest(TestCase):
    """Email test class."""

    def test_send_email(self):
        """Test email."""
        subject = "Test email"
        message = "This is a test email."
        recipient_list = ["test_user@hhs.gov"]

        send_email(subject, message, recipient_list)

        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, subject)

    def test_send_email_fails(self):
        """Test email failure. Expect a failure because the recipient email is invalid."""
        subject = "Test email"
        message = "This is a test email."
        recipient_list = ["test_user"]

        self.assertEqual(send_email(subject, message, recipient_list), False)
        self.assertEqual(len(mail.outbox), 0)

    def test_validate_emails(self):
        """Test validate emails."""
        emails = ["test_user@hhs.gov", "foo", "bar"]

        self.assertEqual(validate_emails(emails), ["test_user@hhs.gov"])

    def test_validate_emails_fails(self):
        """Test validate emails raised ValidationError ."""
        emails = ["foo", "bar"]

        with self.assertRaises(ValidationError):
            validate_emails(emails)

    def test_validate_single_email(self):
        """Test validate single email."""
        email = "test_user@hhs.gov"

        self.assertEqual(validate_single_email(email), True)

    def test_validate_single_email_fails(self):
        """Test validate single email raised ValidationError ."""
        email = "test_user"

        with self.assertRaises(ValidationError):
            validate_single_email(email)

    def test_validate_sender_email(self):
        """Test validate sender email."""
        email = "test_user@hhs.gov"

        self.assertEqual(validate_sender_email(email), True)

    def test_validate_sender_email_fails(self):
        """Test validate sender email raised ValidationError ."""
        email = "test_user"

        with self.assertRaises(ValidationError):
            validate_sender_email(email)
    
    def get_email_template_fails(self):
        """Test get email template failure. Expect a failure because the template does not exist."""
        email_type = "test"
        context = {}

        with self.assertRaises(TemplateDoesNotExist):
            get_email_template(email_type, context)
