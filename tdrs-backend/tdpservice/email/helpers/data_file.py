"""Helper functions for sending data file submission emails."""

from django.conf import settings

from tdpservice.data_files.models import DataFile
from tdpservice.email.email import automated_email, log
from tdpservice.email.email_enums import AdminEmail, FraDataFileEmail, TanfDataFileEmail
from tdpservice.users.models import User


def get_friendly_program_type(program_type):
    """Return the human-readable name for a given program type."""
    match program_type:
        case DataFile.ProgramType.TANF:
            return "TANF"
        case DataFile.ProgramType.SSP:
            return "SSP"
        case DataFile.ProgramType.TRIBAL:
            return "Tribal TANF"
        case DataFile.ProgramType.FRA:
            return "FRA"


def get_program_section_str(program_type, section):
    """Return the human-readable section name, including program type."""
    match program_type:
        case DataFile.ProgramType.TANF:
            return section
        case DataFile.ProgramType.SSP:
            return f"SSP {section}"
        case DataFile.ProgramType.TRIBAL:
            return f"Tribal {section}"
        case DataFile.ProgramType.FRA:
            return section


def get_tanf_aggregates_context_count(datafile_summary):
    """Return the sum of cases with and without errors across all months for TANF files."""
    case_aggregates = datafile_summary.case_aggregates or {}
    cases_without_errors = 0
    cases_with_errors = 0
    rejected = case_aggregates["rejected"] if "rejected" in case_aggregates else 0

    if "months" in case_aggregates:
        for month in case_aggregates["months"]:
            cases_without_errors += (
                month["accepted_without_errors"]
                if "accepted_without_errors" in month
                and month["accepted_without_errors"] != "N/A"
                else 0
            )
            cases_with_errors += (
                month["accepted_with_errors"]
                if "accepted_with_errors" in month
                and month["accepted_with_errors"] != "N/A"
                else 0
            )

    return {
        "cases_without_errors": cases_without_errors,
        "cases_with_errors": cases_with_errors,
        "records_unable_to_process": rejected,
    }


def get_fra_aggregates_context_count(datafile_summary):
    """Return the relevant context data from case aggregates for FRA files."""
    case_aggregates = datafile_summary.case_aggregates or {}
    total_errors = (
        case_aggregates["total_errors"] if "total_errors" in case_aggregates else 0
    )
    return {
        "records_created": datafile_summary.total_number_of_records_created,
        "total_errors": total_errors,
    }


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

    prog_type = datafile.program_type
    section_name = get_program_section_str(prog_type, datafile.section)

    file_type = get_friendly_program_type(prog_type)
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

    if datafile_summary.status == DataFileSummary.Status.PENDING:
        log(
            "Email triggered for pending data file, skipping.",
            logger_context=logger_context,
        )
        return

    match prog_type:
        case (
            DataFile.ProgramType.TANF
            | DataFile.ProgramType.SSP
            | DataFile.ProgramType.TRIBAL
        ):
            context.update(get_tanf_aggregates_context_count(datafile_summary))

            match datafile_summary.status:
                case DataFileSummary.Status.ACCEPTED:
                    template_path = TanfDataFileEmail.ACCEPTED.value
                    subject = f"{section_name} Successfully Submitted Without Errors"
                    text_message = (
                        f"{file_type} has been submitted and processed without errors."
                    )
                case DataFileSummary.Status.ACCEPTED_WITH_ERRORS:
                    template_path = TanfDataFileEmail.ACCEPTED_WITH_ERRORS.value
                    subject = f"Action Required: {section_name} Contains Errors"
                    text_message = (
                        f"{file_type} has been submitted and processed with errors."
                    )
                case DataFileSummary.Status.PARTIALLY_ACCEPTED:
                    template_path = TanfDataFileEmail.PARTIALLY_ACCEPTED.value
                    subject = f"Action Required: {section_name} Contains Errors"
                    text_message = (
                        f"{file_type} has been submitted and processed with errors."
                    )
                case DataFileSummary.Status.REJECTED:
                    template_path = TanfDataFileEmail.REJECTED.value
                    subject = f"Action Required: {section_name} Contains Errors"
                    text_message = (
                        f"{file_type} has been submitted and processed with errors."
                    )

        case DataFile.ProgramType.FRA:
            context.update(get_fra_aggregates_context_count(datafile_summary))

            match datafile_summary.status:
                case DataFileSummary.Status.ACCEPTED:
                    template_path = FraDataFileEmail.ACCEPTED.value
                    subject = f"{section_name} Successfully Submitted Without Errors"
                    text_message = (
                        f"{file_type} has been submitted and processed without errors."
                    )
                case DataFileSummary.Status.ACCEPTED_WITH_ERRORS:
                    template_path = FraDataFileEmail.ACCEPTED_WITH_ERRORS.value
                    subject = f"Action Required: {section_name} Contains Errors"
                    text_message = (
                        f"{file_type} has been submitted and processed with errors."
                    )
                case DataFileSummary.Status.PARTIALLY_ACCEPTED:
                    template_path = FraDataFileEmail.PARTIALLY_ACCEPTED.value
                    subject = f"Action Required: {section_name} Contains Errors"
                    text_message = (
                        f"{file_type} has been submitted and processed with errors."
                    )
                case DataFileSummary.Status.REJECTED:
                    template_path = FraDataFileEmail.REJECTED.value
                    subject = f"Action Required: {section_name} Contains Errors"
                    text_message = (
                        f"{file_type} has been submitted and processed with errors."
                    )

    context.update({"subject": subject})

    log(
        f"Data file submitted; emailing Data Analysts {list(recipients)}",
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


def send_stuck_file_email(stuck_files, recipients):
    """Send an email to sys admins with details of files stuck in Pending."""
    logger_context = {"user_id": User.objects.get_or_create(username="system")[0].pk}

    template_path = AdminEmail.STUCK_FILE_LIST.value
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
