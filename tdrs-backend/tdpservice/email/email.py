"""Wrapper to send emails with Django."""

from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import get_template
from django.contrib.admin.models import LogEntry, ContentType, CHANGE

import logging

logger = logging.getLogger()


def log(msg, logger_context=None, level='info'):
    """Create a log in the terminal and django admin console, for email tasks."""
    from tdpservice.users.models import User

    log_func = logger.info

    match level:
        case 'info':
            log_func = logger.info
        case 'warn':
            log_func = logger.warn
        case 'error':
            log_func = logger.error
        case 'critical':
            log_func = logger.critical
        case 'exception':
            log_func = logger.exception

    log_func(msg)

    if logger_context:
        LogEntry.objects.log_action(
            user_id=logger_context['user_id'],
            change_message=msg,
            action_flag=CHANGE,
            content_type_id=ContentType.objects.get_for_model(User).pk,
            object_id=logger_context['object_id'],
            object_repr=logger_context['object_repr']
        )

def prepare_recipients(recipient_email):
    """
    Prepare a list of recipients to be emailed.

    recipient_email can be either a string (single recipient) or a array of strings.
    """
    recipients = [recipient_email] if type(recipient_email) == str else recipient_email
    logger.info(f"Starting celery task to send email to {recipients}")
    return recipients

def prepare_email(email_path, recipient_email, email_context, logger_context):
    """Prepare a valid email message and valid recipients."""
    recipients = prepare_recipients(recipient_email)
    html_message = get_template(email_path).render(email_context)
    valid_emails = filter_valid_emails(recipients, logger_context)

    return html_message, valid_emails


def automated_email(email_path, recipient_email, subject, email_context, text_message, logger_context=None):
    """Send email to user."""
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


def send_email(subject, message, html_message, recipient_list):
    """Send an email to a list of recipients."""
    num_emails_sent = send_mail(
        subject=subject,
        message=message,
        html_message=html_message,
        recipient_list=recipient_list,
        from_email=settings.EMAIL_HOST_USER,
    )

    if num_emails_sent == 0:
        raise Exception(
            f"Emails were attempted to the following email list: {recipient_list}. \
        But none were sent. They may be invalid."
        )


def filter_valid_emails(emails, logger_context=None):
    """Validate email addresses."""
    valid_emails = []
    for email in emails:
        try:
            validate_email(email)
            valid_emails.append(email)
        except ValidationError:
            log(
                f"{email} is not a valid email address. An email will not be sent to this address.",
                logger_context=logger_context
            )
    if len(valid_emails) == 0:
        raise ValidationError("No valid emails provided.")

    return valid_emails
