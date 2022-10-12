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
    logger.info(f"Preparing email to {recipient_email} with status {new_approval_status}")
    match new_approval_status:
        case AccountApprovalStatusChoices.INITIAL:
            # Stubbed for future use
            return

        case AccountApprovalStatusChoices.ACCESS_REQUEST:
            template_path = EmailType.ACCESS_REQUEST_SUBMITTED.value
            subject = 'Access Request Submitted'
            text_message = 'Your account has been requested.'

        case AccountApprovalStatusChoices.PENDING:
            # Stubbed for future use
            return

        case AccountApprovalStatusChoices.APPROVED:
            template_path = EmailType.REQUEST_APPROVED.value
            subject = 'Access Request Approved'
            text_message = 'Your account request has been approved.'

        case AccountApprovalStatusChoices.DENIED:
            template_path = EmailType.REQUEST_DENIED.value
            subject = 'Access Request Denied'
            text_message = 'Your account request has been denied.'

        case AccountApprovalStatusChoices.DEACTIVATED:
            template_path = EmailType.ACCOUNT_DEACTIVATED.value
            subject = 'Account is Deactivated'
            text_message = 'Your account has been deactivated.'

    context.update({'subject': subject})

    automated_email.delay(
        email_path=template_path,
        recipient_email=recipient_email,
        subject=subject,
        email_context=context,
        text_message=text_message
    )


@shared_task
def automated_email(email_path, recipient_email, subject, email_context, text_message):
    """Send email to user."""
    logger.info(f"Starting celery task to send email to {recipient_email}")
    html_message = construct_email(email_path, email_context)

    send_email(subject, text_message, html_message, [recipient_email])


def construct_email(email_path, context):
    """Get email template."""
    logger.info(f"Constructing email from template {email_path}")
    template = get_template(email_path)
    logger.info(f"Email template rendered from the path {email_path}")

    return template.render(context)


def send_email(subject, message, html_message, recipient_list):
    """Send an email to a list of recipients."""
    logger.info(f"Envoked send_email with subject {subject}")
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

    logger.info(f"{num_emails_sent} email(s) sent to {valid_emails}.")


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
