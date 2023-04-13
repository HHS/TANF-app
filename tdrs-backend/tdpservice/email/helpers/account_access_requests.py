"""Helper methods for sending emails to users about their account deactivation."""
from tdpservice.email.email_enums import EmailType
from tdpservice.email.email import log, prepare_email, prepare_recipients, send_email


def send_num_access_requests_email(recipient_email, text_message, subject, email_context, logger_context=None):
    """Send an email to OFA System Admins notifying them how many access requests there are.

    recipient_email can be either a string (single recipient) or a array of strings.
    """
    email_path = EmailType.ACCESS_REQUEST_COUNT.value
    prepare_recipients(recipient_email)

    html_message, valid_emails = prepare_email(email_path, recipient_email, email_context, logger_context)

    try:
        send_email(subject, text_message, html_message, valid_emails)
        log(
            f"Email sent to {valid_emails} with subject \"{subject}\".",
            logger_context=logger_context
        )
    except Exception:
        log(
            f'Emails were attempted to the following email list {valid_emails}, but none were sent.',
            logger_context=logger_context
        )
