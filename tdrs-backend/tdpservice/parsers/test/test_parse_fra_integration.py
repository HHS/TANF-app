"""Integration tests for FRA parsing scenarios."""

import os

import pytest
from django.conf import settings

from tdpservice.parsers.models import (
    DataFileSummary,
    ParserError,
    ParserErrorCategoryChoices,
)
from tdpservice.parsers.test.helpers import parse_datafile
from tdpservice.search_indexes.models.fra import TANF_Exiter1


class TestParseFraIntegration:
    """Tests for FRA parsing with real fixtures and record creation."""

    @pytest.mark.parametrize(
        "file",
        [
            ("fra_work_outcome_exiter_csv_file"),
            ("fra_work_outcome_exiter_xlsx_file"),
        ],
    )
    @pytest.mark.django_db
    def test_parse_fra_work_outcome_exiters(self, request, file, dfs):
        """Test parsing FRA Work Outcome Exiters files."""
        datafile = request.getfixturevalue(file)
        datafile.year = 2024
        datafile.quarter = "Q2"

        dfs.datafile = datafile
        dfs.save()

        parse_datafile(dfs, datafile)

        assert TANF_Exiter1.objects.all().count() == 5

        errors = ParserError.objects.filter(file=datafile).order_by("id")
        assert errors.count() == 8
        for e in errors:
            assert e.error_type == ParserErrorCategoryChoices.CASE_CONSISTENCY
        assert dfs.total_number_of_records_in_file == 11
        assert dfs.total_number_of_records_created == 5
        assert dfs.get_status() == DataFileSummary.Status.PARTIALLY_ACCEPTED

    @pytest.mark.parametrize(
        "file",
        [
            ("fra_ofa_test_csv"),
            ("fra_ofa_test_xlsx"),
        ],
    )
    @pytest.mark.django_db
    def test_parse_fra_ofa_test_cases(self, request, file, dfs):
        """Test parsing OFA FRA files."""
        datafile = request.getfixturevalue(file)
        datafile.year = 2025
        datafile.quarter = "Q3"

        dfs.datafile = datafile
        dfs.save()

        settings.BULK_CREATE_BATCH_SIZE = 1

        parse_datafile(dfs, datafile)

        settings.BULK_CREATE_BATCH_SIZE = os.getenv("BULK_CREATE_BATCH_SIZE", 10000)

        errors = ParserError.objects.filter(file=datafile).order_by("id")
        for e in errors:
            assert e.error_type == ParserErrorCategoryChoices.CASE_CONSISTENCY

        assert errors.count() == 23
        assert TANF_Exiter1.objects.all().count() == 10
        assert dfs.total_number_of_records_in_file == 28
        assert dfs.total_number_of_records_created == 10
        assert dfs.get_status() == DataFileSummary.Status.PARTIALLY_ACCEPTED

    @pytest.mark.django_db
    def test_parse_fra_formula_fields(self, fra_formula_fields_test_xlsx, dfs):
        """Test parsing a correct FRA file with formula fields."""
        datafile = fra_formula_fields_test_xlsx
        datafile.year = 2025
        datafile.quarter = "Q3"

        dfs.datafile = datafile
        dfs.save()

        parse_datafile(dfs, datafile)

        errors = ParserError.objects.filter(file=datafile).order_by("id")
        assert errors.count() == 0
        assert TANF_Exiter1.objects.all().count() == 8
        assert dfs.total_number_of_records_in_file == 8
        assert dfs.total_number_of_records_created == 8
        assert dfs.get_status() == DataFileSummary.Status.ACCEPTED
