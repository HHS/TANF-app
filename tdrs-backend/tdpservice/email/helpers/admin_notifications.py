"""helper functions to administer user accounts."""
from tdpservice.users.models import User
from tdpservice.email.email_enums import EmailType
from tdpservice.email.email import automated_email, log

def email_admin_deactivated_user(user):
    """Send an email to OFA Admins when a user is deactivated."""
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

def email_system_owner_system_admin_role_change(user, action):
    """Send an email to the System Owner when a user is assigned or removed from the System Admin role."""
    from tdpservice.email.tasks import get_system_owner_email
    recipient_email = get_system_owner_email()
    logger_context = {
        'user_id': user.id,
        'object_id': user.id,
        'object_repr': user.username,
        'content_type': User,
    }

    template_path = EmailType.SYSTEM_ADMIN_ROLE_CHANGED.value

    if action == 'added':
        text_message = 'A user has been assigned to OFA System Admin role.'
    elif action == 'is_staff_assigned':
        text_message = 'A user has been assigned to staff role.'
    elif action == 'is_superuser_assigned':
        text_message = 'A user has been assigned to superuser role.'
    elif action == 'is_staff_removed':
        text_message = 'A user has been removed from staff role.'
    else:
        text_message = 'A user has been removed from OFA System Admin role.'
    subject = 'TDP User Role Change: OFA System Admin'
    context = {
        'user': user,
        'action': action,
    }

    log(f"Preparing email to System Owner for System Admin role change for user {user.username}",
        logger_context=logger_context)

    automated_email(
        email_path=template_path,
        recipient_email=recipient_email,
        subject=subject,
        email_context=context,
        text_message=text_message,
        logger_context=logger_context
    )
