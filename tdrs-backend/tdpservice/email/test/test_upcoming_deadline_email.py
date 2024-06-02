"""Test function for sending upcoming data deadline reminders."""
import pytest
from django.core import mail
from tdpservice.email.tasks import send_data_submission_reminder
from datetime import datetime
from django.contrib.auth.models import Group

from tdpservice.stts.models import STT
from tdpservice.users.models import User
from tdpservice.data_files.models import DataFile


@pytest.mark.parametrize('due_date, reporting_period, fiscal_quarter', [
    ('February 14', 'Oct - Dec', 'Q1'),
    ('May 15th', 'Jan - Mar', 'Q2'),
    ('August 14th', 'Apr - Jun', 'Q3'),
    ('November 14th', 'Jul - Sep', 'Q4'),
])
@pytest.mark.django_db
def test_upcoming_deadline_sends_no_sections_submitted(
        due_date, reporting_period, fiscal_quarter):
    """Test that the send_deactivation_warning_email function runs when no sections have been submitted."""

    stt = STT.objects.create(
        name='Arkansas',
        filenames={
            "Active Case Data": "test-filename.txt",
            "Closed Case Data": "test-filename-closed.txt",
        }
    )

    data_analyst = User.objects.create(
        username='test@email.com',
        stt=stt,
        account_approval_status='Approved'
    )
    data_analyst.groups.add(Group.objects.get(name='Data Analyst'))
    data_analyst.save()

    send_data_submission_reminder(due_date, reporting_period, fiscal_quarter)

    assert len(mail.outbox) == 1
    assert mail.outbox[0].subject == f"Upcoming submission deadline: {due_date}"


@pytest.mark.parametrize('due_date, reporting_period, fiscal_quarter', [
    ('February 14', 'Oct - Dec', 'Q1'),
    ('May 15th', 'Jan - Mar', 'Q2'),
    ('August 14th', 'Apr - Jun', 'Q3'),
    ('November 14th', 'Jul - Sep', 'Q4'),
])
@pytest.mark.django_db
def test_upcoming_deadline_sends_some_sections_submitted(
        due_date, reporting_period, fiscal_quarter):
    """Test that the send_deactivation_warning_email function runs when some sections have been submitted."""

    stt = STT.objects.create(
        name='Arkansas',
        filenames={
            "Active Case Data": "test-filename.txt",
            "Closed Case Data": "test-filename-closed.txt",
        }
    )

    data_analyst = User.objects.create(
        username='test@email.com',
        stt=stt,
        account_approval_status='Approved'
    )
    data_analyst.groups.add(Group.objects.get(name='Data Analyst'))
    data_analyst.save()

    now = datetime.now()
    fiscal_year = now.year - 1 if fiscal_quarter == 'Q1' else now.year

    data_file = DataFile.create_new_version({
        "section": 'Active Case Data',
        "quarter": fiscal_quarter,
        "year": fiscal_year,
        "stt": stt,
        "user": data_analyst,
    })

    send_data_submission_reminder(due_date, reporting_period, fiscal_quarter)

    assert len(mail.outbox) == 1
    assert mail.outbox[0].subject == f"Upcoming submission deadline: {due_date}"


"""Test function for sending upcoming data deadline reminders."""
import pytest
from django.core import mail
from tdpservice.email.tasks import send_data_submission_reminder
from django.contrib.auth.models import Group

from tdpservice.stts.models import STT
from tdpservice.users.models import User


@pytest.mark.parametrize('due_date, reporting_period, fiscal_quarter', [
    ('February 14', 'Oct - Dec', 'Q1'),
    ('May 15th', 'Jan - Mar', 'Q2'),
    ('August 14th', 'Apr - Jun', 'Q3'),
    ('November 14th', 'Jul - Sep', 'Q4'),
])
@pytest.mark.django_db
def test_upcoming_deadline_no_send_when_all_sections_complete(
        due_date, reporting_period, fiscal_quarter):
    """Test that the send_deactivation_warning_email function does not run when all sections have been submitted."""

    stt = STT.objects.create(
        name='Arkansas',
        filenames={
            "Active Case Data": "test-filename.txt",
            "Closed Case Data": "test-filename-closed.txt",
        }
    )

    data_analyst = User.objects.create(
        username='test@email.com',
        stt=stt,
        account_approval_status='Approved'
    )
    data_analyst.groups.add(Group.objects.get(name='Data Analyst'))
    data_analyst.save()

    now = datetime.now()
    fiscal_year = now.year - 1 if fiscal_quarter == 'Q1' else now.year

    data_file = DataFile.create_new_version({
        "section": 'Active Case Data',
        "quarter": fiscal_quarter,
        "year": fiscal_year,
        "stt": stt,
        "user": data_analyst,
    })

    data_file2 = DataFile.create_new_version({
        "section": 'Closed Case Data',
        "quarter": fiscal_quarter,
        "year": fiscal_year,
        "stt": stt,
        "user": data_analyst,
    })

    send_data_submission_reminder(due_date, reporting_period, fiscal_quarter)

    assert len(mail.outbox) == 0
