"""An implementation of EmailBackend that uses the Sendgrid web api to send messages."""

from django.core.mail.backends.base import BaseEmailBackend
from django.conf import settings
from django.core.mail.message import sanitize_address
import sendgrid
from sendgrid.helpers.mail import Mail, From, To, Subject, PlainTextContent, HtmlContent


class SendgridEmailBackend(BaseEmailBackend):
    """A custom EmailBackend that sends messages via the Sendgrid web api."""

    def __init__(self, fail_silently=False, **kwargs):
        super().__init__(fail_silently, **kwargs)
        self.connection = sendgrid.SendGridAPIClient(api_key=settings.SENDGRID_API_KEY)

    def send_messages(self, email_messages):
        """Send one or more EmailMessage objects and return the number of email messages sent."""
        if not email_messages:
            return 0

        if not self.connection:
            # We failed silently on open().
            # Trying to send would be pointless.
            return 0
        num_sent = 0
        try:
            for message in email_messages:
                sent = self._send(message)
                if sent:
                    num_sent += 1
        except Exception as e:
            raise e

        return num_sent

    def _send(self, email_message):
        encoding = email_message.encoding or settings.DEFAULT_CHARSET
        from_email = From(sanitize_address(email_message.from_email, encoding))
        subject = Subject(email_message.subject)
        content = PlainTextContent(email_message.body)
        html_content = HtmlContent(email_message.alternatives[0][0]) if len(email_message.alternatives) > 0 else None

        mail = Mail(
            from_email=from_email,
            subject=subject,
            plain_text_content=content,
            html_content=html_content
        )

        for addr in email_message.recipients():
            mail.add_to(To(sanitize_address(addr, encoding)))

        response = self.connection.send(message=mail)

        if response.status_code == 202:
            return True

        return False
