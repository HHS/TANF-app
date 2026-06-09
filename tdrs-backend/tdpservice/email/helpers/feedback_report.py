"""Helper functions for sending feedback report notification emails."""

from django.conf import settings

from tdpservice.email.email import automated_email, log
from tdpservice.email.email_enums import FeedbackReportEmail
from tdpservice.reports.models import ReportFile, ReportType


REPORT_TYPE_LABELS = {
    ReportType.TANF_SSP: ReportType.TANF_SSP.label,
    ReportType.TRIBAL_TANF: ReportType.TRIBAL_TANF.label,
    ReportType.FRA: ReportType.FRA.label,
}


def send_feedback_report_available_email(report_file: ReportFile, recipients):
    """
    Send an email when a feedback report is available.

    Parameters
    ----------
        report_file: The ReportFile that was created
        recipients: List of email addresses (usernames) to send to
    """
    if not recipients:
        return

    # Format date_extracted_on as MM/DD/YYYY
    date_extracted_str = (
        report_file.date_extracted_on.strftime("%m/%d/%Y")
        if report_file.date_extracted_on
        else "N/A"
    )

    # Only create logger_context if we have a valid user (LogEntry requires user_id)
    logger_context = None
    if report_file.user:
        logger_context = {
            "user_id": report_file.user.id,
            "object_id": report_file.id,
            "object_repr": f"ReportFile for {report_file.stt.name} FY {report_file.year} ({date_extracted_str})",
            "content_type": ReportFile,
        }

    template_path = FeedbackReportEmail.REPORT_AVAILABLE.value
    report_type = getattr(report_file, "report_type", ReportType.TANF_SSP)
    report_type_label = REPORT_TYPE_LABELS.get(
        report_type, ReportType.TANF_SSP.label
    )
    subject = f"{report_type_label} Feedback Report Available: {report_file.stt.name} - FY {report_file.year}"
    text_message = (
        f"A new {report_type_label} feedback report is available for {report_file.stt.name} "
        f"for Fiscal Year {report_file.year} (reflects data submitted through {date_extracted_str})."
    )

    context = {
        "stt_name": report_file.stt.name,
        "fiscal_year": report_file.year,
        "date_extracted_on": date_extracted_str,
        "report_date": report_file.created_at.strftime("%m/%d/%Y"),
        "report_type": report_type,
        "report_type_label": report_type_label,
        "url": settings.FRONTEND_BASE_URL,
        "subject": subject,
    }

    log(
        f"Feedback report available; emailing recipients {list(recipients)}",
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
