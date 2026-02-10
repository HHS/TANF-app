"""Test function for sending upcoming data deadline reminders."""

from datetime import datetime

from django.contrib.auth.models import Group
from django.core import mail

import pytest

from tdpservice.data_files.models import DataFile
from tdpservice.email.tasks import send_data_submission_reminder
from tdpservice.stts.models import STT
from tdpservice.users.models import User


QUARTERLY_PARAMS = pytest.mark.parametrize(
    "due_date, reporting_period, fiscal_quarter",
    [
        ("February 14", "Oct - Dec", "Q1"),
        ("May 15th", "Jan - Mar", "Q2"),
        ("August 14th", "Apr - Jun", "Q3"),
        ("November 14th", "Jul - Sep", "Q4"),
    ],
)


def _create_stt_with_analyst(name, filenames, ssp=False):
    """Create an STT and an approved Data Analyst assigned to it."""
    stt = STT.objects.create(name=name, filenames=filenames, ssp=ssp)
    data_analyst = User.objects.create(
        username=f"{name.lower().replace(' ', '')}@test.com",
        stt=stt,
        account_approval_status="Approved",
    )
    data_analyst.groups.add(Group.objects.get(name="Data Analyst"))
    data_analyst.save()
    return stt, data_analyst


def _submit_file(stt, user, program_type, section, fiscal_quarter):
    """Create a DataFile for the current fiscal year and given quarter."""
    return DataFile.create_new_version(
        {
            "section": section,
            "program_type": program_type,
            "quarter": fiscal_quarter,
            "year": datetime.now().year,
            "stt": stt,
            "user": user,
            "is_program_audit": False,
        }
    )


@QUARTERLY_PARAMS
@pytest.mark.django_db
def test_upcoming_deadline_sends_no_sections_submitted(
    due_date, reporting_period, fiscal_quarter
):
    """Reminder is sent when no sections have been submitted."""
    stt, _ = _create_stt_with_analyst(
        "Arkansas",
        {
            "TAN Active Case Data": "test-filename.txt",
            "TAN Closed Case Data": "test-filename-closed.txt",
        },
    )

    send_data_submission_reminder(due_date, reporting_period, fiscal_quarter)

    assert len(mail.outbox) == 1
    assert (
        mail.outbox[0].subject
        == "Action Requested: Please submit your TANF data files"
    )


@QUARTERLY_PARAMS
@pytest.mark.django_db
def test_upcoming_deadline_sends_some_sections_submitted(
    due_date, reporting_period, fiscal_quarter
):
    """Reminder is sent when only some sections have been submitted."""
    stt, analyst = _create_stt_with_analyst(
        "Arkansas",
        {
            "TAN Active Case Data": "test-filename.txt",
            "TAN Closed Case Data": "test-filename-closed.txt",
        },
    )

    _submit_file(stt, analyst, "TAN", "Active Case Data", fiscal_quarter)

    send_data_submission_reminder(due_date, reporting_period, fiscal_quarter)

    assert len(mail.outbox) == 1
    assert (
        mail.outbox[0].subject
        == "Action Requested: Please submit your TANF data files"
    )


@QUARTERLY_PARAMS
@pytest.mark.django_db
def test_upcoming_deadline_no_send_when_all_sections_complete(
    due_date, reporting_period, fiscal_quarter
):
    """No reminder is sent when all required sections have been submitted."""
    stt, analyst = _create_stt_with_analyst(
        "Arkansas",
        {
            "TAN Active Case Data": "test-filename.txt",
            "TAN Closed Case Data": "test-filename-closed.txt",
        },
    )

    _submit_file(stt, analyst, "TAN", "Active Case Data", fiscal_quarter)
    _submit_file(stt, analyst, "TAN", "Closed Case Data", fiscal_quarter)

    send_data_submission_reminder(due_date, reporting_period, fiscal_quarter)

    assert len(mail.outbox) == 0


@pytest.mark.django_db
def test_q1_files_found_using_current_year():
    """Q1 DataFiles stored with the current year are found by the task."""
    stt, analyst = _create_stt_with_analyst(
        "TestState",
        {
            "TAN Active Case Data": "file1.txt",
            "TAN Closed Case Data": "file2.txt",
        },
    )

    # Submit all required files for Q1 using the current year
    _submit_file(stt, analyst, "TAN", "Active Case Data", "Q1")
    _submit_file(stt, analyst, "TAN", "Closed Case Data", "Q1")

    send_data_submission_reminder("February 14", "Oct - Dec", "Q1")

    # All files submitted → no reminder should be sent
    assert len(mail.outbox) == 0


@pytest.mark.django_db
def test_q1_files_with_previous_year_are_not_matched():
    """DataFiles stored with the previous year should not satisfy the current period."""
    stt, analyst = _create_stt_with_analyst(
        "TestState",
        {
            "TAN Active Case Data": "file1.txt",
            "TAN Closed Case Data": "file2.txt",
        },
    )

    # Submit files with LAST year — these should not count
    last_year = datetime.now().year - 1
    DataFile.create_new_version(
        {
            "section": "Active Case Data",
            "program_type": "TAN",
            "quarter": "Q1",
            "year": last_year,
            "stt": stt,
            "user": analyst,
            "is_program_audit": False,
        }
    )
    DataFile.create_new_version(
        {
            "section": "Closed Case Data",
            "program_type": "TAN",
            "quarter": "Q1",
            "year": last_year,
            "stt": stt,
            "user": analyst,
            "is_program_audit": False,
        }
    )

    send_data_submission_reminder("February 14", "Oct - Dec", "Q1")

    # Files are for the wrong year → reminder should still be sent
    assert len(mail.outbox) == 1


@pytest.mark.django_db
def test_tribal_submission_does_not_satisfy_tanf_requirement():
    """A Tribal DataFile should not count toward TANF filing requirements.

    Regression: the old code only checked section name, so a Tribal 'Active
    Case Data' submission would satisfy a TANF 'Active Case Data' requirement.
    """
    stt, analyst = _create_stt_with_analyst(
        "TestState",
        {
            "TAN Active Case Data": "file1.txt",
            "TAN Closed Case Data": "file2.txt",
        },
    )

    # Submit Tribal files — wrong program type for this STT
    _submit_file(stt, analyst, "TRIBAL", "Active Case Data", "Q1")
    _submit_file(stt, analyst, "TRIBAL", "Closed Case Data", "Q1")

    send_data_submission_reminder("February 14", "Oct - Dec", "Q1")

    # Tribal files don't satisfy TANF requirement → reminder sent
    assert len(mail.outbox) == 1


@pytest.mark.django_db
def test_tanf_submission_does_not_satisfy_tribal_requirement():
    """A TANF DataFile should not count toward Tribal filing requirements."""
    stt, analyst = _create_stt_with_analyst(
        "TestTribe",
        {
            "Tribal Active Case Data": "file1.txt",
            "Tribal Closed Case Data": "file2.txt",
            "Tribal Aggregate Data": "file3.txt",
        },
    )

    # Submit TANF files — wrong program type for a tribal STT
    _submit_file(stt, analyst, "TAN", "Active Case Data", "Q1")
    _submit_file(stt, analyst, "TAN", "Closed Case Data", "Q1")
    _submit_file(stt, analyst, "TAN", "Aggregate Data", "Q1")

    send_data_submission_reminder("February 14", "Oct - Dec", "Q1")

    # TANF files don't satisfy Tribal requirement → reminder sent
    assert len(mail.outbox) == 1


@pytest.mark.django_db
def test_tribal_stt_no_reminder_when_all_tribal_sections_submitted():
    """A Tribal STT that has submitted all Tribal files should not get a reminder."""
    stt, analyst = _create_stt_with_analyst(
        "TestTribe",
        {
            "Tribal Active Case Data": "file1.txt",
            "Tribal Closed Case Data": "file2.txt",
            "Tribal Aggregate Data": "file3.txt",
        },
    )

    _submit_file(stt, analyst, "TRIBAL", "Active Case Data", "Q1")
    _submit_file(stt, analyst, "TRIBAL", "Closed Case Data", "Q1")
    _submit_file(stt, analyst, "TRIBAL", "Aggregate Data", "Q1")

    send_data_submission_reminder("February 14", "Oct - Dec", "Q1")

    assert len(mail.outbox) == 0


@pytest.mark.django_db
def test_ssp_stt_requires_both_tanf_and_ssp_submissions():
    """An SSP state must submit both TANF and SSP files to avoid a reminder.

    Regression: the old code ignored program type, so submitting only TANF
    files could falsely satisfy SSP requirements (since both have the same
    section names).
    """
    stt, analyst = _create_stt_with_analyst(
        "RhodeIsland",
        {
            "TAN Active Case Data": "tanf1.txt",
            "TAN Closed Case Data": "tanf2.txt",
            "TAN Aggregate Data": "tanf3.txt",
            "SSP Active Case Data": "ssp1.txt",
            "SSP Closed Case Data": "ssp2.txt",
            "SSP Aggregate Data": "ssp3.txt",
        },
        ssp=True,
    )

    # Only submit TANF files — SSP requirements are not satisfied
    _submit_file(stt, analyst, "TAN", "Active Case Data", "Q2")
    _submit_file(stt, analyst, "TAN", "Closed Case Data", "Q2")
    _submit_file(stt, analyst, "TAN", "Aggregate Data", "Q2")

    send_data_submission_reminder("May 15th", "Jan - Mar", "Q2")

    # Missing SSP files → reminder sent
    assert len(mail.outbox) == 1
    assert "SSP" in mail.outbox[0].subject


@pytest.mark.django_db
def test_ssp_stt_no_reminder_when_all_programs_submitted():
    """An SSP state that has submitted all TANF and SSP files should not get a reminder."""
    stt, analyst = _create_stt_with_analyst(
        "RhodeIsland",
        {
            "TAN Active Case Data": "tanf1.txt",
            "TAN Closed Case Data": "tanf2.txt",
            "TAN Aggregate Data": "tanf3.txt",
            "SSP Active Case Data": "ssp1.txt",
            "SSP Closed Case Data": "ssp2.txt",
            "SSP Aggregate Data": "ssp3.txt",
        },
        ssp=True,
    )

    # Submit both TANF and SSP files
    for program_type in ("TAN", "SSP"):
        _submit_file(stt, analyst, program_type, "Active Case Data", "Q2")
        _submit_file(stt, analyst, program_type, "Closed Case Data", "Q2")
        _submit_file(stt, analyst, program_type, "Aggregate Data", "Q2")

    send_data_submission_reminder("May 15th", "Jan - Mar", "Q2")

    assert len(mail.outbox) == 0
