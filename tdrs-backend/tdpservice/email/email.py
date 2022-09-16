"""Send emails."""

from celery import shared_task
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from django.template.loader import get_template
from django.template import TemplateDoesNotExist
from tdpservice.email.email_enums import EmailType

import logging

logger = logging.getLogger(__name__)

@shared_task
def construct_email(email_type: EmailType, context: dict):
    """Get email template."""
    template_path = email_type.value + ".html"
    try:
        template = get_template(template_path)
    except TemplateDoesNotExist:
        logger.error(f'Template {template_path} does not exist')
        return

    return template.render(context)

@shared_task
def mail(email_type: EmailType, recipient_email: str, email_context: dict = None) -> None:
    """Send email to user."""
    subject = email_context['subject']
    html_message = construct_email(email_type, email_context)

    if email_context['text_message']:
        text_message = email_context['text_message']
    else:
        text_message = 'An email was sent with HTML content. Please view in an HTML capable email client.'

    send_email(subject, text_message, html_message, [recipient_email])

@shared_task
def send_email(subject: str, message: str, html_message: str, recipient_list: list) -> bool:
    """Send an email to a list of recipients."""
    valid_emails = validate_emails(recipient_list)

    # use EmailMultiAlternatives using the html_message and message

    msg = EmailMultiAlternatives(subject, message, settings.DEFAULT_FROM_EMAIL, valid_emails)
    msg.attach_alternative(html_message, "text/html")
    response = msg.send()

    if response == 0:
        logger.error('Email failed to send')
        return False

    logger.info('Email sent successfully')
    return True

@shared_task
def validate_emails(emails: list) -> list:
    """Validate email addresses."""
    valid_emails = []
    for email in emails:
        if validate_single_email(email):
            valid_emails.append(email)
    if len(valid_emails) == 0:
        raise ValidationError("No valid emails provided.")
    return valid_emails

@shared_task
def validate_single_email(email: str) -> bool:
    """Validate email address."""
    try:
        validate_email(email)
        return True
    except ValidationError:
        logger.info(f"{email} is not a valid email address. An email will not be sent to this address.")
        return False

@shared_task
def validate_sender_email(email: str) -> bool:
    """Validate sender email address."""
    try:
        validate_email(email)
        return True
    except ValidationError:
        logger.info(f"{email} is not a valid email address. Cannot send from this email. No emails will be sent.")
        return False
