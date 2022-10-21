"""Helper functions for sending data file submission emails."""
from tdpservice.email.email_enums import EmailType
from tdpservice.email.email import automated_email, log


def send_data_submitted_email(recipients, context):
    """Send an email to a user when their data has been submitted."""
    template_path = EmailType.DATA_SUBMITTED.value
    subject = 'Data Submitted'
    text_message = 'Your data has been submitted.'

    log(f'emailing {recipients}')

    automated_email.delay(
        email_path=template_path,
        recipient_email=recipients,
        subject=subject,
        email_context=context,
        text_message=text_message
    )
