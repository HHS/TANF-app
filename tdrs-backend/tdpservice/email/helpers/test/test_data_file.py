"""Test functions for data_file email helper."""
import pytest
from django.core import mail
from tdpservice.email.helpers.data_file import send_data_submitted_email
from tdpservice.data_files.models import DataFile
from tdpservice.parsers.models import DataFileSummary


@pytest.mark.django_db
def test_send_data_submitted_email_no_email_for_pending(user, stt):
    """Test that send_data_submitted_email sends nothing for PENDING datafiles."""
    df = DataFile(
        user=user,
        section=DataFile.Section.ACTIVE_CASE_DATA,
        quarter='Q1',
        year=2021,
        stt=stt,
    )

    dfs = DataFileSummary(
        datafile=df,
        status=DataFileSummary.Status.PENDING,
    )

    recipients = ['test@not-real.com']

    send_data_submitted_email(dfs, recipients)

    assert len(mail.outbox) == 0


@pytest.mark.django_db
@pytest.mark.parametrize('section,status,subject,program_type', [
    # tribal
    (
        DataFile.Section.TRIBAL_CLOSED_CASE_DATA, DataFileSummary.Status.ACCEPTED,
        'Tribal Closed Case Data Processed Without Errors', 'Tribal TAN'
    ),
    (
        DataFile.Section.TRIBAL_ACTIVE_CASE_DATA, DataFileSummary.Status.ACCEPTED,
        'Tribal Active Case Data Processed Without Errors', 'Tribal TAN'
    ),
    (
        DataFile.Section.TRIBAL_AGGREGATE_DATA, DataFileSummary.Status.ACCEPTED_WITH_ERRORS,
        'Tribal Aggregate Data Processed With Errors', 'Tribal TAN',
    ),
    (
        DataFile.Section.TRIBAL_STRATUM_DATA, DataFileSummary.Status.PARTIALLY_ACCEPTED,
        'Tribal Stratum Data Processed With Errors', 'Tribal TAN',
    ),
    (
        DataFile.Section.TRIBAL_STRATUM_DATA, DataFileSummary.Status.REJECTED,
        'Tribal Stratum Data Processed With Errors', 'Tribal TAN',
    ),

    # ssp
    (
        DataFile.Section.SSP_AGGREGATE_DATA, DataFileSummary.Status.ACCEPTED,
        'SSP Aggregate Data Processed Without Errors', 'SSP',
    ),
    (
        DataFile.Section.SSP_CLOSED_CASE_DATA, DataFileSummary.Status.ACCEPTED,
        'SSP Closed Case Data Processed Without Errors', 'SSP',
    ),
    (
        DataFile.Section.SSP_ACTIVE_CASE_DATA, DataFileSummary.Status.ACCEPTED_WITH_ERRORS,
        'SSP Active Case Data Processed With Errors', 'SSP',
    ),
    (
        DataFile.Section.SSP_STRATUM_DATA, DataFileSummary.Status.PARTIALLY_ACCEPTED,
        'SSP Stratum Data Processed With Errors', 'SSP',
    ),
    (
        DataFile.Section.SSP_STRATUM_DATA, DataFileSummary.Status.REJECTED,
        'SSP Stratum Data Processed With Errors', 'SSP',
    ),

    # tanf
    (
        DataFile.Section.ACTIVE_CASE_DATA, DataFileSummary.Status.ACCEPTED,
        'Active Case Data Processed Without Errors', 'TAN',
    ),
    (
        DataFile.Section.CLOSED_CASE_DATA, DataFileSummary.Status.ACCEPTED,
        'Closed Case Data Processed Without Errors', 'TAN',
    ),
    (
        DataFile.Section.AGGREGATE_DATA, DataFileSummary.Status.ACCEPTED_WITH_ERRORS,
        'Aggregate Data Processed With Errors', 'TAN',
    ),
    (
        DataFile.Section.STRATUM_DATA, DataFileSummary.Status.PARTIALLY_ACCEPTED,
        'Stratum Data Processed With Errors', 'TAN',
    ),
    (
        DataFile.Section.STRATUM_DATA, DataFileSummary.Status.REJECTED,
        'Stratum Data Processed With Errors', 'TAN',
    ),
])
def test_send_data_submitted_email(user, stt, section, status, subject, program_type):
    """Test that the send_data_submitted_email function runs."""
    df = DataFile(
        user=user,
        section=section,
        quarter='Q1',
        year=2021,
        stt=stt,
    )

    dfs = DataFileSummary(
        datafile=df,
        status=status,
    )

    recipients = ['test@not-real.com']

    send_data_submitted_email(dfs, recipients)

    has_errors = status != DataFileSummary.Status.ACCEPTED
    has_errors_msg = f'{program_type} has been submitted and processed with errors.'
    no_errors_msg = f'{program_type} has been submitted and processed without errors.'
    msg = has_errors_msg if has_errors else no_errors_msg

    assert len(mail.outbox) == 1
    assert mail.outbox[0].subject == subject
    assert mail.outbox[0].body == msg
