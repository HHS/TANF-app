"""Helper methods for sending emails to users about their account deactivation."""
from tdpservice.email.email_enums import EmailType
from tdpservice.email.email import automated_email
from datetime import datetime, timedelta, timezone
from django.conf import settings


def send_deactivation_warning_email(users, days):
    """Send an email to users that are about to be deactivated."""
    from tdpservice.users.models import User

    template_path = EmailType.DEACTIVATION_WARNING.value
    text_message = f'Your account will be deactivated in {days} days.'
    subject = f'Account Deactivation Warning: {days} days remaining'
    deactivation_date = datetime.now(timezone.utc) + timedelta(days=days)

    for user in users:
        recipient_email = user.email
        context = {
            'first_name': user.first_name,
            'days': days,
            'deactivation_date': deactivation_date,
            'url': f'{settings.FRONTEND_BASE_URL}/login/'
        }

        logger_context = {
           'user_id': user.id,
           'object_id': user.id,
           'object_repr': user.email,
           'content_type': User,
        }

        automated_email(
            email_path=template_path,
            recipient_email=recipient_email,
            subject=subject,
            email_context=context,
            text_message=text_message,
            logger_context=logger_context
        )
