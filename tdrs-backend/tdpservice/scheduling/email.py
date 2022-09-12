from django.core.mail import send_mail, send_mass_mail
from celery import shared_task
from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
import logging

logger = logging.getLogger(__name__)


@shared_task
def send_email(subject: str, message: str, recipient_list: list) -> bool:
    """Send an email to a list of recipients."""
    valid_emails = validate_emails(recipient_list)
    response = send_mail(
        subject=subject,
        message=message,
        from_email='test_user@hhs.gov',
        recipient_list=valid_emails,
        fail_silently=False,
    )
    return True

@shared_task
def send_mass_email(subject: str, message: str, sender: str, recipient_list: list):
    send_mass_mail(
        subject,
        message,
        sender,
        recipient_list,
        fail_silently=False,
    )

@shared_task
def validate_emails(emails: list) -> list:
    """Validate email addresses."""
    valid_emails = []
    for email in emails:
        if validate_single_email(email):
            valid_emails.append(email)
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