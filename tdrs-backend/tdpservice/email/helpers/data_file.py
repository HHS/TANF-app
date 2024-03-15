"""Helper functions for sending data file submission emails."""
from tdpservice.email.email_enums import EmailType
from tdpservice.email.email import automated_email, log


def send_data_submitted_email(recipients, data_file, context, subject):
    """Send an email to a user when their data has been submitted."""
    from tdpservice.users.models import User

    template_path = EmailType.DATA_SUBMITTED.value
    text_message = 'Your data has been submitted.'

    logger_context = {
        'user_id': data_file.user.id,
        'object_id': data_file.id,
        'object_repr': f"Uploaded data file for quarter: {data_file.fiscal_year}",
        'content_type': User,
    }

    log(f'Data file submitted; emailing Data Analysts {recipients}', logger_context=logger_context)

    automated_email(
        email_path=template_path,
        recipient_email=recipients,
        subject=subject,
        email_context=context,
        text_message=text_message
    )
