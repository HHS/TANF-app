"""Test functions for data_file email helper."""

from django.core import mail

import pytest

from tdpservice.data_files.models import DataFile
from tdpservice.email.helpers.data_file import (
    get_tanf_aggregates_context_count,
    get_tanf_total_errors_context_count,
    send_data_submitted_email,
    send_stuck_file_email,
)
from tdpservice.parsers.models import DataFileSummary


@pytest.mark.django_db
def test_send_data_submitted_email_no_email_for_pending(user, stt):
    """Test that send_data_submitted_email sends nothing for PENDING datafiles."""
    df = DataFile(
        user=user,
        section=DataFile.Section.ACTIVE_CASE_DATA,
        quarter="Q1",
        year=2021,
        stt=stt,
    )

    dfs = DataFileSummary(
        datafile=df,
        status=DataFileSummary.Status.PENDING,
    )

    recipients = ["test@not-real.com"]

    send_data_submitted_email(dfs, recipients)

    assert len(mail.outbox) == 0


@pytest.mark.django_db
@pytest.mark.parametrize(
    "section,status,subject,friendly_program_type,program_type",
    [
        # tribal
        (
            DataFile.Section.CLOSED_CASE_DATA,
            DataFileSummary.Status.ACCEPTED,
            f"Tribal {DataFile.Section.CLOSED_CASE_DATA} Successfully Submitted Without Errors",
            "Tribal TANF",
            DataFile.ProgramType.TRIBAL,
        ),
        (
            DataFile.Section.ACTIVE_CASE_DATA,
            DataFileSummary.Status.ACCEPTED,
            f"Tribal {DataFile.Section.ACTIVE_CASE_DATA} Successfully Submitted Without Errors",
            "Tribal TANF",
            DataFile.ProgramType.TRIBAL,
        ),
        (
            DataFile.Section.AGGREGATE_DATA,
            DataFileSummary.Status.ACCEPTED_WITH_ERRORS,
            f"Action Required: Tribal {DataFile.Section.AGGREGATE_DATA} Contains Errors",
            "Tribal TANF",
            DataFile.ProgramType.TRIBAL,
        ),
        (
            DataFile.Section.STRATUM_DATA,
            DataFileSummary.Status.PARTIALLY_ACCEPTED,
            f"Action Required: Tribal {DataFile.Section.STRATUM_DATA} Contains Errors",
            "Tribal TANF",
            DataFile.ProgramType.TRIBAL,
        ),
        (
            DataFile.Section.STRATUM_DATA,
            DataFileSummary.Status.REJECTED,
            f"Action Required: Tribal {DataFile.Section.STRATUM_DATA} Contains Errors",
            "Tribal TANF",
            DataFile.ProgramType.TRIBAL,
        ),
        # ssp
        (
            DataFile.Section.AGGREGATE_DATA,
            DataFileSummary.Status.ACCEPTED,
            f"SSP {DataFile.Section.AGGREGATE_DATA} Successfully Submitted Without Errors",
            "SSP",
            DataFile.ProgramType.SSP,
        ),
        (
            DataFile.Section.CLOSED_CASE_DATA,
            DataFileSummary.Status.ACCEPTED,
            f"SSP {DataFile.Section.CLOSED_CASE_DATA} Successfully Submitted Without Errors",
            "SSP",
            DataFile.ProgramType.SSP,
        ),
        (
            DataFile.Section.ACTIVE_CASE_DATA,
            DataFileSummary.Status.ACCEPTED_WITH_ERRORS,
            f"Action Required: SSP {DataFile.Section.ACTIVE_CASE_DATA} Contains Errors",
            "SSP",
            DataFile.ProgramType.SSP,
        ),
        (
            DataFile.Section.STRATUM_DATA,
            DataFileSummary.Status.PARTIALLY_ACCEPTED,
            f"Action Required: SSP {DataFile.Section.STRATUM_DATA} Contains Errors",
            "SSP",
            DataFile.ProgramType.SSP,
        ),
        (
            DataFile.Section.STRATUM_DATA,
            DataFileSummary.Status.REJECTED,
            f"Action Required: SSP {DataFile.Section.STRATUM_DATA} Contains Errors",
            "SSP",
            DataFile.ProgramType.SSP,
        ),
        # tanf
        (
            DataFile.Section.ACTIVE_CASE_DATA,
            DataFileSummary.Status.ACCEPTED,
            f"{DataFile.Section.ACTIVE_CASE_DATA} Successfully Submitted Without Errors",
            "TANF",
            DataFile.ProgramType.TANF,
        ),
        (
            DataFile.Section.CLOSED_CASE_DATA,
            DataFileSummary.Status.ACCEPTED,
            f"{DataFile.Section.CLOSED_CASE_DATA} Successfully Submitted Without Errors",
            "TANF",
            DataFile.ProgramType.TANF,
        ),
        (
            DataFile.Section.AGGREGATE_DATA,
            DataFileSummary.Status.ACCEPTED_WITH_ERRORS,
            f"Action Required: {DataFile.Section.AGGREGATE_DATA} Contains Errors",
            "TANF",
            DataFile.ProgramType.TANF,
        ),
        (
            DataFile.Section.STRATUM_DATA,
            DataFileSummary.Status.PARTIALLY_ACCEPTED,
            f"Action Required: {DataFile.Section.STRATUM_DATA} Contains Errors",
            "TANF",
            DataFile.ProgramType.TANF,
        ),
        (
            DataFile.Section.STRATUM_DATA,
            DataFileSummary.Status.REJECTED,
            f"Action Required: {DataFile.Section.STRATUM_DATA} Contains Errors",
            "TANF",
            DataFile.ProgramType.TANF,
        ),
        # fra
        (
            DataFile.Section.FRA_WORK_OUTCOME_TANF_EXITERS,
            DataFileSummary.Status.ACCEPTED,
            f"{DataFile.Section.FRA_WORK_OUTCOME_TANF_EXITERS} Successfully Submitted Without Errors",
            "FRA",
            DataFile.ProgramType.FRA,
        ),
        (
            DataFile.Section.FRA_WORK_OUTCOME_TANF_EXITERS,
            DataFileSummary.Status.REJECTED,
            f"Action Required: {DataFile.Section.FRA_WORK_OUTCOME_TANF_EXITERS} Contains Errors",
            "FRA",
            DataFile.ProgramType.FRA,
        ),
    ],
)
def test_send_data_submitted_email(
    user, stt, section, status, subject, friendly_program_type, program_type
):
    """Test that the send_data_submitted_email function runs."""
    df = DataFile(
        user=user,
        section=section,
        program_type=program_type,
        quarter="Q1",
        year=2021,
        stt=stt,
    )

    dfs = DataFileSummary(
        datafile=df,
        status=status,
    )

    recipients = ["test@not-real.com"]

    send_data_submitted_email(dfs, recipients)

    has_errors = status != DataFileSummary.Status.ACCEPTED
    has_errors_msg = (
        f"{friendly_program_type} has been submitted and processed with errors."
    )
    no_errors_msg = (
        f"{friendly_program_type} has been submitted and processed without errors."
    )
    msg = has_errors_msg if has_errors else no_errors_msg

    assert len(mail.outbox) == 1
    assert mail.outbox[0].subject == subject
    assert mail.outbox[0].body == msg


class TestGetTanfAggregatesContextCount:
    """Tests for get_tanf_aggregates_context_count."""

    def test_with_case_data(self):
        """Test aggregation with typical case data months."""
        dfs = DataFileSummary()
        dfs.case_aggregates = {
            "months": [
                {
                    "month": "Jan",
                    "accepted_without_errors": 10,
                    "accepted_with_errors": 2,
                },
                {
                    "month": "Feb",
                    "accepted_without_errors": 8,
                    "accepted_with_errors": 3,
                },
                {
                    "month": "Mar",
                    "accepted_without_errors": 12,
                    "accepted_with_errors": 1,
                },
            ],
            "rejected": 5,
        }
        result = get_tanf_aggregates_context_count(dfs)
        assert result == {
            "cases_without_errors": 30,
            "cases_with_errors": 6,
            "records_unable_to_process": 5,
        }

    def test_with_na_values(self):
        """Test aggregation handles N/A values from rejected status."""
        dfs = DataFileSummary()
        dfs.case_aggregates = {
            "months": [
                {
                    "month": "Jan",
                    "accepted_without_errors": "N/A",
                    "accepted_with_errors": "N/A",
                },
            ],
            "rejected": 0,
        }
        result = get_tanf_aggregates_context_count(dfs)
        assert result == {
            "cases_without_errors": 0,
            "cases_with_errors": 0,
            "records_unable_to_process": 0,
        }

    def test_with_empty_aggregates(self):
        """Test aggregation handles empty/None case_aggregates."""
        dfs = DataFileSummary()
        dfs.case_aggregates = None
        result = get_tanf_aggregates_context_count(dfs)
        assert result == {
            "cases_without_errors": 0,
            "cases_with_errors": 0,
            "records_unable_to_process": 0,
        }


class TestGetTanfTotalErrorsContextCount:
    """Tests for get_tanf_total_errors_context_count."""

    def test_with_total_errors_data(self):
        """Test aggregation sums total_errors across months."""
        dfs = DataFileSummary()
        dfs.case_aggregates = {
            "months": [
                {"month": "Jan", "total_errors": 5},
                {"month": "Feb", "total_errors": 3},
                {"month": "Mar", "total_errors": 7},
            ],
        }
        result = get_tanf_total_errors_context_count(dfs)
        assert result == {"total_errors": 15}

    def test_with_na_values(self):
        """Test aggregation handles N/A values from rejected status."""
        dfs = DataFileSummary()
        dfs.case_aggregates = {
            "months": [
                {"month": "Jan", "total_errors": "N/A"},
                {"month": "Feb", "total_errors": "N/A"},
            ],
        }
        result = get_tanf_total_errors_context_count(dfs)
        assert result == {"total_errors": 0}

    def test_with_empty_aggregates(self):
        """Test aggregation handles empty/None case_aggregates."""
        dfs = DataFileSummary()
        dfs.case_aggregates = None
        result = get_tanf_total_errors_context_count(dfs)
        assert result == {"total_errors": 0}

    def test_with_mixed_values(self):
        """Test aggregation handles mix of numeric and N/A values."""
        dfs = DataFileSummary()
        dfs.case_aggregates = {
            "months": [
                {"month": "Jan", "total_errors": 5},
                {"month": "Feb", "total_errors": "N/A"},
                {"month": "Mar", "total_errors": 10},
            ],
        }
        result = get_tanf_total_errors_context_count(dfs)
        assert result == {"total_errors": 15}


@pytest.mark.django_db
def test_send_stuck_file_email(user, stt):
    """Test that the send_stuck_file_email function runs."""

    df1 = DataFile(
        user=user,
        section=DataFile.Section.ACTIVE_CASE_DATA,
        program_type=DataFile.ProgramType.TANF,
        quarter="Q1",
        year=2025,
        stt=stt,
    )
    df2 = DataFile(
        user=user,
        section=DataFile.Section.CLOSED_CASE_DATA,
        program_type=DataFile.ProgramType.TANF,
        quarter="Q1",
        year=2025,
        stt=stt,
    )
    stuck_files = [df1, df2]

    recipients = ["test@not-real.com"]

    send_stuck_file_email(stuck_files, recipients)

    assert len(mail.outbox) == 1
    assert (
        mail.outbox[0].subject
        == "List of submitted files with pending status after 1 hour"
    )
    assert mail.outbox[0].body == "The system has detected stuck files."
