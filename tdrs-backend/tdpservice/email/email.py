"""
Send emails.

This module currently uses the EmailMultiAlternatives class from Django to send emails with HTML content.
A optional plain text message can be included as well. Emails should be sent using mail.delay()

The mail function is the main entry point for sending emails.
It takes in a EmailType enum(that has a template path as the value), a list of recipients,
and a dictionary of context variables to be used in the email template. The context vlaues can be found in the
templates directory.

There are optimizations that can be made to this module for sending mass emails.
Django's send_mass_mail function can be used to send multiple emails at once.
https://docs.djangoproject.com/en/4.1/topics/email/#send-mass-mail
"""

from celery import shared_task
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from django.template.loader import get_template
from django.template import TemplateDoesNotExist

import logging

logger = logging.getLogger(__name__)


@shared_task
def mail(email_path: str, recipient_email: str, email_context: dict = None) -> None:
    """Send email to user.

    Args:
        email_path (str): Path to email template.
        recipient_email (str): Email address of recipient.
        email_context (dict): Context variables to be used in email template.
    """
    subject = email_context["subject"]
    html_message = construct_email(email_path, email_context)

    if email_context["text_message"]:
        text_message = email_context["text_message"]
    else:
        text_message = "An email was sent with HTML content. Please view in an HTML capable email client."
    send_email(subject, text_message, html_message, [recipient_email])


def construct_email(email_path: str, context: dict):
    """Get email template."""
    try:
        template = get_template(email_path)
        return template.render(context)
    except TemplateDoesNotExist as exc:
        raise TemplateDoesNotExist(f"Template {email_path} does not exist") from exc


def send_email(
    subject: str, message: str, html_message: str, recipient_list: list
) -> bool:
    """Send an email to a list of recipients."""
    valid_emails = validate_emails(recipient_list)
    if validate_sender_email(settings.EMAIL_HOST_USER):
        email = EmailMultiAlternatives(
            subject=subject,
            body=message,
            from_email=settings.EMAIL_HOST_USER,
            to=valid_emails,
        )
        email.attach_alternative(html_message, "text/html")
        num_emails_sent = email.send()
        if num_emails_sent == 0:
            raise Exception(
                f"Emails were attempted to the following email list: {valid_emails}. \
            But none were sent. They may be invalid."
            )
        else:
            logger.info("Email sent successfully")
            return True
    return False


def validate_emails(emails: list) -> list:
    """Validate email addresses."""
    valid_emails = []
    for email in emails:
        try:
            validate_email(email)
            valid_emails.append(email)
        except ValidationError:
            logger.info(
                f"{email} is not a valid email address. An email will not be sent to this address."
            )
    if len(valid_emails) == 0:
        raise ValidationError("No valid emails provided.")
    return valid_emails


def validate_sender_email(email: str) -> bool:
    """Validate sender email address."""
    try:
        validate_email(email)
        return True
    except ValidationError as exc:
        raise ValidationError(
            f"{email} is not a valid email address. Cannot send from this email. No emails will be sent."
        ) from exc
