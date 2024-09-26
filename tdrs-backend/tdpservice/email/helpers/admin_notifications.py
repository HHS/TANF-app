"""helper functions to administer user accounts."""

def email_admin_deactivated_user(user):
    """Send an email to OFA Admins when a user is deactivated."""
    from tdpservice.users.models import User
    from tdpservice.email.email_enums import EmailType
    from tdpservice.email.email import automated_email, log
    from tdpservice.email.tasks import get_ofa_admin_user_emails

    recipient_emails = get_ofa_admin_user_emails()
    logger_context = {
        'user_id': user.id,
        'object_id': user.id,
        'object_repr': user.username,
        'content_type': User,
    }

    template_path = EmailType.ACCOUNT_DEACTIVATED_ADMIN.value
    text_message = 'A user account has been deactivated.'
    subject = ' TDP User Account Deactivated due to Inactivity'
    context = {
        'user': user,
    }

    log(f"Preparing email to OFA Admins for deactivated user {user.username}", logger_context=logger_context)

    for recipient_email in recipient_emails:
        automated_email(
            email_path=template_path,
            recipient_email=recipient_email,
            subject=subject,
            email_context=context,
            text_message=text_message,
            logger_context=logger_context
        )
