"""Integration tests for Program Audit parsing."""

import pytest

from tdpservice.parsers import aggregates
from tdpservice.parsers.models import (
    DataFileSummary,
    ParserError,
    ParserErrorCategoryChoices,
)
from tdpservice.parsers.test.helpers import parse_datafile
from tdpservice.search_indexes.models.program_audit import (
    ProgramAudit_T1,
    ProgramAudit_T2,
    ProgramAudit_T3,
)


class TestParseProgramAudit:
    """Tests for Program Audit parsing scenarios."""

    @pytest.fixture
    def parsed_program_audit_ftanf(self, program_audit_ftanf, dfs):
        """Return parsed program audit FTANF file and its DataFileSummary."""
        datafile = program_audit_ftanf
        datafile.year = 2024
        datafile.quarter = "Q2"

        dfs.datafile = datafile
        dfs.save()

        parse_datafile(dfs, datafile, is_program_audit=datafile.is_program_audit)

        return datafile, dfs

    @pytest.fixture
    def parsed_program_audit_duplicates(self, program_audit_duplicates, dfs):
        """Return parsed program audit duplicates file and its DataFileSummary."""
        datafile = program_audit_duplicates
        datafile.year = 2024
        datafile.quarter = "Q2"

        dfs.datafile = datafile
        dfs.save()

        parse_datafile(dfs, datafile, is_program_audit=datafile.is_program_audit)

        return datafile, dfs

    def _parse_program_audit_file(self, request, dfs, fixture_name, year, quarter):
        """Parse a program audit fixture and return the datafile and dfs."""
        datafile = request.getfixturevalue(fixture_name)
        datafile.year = year
        datafile.quarter = quarter

        dfs.datafile = datafile
        dfs.save()

        parse_datafile(dfs, datafile, is_program_audit=datafile.is_program_audit)

        return datafile, dfs

    @pytest.mark.django_db
    def test_program_audit_ftanf_record_counts(self, parsed_program_audit_ftanf):
        """Test record counts for Program Audit FTANF file."""
        _datafile, _dfs = parsed_program_audit_ftanf
        assert ProgramAudit_T1.objects.all().count() == 1
        assert ProgramAudit_T2.objects.all().count() == 2
        assert ProgramAudit_T3.objects.all().count() == 1

    @pytest.mark.django_db
    def test_program_audit_ftanf_errors(self, parsed_program_audit_ftanf):
        """Test error types for Program Audit FTANF file."""
        datafile, _dfs = parsed_program_audit_ftanf
        errors = ParserError.objects.filter(file=datafile).order_by("id")
        assert len(errors) == 2
        for e in errors:
            assert e.error_type == ParserErrorCategoryChoices.FIELD_VALUE

    @pytest.mark.django_db
    def test_program_audit_ftanf_case_aggregates(self, parsed_program_audit_ftanf):
        """Test case aggregates for Program Audit FTANF file."""
        _datafile, dfs = parsed_program_audit_ftanf
        dfs.status = dfs.get_status()
        assert dfs.status == DataFileSummary.Status.ACCEPTED_WITH_ERRORS
        dfs.case_aggregates = aggregates.case_aggregates_by_month(
            dfs.datafile, dfs.status
        )
        assert dfs.case_aggregates == {
            "months": [
                {
                    "month": "Jan",
                    "accepted_without_errors": 0,
                    "accepted_with_errors": 0,
                },
                {
                    "month": "Feb",
                    "accepted_without_errors": 0,
                    "accepted_with_errors": 0,
                },
                {
                    "month": "Mar",
                    "accepted_without_errors": 0,
                    "accepted_with_errors": 1,
                },
            ],
            "rejected": 0,
        }

    @pytest.mark.django_db
    def test_program_audit_duplicates_record_counts(
        self, parsed_program_audit_duplicates
    ):
        """Test record counts for Program Audit duplicates file."""
        _datafile, _dfs = parsed_program_audit_duplicates
        assert ProgramAudit_T1.objects.all().count() == 1
        assert ProgramAudit_T2.objects.all().count() == 3
        assert ProgramAudit_T3.objects.all().count() == 2

    @pytest.mark.django_db
    def test_program_audit_duplicates_errors(self, parsed_program_audit_duplicates):
        """Test error counts for Program Audit duplicates file."""
        datafile, _dfs = parsed_program_audit_duplicates
        errors = ParserError.objects.filter(file=datafile).order_by("id")
        assert len(errors) == 7

        duplicate_errors = errors.filter(
            error_message__contains="Duplicate record detected"
        )
        assert duplicate_errors.count() == 2

    @pytest.mark.django_db
    def test_program_audit_duplicates_case_aggregates(
        self, parsed_program_audit_duplicates
    ):
        """Test case aggregates for Program Audit duplicates file."""
        _datafile, dfs = parsed_program_audit_duplicates
        dfs.status = dfs.get_status()
        assert dfs.status == DataFileSummary.Status.PARTIALLY_ACCEPTED
        dfs.case_aggregates = aggregates.case_aggregates_by_month(
            dfs.datafile, dfs.status
        )
        assert dfs.case_aggregates == {
            "months": [
                {
                    "month": "Jan",
                    "accepted_without_errors": 0,
                    "accepted_with_errors": 0,
                },
                {
                    "month": "Feb",
                    "accepted_without_errors": 0,
                    "accepted_with_errors": 0,
                },
                {
                    "month": "Mar",
                    "accepted_without_errors": 0,
                    "accepted_with_errors": 1,
                },
            ],
            "rejected": 2,
        }

    @pytest.mark.parametrize(
        "fixture_name",
        [
            "program_audit_space_fill",
            "program_audit_zero_fill",
        ],
    )
    @pytest.mark.django_db
    def test_program_audit_space_zero_fill_record_counts(
        self, request, fixture_name, dfs
    ):
        """Test record counts for Program Audit space/zero fill files."""
        _datafile, _dfs = self._parse_program_audit_file(
            request, dfs, fixture_name, 2024, "Q1"
        )
        assert ProgramAudit_T1.objects.all().count() == 1
        assert ProgramAudit_T2.objects.all().count() == 1
        assert ProgramAudit_T3.objects.all().count() == 3

    @pytest.mark.parametrize(
        "fixture_name",
        [
            "program_audit_space_fill",
            "program_audit_zero_fill",
        ],
    )
    @pytest.mark.django_db
    def test_program_audit_space_zero_fill_errors(
        self, request, fixture_name, dfs
    ):
        """Test error counts for Program Audit space/zero fill files."""
        datafile, _dfs = self._parse_program_audit_file(
            request, dfs, fixture_name, 2024, "Q1"
        )
        errors = ParserError.objects.filter(file=datafile).order_by("id")
        assert len(errors) == 13

    @pytest.mark.parametrize(
        "fixture_name",
        [
            "program_audit_space_fill",
            "program_audit_zero_fill",
        ],
    )
    @pytest.mark.django_db
    def test_program_audit_space_zero_fill_case_aggregates(
        self, request, fixture_name, dfs
    ):
        """Test case aggregates for Program Audit space/zero fill files."""
        _datafile, dfs = self._parse_program_audit_file(
            request, dfs, fixture_name, 2024, "Q1"
        )
        dfs.status = dfs.get_status()
        assert dfs.status == DataFileSummary.Status.ACCEPTED_WITH_ERRORS
        dfs.case_aggregates = aggregates.case_aggregates_by_month(
            dfs.datafile, dfs.status
        )
        assert dfs.case_aggregates == {
            "months": [
                {
                    "month": "Oct",
                    "accepted_without_errors": 0,
                    "accepted_with_errors": 1,
                },
                {
                    "month": "Nov",
                    "accepted_without_errors": 0,
                    "accepted_with_errors": 0,
                },
                {
                    "month": "Dec",
                    "accepted_without_errors": 0,
                    "accepted_with_errors": 0,
                },
            ],
            "rejected": 0,
        }
