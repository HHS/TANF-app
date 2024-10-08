"""Celery shared tasks for use in scheduled jobs."""

from celery import shared_task
from datetime import timedelta
from django.utils import timezone
from django.contrib.auth.models import Group
from django.db.models import Q, Count
from tdpservice.users.models import AccountApprovalStatusChoices, User
from tdpservice.data_files.models import DataFile
from tdpservice.parsers.models import DataFileSummary
from tdpservice.email.helpers.data_file import send_stuck_file_email


def get_stuck_files():
    """Return a queryset containing files in a 'stuck' state."""
    stuck_files = DataFile.objects.annotate(reparse_count=Count('reparses')).filter(
        # non-reparse submissions over an hour old
        Q(
            reparse_count=0,
            created_at__lte=timezone.now() - timedelta(hours=1),
        ) |  # OR
        # reparse submissions past the timeout, where the reparse did not complete
        Q(
            reparse_count__gt=0,
            reparses__timeout_at__lte=timezone.now(),
            reparses__finished=False,
            reparses__success=False
        )
    ).filter(
        # where there is NO summary or the summary is in PENDING status
        Q(summary=None) | Q(summary__status=DataFileSummary.Status.PENDING)
    )

    return stuck_files


@shared_task
def notify_stuck_files():
    """Find files stuck in 'Pending' and notify SysAdmins."""
    stuck_files = get_stuck_files()

    if stuck_files.count() > 0:
        recipients = User.objects.filter(
            account_approval_status=AccountApprovalStatusChoices.APPROVED,
            groups=Group.objects.get(name='OFA System Admin')
        ).values_list('username', flat=True).distinct()

        send_stuck_file_email(stuck_files, recipients)
