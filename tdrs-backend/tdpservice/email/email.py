"""Send emails."""

from django.core.mail import send_mail, send_mass_mail
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
def get_email_template(email_type, context):
    """Get email template."""
    try:
        template = get_template(email_type.value)
    except TemplateDoesNotExist:
        logger.error('Template does not exist')
        return
    template += '.html'
    return template.render(context)

@shared_task
def mail(email_type: EmailType, recipient_email:str, email_context: dict = None) -> None:
    """Send email to user."""
    subject = email_context['subject']
    html_message = get_email_template(email_type, email_context)
    send_email(subject, html_message, [recipient_email])

@shared_task
def send_email(subject: str, message: str, recipient_list: list) -> bool:
    """Send an email to a list of recipients."""
    valid_emails = validate_emails(recipient_list)

    # error handling for emails that worked
    response = send_mail(
        subject=subject,
        message='This is a test message.',
        html_message=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=valid_emails,
        fail_silently=False,
    )

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
