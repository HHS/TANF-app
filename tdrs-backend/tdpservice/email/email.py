"""Wrapper to send emails with Django."""

from tdpservice.email.email_enums import EmailType

from celery import shared_task
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from django.template.loader import get_template

import logging

logger = logging.getLogger(__name__)


def send_approval_status_update_email(
    new_approval_status,
    recipient_email,
    context
):
    """Send an email to a user when their account approval status is updated."""
    from tdpservice.users.models import AccountApprovalStatusChoices

    template_path = None
    subject = None
    text_message = None

    match new_approval_status:
        case AccountApprovalStatusChoices.INITIAL:
            print("initial")
            return

        case AccountApprovalStatusChoices.ACCESS_REQUEST:
            template_path = EmailType.ACCESS_REQUEST_SUBMITTED.value
            subject = 'Account requested'
            text_message = 'Your account has been requested.'

        case AccountApprovalStatusChoices.PENDING:
            print("pending")
            return

        case AccountApprovalStatusChoices.APPROVED:
            template_path = EmailType.REQUEST_APPROVED.value
            subject = 'Access request approved'
            text_message = 'Your account request has been approved.'

        case AccountApprovalStatusChoices.DENIED:
            template_path = EmailType.REQUEST_DENIED.value
            subject = 'Access request denied'
            text_message = 'Your account request has been denied.'

        case AccountApprovalStatusChoices.DEACTIVATED:
            template_path = EmailType.ACCOUNT_DEACTIVATED.value
            subject = 'Account deactivated'
            text_message = 'Your account has been deactivated.'

    mail.delay(
        email_path=template_path,
        recipient_email=recipient_email,
        subject=subject,
        email_context=context,
        text_message=text_message
    )


@shared_task
def mail(email_path, recipient_email, subject, email_context, text_message):
    """Send email to user."""
    subject = email_context['subject']
    html_message = construct_email(email_path, email_context)

    if not text_message:
        text_message = 'An email was sent with HTML content. Please view in an HTML capable email client.'

    send_email(subject, text_message, html_message, [recipient_email])


def construct_email(email_path, context):
    """Get email template."""
    template = get_template(email_path)
    return template.render(context)


def send_email(subject, message, html_message, recipient_list):
    """Send an email to a list of recipients."""
    valid_emails = filter_valid_emails(recipient_list)
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
    return False


def filter_valid_emails(emails):
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