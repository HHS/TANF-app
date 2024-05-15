"""Helper functions for sending approval status update emails."""
from tdpservice.email.email_enums import EmailType
from tdpservice.email.email import automated_email, log


def send_approval_status_update_email(
    new_approval_status,
    user,
    context,
):
    """Send an email to a user when their account approval status is updated."""
    from tdpservice.users.models import AccountApprovalStatusChoices, User

    recipient_email = user.email
    logger_context = {
        'user_id': user.id,
        'object_id': user.id,
        'object_repr': user.email,
        'content_type': User,
    }

    template_path = None
    subject = None
    text_message = None

    log(f"Preparing email to {recipient_email} with status {new_approval_status}", logger_context=logger_context)

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

    automated_email(
        email_path=template_path,
        recipient_email=recipient_email,
        subject=subject,
        email_context=context,
        text_message=text_message,
        logger_context=logger_context
    )
