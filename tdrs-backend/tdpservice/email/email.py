"""Send emails."""

from django.core.mail import send_mail, send_mass_mail
from celery import shared_task
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from django.template.loader import get_template
from tdpservice.email.email_enums import EmailType


import logging
import datetime

logger = logging.getLogger(__name__)

@shared_task
def get_email_template(email_type, context):
    """Get email template."""
    template = get_template("datasubmitted.html")
    return template.render(context)

@shared_task
def mail(email_type: EmailType,
        recipient_email:str,
        date: datetime.datetime = datetime.datetime.now(),
        first_name: str = None,
        group_permission: str = None,
        stt_name: str = None,
        submission_date: str = None) -> None:
    """Send email to user."""
    subject = email_type.value
    email_context = {
        'first_name': first_name,
        'group_permission': group_permission,
        'stt_name': stt_name,
        'submission_date': submission_date,
        'fiscal_year': get_fiscal_year(date)
        }
    html_message = get_email_template(email_type, email_context)
    print(html_message)
    send_email(subject, html_message, [recipient_email])


@shared_task
def get_fiscal_year(date: datetime.datetime) -> str:
    """Given a date, return the fiscal year and quater formatted as YYYY Quarter."""

    current_date = datetime.datetime.now()
    current_year = current_date.year
    current_month = current_date.month
    if current_month >= 10:
        fiscal_year = current_year + 1
    else:
        fiscal_year = current_year

    if date.month >= 10:
        qt = 'Q1'
        quarter = 'October - December'
    elif date.month >= 7:
        qt = 'Q4'
        quarter = 'July - September'
    elif date.month >= 4:
        qt = 'Q3'
        quarter = 'April - June'
    else:
        qt = 'Q2'
        quarter = 'January - March'

    return f'{fiscal_year} {qt} ({quarter})'


@shared_task
def load_template(template_path: str, context: dict) -> str:
    """Send email with html content."""
    # error handling for template path
    template = get_template(template_path)
    return template.render(context)

@shared_task
def send_email(subject: str, message: str, recipient_list: list) -> bool:
    """Send an email to a list of recipients."""
    valid_emails = validate_emails(recipient_list)

    # error handling for emails that worked
    send_mail(
        subject=subject,
        message=message,
        html_message=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=valid_emails,
        fail_silently=False,
    )
    return True

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
