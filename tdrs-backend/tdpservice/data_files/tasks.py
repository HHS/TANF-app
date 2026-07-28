"""Celery shared tasks for use in scheduled jobs."""

import logging
from datetime import timedelta

from django.contrib.auth.models import Group
from django.db.models import Count, Q
from django.utils import timezone

from celery import shared_task

from tdpservice.data_files.models import DataFile
from tdpservice.data_files.submission_lifecycle import revert_reparse_request
from tdpservice.email.helpers.data_file import send_stuck_file_email
from tdpservice.parsers.models import DataFileSummary
from tdpservice.search_indexes.reparse import (
    ReparseDestructiveCleanupStarted,
    clean_reparse,
)
from tdpservice.users.models import AccountApprovalStatusChoices, User

logger = logging.getLogger(__name__)


def get_stuck_files():
    """Return a queryset containing files in a 'stuck' state."""
    stuck_files = (
        DataFile.objects.annotate(reparse_count=Count("reparses"))
        .filter(
            # non-reparse submissions over an hour old
            Q(
                reparse_count=0,
                created_at__lte=timezone.now() - timedelta(hours=1),
            )
            |  # OR
            # reparse submissions past the timeout, where the reparse did not complete
            Q(
                reparse_count__gt=0,
                reparses__timeout_at__lte=timezone.now(),
                reparse_file_metas__finished=False,
                reparse_file_metas__success=False,
            )
        )
        .filter(
            # where there is NO summary or the summary is in PENDING status
            Q(summary=None) | Q(summary__status=DataFileSummary.Status.PENDING)
        )
    )

    return stuck_files


@shared_task
def notify_stuck_files():
    """Find files stuck in 'Pending' and notify SysAdmins."""
    stuck_files = get_stuck_files()

    if stuck_files.count() > 0:
        recipients = (
            User.objects.filter(
                account_approval_status=AccountApprovalStatusChoices.APPROVED,
                groups=Group.objects.get(name="OFA System Admin"),
            )
            .values_list("username", flat=True)
            .distinct()
        )

        send_stuck_file_email(stuck_files, recipients)


@shared_task
def reparse_files(file_ids, original_states=None):
    """Call the clean_and_reparse management command with a list of file ids.

    Failure handling distinguishes two regimes inside ``clean_reparse``:

    * **Pre-destructive failure** (e.g. sequential-execution check, backup
      step, ``count_total_num_records`` calling ``exit(1)``) raises a plain
      exception or ``SystemExit``. In this case the file's summary/errors
      have not been touched, so we revert each affected DataFile from
      ``REPARSE_REQUESTED`` back to its original state using
      ``original_states``. ``SystemExit`` is caught explicitly because
      ``count_total_num_records`` in ``search_indexes.utils`` cancels the
      reparse via ``exit(1)`` (its own log message confirms the DB is still
      consistent at that point).
    * **Destructive failure** raises ``ReparseDestructiveCleanupStarted`` from
      ``clean_reparse``. Associated summaries/errors have already been
      deleted, so reverting state would lie about the data and mask the
      existing "restore from backup" inconsistent-DB recovery path. We leave
      DataFile.state at ``REPARSE_REQUESTED`` and re-raise without reverting.

    In all failure modes the underlying exception is re-raised so Celery
    surfaces the task as failed.
    """
    file_ids_str = ",".join(map(str, file_ids))
    try:
        clean_reparse([file_ids_str])
    except ReparseDestructiveCleanupStarted:
        # Destructive cleanup already ran; reverting state would be unsafe.
        # The DB is in the documented "restore from backup" state. Re-raise
        # without touching DataFile.state.
        logger.critical(
            "clean_reparse failed after destructive cleanup for files %s; "
            "DataFile.state left at REPARSE_REQUESTED. Restore the DB from "
            "the most recent reparse backup.",
            file_ids,
        )
        raise
    except (Exception, SystemExit):
        if not original_states:
            raise

        # Celery's JSON serializer turns int keys into strings; normalize so
        # lookups by either work.
        normalized = {int(k): v for k, v in original_states.items()}
        for data_file in DataFile.objects.filter(id__in=file_ids):
            original = normalized.get(data_file.id)
            if original is None:
                continue
            try:
                revert_reparse_request(
                    data_file,
                    original,
                    note="clean_reparse worker failure (pre-destructive)",
                )
            except Exception:
                # Best-effort recovery; swallow per-file revert errors so one
                # bad row doesn't mask the original exception.
                logger.exception(
                    "Failed to revert reparse_requested state for DataFile %s.",
                    data_file.id,
                )
        raise
