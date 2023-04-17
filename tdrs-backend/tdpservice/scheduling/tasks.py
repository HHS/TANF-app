"""Shared celery tasks file for beat."""

from __future__ import absolute_import
from tdpservice.users.models import User, AccountApprovalStatusChoices
from django.conf import settings
from django.urls import reverse
from django.utils import timezone
from celery import shared_task
from datetime import datetime, timedelta
import logging
from tdpservice.email.helpers.account_access_requests import send_num_access_requests_email
from tdpservice.email.helpers.account_deactivation_warning import send_deactivation_warning_email
from .db_backup import run_backup

logger = logging.getLogger(__name__)

@shared_task
def postgres_backup(*args):
    """Run nightly postgres backup."""
    arg = ''.join(args)
    logger.debug("postgres_backup::run_backup() run with arg: " + arg)
    run_backup(arg)
    return True

@shared_task
def check_for_accounts_needing_deactivation_warning():
    """Check for accounts that need deactivation warning emails."""
    deactivate_in_10_days = users_to_deactivate(10)
    deactivate_in_3_days = users_to_deactivate(3)
    deactivate_in_1_day = users_to_deactivate(1)

    if deactivate_in_10_days:
        send_deactivation_warning_email(deactivate_in_10_days, 10)
    if deactivate_in_3_days:
        send_deactivation_warning_email(deactivate_in_3_days, 3)
    if deactivate_in_1_day:
        send_deactivation_warning_email(deactivate_in_1_day, 1)

def users_to_deactivate(days):
    """Return a list of users that have not logged in in the last {180 - days} days."""
    days = 180 - days
    return User.objects.filter(
        last_login__lte=datetime.now(tz=timezone.utc) - timedelta(days=days),
        last_login__gte=datetime.now(tz=timezone.utc) - timedelta(days=days+1),
        account_approval_status=AccountApprovalStatusChoices.APPROVED,
        )

def get_ofa_admin_user_emails():
    """Return a list of OFA System Admin users."""
    return [user.email for user in User.objects.filter(
        groups='4'
    )]

def get_num_access_requests():
    """Return the number of users requesting access."""
    return len(User.objects.filter(
        account_approval_status=AccountApprovalStatusChoices.ACCESS_REQUEST,
    ))

@shared_task
def email_admin_num_access_requests():
    """Send all OFA System Admins an email with how many users have requested access."""
    recipient_email = 'elipe@teamraft.com'  # get_ofa_admin_user_emails()
    text_message = ''
    subject = 'Number of Active Access Requests'
    url = settings.FRONTEND_BASE_URL + reverse("admin:users_user_changelist")
    email_context = {
        'date': datetime.today(),
        'num_requests': get_num_access_requests(),
        'admin_user_pg': url,
    }

    send_num_access_requests_email(recipient_email,
                                   text_message,
                                   subject,
                                   email_context,
                                   )
