"""Helper functions for sending data file submission emails."""
from django.conf import settings
from tdpservice.email.email_enums import EmailType
from tdpservice.email.email import automated_email, log
from tdpservice.parsers.util import get_prog_from_section


def send_data_submitted_email(
    datafile_summary,
    recipients,
):
    """Send an email to a user when their account approval status is updated."""
    from tdpservice.parsers.models import DataFileSummary

    datafile = datafile_summary.datafile

    logger_context = {
        'user_id': datafile.user.id,
        'object_id': datafile.id,
        'object_repr': f"Uploaded data file for quarter: {datafile.fiscal_year}"
    }

    template_path = None
    subject = None
    text_message = None

    section_name = datafile.section
    prog_type = get_prog_from_section(section_name)
    file_type = f'{prog_type}F' if prog_type != 'SSP' else prog_type
    stt_name = datafile.stt.name
    submission_date = datafile.created_at
    fiscal_year = datafile.fiscal_year
    submitted_by = datafile.submitted_by

    context = {
        'stt_name': stt_name,
        'submission_date': submission_date,
        'fiscal_year': fiscal_year,
        'section_name': section_name,
        'submitted_by': submitted_by,
        'file_type': file_type,
        'has_errors': datafile_summary.status != DataFileSummary.Status.ACCEPTED,
        "url": settings.FRONTEND_BASE_URL
    }

    log(f'Data file submitted; emailing Data Analysts {recipients}', logger_context=logger_context)

    match datafile_summary.status:
        case DataFileSummary.Status.PENDING:
            return

        case DataFileSummary.Status.ACCEPTED:
            template_path = EmailType.DATA_SUBMITTED.value
            subject = f'{section_name} Processed Without Errors'
            text_message = f'{file_type} has been submitted and processed without errors.'

        case _:
            template_path = EmailType.DATA_SUBMITTED.value
            subject = f'{section_name} Processed With Errors'
            text_message = f'{file_type} has been submitted and processed with errors.'

    context.update({'subject': subject})

    automated_email(
        email_path=template_path,
        recipient_email=recipients,
        subject=subject,
        email_context=context,
        text_message=text_message,
        logger_context=logger_context
    )
