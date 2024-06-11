"""Shared celery email tasks for beat."""

from __future__ import absolute_import
from tdpservice.users.models import User, AccountApprovalStatusChoices
from django.contrib.auth.models import Group
from django.conf import settings
from django.urls import reverse
from django.utils import timezone
from celery import shared_task
from datetime import datetime, timedelta
import logging
from tdpservice.email.helpers.account_access_requests import send_num_access_requests_email
from tdpservice.email.helpers.account_deactivation_warning import send_deactivation_warning_email
from tdpservice.stts.models import STT
from tdpservice.data_files.models import DataFile
from tdpservice.email.email import automated_email, log
from tdpservice.email.email_enums import EmailType
from tdpservice.parsers.util import calendar_to_fiscal


logger = logging.getLogger(__name__)


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
    """Return a list of OFA System Admin and OFA Admin users."""
    return User.objects.filter(
        groups__in=Group.objects.filter(name__in=('OFA Admin', 'OFA System Admin'))
    ).values_list('email', flat=True).distinct()

def get_num_access_requests():
    """Return the number of users requesting access."""
    return User.objects.filter(
        account_approval_status=AccountApprovalStatusChoices.ACCESS_REQUEST,
    ).count()

@shared_task
def email_admin_num_access_requests():
    """Send all OFA System Admins an email with how many users have requested access."""
    recipient_email = get_ofa_admin_user_emails()
    text_message = ''
    subject = 'Number of Active Access Requests'
    url = f'{settings.FRONTEND_BASE_URL}{reverse("admin:users_user_changelist")}?o=-2'
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


@shared_task
def send_data_submission_reminder(due_date, reporting_period, fiscal_quarter):
    """Send all Data Analysts a reminder to submit if they have not already."""

    now = datetime.now()
    fiscal_year = calendar_to_fiscal(now.year, fiscal_quarter)

    all_locations = STT.objects.all()

    reminder_locations = []
    year_quarter_files = DataFile.objects.all().filter(
        year=fiscal_year,
        quarter=fiscal_quarter,
    )

    for loc in all_locations:
        submitted_sections = year_quarter_files.filter(stt=loc).values_list('section', flat=True).distinct()
        required_sections = loc.filenames.keys()

        submitted_all_sections = True
        for s in required_sections:
            if s not in submitted_sections:
                submitted_all_sections = False

        if not submitted_all_sections:
            reminder_locations.append(loc)

    template_path = EmailType.UPCOMING_SUBMISSION_DEADLINE.value
    text_message = f'Your datafiles are due by {due_date}.'

    all_data_analysts = User.objects.all().filter(
        account_approval_status=AccountApprovalStatusChoices.APPROVED,
        groups=Group.objects.get(name='Data Analyst')
    )

    for loc in reminder_locations:
        tanf_ssp_label = 'TANF and SSP' if loc.ssp else 'TANF'
        subject = f'Action Requested: Please submit your {tanf_ssp_label} data files'

        recipients = all_data_analysts.filter(stt=loc)

        for rec in recipients:
            context = {
                'first_name': rec.first_name,
                'fiscal_year': fiscal_year,
                'fiscal_quarter': fiscal_quarter,
                'submission_deadline': due_date,
                'url': settings.FRONTEND_BASE_URL,
                'subject': subject
            }

            logger_context = {
                'user_id': rec.id,
                'object_id': rec.id,
                'object_repr': rec.username,
            }

            automated_email(
                email_path=template_path,
                recipient_email=rec.username,
                subject=subject,
                email_context=context,
                text_message=text_message,
                logger_context=logger_context
            )

        if len(recipients) == 0:
            system_user, created = User.objects.get_or_create(username='system')
            if created:
                log('Created reserved system user.')

            logger_context = {
                'user_id': system_user.pk,
                'object_id': loc.id,
                'object_repr': loc.name,
            }
            log(f"{loc.name} has no recipients for data submission deadline reminder.", logger_context=logger_context)
