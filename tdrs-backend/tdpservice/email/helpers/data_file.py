"""Helper functions for sending data file submission emails."""

from zoneinfo import ZoneInfo

from django.conf import settings

from tdpservice.data_files.models import DataFile
from tdpservice.email.email import automated_email, log
from tdpservice.email.email_enums import AdminEmail, FraDataFileEmail, TanfDataFileEmail
from tdpservice.parsers.models import DataFileSummary
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


def get_tanf_total_errors_context_count(datafile_summary):
    """Return the sum of total errors across all months for aggregate/stratum TANF files."""
    case_aggregates = datafile_summary.case_aggregates or {}
    total_errors = 0

    if "months" in case_aggregates:
        for month in case_aggregates["months"]:
            total_errors += (
                month["total_errors"]
                if "total_errors" in month and month["total_errors"] != "N/A"
                else 0
            )

    return {"total_errors": total_errors}


def get_pia_quarter_label(quarter):
    """Return the human-readable quarter label for PIA submissions."""
    match quarter:
        case DataFile.Quarter.Q1:
            return "Quarter 1 (October - December)"
        case DataFile.Quarter.Q2:
            return "Quarter 2 (January - March)"
        case DataFile.Quarter.Q3:
            return "Quarter 3 (April - June)"
        case DataFile.Quarter.Q4:
            return "Quarter 4 (July - September)"


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


def get_base_context(datafile_summary):
    """Build the context object shared by all submission emails."""
    datafile = datafile_summary.datafile

    prog_type = datafile.program_type
    section_name = get_program_section_str(prog_type, datafile.section)
    is_program_audit = datafile.is_program_audit

    file_type = (
        "TANF Program Integrity Audit"
        if is_program_audit
        else get_friendly_program_type(prog_type)
    )
    stt_name = datafile.stt.name
    if datafile.created_at is not None:
        stt_tz = ZoneInfo(datafile.stt.timezone or "UTC")
        local_time = datafile.created_at.astimezone(stt_tz)
        submission_date = local_time.strftime("%m/%d/%Y %I:%M %p %Z")
    else:
        submission_date = datafile.created_at
    fiscal_year = datafile.fiscal_year
    submitted_by = datafile.submitted_by

    is_aggregate = datafile.section in (
        DataFile.Section.AGGREGATE_DATA,
        DataFile.Section.STRATUM_DATA,
    )

    context = {
        "stt_name": stt_name,
        "submission_date": submission_date,
        "fiscal_year": fiscal_year,
        "section_name": section_name,
        "submitted_by": submitted_by,
        "file_type": file_type,
        "status": datafile_summary.status,
        "has_errors": datafile_summary.status != DataFileSummary.Status.ACCEPTED,
        "is_aggregate": is_aggregate,
        "is_program_audit": is_program_audit,
        "url": settings.FRONTEND_BASE_URL,
    }

    return context


def get_tanf_template_options(is_reprocessed):
    """Return the templates to use for TANF emails based on the reparsing status."""
    if is_reprocessed:
        return {
            DataFileSummary.Status.ACCEPTED: TanfDataFileEmail.REPARSE_ERRORS_RESOLVED.value,
            DataFileSummary.Status.ACCEPTED_WITH_ERRORS: TanfDataFileEmail.REPARSE_ACTION_REQUIRED.value,
            DataFileSummary.Status.PARTIALLY_ACCEPTED: TanfDataFileEmail.REPARSE_ACTION_REQUIRED.value,
            DataFileSummary.Status.REJECTED: TanfDataFileEmail.REPARSE_ACTION_REQUIRED.value,
        }

    return {
        DataFileSummary.Status.ACCEPTED: TanfDataFileEmail.ACCEPTED.value,
        DataFileSummary.Status.ACCEPTED_WITH_ERRORS: TanfDataFileEmail.ACCEPTED_WITH_ERRORS.value,
        DataFileSummary.Status.PARTIALLY_ACCEPTED: TanfDataFileEmail.PARTIALLY_ACCEPTED.value,
        DataFileSummary.Status.REJECTED: TanfDataFileEmail.REJECTED.value,
    }


def get_fra_template_options(is_reprocessed):
    """Return the templates to use for FRA emails based on the reparsing status."""
    if is_reprocessed:
        return {
            DataFileSummary.Status.ACCEPTED: FraDataFileEmail.REPARSE_ERRORS_RESOLVED.value,
            DataFileSummary.Status.ACCEPTED_WITH_ERRORS: FraDataFileEmail.REPARSE_ACTION_REQUIRED.value,
            DataFileSummary.Status.PARTIALLY_ACCEPTED: FraDataFileEmail.REPARSE_ACTION_REQUIRED.value,
            DataFileSummary.Status.REJECTED: FraDataFileEmail.REPARSE_ACTION_REQUIRED.value,
        }

    return {
        DataFileSummary.Status.ACCEPTED: FraDataFileEmail.ACCEPTED.value,
        DataFileSummary.Status.ACCEPTED_WITH_ERRORS: FraDataFileEmail.ACCEPTED_WITH_ERRORS.value,
        DataFileSummary.Status.PARTIALLY_ACCEPTED: FraDataFileEmail.PARTIALLY_ACCEPTED.value,
        DataFileSummary.Status.REJECTED: FraDataFileEmail.REJECTED.value,
    }


def get_pia_email_subject(status, file_type, quarter_label, is_reprocessed):
    """Return the email subject to use for Program Integrity Audit emails."""
    if status == DataFileSummary.Status.ACCEPTED:
        if is_reprocessed:
            return f"{file_type}: {quarter_label} Submission Errors Resolved"
        else:
            return f"{file_type}: {quarter_label} Successfully Submitted Without Errors"
    else:
        if is_reprocessed:
            return f"Action Required: Error Report Available for {file_type}: {quarter_label} Submission"
        else:
            return f"Action Required: {file_type}: {quarter_label} Contains Errors"


def get_tanf_fra_email_subject(status, section_name, is_reprocessed):
    """Return the email subject to use for TANF/FRA submission emails."""
    if status == DataFileSummary.Status.ACCEPTED:
        if is_reprocessed:
            return f"{section_name} Submission Errors Resolved"
        return f"{section_name} Successfully Submitted Without Errors"
    else:
        if is_reprocessed:
            return (
                f"Action Required: Error Report Available for {section_name} Submission"
            )
        return f"Action Required: {section_name} Contains Errors"


def send_data_submitted_email(datafile_summary, recipients, is_reprocessed=False):
    """Send an email to a user when their account approval status is updated."""
    datafile = datafile_summary.datafile
    prog_type = datafile.program_type

    logger_context = {
        "user_id": datafile.user.id,
        "object_id": datafile.id,
        "object_repr": f"Uploaded data file for quarter: {datafile.fiscal_year}",
        "content_type": DataFile,
    }

    template_path = None
    subject = None
    text_message = None

    context = get_base_context(datafile_summary)

    file_type = context["file_type"]
    section_name = context["section_name"]
    is_program_audit = context["is_program_audit"]
    is_aggregate = context["is_aggregate"]

    if datafile_summary.status == DataFileSummary.Status.PENDING:
        return

    text_message = (
        f"{file_type} has been submitted and processed without errors."
        if datafile_summary.status == DataFileSummary.Status.ACCEPTED
        else f"{file_type} has been submitted and processed with errors."
    )

    if is_program_audit:
        quarter_label = get_pia_quarter_label(datafile.quarter)
        context.update({"quarter_label": quarter_label})
        context.update(get_tanf_aggregates_context_count(datafile_summary))

        subject = get_pia_email_subject(
            datafile_summary.status, file_type, quarter_label, is_reprocessed
        )

        template_options = get_tanf_template_options(is_reprocessed)
        template_path = template_options[datafile_summary.status]
    else:
        subject = get_tanf_fra_email_subject(
            datafile_summary.status, section_name, is_reprocessed
        )

        match prog_type:
            case (
                DataFile.ProgramType.TANF
                | DataFile.ProgramType.SSP
                | DataFile.ProgramType.TRIBAL
            ):
                if is_aggregate:
                    context.update(
                        get_tanf_total_errors_context_count(datafile_summary)
                    )
                else:
                    context.update(get_tanf_aggregates_context_count(datafile_summary))

                template_options = get_tanf_template_options(is_reprocessed)
                template_path = template_options[datafile_summary.status]

            case DataFile.ProgramType.FRA:
                context.update(get_fra_aggregates_context_count(datafile_summary))

                template_options = get_fra_template_options(is_reprocessed)
                template_path = template_options[datafile_summary.status]

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
