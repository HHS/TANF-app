"""Integration tests for large TANF datafile parsing."""

import pytest

from tdpservice.parsers import aggregates
from tdpservice.parsers.models import (
    DataFileSummary,
    ParserError,
    ParserErrorCategoryChoices,
)
from tdpservice.parsers.test.helpers import parse_datafile
from tdpservice.search_indexes.models.tanf import TANF_T1, TANF_T2, TANF_T3


class TestParseLargeFiles:
    """Tests for large and long-running parse scenarios."""

    @pytest.fixture
    def parsed_big_file(self, big_file, dfs):
        """Return parsed big_file and its DataFileSummary."""
        big_file.year = 2022
        big_file.quarter = "Q1"
        big_file.save()
        parse_datafile(dfs, big_file)
        return big_file, dfs

    @pytest.mark.django_db
    def test_big_file_status_and_case_aggregates(self, parsed_big_file):
        """Test status and case aggregates for ADS.E2J.FTP1.TS06."""
        _datafile, dfs = parsed_big_file
        dfs.status = dfs.get_status()
        assert dfs.status == DataFileSummary.Status.ACCEPTED_WITH_ERRORS

        dfs.case_aggregates = aggregates.case_aggregates_by_month(
            dfs.datafile, dfs.status
        )
        assert dfs.case_aggregates == {
            "months": [
                {
                    "month": "Oct",
                    "accepted_without_errors": 11,
                    "accepted_with_errors": 259,
                },
                {
                    "month": "Nov",
                    "accepted_without_errors": 12,
                    "accepted_with_errors": 261,
                },
                {
                    "month": "Dec",
                    "accepted_without_errors": 15,
                    "accepted_with_errors": 257,
                },
            ],
            "rejected": 0,
        }

    @pytest.mark.django_db
    def test_big_file_record_counts(self, parsed_big_file):
        """Test record counts for ADS.E2J.FTP1.TS06."""
        _datafile, _dfs = parsed_big_file
        assert TANF_T1.objects.count() == 815
        assert TANF_T2.objects.count() == 882
        assert TANF_T3.objects.count() == 1376

    @pytest.mark.django_db
    @pytest.mark.skip(reason="long runtime")
    def test_parse_super_big_s1_file(self, super_big_s1_file, dfs):
        """Test parsing super_big_s1_file and validate all records are created."""
        super_big_s1_file.year = 2023
        super_big_s1_file.quarter = "Q2"
        super_big_s1_file.save()

        dfs.datafile = super_big_s1_file
        dfs.save()

        parse_datafile(dfs, super_big_s1_file)
        expected_t1_record_count = 96607
        expected_t2_record_count = 112753
        expected_t3_record_count = 172525

        assert TANF_T1.objects.count() == expected_t1_record_count
        assert TANF_T2.objects.count() == expected_t2_record_count
        assert TANF_T3.objects.count() == expected_t3_record_count

    @pytest.mark.django_db
    def test_parse_big_s1_file_with_rollback(self, big_s1_rollback_file, dfs):
        """Test parsing big_s1_rollback_file with rollback on error."""
        big_s1_rollback_file.year = 2023
        big_s1_rollback_file.quarter = "Q2"
        big_s1_rollback_file.save()

        dfs.datafile = big_s1_rollback_file
        dfs.save()

        parse_datafile(dfs, big_s1_rollback_file)

        parser_errors = ParserError.objects.filter(file=big_s1_rollback_file)
        assert parser_errors.count() == 1

        err = parser_errors.first()

        assert err.row_number == 13609
        assert err.error_type == ParserErrorCategoryChoices.PRE_CHECK
        assert err.error_message == "Multiple headers found."
        assert err.content_type is None
        assert err.object_id is None

        assert TANF_T1.objects.count() == 0
        assert TANF_T2.objects.count() == 0
        assert TANF_T3.objects.count() == 0
