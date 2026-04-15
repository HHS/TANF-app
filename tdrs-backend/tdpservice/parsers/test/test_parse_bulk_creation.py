"""Integration tests covering bulk creation and duplicate handling."""

import os

import pytest
from django.conf import settings

from tdpservice.parsers.models import (
    DataFileSummary,
    ParserError,
    ParserErrorCategoryChoices,
)
from tdpservice.parsers.test.helpers import parse_datafile
from tdpservice.search_indexes.models.ssp import SSP_M1, SSP_M4, SSP_M5, SSP_M6, SSP_M7
from tdpservice.search_indexes.models.tanf import (
    TANF_T1,
    TANF_T2,
    TANF_T3,
    TANF_T4,
    TANF_T5,
    TANF_T6,
    TANF_T7,
)


class TestParseBulkCreation:
    """Tests for bulk create behavior, duplicates, and edge-case consistency."""

    @pytest.mark.parametrize(
        "file, batch_size, model, record_type, num_errors",
        [
            ("tanf_s1_exact_dup_file", 10000, TANF_T1, "T1", 3),
            ("tanf_s1_exact_dup_file", 1, TANF_T1, "T1", 3),
            ("tanf_s2_exact_dup_file", 10000, TANF_T4, "T4", 3),
            ("tanf_s2_exact_dup_file", 1, TANF_T4, "T4", 3),
            ("tanf_s3_exact_dup_file", 10000, TANF_T6, "T6", 3),
            ("tanf_s3_exact_dup_file", 1, TANF_T6, "T6", 3),
            ("tanf_s4_exact_dup_file", 10000, TANF_T7, "T7", 18),
            ("tanf_s4_exact_dup_file", 1, TANF_T7, "T7", 18),
            ("ssp_s1_exact_dup_file", 10000, SSP_M1, "M1", 3),
            ("ssp_s1_exact_dup_file", 1, SSP_M1, "M1", 3),
            ("ssp_s2_exact_dup_file", 10000, SSP_M4, "M4", 3),
            ("ssp_s2_exact_dup_file", 1, SSP_M4, "M4", 3),
            ("ssp_s3_exact_dup_file", 10000, SSP_M6, "M6", 3),
            ("ssp_s3_exact_dup_file", 1, SSP_M6, "M6", 3),
            ("ssp_s4_exact_dup_file", 10000, SSP_M7, "M7", 12),
            ("ssp_s4_exact_dup_file", 1, SSP_M7, "M7", 12),
        ],
    )
    @pytest.mark.django_db
    def test_parse_duplicate(
        self, file, batch_size, model, record_type, num_errors, dfs, request
    ):
        """Test cases for datafiles that have exact duplicate records."""
        datafile = request.getfixturevalue(file)
        dfs.datafile = datafile

        settings.BULK_CREATE_BATCH_SIZE = batch_size

        parse_datafile(dfs, datafile)

        settings.BULK_CREATE_BATCH_SIZE = os.getenv("BULK_CREATE_BATCH_SIZE", 10000)

        parser_errors = ParserError.objects.filter(
            file=datafile, error_type=ParserErrorCategoryChoices.CASE_CONSISTENCY
        ).order_by("id")
        for e in parser_errors:
            assert e.error_type == ParserErrorCategoryChoices.CASE_CONSISTENCY
        assert parser_errors.count() == num_errors

        dup_error = parser_errors.first()
        assert (
            dup_error.error_message
            == f"Duplicate record detected with record type {record_type} at line 3. "
            + "Record is a duplicate of the record at line number 2."
        )

        model.objects.count() == 0

    @pytest.mark.parametrize(
        "file, batch_size, model, record_type, num_errors, err_msg",
        [
            ("tanf_s1_partial_dup_file", 10000, TANF_T1, "T1", 3, "partial_dup_t1_err_msg"),
            ("tanf_s1_partial_dup_file", 1, TANF_T1, "T1", 3, "partial_dup_t1_err_msg"),
            ("tanf_s2_partial_dup_file", 10000, TANF_T5, "T5", 3, "partial_dup_t5_err_msg"),
            ("tanf_s2_partial_dup_file", 1, TANF_T5, "T5", 3, "partial_dup_t5_err_msg"),
            ("ssp_s1_partial_dup_file", 10000, SSP_M1, "M1", 3, "partial_dup_t1_err_msg"),
            ("ssp_s1_partial_dup_file", 1, SSP_M1, "M1", 3, "partial_dup_t1_err_msg"),
            ("ssp_s2_partial_dup_file", 10000, SSP_M5, "M5", 3, "partial_dup_t5_err_msg"),
            ("ssp_s2_partial_dup_file", 1, SSP_M5, "M5", 3, "partial_dup_t5_err_msg"),
        ],
    )
    @pytest.mark.django_db
    def test_parse_partial_duplicate(
        self, file, batch_size, model, record_type, num_errors, err_msg, dfs, request
    ):
        """Test cases for datafiles that have partial duplicate records."""
        datafile = request.getfixturevalue(file)
        expected_error_msg = request.getfixturevalue(err_msg)

        dfs.datafile = datafile

        settings.BULK_CREATE_BATCH_SIZE = batch_size

        parse_datafile(dfs, datafile)

        settings.BULK_CREATE_BATCH_SIZE = os.getenv("BULK_CREATE_BATCH_SIZE", 10000)

        parser_errors = ParserError.objects.filter(
            file=datafile, error_type=ParserErrorCategoryChoices.CASE_CONSISTENCY
        ).order_by("id")
        for e in parser_errors:
            assert e.error_type == ParserErrorCategoryChoices.CASE_CONSISTENCY
        assert parser_errors.count() == num_errors

        dup_error = parser_errors.first()
        assert expected_error_msg.format(record_type=record_type) in dup_error.error_message

        model.objects.count() == 0

    @pytest.mark.django_db
    def test_parse_cat_4_edge_case_file(self, cat4_edge_case_file, dfs):
        """Test parsing file with a cat4 error edge case submission."""
        cat4_edge_case_file.year = 2024
        cat4_edge_case_file.quarter = "Q1"

        dfs.datafile = cat4_edge_case_file
        dfs.save()

        settings.BULK_CREATE_BATCH_SIZE = 1

        parse_datafile(dfs, cat4_edge_case_file)

        settings.BULK_CREATE_BATCH_SIZE = os.getenv("BULK_CREATE_BATCH_SIZE", 10000)

        parser_errors = ParserError.objects.filter(file=cat4_edge_case_file).filter(
            error_type=ParserErrorCategoryChoices.CASE_CONSISTENCY
        )

        assert TANF_T1.objects.all().count() == 2
        assert TANF_T2.objects.all().count() == 2
        assert TANF_T3.objects.all().count() == 4

        assert dfs.total_number_of_records_in_file == 17
        assert dfs.total_number_of_records_created == 8

        err = parser_errors.first()
        assert err.error_message == (
            "Every T1 record should have at least one corresponding T2 or T3 record with the "
            "same Item 4 (Reporting Year and Month) and Item 6 (Case Number)."
        )
        assert dfs.get_status() == DataFileSummary.Status.PARTIALLY_ACCEPTED
