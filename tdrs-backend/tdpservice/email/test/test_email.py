"""Django test case that tests the send_email function in the email.py file."""

from tdpservice.email.email import send_email
from django.core import mail
from django.test import TestCase


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
