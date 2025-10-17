"""Helper functions for sending data file submission emails."""

from django.conf import settings

from tdpservice.data_files.models import DataFile
from tdpservice.email.email import automated_email, log
from tdpservice.email.email_enums import EmailType
from tdpservice.users.models import User


def send_data_submitted_email(
    datafile_summary,
    recipients,
):
    """Send an email to a user when their account approval status is updated."""
    from tdpservice.parsers.models import DataFileSummary

    datafile = datafile_summary.datafile

    logger_context = {
        "user_id": datafile.user.id,
        "object_id": datafile.id,
        "object_repr": f"Uploaded data file for quarter: {datafile.fiscal_year}",
        "content_type": DataFile,
    }

    template_path = None
    subject = None
    text_message = None

    section_name = datafile.section

    file_type = datafile.prog_type  # e.g. "TAN", "SSP", "FRA"
    # TANF and Tribal TANF file types are stored as "TAN" in prog_type
    if file_type == "TAN":
        if section_name.startswith("Tribal"):
            file_type = f"Tribal {file_type}"
        file_type = f"{file_type}F"

    stt_name = datafile.stt.name
    submission_date = datafile.created_at
    fiscal_year = datafile.fiscal_year
    submitted_by = datafile.submitted_by

    context = {
        "stt_name": stt_name,
        "submission_date": submission_date,
        "fiscal_year": fiscal_year,
        "section_name": section_name,
        "submitted_by": submitted_by,
        "file_type": file_type,
        "status": datafile_summary.status,
        "has_errors": datafile_summary.status != DataFileSummary.Status.ACCEPTED,
        "url": settings.FRONTEND_BASE_URL,
    }

    log(
        f"Data file submitted; emailing Data Analysts {list(recipients)}",
        logger_context=logger_context,
    )

    match datafile_summary.status:
        case DataFileSummary.Status.PENDING:
            return

        case DataFileSummary.Status.ACCEPTED:
            match file_type:
                case "FRA":
                    template_path = EmailType.FRA_SUBMITTED.value
                    subject = f"{section_name} Successfully Submitted"
                case _:
                    template_path = EmailType.DATA_SUBMITTED.value
                    subject = f"{section_name} Processed Without Errors"
            text_message = (
                f"{file_type} has been submitted and processed without errors."
            )

        case _:
            match file_type:
                case "FRA":
                    template_path = EmailType.FRA_SUBMITTED.value
                    subject = f"Action Required: {section_name} Contains Errors"
                case _:
                    template_path = EmailType.DATA_SUBMITTED.value
                    subject = f"{section_name} Processed With Errors"
            text_message = f"{file_type} has been submitted and processed with errors."

    context.update({"subject": subject})

    automated_email(
        email_path=template_path,
        recipient_email=recipients,
        subject=subject,
        email_context=context,
        text_message=text_message,
        logger_context=logger_context,
    )


def send_stuck_file_email(stuck_files, recipients):
    """Send an email to sys admins with details of files stuck in Pending."""
    logger_context = {"user_id": User.objects.get_or_create(username="system")[0].pk}

    template_path = EmailType.STUCK_FILE_LIST.value
    subject = "List of submitted files with pending status after 1 hour"
    text_message = "The system has detected stuck files."

    context = {
        "subject": subject,
        "url": settings.FRONTEND_BASE_URL,
        "files": stuck_files,
    }

    log(
        f"Emailing stuck files to SysAdmins: {list(recipients)}",
        logger_context=logger_context,
    )

    automated_email(
        email_path=template_path,
        recipient_email=recipients,
        subject=subject,
        email_context=context,
        text_message=text_message,
        logger_context=logger_context,
    )
