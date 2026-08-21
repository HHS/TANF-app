"""Notification helpers for ETL pipelines."""

import logging

from django.db.models import Q

from tdpservice.email.helpers.etl import (
    send_statistical_weights_run_email,
    statistical_weights_run_detail_url,
)
from tdpservice.etl.models import ETLPipelineRun
from tdpservice.users.models import AccountApprovalStatusChoices, User

logger = logging.getLogger(__name__)


def _operational_recipient_emails() -> list[str]:
    """Return approved operational recipients for ETL notifications."""
    return list(
        User.objects.filter(
            Q(groups__name="OFA System Admin") | Q(groups__name="DIGIT Team"),
            account_approval_status=AccountApprovalStatusChoices.APPROVED,
        )
        .exclude(email="")
        .values_list("email", flat=True)
        .distinct()
    )


def send_statistical_weights_notification(pipeline_run: ETLPipelineRun) -> dict:
    """Send the statistical weights run-completion notification."""
    recipients = _operational_recipient_emails()
    if not recipients:
        return {"notification": "no_recipients"}

    try:
        send_statistical_weights_run_email(pipeline_run, recipients)
    except Exception as exc:
        logger.exception("Failed to send ETL notification email.")
        return {
            "notification": "failed",
            "error": str(exc),
            "recipients": recipients,
        }

    return {
        "notification": "sent",
        "recipient_count": len(recipients),
        "run_detail_url": statistical_weights_run_detail_url(pipeline_run),
    }
