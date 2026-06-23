"""Integration tests for the live Go parser worker."""

import logging
import os
import time

from django.conf import settings
from django.db.models import Q as Query

import pytest
from celery import current_app as celery_app
from celery.exceptions import TimeoutError as CeleryTimeoutError

from tdpservice.data_files.models import DataFile
from tdpservice.parsers import aggregates
from tdpservice.parsers.models import (
    DataFileSummary,
    ParserError,
    ParserErrorCategoryChoices,
)
from tdpservice.parsers.test.factories import ParsingFileFactory
from tdpservice.search_indexes.models.fra import TANF_Exiter1
from tdpservice.search_indexes.models.ssp import (
    SSP_M1,
    SSP_M2,
    SSP_M3,
    SSP_M4,
    SSP_M5,
    SSP_M6,
    SSP_M7,
)
from tdpservice.search_indexes.models.tanf import (
    TANF_T1,
    TANF_T2,
    TANF_T3,
    TANF_T4,
    TANF_T5,
    TANF_T6,
    TANF_T7,
)
from tdpservice.search_indexes.models.tribal import (
    Tribal_TANF_T1,
    Tribal_TANF_T2,
    Tribal_TANF_T3,
    Tribal_TANF_T4,
    Tribal_TANF_T5,
    Tribal_TANF_T6,
    Tribal_TANF_T7,
)

logger = logging.getLogger(__name__)

GO_PARSE_TASK_NAME = "tdpservice.scheduling.parser_task.go_parse"
GO_PARSE_TIMEOUT_SECONDS = 300
GO_PARSE_LARGE_FILE_TIMEOUT_SECONDS = 300
_GO_PARSER_DATAFILE_IDS = None

os.environ["GO_PARSER_SHADOW_MODE"] = "False"


@pytest.fixture(autouse=True)
def disable_go_parser_shadow_mode(settings, monkeypatch):
    """Keep Go parser integration tests pointed at production tables."""
    monkeypatch.setenv("GO_PARSER_SHADOW_MODE", "False")
    settings.GO_PARSER_SHADOW_MODE = False


def register_go_parser_datafile_for_cleanup(datafile):
    """Register a DataFile for committed cleanup after a Go parser test."""
    if _GO_PARSER_DATAFILE_IDS is not None and datafile is not None and datafile.pk:
        _GO_PARSER_DATAFILE_IDS.add(datafile.pk)


def parse_datafile(dfs, datafile, timeout_seconds=GO_PARSE_TIMEOUT_SECONDS):
    """Submit a datafile to the Go parser worker and wait for completion."""
    register_go_parser_datafile_for_cleanup(datafile)

    dfs.datafile = datafile
    dfs.status = DataFileSummary.Status.PENDING
    dfs.save()

    async_result = celery_app.send_task(
        GO_PARSE_TASK_NAME,
        args=[datafile.pk, 0],
        queue=settings.CELERY_GO_PARSER_QUEUE,
    )

    try:
        task_result = async_result.get(timeout=timeout_seconds, propagate=True)
    except CeleryTimeoutError as exc:
        raise RuntimeError(
            f"Timed out waiting for Go parser task {async_result.id} "
            f"for datafile {datafile.pk} on queue {settings.CELERY_GO_PARSER_QUEUE}."
        ) from exc

    if task_result != "success":
        raise RuntimeError(
            f"Go parser task failed for datafile {datafile.pk}: {task_result}"
        )

    # Give the database a brief moment to surface writes after the worker acks success.
    time.sleep(0.1)

    dfs.refresh_from_db()
    return dfs


@pytest.mark.go_parser_integration
class TestGoParse:
    """Tests for parse and validation flows."""

    @pytest.fixture
    def parsed_small_correct_file(self, small_correct_file, dfs):
        """Return parsed small_correct_file and its DataFileSummary."""
        small_correct_file.year = 2021
        small_correct_file.quarter = "Q1"
        small_correct_file.save()

        parse_datafile(dfs, small_correct_file)

        return small_correct_file, dfs

    # @pytest.fixture
    # def parsed_bad_trailer_file(self, bad_trailer_file, dfs):
    #     """Return parsed bad_trailer_file and its errors."""
    #     bad_trailer_file.year = 2021
    #     bad_trailer_file.quarter = "Q1"

    #     parse_datafile(dfs, bad_trailer_file)

    #     parser_errors = ParserError.objects.filter(file=bad_trailer_file)
    #     return bad_trailer_file, dfs, parser_errors

    # @pytest.fixture
    # def parsed_bad_trailer_file_2(self, bad_trailer_file_2, dfs):
    #     """Return parsed bad_trailer_file_2 and its errors."""
    #     dfs.datafile = bad_trailer_file_2
    #     dfs.save()

    #     bad_trailer_file_2.year = 2021
    #     bad_trailer_file_2.quarter = "Q1"

    #     parse_datafile(dfs, bad_trailer_file_2)

    #     parser_errors = ParserError.objects.filter(file=bad_trailer_file_2)
    #     return bad_trailer_file_2, dfs, parser_errors

    @pytest.mark.django_db(transaction=True)
    @pytest.mark.parametrize(
        "program_type,section_name,header",
        [
            (
                DataFile.ProgramType.TANF,
                DataFile.Section.ACTIVE_CASE_DATA,
                "HEADER20244A06   TAN1ED",
            ),
            (
                DataFile.ProgramType.TANF,
                DataFile.Section.AGGREGATE_DATA,
                "HEADER20244G06   TAN1ED",
            ),
            (
                DataFile.ProgramType.TANF,
                DataFile.Section.STRATUM_DATA,
                "HEADER20244S06   TAN1ED",
            ),
            (
                DataFile.ProgramType.SSP,
                DataFile.Section.ACTIVE_CASE_DATA,
                "HEADER20244A06   SSP1ED",
            ),
            (
                DataFile.ProgramType.SSP,
                DataFile.Section.AGGREGATE_DATA,
                "HEADER20244G06   SSP1ED",
            ),
            (
                DataFile.ProgramType.SSP,
                DataFile.Section.STRATUM_DATA,
                "HEADER20244S06   SSP1ED",
            ),
            (
                DataFile.ProgramType.TRIBAL,
                DataFile.Section.ACTIVE_CASE_DATA,
                "HEADER20244A00123TAN1ED",
            ),
            (
                DataFile.ProgramType.TRIBAL,
                DataFile.Section.AGGREGATE_DATA,
                "HEADER20244G00123TAN1ED",
            ),
            (
                DataFile.ProgramType.TRIBAL,
                DataFile.Section.STRATUM_DATA,
                "HEADER20244S00123TAN1ED",
            ),
        ],
    )
    def test_go_parse_zero_record_header_trailer_only_files(
        self, dfs, program_type, section_name, header
    ):
        """Test Go parser accepts valid zero-record TANF, SSP, and Tribal files."""
        datafile = ParsingFileFactory(
            year=2025,
            quarter="Q1",
            section=section_name,
            program_type=program_type,
            file__name=f"{program_type}-{section_name}-zero-records.txt",
            file__section=section_name,
            file__data=(f"{header}\nTRAILER0000000         ".encode()),
        )

        parse_datafile(dfs, datafile)

        assert ParserError.objects.filter(file=datafile).count() == 0
        assert dfs.total_number_of_records_in_file == 0
        assert dfs.total_number_of_records_created == 0
        assert dfs.get_status() == DataFileSummary.Status.ACCEPTED

    @pytest.mark.django_db(transaction=True)
    def test_go_parse_zero_record_bad_trailer_count_rejected(self, dfs):
        """Test Go parser rejects zero-record files when trailer count is not zero."""
        datafile = ParsingFileFactory(
            year=2025,
            quarter="Q1",
            section=DataFile.Section.ACTIVE_CASE_DATA,
            program_type=DataFile.ProgramType.TANF,
            file__name="tanf-active-zero-records-bad-trailer-count.txt",
            file__section=DataFile.Section.ACTIVE_CASE_DATA,
            file__data=(b"HEADER20244A06   TAN1ED\n" b"TRAILER0000001         "),
        )

        parse_datafile(dfs, datafile)

        assert dfs.get_status() == DataFileSummary.Status.REJECTED
        trailer_count_error = (
            "The number of records in the TRAILER row count: 1, does not match "
            "the number of records detected in the file: 0."
        )
        assert ParserError.objects.filter(
            file=datafile,
            error_message=trailer_count_error,
            error_type=ParserErrorCategoryChoices.PRE_CHECK,
        ).exists()
        assert ParserError.objects.filter(
            file=datafile,
            error_message="No records created.",
            error_type=ParserErrorCategoryChoices.PRE_CHECK,
        ).exists()

    @pytest.mark.django_db(transaction=True)
    def test_go_small_correct_file_case_consistency_error(
        self, parsed_small_correct_file
    ):
        """Test case consistency errors are recorded for small_correct_file."""
        datafile, _dfs = parsed_small_correct_file
        errors = ParserError.objects.filter(file=datafile).order_by("id")
        # Go parser generates cat4 error that the python parser misses
        assert errors.count() == 3
        assert errors.first().error_type == ParserErrorCategoryChoices.CASE_CONSISTENCY

    @pytest.mark.django_db(transaction=True)
    def test_go_small_correct_file_case_aggregates_rejected(
        self, parsed_small_correct_file
    ):
        """Test case aggregates for rejected small_correct_file."""
        _datafile, dfs = parsed_small_correct_file
        dfs.status = dfs.get_status()
        dfs.case_aggregates = aggregates.case_aggregates_by_month(
            dfs.datafile, dfs.status
        )
        assert dfs.case_aggregates == {
            "rejected": 1,
            "months": [
                {
                    "accepted_without_errors": "N/A",
                    "accepted_with_errors": "N/A",
                    "month": "Oct",
                },
                {
                    "accepted_without_errors": "N/A",
                    "accepted_with_errors": "N/A",
                    "month": "Nov",
                },
                {
                    "accepted_without_errors": "N/A",
                    "accepted_with_errors": "N/A",
                    "month": "Dec",
                },
            ],
        }
        assert dfs.get_status() == DataFileSummary.Status.REJECTED

    @pytest.mark.django_db(transaction=True)
    def test_go_small_correct_file_no_records_created(self, parsed_small_correct_file):
        """Test that small_correct_file does not create records when rejected."""
        datafile, _dfs = parsed_small_correct_file
        assert TANF_T1.objects.filter(datafile=datafile).count() == 0

    @pytest.mark.django_db(transaction=True)
    @pytest.mark.parametrize(
        "program, section, expected_message, expected_aggregates, save_dfs, num_errors",
        [
            (
                "TAN",
                "Closed Case Data",
                "Data does not match the expected layout for Closed Case Data.",
                {
                    "rejected": 1,
                    "months": [
                        {
                            "accepted_without_errors": "N/A",
                            "accepted_with_errors": "N/A",
                            "month": "Oct",
                        },
                        {
                            "accepted_without_errors": "N/A",
                            "accepted_with_errors": "N/A",
                            "month": "Nov",
                        },
                        {
                            "accepted_without_errors": "N/A",
                            "accepted_with_errors": "N/A",
                            "month": "Dec",
                        },
                    ],
                },
                False,
                2,
            ),
            (
                "SSP",
                "Active Case Data",
                "Submitted program type (SSP) does not match file program type (TAN).",
                None,
                True,
                2,
            ),
        ],
    )
    def test_go_parse_section_mismatch_variants(
        self,
        small_correct_file,
        dfs,
        program,
        section,
        expected_message,
        expected_aggregates,
        save_dfs,
        num_errors,
    ):
        """Test parsing when file metadata does not match the raw data layout."""
        small_correct_file.program_type = program
        small_correct_file.section = section
        small_correct_file.version = small_correct_file.id
        small_correct_file.save()

        dfs.datafile = small_correct_file
        if save_dfs:
            dfs.save()

        parse_datafile(dfs, small_correct_file)

        dfs.status = dfs.get_status()
        assert dfs.status == DataFileSummary.Status.REJECTED
        parser_errors = ParserError.objects.filter(file=small_correct_file).order_by(
            "-row_number"
        )
        assert parser_errors.count() == num_errors

        if expected_aggregates is not None:
            dfs.case_aggregates = aggregates.case_aggregates_by_month(
                dfs.datafile, dfs.status
            )
            assert dfs.case_aggregates == expected_aggregates

        err = parser_errors.first()
        assert err.error_type in [
            ParserErrorCategoryChoices.PRE_CHECK,
            ParserErrorCategoryChoices.RECORD_PRE_CHECK,
        ]
        assert err.error_message == expected_message
        assert err.content_type is None
        assert err.object_id is None

        if program == "SSP" and section == "Active Case Data":
            assert TANF_T1.objects.filter(datafile=small_correct_file).count() == 0
            assert TANF_T2.objects.filter(datafile=small_correct_file).count() == 0
            assert TANF_T3.objects.filter(datafile=small_correct_file).count() == 0

    @pytest.mark.django_db(transaction=True)
    @pytest.mark.parametrize(
        "fixture_name, updates, expected",
        [
            (
                "bad_test_file",
                {},
                {
                    "count": 3,
                    "row_number": 1,
                    "error_message": (
                        "HEADER: record length is 24 characters but must be 23."
                    ),
                },
            ),
            (
                "bad_file_missing_header",
                {},
                {
                    "count": 2,
                    "row_number": 1,
                    "error_message": ("Your file does not start with a HEADER."),
                    "status": DataFileSummary.Status.REJECTED,
                },
            ),
            (
                "bad_file_multiple_headers",
                {"year": 2024, "quarter": "Q1"},
                {
                    "count": 1,
                    "row_number": 9,
                    "error_message": "Multiple headers found.",
                    "status": DataFileSummary.Status.REJECTED,
                },
            ),
            (
                "big_bad_test_file",
                {"year": 2022, "quarter": "Q1"},
                {
                    "count": 1,
                    "row_number": 3679,
                    "error_message": "Multiple headers found.",
                },
            ),
        ],
    )
    def test_go_parse_precheck_header_errors(
        self, request, fixture_name, updates, expected, dfs
    ):
        """Test parsing failures triggered by header/pre-check validation."""
        datafile = request.getfixturevalue(fixture_name)
        for field, value in updates.items():
            setattr(datafile, field, value)
        if updates:
            datafile.save()

        parse_datafile(dfs, datafile)

        if expected.get("status"):
            assert dfs.get_status() == expected["status"]

        parser_errors = ParserError.objects.filter(file=datafile).order_by("id")
        assert parser_errors.count() == expected["count"]

        err = parser_errors.first()
        assert err.row_number == expected["row_number"]
        assert err.error_type == ParserErrorCategoryChoices.PRE_CHECK
        assert err.error_message == expected["error_message"]
        assert err.content_type is None
        assert err.object_id is None

    # @pytest.mark.django_db(transaction=True)
    # def test_bad_trailer_file_trailer_error(self, parsed_bad_trailer_file):
    #     """Test trailer errors for bad_trailer_1."""
    #     _datafile, _dfs, parser_errors = parsed_bad_trailer_file
    #     assert parser_errors.count() == 5

    #     trailer_error = parser_errors.get(row_number=3)
    #     assert trailer_error.error_type == ParserErrorCategoryChoices.RECORD_PRE_CHECK
    #     assert (
    #         trailer_error.error_message
    #         == "TRAILER: record length is 11 characters but must be 23."
    #     )
    #     assert trailer_error.content_type is None
    #     assert trailer_error.object_id is None

    # @pytest.mark.django_db(transaction=True)
    # def test_bad_trailer_file_row_errors(self, parsed_bad_trailer_file):
    #     """Test row-level errors for bad_trailer_1."""
    #     _datafile, _dfs, parser_errors = parsed_bad_trailer_file

    #     # reporting month/year test
    #     row_errors = parser_errors.filter(row_number=2)
    #     row_errors_list = []
    #     for row_error in row_errors:
    #         row_errors_list.append(row_error)
    #         assert row_error.error_type == ParserErrorCategoryChoices.RECORD_PRE_CHECK
    #         assert row_error.error_message in [
    #             "TRAILER: record length is 11 characters but must be 23.",
    #             "T1: Case number T1trash cannot contain blanks.",
    #             "T1: record length should be at least 117 characters but it is 7 characters.",
    #             "T1: Reporting month year None does not match file reporting year:2021, quarter:Q1.",
    #         ]
    #         assert row_error.content_type is None
    #         assert row_error.object_id is None

    #     row_errors = list(parser_errors.filter(row_number=2).order_by("id"))
    #     length_error = row_errors[0]
    #     assert length_error.error_type == ParserErrorCategoryChoices.RECORD_PRE_CHECK
    #     assert (
    #         length_error.error_message
    #         == "T1: record length should be at least 117 characters but it is 7 characters."
    #     )
    #     assert length_error.content_type is None
    #     assert length_error.object_id is None

    # @pytest.mark.django_db(transaction=True)
    # def test_bad_trailer_file2_trailer_errors(self, parsed_bad_trailer_file_2):
    #     """Test trailer errors for bad_trailer_2."""
    #     _datafile, _dfs, parser_errors = parsed_bad_trailer_file_2
    #     assert parser_errors.count() == 9

    #     parser_errors = parser_errors.exclude(
    #         error_type=ParserErrorCategoryChoices.CASE_CONSISTENCY
    #     )
    #     trailer_errors = list(parser_errors.filter(row_number=3).order_by("id"))

    #     trailer_error_1 = trailer_errors[0]
    #     assert trailer_error_1.error_type == ParserErrorCategoryChoices.RECORD_PRE_CHECK
    #     assert (
    #         trailer_error_1.error_message
    #         == "TRAILER: record length is 7 characters but must be 23."
    #     )
    #     assert trailer_error_1.content_type is None
    #     assert trailer_error_1.object_id is None

    #     trailer_error_2 = trailer_errors[1]
    #     assert trailer_error_2.error_type == ParserErrorCategoryChoices.RECORD_PRE_CHECK
    #     assert (
    #         trailer_error_2.error_message
    #         == "Your file does not end with a TRAILER record."
    #     )
    #     assert trailer_error_2.content_type is None
    #     assert trailer_error_2.object_id is None

    # @pytest.mark.django_db(transaction=True)
    # def test_bad_trailer_file2_row_2_error(self, parsed_bad_trailer_file_2):
    #     """Test row 2 validation error for bad_trailer_2."""
    #     _datafile, _dfs, parser_errors = parsed_bad_trailer_file_2

    #     parser_errors = parser_errors.exclude(
    #         error_type=ParserErrorCategoryChoices.CASE_CONSISTENCY
    #     )
    #     row_2_errors = parser_errors.filter(row_number=2).order_by("id")
    #     row_2_error = row_2_errors.first()
    #     assert row_2_error.error_type == ParserErrorCategoryChoices.FIELD_VALUE
    #     assert row_2_error.error_message == (
    #         "T1 Item 13 (Receives Subsidized Housing): 3 is not in range [1, 2]."
    #     )

    # @pytest.mark.django_db(transaction=True)
    # def test_bad_trailer_file2_row_3_errors(self, parsed_bad_trailer_file_2):
    #     """Test row 3 errors and case number validation for bad_trailer_2."""
    #     _datafile, _dfs, parser_errors = parsed_bad_trailer_file_2

    #     parser_errors = parser_errors.exclude(
    #         error_type=ParserErrorCategoryChoices.CASE_CONSISTENCY
    #     )
    #     trailer_errors = list(parser_errors.filter(row_number=3).order_by("id"))

    #     # catch-rpt-month-year-mismatches
    #     row_3_errors = parser_errors.filter(row_number=3)
    #     row_3_error_list = []

    #     for row_3_error in row_3_errors:
    #         row_3_error_list.append(row_3_error)
    #         assert row_3_error.error_type == ParserErrorCategoryChoices.RECORD_PRE_CHECK
    #         assert row_3_error.error_message in {
    #             "T1: record length should be at least 117 characters but it is 7 characters.",
    #             "T1: Reporting month year None does not match file reporting year:2021, quarter:Q1.",
    #             "TRAILER: record length is 7 characters but must be 23.",
    #             "T1: Case number T1trash cannot contain blanks.",
    #             "Your file does not end with a TRAILER record.",
    #         }
    #         assert row_3_error.content_type is None
    #         assert row_3_error.object_id is None

    #     # case number validators
    #     row_3_errors = [trailer_errors[2], trailer_errors[3]]
    #     length_error = row_3_errors[0]
    #     assert length_error.error_type == ParserErrorCategoryChoices.RECORD_PRE_CHECK
    #     assert (
    #         length_error.error_message
    #         == "T1: record length should be at least 117 characters but it is 7 characters."
    #     )
    #     assert length_error.content_type is None
    #     assert length_error.object_id is None

    #     trailer_error_3 = trailer_errors[3]
    #     assert trailer_error_3.error_type == ParserErrorCategoryChoices.RECORD_PRE_CHECK
    #     assert (
    #         trailer_error_3.error_message
    #         == "T1: Case number T1trash cannot contain blanks."
    #     )
    #     assert trailer_error_3.content_type is None
    #     assert trailer_error_3.object_id is None

    #     trailer_error_4 = trailer_errors[4]
    #     assert trailer_error_4.error_type == ParserErrorCategoryChoices.RECORD_PRE_CHECK
    #     assert trailer_error_4.error_message == (
    #         "T1: Reporting month year None does not "
    #         "match file reporting year:2021, quarter:Q1."
    #     )
    #     assert trailer_error_4.content_type is None
    #     assert trailer_error_4.object_id is None

    @pytest.mark.django_db(transaction=True)
    def test_go_parse_big_file(self, big_file, dfs):
        """Test parsing large TANF section 1 file."""
        dfs.datafile = big_file
        dfs.save()

        parse_datafile(dfs, big_file)

        errors = ParserError.objects.filter(file=big_file)
        assert errors.count() == 2155

        assert TANF_T1.objects.filter(datafile=big_file).count() == 815
        assert TANF_T2.objects.filter(datafile=big_file).count() == 882
        assert TANF_T3.objects.filter(datafile=big_file).count() == 1376

    @pytest.mark.django_db(transaction=True)
    def test_go_parse_empty_file(self, empty_file, dfs):
        """Test parsing of empty_file."""
        dfs.datafile = empty_file
        dfs.save()
        parse_datafile(dfs, empty_file)

        dfs.status = dfs.get_status()
        dfs.case_aggregates = aggregates.case_aggregates_by_month(
            empty_file, dfs.status
        )

        assert dfs.status == DataFileSummary.Status.REJECTED
        assert dfs.case_aggregates == {
            "rejected": 1,
            "months": [
                {
                    "accepted_without_errors": "N/A",
                    "accepted_with_errors": "N/A",
                    "month": "Oct",
                },
                {
                    "accepted_without_errors": "N/A",
                    "accepted_with_errors": "N/A",
                    "month": "Nov",
                },
                {
                    "accepted_without_errors": "N/A",
                    "accepted_with_errors": "N/A",
                    "month": "Dec",
                },
            ],
        }

        parser_errors = ParserError.objects.filter(file=empty_file).order_by("id")

        assert parser_errors.filter(file=empty_file).count() == 2

        err = parser_errors.first()

        assert err.row_number == 1
        assert err.error_type == ParserErrorCategoryChoices.PRE_CHECK
        # Go parser has a better error message which is why this is different
        assert err.error_message == "Your file does not start with a HEADER."
        assert err.content_type is None
        assert err.object_id is None

    @pytest.mark.django_db(transaction=True)
    def test_go_parse_small_ssp_section1_datafile(
        self, small_ssp_section1_datafile, dfs
    ):
        """Test parsing small_ssp_section1_datafile."""
        expected_m1_record_count = 5
        expected_m2_record_count = 6
        expected_m3_record_count = 8

        dfs.datafile = small_ssp_section1_datafile
        dfs.save()
        parse_datafile(dfs, small_ssp_section1_datafile)

        parser_errors = ParserError.objects.filter(
            file=small_ssp_section1_datafile
        ).order_by("error_type")
        dfs.status = dfs.get_status()

        # Go parser doesnt generate Trailer errors which is why the status is different
        assert dfs.status == DataFileSummary.Status.PARTIALLY_ACCEPTED
        dfs.case_aggregates = aggregates.case_aggregates_by_month(
            dfs.datafile, dfs.status
        )

        assert dfs.case_aggregates["rejected"] == 1
        for month in dfs.case_aggregates["months"]:
            if month["month"] == "Oct":
                assert month["accepted_without_errors"] == 0
                assert month["accepted_with_errors"] == 5
            else:
                assert month["accepted_without_errors"] == 0
                assert month["accepted_with_errors"] == 0

        parser_errors = ParserError.objects.filter(file=small_ssp_section1_datafile)
        assert parser_errors.filter(file=small_ssp_section1_datafile).count() == 9
        assert (
            SSP_M1.objects.filter(datafile=small_ssp_section1_datafile).count()
            == expected_m1_record_count
        )
        assert (
            SSP_M2.objects.filter(datafile=small_ssp_section1_datafile).count()
            == expected_m2_record_count
        )
        assert (
            SSP_M3.objects.filter(datafile=small_ssp_section1_datafile).count()
            == expected_m3_record_count
        )

    @pytest.mark.django_db(transaction=True)()
    def test_go_parse_ssp_section1_datafile(self, ssp_section1_datafile, dfs):
        """Test parsing ssp_section1_datafile."""
        expected_m1_record_count = 818
        expected_m2_record_count = 989
        expected_m3_record_count = 1748

        dfs.datafile = ssp_section1_datafile
        dfs.save()

        parse_datafile(dfs, ssp_section1_datafile)

        parser_errors = ParserError.objects.filter(file=ssp_section1_datafile).order_by(
            "row_number"
        )

        err = parser_errors.first()

        assert err.row_number == 2
        assert err.error_type == ParserErrorCategoryChoices.FIELD_VALUE
        assert err.error_message == ("M1 Item 11: must be one of [1 2], got 3")
        assert err.content_type is not None
        assert err.object_id is not None

        cat4_errors = parser_errors.filter(
            error_type=ParserErrorCategoryChoices.CASE_CONSISTENCY
        ).order_by("id")

        # We have more Cat4 errors here than the Python equivalent because in Go they run before precheck validators.
        # The Go parser captures all the same errors if the Python prechecks are disabled.
        assert cat4_errors.count() == 20
        assert (
            cat4_errors[0].error_message
            == "Duplicate record detected with record type M3 at line 453. Record is a duplicate of the record at line number 452."
        )
        assert (
            cat4_errors[1].error_message
            == "Duplicate record detected with record type M3 at line 3273. Record is a duplicate of the record at line number 3272."
        )
        assert (
            cat4_errors[2].error_message
            == "Partial duplicate record detected with record type M3 at line 3275. Record is a partial duplicate of the record at line number 3274. Duplicated fields causing error: Item 0 (Record Type), Item 3 (Reporting Month/Year), Item 5 (Case Number), Item 60 (Family Affiliation), Item 61 (Date of Birth), and Item 62 (Social Security Number)."
        )

        # We have a few more errors because the go parser separates the the OR'd
        # category1.validate_fieldYearMonth_with_headerYearQuarter(). and
        # category1.validateRptMonthYear() into separate checks.
        assert parser_errors.count() == 31739

        assert (
            SSP_M1.objects.filter(datafile=ssp_section1_datafile).count()
            == expected_m1_record_count
        )
        assert (
            SSP_M2.objects.filter(datafile=ssp_section1_datafile).count()
            == expected_m2_record_count
        )
        assert (
            SSP_M3.objects.filter(datafile=ssp_section1_datafile).count()
            == expected_m3_record_count
        )

    @pytest.mark.django_db(transaction=True)
    def test_go_parse_tanf_section1_datafile(self, small_tanf_section1_datafile, dfs):
        """Test parsing of small_tanf_section1_datafile and validate T2 model data."""
        dfs.datafile = small_tanf_section1_datafile

        parse_datafile(dfs, small_tanf_section1_datafile)

        dfs.status = dfs.get_status()
        assert dfs.status == DataFileSummary.Status.ACCEPTED_WITH_ERRORS
        dfs.case_aggregates = aggregates.case_aggregates_by_month(
            dfs.datafile, dfs.status
        )
        assert dfs.case_aggregates == {
            "months": [
                {
                    "month": "Oct",
                    "accepted_without_errors": 1,
                    "accepted_with_errors": 4,
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

        assert (
            TANF_T2.objects.filter(datafile=small_tanf_section1_datafile).count() == 5
        )

        t2_models = TANF_T2.objects.filter(
            datafile=small_tanf_section1_datafile
        ).order_by("CASE_NUMBER")

        t2 = t2_models[0]
        assert t2.RPT_MONTH_YEAR == 202010
        assert t2.CASE_NUMBER == "11111111112"
        assert t2.FAMILY_AFFILIATION == 1
        assert t2.OTHER_UNEARNED_INCOME == "0291"

        t2_2 = t2_models[1]
        assert t2_2.RPT_MONTH_YEAR == 202010
        assert t2_2.CASE_NUMBER == "11111111115"
        assert t2_2.FAMILY_AFFILIATION == 2
        assert t2_2.OTHER_UNEARNED_INCOME == "0000"

    @pytest.mark.django_db(transaction=True)()
    def test_go_parse_tanf_section1_datafile_obj_counts(
        self, small_tanf_section1_datafile, dfs
    ):
        """Test parsing of small_tanf_section1_datafile in general."""
        dfs.datafile = small_tanf_section1_datafile
        dfs.save()

        parse_datafile(dfs, small_tanf_section1_datafile)

        assert (
            TANF_T1.objects.filter(datafile=small_tanf_section1_datafile).count() == 5
        )
        assert (
            TANF_T2.objects.filter(datafile=small_tanf_section1_datafile).count() == 5
        )
        assert (
            TANF_T3.objects.filter(datafile=small_tanf_section1_datafile).count() == 6
        )

    @pytest.mark.django_db(transaction=True)()
    def test_go_parse_tanf_section1_datafile_t3s(
        self, small_tanf_section1_datafile, dfs
    ):
        """Test parsing of small_tanf_section1_datafile and validate T3 model data."""
        dfs.datafile = small_tanf_section1_datafile
        dfs.save()

        parse_datafile(dfs, small_tanf_section1_datafile)

        assert (
            TANF_T3.objects.filter(datafile=small_tanf_section1_datafile).count() == 6
        )

        t3_models = TANF_T3.objects.filter(
            datafile=small_tanf_section1_datafile
        ).order_by("CASE_NUMBER")
        t3_1 = t3_models[0]
        assert t3_1.RPT_MONTH_YEAR == 202010
        assert t3_1.CASE_NUMBER == "11111111112"
        assert t3_1.FAMILY_AFFILIATION == 1
        assert t3_1.SEX == 2
        assert t3_1.EDUCATION_LEVEL == "98"

        t3_5 = t3_models[4]
        assert t3_5.RPT_MONTH_YEAR == 202010
        assert t3_5.CASE_NUMBER == "11111111151"
        assert t3_5.FAMILY_AFFILIATION == 1
        assert t3_5.SEX == 1
        assert t3_5.EDUCATION_LEVEL == "98"

    @pytest.mark.django_db(transaction=True)
    def test_go_parse_bad_tfs1_missing_required(
        self, bad_tanf_s1__row_missing_required_field, dfs
    ):
        """Test parsing a bad TANF Section 1 submission where a row is missing required data."""
        dfs.datafile = bad_tanf_s1__row_missing_required_field
        dfs.save()

        parse_datafile(dfs, bad_tanf_s1__row_missing_required_field)

        parser_errors = ParserError.objects.filter(
            file=bad_tanf_s1__row_missing_required_field
        )

        assert dfs.get_status() == DataFileSummary.Status.REJECTED

        # Again we get more errors here because the Go parser splits the RPT_MONTH_YEAR Cat1 validator
        # into two validators
        assert parser_errors.count() == 9

        error_message = "T1: Reporting month year <no value> does not match file reporting year:2021, quarter:Q1."
        row_2_error = parser_errors.get(row_number=2, error_message=error_message)
        assert row_2_error.error_type == ParserErrorCategoryChoices.RECORD_PRE_CHECK
        assert row_2_error.error_message == error_message

        error_message = "T2: Reporting month year <no value> does not match file reporting year:2021, quarter:Q1."
        row_3_error = parser_errors.get(row_number=3, error_message=error_message)
        assert row_3_error.error_type == ParserErrorCategoryChoices.RECORD_PRE_CHECK
        assert row_3_error.error_message == error_message

        error_message = "T3: Reporting month year <no value> does not match file reporting year:2021, quarter:Q1."
        row_4_error = parser_errors.get(row_number=4, error_message=error_message)
        assert row_4_error.error_type == ParserErrorCategoryChoices.RECORD_PRE_CHECK
        assert row_4_error.error_message == error_message

        error_message = "Unknown record type was found."
        row_5_error = parser_errors.get(row_number=5, error_message=error_message)
        assert row_5_error.error_type == ParserErrorCategoryChoices.RECORD_PRE_CHECK
        assert row_5_error.error_message == error_message
        assert row_5_error.content_type is None
        assert row_5_error.object_id is None

    @pytest.mark.django_db(transaction=True)()
    def test_go_parse_bad_ssp_s1_missing_required(
        self, bad_ssp_s1__row_missing_required_field, dfs
    ):
        """Test parsing a bad TANF Section 1 submission where a row is missing required data."""
        dfs.datafile = bad_ssp_s1__row_missing_required_field
        dfs.save()

        parse_datafile(dfs, bad_ssp_s1__row_missing_required_field)

        parser_errors = ParserError.objects.filter(
            file=bad_ssp_s1__row_missing_required_field
        )
        # Again we get more errors here because the Go parser splits the RPT_MONTH_YEAR Cat1 validator
        # into two validators
        assert parser_errors.count() == 9

        row_2_error = parser_errors.get(
            row_number=2,
            error_message__contains="M1: Reporting month year <no value> does not match file reporting year:2019, quarter:Q1.",
        )
        assert row_2_error.error_type == ParserErrorCategoryChoices.RECORD_PRE_CHECK

        row_3_error = parser_errors.get(
            row_number=3,
            error_message__contains="M2: Reporting month year <no value> does not match file reporting year:2019, quarter:Q1.",
        )
        assert row_3_error.error_type == ParserErrorCategoryChoices.RECORD_PRE_CHECK

        row_4_error = parser_errors.get(
            row_number=4,
            error_message__contains="M3: Reporting month year <no value> does not match file reporting year:2019, quarter:Q1.",
        )
        assert row_4_error.error_type == ParserErrorCategoryChoices.RECORD_PRE_CHECK

        error_message = "Reporting month year <no value> does not match file reporting year:2019, quarter:Q1."
        rpt_month_errors = parser_errors.filter(error_message__contains=error_message)
        assert len(rpt_month_errors) == 3
        for i, e in enumerate(rpt_month_errors):
            assert e.error_type == ParserErrorCategoryChoices.RECORD_PRE_CHECK
            assert error_message.format(i + 1) in e.error_message
            assert e.object_id is None

        row_5_error = parser_errors.get(
            row_number=5, error_message="Unknown record type was found."
        )
        assert row_5_error.error_type == ParserErrorCategoryChoices.RECORD_PRE_CHECK
        assert row_5_error.content_type is None
        assert row_5_error.object_id is None

    @pytest.mark.django_db(transaction=True)
    def test_go_dfs_set_case_aggregates(self, small_correct_file, dfs):
        """Test that the case aggregates are set correctly."""
        small_correct_file.year = 2020
        small_correct_file.quarter = "Q3"
        small_correct_file.section = "Active Case Data"
        small_correct_file.save()
        # this still needs to execute to create db objects to be queried
        parse_datafile(dfs, small_correct_file)
        dfs.file = small_correct_file
        dfs.status = dfs.get_status()
        dfs.case_aggregates = aggregates.case_aggregates_by_month(
            small_correct_file, dfs.status
        )

        for month in dfs.case_aggregates["months"]:
            if month["month"] == "Oct":
                assert month["accepted_without_errors"] == 1
                assert month["accepted_with_errors"] == 0

    @pytest.mark.django_db(transaction=True)()
    def test_go_parse_small_tanf_section2_file(self, small_tanf_section2_file, dfs):
        """Test parsing a small TANF Section 2 submission."""
        dfs.datafile = small_tanf_section2_file
        dfs.save()

        parse_datafile(dfs, small_tanf_section2_file)

        assert TANF_T4.objects.filter(datafile=small_tanf_section2_file).count() == 1
        assert TANF_T5.objects.filter(datafile=small_tanf_section2_file).count() == 1

        parser_errors = ParserError.objects.filter(file=small_tanf_section2_file)

        assert parser_errors.count() == 0

        t4 = TANF_T4.objects.filter(datafile=small_tanf_section2_file).first()
        t5 = TANF_T5.objects.filter(datafile=small_tanf_section2_file).first()

        assert t4.DISPOSITION == 1
        assert t4.REC_SUB_CC == 3

        assert t5.SEX == 2
        assert t5.AMOUNT_UNEARNED_INCOME == "0000"

    @pytest.mark.django_db(transaction=True)()
    def test_go_parse_tanf_section2_file(self, tanf_section2_file, dfs):
        """Test parsing TANF Section 2 submission."""
        dfs.datafile = tanf_section2_file
        dfs.save()

        parse_datafile(dfs, tanf_section2_file)

        assert TANF_T4.objects.filter(datafile=tanf_section2_file).count() == 223
        assert TANF_T5.objects.filter(datafile=tanf_section2_file).count() == 605

        parser_errors = ParserError.objects.filter(file=tanf_section2_file).order_by(
            "row_number"
        )

        err = parser_errors.first()
        assert err.error_type == ParserErrorCategoryChoices.FIELD_VALUE
        assert err.error_message == ("T4 Item 10: must be one of [1 2], got 3")
        assert err.content_type.model == "tanf_t4"
        assert err.object_id is not None

    @pytest.mark.django_db(transaction=True)()
    def test_go_parse_tanf_section3_file(self, tanf_section3_file, dfs):
        """Test parsing TANF Section 3 submission."""
        dfs.datafile = tanf_section3_file

        parse_datafile(dfs, tanf_section3_file)

        dfs.status = dfs.get_status()
        dfs.case_aggregates = aggregates.total_errors_by_month(dfs.datafile, dfs.status)
        parser_errors = ParserError.objects.filter(file=tanf_section3_file)

        assert dfs.case_aggregates == {
            "months": [
                {"month": "Oct", "total_errors": 0},
                {"month": "Nov", "total_errors": 0},
                {"month": "Dec", "total_errors": 0},
            ]
        }

        assert dfs.get_status() == DataFileSummary.Status.ACCEPTED

        assert TANF_T6.objects.filter(datafile=tanf_section3_file).count() == 3

        assert parser_errors.count() == 0

        t6_objs = TANF_T6.objects.filter(datafile=tanf_section3_file).order_by(
            "NUM_APPROVED"
        )

        first = t6_objs.first()
        second = t6_objs[1]
        third = t6_objs[2]

        assert first.RPT_MONTH_YEAR == 202112
        assert second.RPT_MONTH_YEAR == 202111
        assert third.RPT_MONTH_YEAR == 202110

        assert first.NUM_APPROVED == 3924
        assert second.NUM_APPROVED == 3977
        assert third.NUM_APPROVED == 4301

        assert first.NUM_CLOSED_CASES == 3884
        assert second.NUM_CLOSED_CASES == 3881
        assert third.NUM_CLOSED_CASES == 5453

    @pytest.mark.django_db(transaction=True)()
    def test_go_parse_tanf_section1_blanks_file(
        self, tanf_section1_file_with_blanks, dfs
    ):
        """Test section 1 fields that are allowed to have blanks."""
        dfs.datafile = tanf_section1_file_with_blanks
        dfs.save()

        parse_datafile(dfs, tanf_section1_file_with_blanks)

        parser_errors = ParserError.objects.filter(file=tanf_section1_file_with_blanks)

        assert parser_errors.count() == 23

        # Should only be cat3 validator errors
        for error in parser_errors:
            assert error.error_type == ParserErrorCategoryChoices.VALUE_CONSISTENCY

        t1 = TANF_T1.objects.filter(datafile=tanf_section1_file_with_blanks).first()
        t2 = TANF_T2.objects.filter(datafile=tanf_section1_file_with_blanks).first()
        t3 = TANF_T3.objects.filter(datafile=tanf_section1_file_with_blanks).first()

        assert t1.FAMILY_SANC_ADULT is None
        assert t2.MARITAL_STATUS is None
        assert t3.CITIZENSHIP_STATUS is None

    @pytest.mark.django_db(transaction=True)()
    def test_go_parse_tanf_section4_file(self, tanf_section4_file, dfs):
        """Test parsing TANF Section 4 submission."""
        dfs.datafile = tanf_section4_file

        parse_datafile(dfs, tanf_section4_file)

        dfs.status = dfs.get_status()
        dfs.case_aggregates = aggregates.total_errors_by_month(dfs.datafile, dfs.status)
        assert dfs.case_aggregates == {
            "months": [
                {"month": "Oct", "total_errors": 0},
                {"month": "Nov", "total_errors": 0},
                {"month": "Dec", "total_errors": 0},
            ]
        }

        assert dfs.get_status() == DataFileSummary.Status.ACCEPTED

        assert TANF_T7.objects.filter(datafile=tanf_section4_file).count() == 18

        parser_errors = ParserError.objects.filter(file=tanf_section4_file)
        assert parser_errors.count() == 0

        t7_objs = TANF_T7.objects.filter(datafile=tanf_section4_file).order_by(
            "FAMILIES_MONTH"
        )

        first = t7_objs.first()
        sixth = t7_objs[5]

        assert first.RPT_MONTH_YEAR == 202111
        assert sixth.RPT_MONTH_YEAR == 202112

        assert first.TDRS_SECTION_IND == "2"
        assert sixth.TDRS_SECTION_IND == "2"

        assert first.FAMILIES_MONTH == 274
        assert sixth.FAMILIES_MONTH == 499

    @pytest.mark.django_db(transaction=True)()
    def test_go_parse_bad_tanf_section4_file(self, bad_tanf_section4_file, dfs):
        """Test parsing TANF Section 4 submission when no records are created."""
        dfs.datafile = bad_tanf_section4_file

        parse_datafile(dfs, bad_tanf_section4_file)

        dfs.status = dfs.get_status()
        dfs.case_aggregates = aggregates.total_errors_by_month(dfs.datafile, dfs.status)

        assert dfs.case_aggregates == {
            "months": [
                {"month": "Oct", "total_errors": "N/A"},
                {"month": "Nov", "total_errors": "N/A"},
                {"month": "Dec", "total_errors": "N/A"},
            ]
        }

        assert dfs.get_status() == DataFileSummary.Status.REJECTED

        assert TANF_T7.objects.filter(datafile=bad_tanf_section4_file).count() == 0

        parser_errors = ParserError.objects.filter(
            file=bad_tanf_section4_file
        ).order_by("id")
        assert parser_errors.count() == 19

        error = parser_errors.first()
        # This check is now evaluated against every record that can be made against each schema segment. Thats why we
        # have 18 of them
        error.error_message == "Value length 151 does not match 247."
        error.error_type == ParserErrorCategoryChoices.PRE_CHECK

        error = parser_errors.last()
        error.error_message == "No records created."
        error.error_type == ParserErrorCategoryChoices.PRE_CHECK

    @pytest.mark.django_db(transaction=True)()
    def test_go_parse_ssp_section4_file(self, ssp_section4_file, dfs):
        """Test parsing SSP Section 4 submission."""
        dfs.datafile = ssp_section4_file

        parse_datafile(dfs, ssp_section4_file)

        m7_objs = SSP_M7.objects.filter(datafile=ssp_section4_file).order_by(
            "FAMILIES_MONTH"
        )

        dfs.status = dfs.get_status()
        dfs.case_aggregates = aggregates.total_errors_by_month(dfs.datafile, dfs.status)

        assert dfs.case_aggregates == {
            "months": [
                {"month": "Oct", "total_errors": 0},
                {"month": "Nov", "total_errors": 0},
                {"month": "Dec", "total_errors": 0},
            ]
        }

        assert m7_objs.count() == 12

        first = m7_objs.first()
        assert first.RPT_MONTH_YEAR == 202110
        assert first.FAMILIES_MONTH == 748

    @pytest.mark.django_db(transaction=True)()
    def test_go_parse_ssp_section2_rec_oadsi_file(
        self, ssp_section2_rec_oadsi_file, dfs
    ):
        """Test parsing SSP Section 2 REC_OADSI."""
        dfs.datafile = ssp_section2_rec_oadsi_file

        parse_datafile(dfs, ssp_section2_rec_oadsi_file)
        parser_errors = ParserError.objects.filter(file=ssp_section2_rec_oadsi_file)

        assert parser_errors.count() == 0

    @pytest.mark.django_db(transaction=True)()
    def test_go_parse_ssp_section2_file(self, ssp_section2_file, dfs):
        """Test parsing SSP Section 2 submission."""
        dfs.datafile = ssp_section2_file

        parse_datafile(dfs, ssp_section2_file)

        dfs.status = dfs.get_status()
        dfs.case_aggregates = aggregates.case_aggregates_by_month(
            dfs.datafile, dfs.status
        )
        for dfs_case_aggregate in dfs.case_aggregates["months"]:
            assert dfs_case_aggregate["accepted_without_errors"] == 0
            assert dfs_case_aggregate["accepted_with_errors"] in [75, 78]
            assert dfs_case_aggregate["month"] in ["Oct", "Nov", "Dec"]
        assert dfs.get_status() == DataFileSummary.Status.PARTIALLY_ACCEPTED

        m4_objs = SSP_M4.objects.filter(datafile=ssp_section2_file).order_by("id")
        m5_objs = SSP_M5.objects.filter(datafile=ssp_section2_file).order_by(
            "AMOUNT_EARNED_INCOME"
        )

        expected_m4_count = 231
        expected_m5_count = 703

        assert (
            SSP_M4.objects.filter(datafile=ssp_section2_file).count()
            == expected_m4_count
        )
        assert (
            SSP_M5.objects.filter(datafile=ssp_section2_file).count()
            == expected_m5_count
        )

        # Because the go parser inserts into tables in parallel we cant rely on ID ordering
        m4 = m4_objs.filter(DISPOSITION=1, REC_SUB_CC=3).first()
        assert m4.DISPOSITION == 1
        assert m4.REC_SUB_CC == 3

        m5 = m5_objs.filter(
            FAMILY_AFFILIATION=1,
            AMOUNT_EARNED_INCOME="0000",
            AMOUNT_UNEARNED_INCOME="0000",
        ).first()
        assert m5.FAMILY_AFFILIATION == 1
        assert m5.AMOUNT_EARNED_INCOME == "0000"
        assert m5.AMOUNT_UNEARNED_INCOME == "0000"

    @pytest.mark.django_db(transaction=True)()
    def test_go_parse_ssp_section3_file(self, ssp_section3_file, dfs):
        """Test parsing TANF Section 3 submission."""
        dfs.datafile = ssp_section3_file

        parse_datafile(dfs, ssp_section3_file)

        dfs.status = dfs.get_status()
        dfs.case_aggregates = aggregates.total_errors_by_month(dfs.datafile, dfs.status)
        assert dfs.case_aggregates == {
            "months": [
                {"month": "Oct", "total_errors": 0},
                {"month": "Nov", "total_errors": 0},
                {"month": "Dec", "total_errors": 0},
            ]
        }

        assert dfs.get_status() == DataFileSummary.Status.ACCEPTED

        m6_objs = SSP_M6.objects.filter(datafile=ssp_section3_file).order_by(
            "RPT_MONTH_YEAR"
        )
        assert m6_objs.count() == 3

        parser_errors = ParserError.objects.filter(file=ssp_section3_file)
        assert parser_errors.count() == 0

        first = m6_objs.first()
        second = m6_objs[1]
        third = m6_objs[2]

        assert first.RPT_MONTH_YEAR == 202110
        assert second.RPT_MONTH_YEAR == 202111
        assert third.RPT_MONTH_YEAR == 202112

        assert first.SSPMOE_FAMILIES == 15869
        assert second.SSPMOE_FAMILIES == 16008
        assert third.SSPMOE_FAMILIES == 15956

        assert first.NUM_RECIPIENTS == 51355
        assert second.NUM_RECIPIENTS == 51696
        assert third.NUM_RECIPIENTS == 51348

    @pytest.mark.django_db(transaction=True)
    def test_go_rpt_month_year_mismatch(self, header_datafile, dfs):
        """Test that the rpt_month_year mismatch error is raised."""
        datafile = header_datafile

        dfs.datafile = header_datafile
        dfs.save()

        parse_datafile(dfs, datafile)

        parser_errors = ParserError.objects.filter(file=datafile)

        # Three errors here because the go parser actually catches/throws another cat4 error that python doesn't catch.
        # Python only catches the T1 missing T2/T3 error. Go catches that and the "Every T1 record should have at least
        # one corresponding T2 or T3 record with FAMILY_AFFILIATION == 1" error.
        assert parser_errors.count() == 3
        assert (
            parser_errors.first().error_type
            == ParserErrorCategoryChoices.CASE_CONSISTENCY
        )

        datafile.year = 2023
        datafile.save()

        parse_datafile(dfs, datafile)

        parser_errors = ParserError.objects.filter(file=datafile).order_by("-id")
        # Then we get 2 more errors here because the Go parser catches the HEADER precheck error and rethrows the "no
        # records created" error. Python doesn't rethrow the no records created error for some reason.
        assert parser_errors.count() == 5

        msg = "Submitted reporting year:2020, quarter:Q4 doesn't match file reporting year:2023, quarter:Q1."
        err = parser_errors.get(error_message=msg)
        assert err.error_type == ParserErrorCategoryChoices.PRE_CHECK

    @pytest.mark.django_db(transaction=True)()
    def test_go_parse_tribal_section_1_file(self, tribal_section_1_file, dfs):
        """Test parsing Tribal TANF Section 1 submission."""
        tribal_section_1_file.year = 2022
        tribal_section_1_file.quarter = "Q1"
        tribal_section_1_file.save()

        dfs.datafile = tribal_section_1_file

        parse_datafile(dfs, tribal_section_1_file)

        dfs.status = dfs.get_status()
        assert dfs.status == DataFileSummary.Status.ACCEPTED
        dfs.case_aggregates = aggregates.case_aggregates_by_month(
            dfs.datafile, dfs.status
        )
        assert dfs.case_aggregates == {
            "rejected": 0,
            "months": [
                {
                    "month": "Oct",
                    "accepted_without_errors": 1,
                    "accepted_with_errors": 0,
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
        }

        assert (
            Tribal_TANF_T1.objects.filter(datafile=tribal_section_1_file).count() == 1
        )
        assert (
            Tribal_TANF_T2.objects.filter(datafile=tribal_section_1_file).count() == 1
        )
        assert (
            Tribal_TANF_T3.objects.filter(datafile=tribal_section_1_file).count() == 2
        )
        assert not ParserError.objects.filter(
            file=tribal_section_1_file,
            error_message__contains="Submitted program type",
        ).exists()

        t1_objs = Tribal_TANF_T1.objects.filter(
            datafile=tribal_section_1_file
        ).order_by("CASH_AMOUNT")
        t2_objs = Tribal_TANF_T2.objects.filter(
            datafile=tribal_section_1_file
        ).order_by("MONTHS_FED_TIME_LIMIT")
        t3_objs = Tribal_TANF_T3.objects.filter(
            datafile=tribal_section_1_file
        ).order_by("EDUCATION_LEVEL")

        t1 = t1_objs.first()
        t2 = t2_objs.first()
        t3 = t3_objs.last()

        assert t1.CASH_AMOUNT == 502
        assert t2.MONTHS_FED_TIME_LIMIT == "  0"
        assert t3.EDUCATION_LEVEL == "98"

    @pytest.mark.django_db(transaction=True)()
    def test_go_parse_tribal_section_1_inconsistency_file(
        self, tribal_section_1_inconsistency_file, dfs
    ):
        """Test parsing inconsistent Tribal TANF Section 1 submission."""
        parse_datafile(dfs, tribal_section_1_inconsistency_file)

        assert (
            Tribal_TANF_T1.objects.filter(
                datafile=tribal_section_1_inconsistency_file
            ).count()
            == 0
        )

        parser_errors = ParserError.objects.filter(
            file=tribal_section_1_inconsistency_file
        )
        # Extra error for no records created
        assert parser_errors.count() == 2

        assert (
            parser_errors.first().error_message
            == "Tribe Code (142) inconsistency with Program Type (TAN) "
            + "and FIPS Code (01)."
        )

    @pytest.mark.django_db(transaction=True)()
    def test_go_parse_tribal_section_2_file(self, tribal_section_2_file, dfs):
        """Test parsing Tribal TANF Section 2 submission."""
        tribal_section_2_file.year = 2020
        tribal_section_2_file.quarter = "Q1"
        tribal_section_2_file.save()

        dfs.datafile = tribal_section_2_file

        parse_datafile(dfs, tribal_section_2_file)

        dfs.status = dfs.get_status()
        dfs.case_aggregates = aggregates.case_aggregates_by_month(
            dfs.datafile, dfs.status
        )
        assert dfs.case_aggregates == {
            "rejected": 0,
            "months": [
                {
                    "accepted_without_errors": 3,
                    "accepted_with_errors": 0,
                    "month": "Oct",
                },
                {
                    "accepted_without_errors": 3,
                    "accepted_with_errors": 0,
                    "month": "Nov",
                },
                {
                    "accepted_without_errors": 0,
                    "accepted_with_errors": 0,
                    "month": "Dec",
                },
            ],
        }

        assert dfs.get_status() == DataFileSummary.Status.ACCEPTED

        assert (
            Tribal_TANF_T4.objects.filter(datafile=tribal_section_2_file).count() == 6
        )
        assert (
            Tribal_TANF_T5.objects.filter(datafile=tribal_section_2_file).count() == 13
        )

        t4_objs = Tribal_TANF_T4.objects.filter(
            datafile=tribal_section_2_file
        ).order_by("CLOSURE_REASON")
        t5_objs = Tribal_TANF_T5.objects.filter(
            datafile=tribal_section_2_file
        ).order_by("COUNTABLE_MONTH_FED_TIME")

        t4 = t4_objs.first()
        t5 = t5_objs.last()

        assert t4.CLOSURE_REASON == "15"
        assert t5.COUNTABLE_MONTH_FED_TIME == "  8"

    @pytest.mark.django_db(transaction=True)()
    def test_go_parse_tribal_section_3_file(self, tribal_section_3_file, dfs):
        """Test parsing Tribal TANF Section 3 submission."""
        tribal_section_3_file.year = 2022
        tribal_section_3_file.quarter = "Q1"
        tribal_section_3_file.save()

        dfs.datafile = tribal_section_3_file

        parse_datafile(dfs, tribal_section_3_file)

        dfs.status = dfs.get_status()
        dfs.case_aggregates = aggregates.total_errors_by_month(dfs.datafile, dfs.status)
        assert dfs.case_aggregates == {
            "months": [
                {"month": "Oct", "total_errors": 0},
                {"month": "Nov", "total_errors": 0},
                {"month": "Dec", "total_errors": 0},
            ]
        }

        assert dfs.get_status() == DataFileSummary.Status.ACCEPTED

        assert (
            Tribal_TANF_T6.objects.filter(datafile=tribal_section_3_file).count() == 3
        )

        t6_objs = Tribal_TANF_T6.objects.filter(
            datafile=tribal_section_3_file
        ).order_by("NUM_APPLICATIONS")

        t6 = t6_objs.first()

        assert t6.NUM_APPLICATIONS == 1
        assert t6.NUM_FAMILIES == 41
        assert t6.NUM_CLOSED_CASES == 3

    @pytest.mark.django_db(transaction=True)()
    def test_go_parse_tribal_section_4_file(self, tribal_section_4_file, dfs):
        """Test parsing Tribal TANF Section 4 submission."""
        tribal_section_4_file.year = 2022
        tribal_section_4_file.quarter = "Q1"
        tribal_section_4_file.save()

        dfs.datafile = tribal_section_4_file

        parse_datafile(dfs, tribal_section_4_file)

        dfs.status = dfs.get_status()
        dfs.case_aggregates = aggregates.total_errors_by_month(dfs.datafile, dfs.status)
        assert dfs.case_aggregates == {
            "months": [
                {"month": "Oct", "total_errors": 0},
                {"month": "Nov", "total_errors": 0},
                {"month": "Dec", "total_errors": 0},
            ]
        }

        assert (
            Tribal_TANF_T7.objects.filter(datafile=tribal_section_4_file).count() == 18
        )

        t7_objs = Tribal_TANF_T7.objects.filter(
            datafile=tribal_section_4_file
        ).order_by("FAMILIES_MONTH")

        first = t7_objs.first()
        sixth = t7_objs[5]

        assert first.RPT_MONTH_YEAR == 202111
        assert sixth.RPT_MONTH_YEAR == 202112

        assert first.TDRS_SECTION_IND == "2"
        assert sixth.TDRS_SECTION_IND == "2"

        assert first.FAMILIES_MONTH == 274
        assert sixth.FAMILIES_MONTH == 499

    # TODO: this requires more sophisticated segment based validation to gain parity with python parser. I made a test
    # branch `segment-validation-arch` to see what this could look like. Will explore other options and discuss with
    # dev team.
    # @pytest.mark.parametrize(
    #     "file_fixture, result, number_of_errors, error_message",
    #     [
    #         ("second_child_only_space_t3_file", 1, 0, ""),
    #         ("one_child_t3_file", 1, 0, ""),
    #         ("t3_file", 1, 0, ""),
    #         (
    #             "t3_file_two_child",
    #             1,
    #             1,
    #             "The second child record is too short at 97 characters"
    #             + " and must be at least 101 characters.",
    #         ),
    #         ("t3_file_two_child_with_space_filled", 2, 0, ""),
    #         (
    #             "two_child_second_filled",
    #             2,
    #             8,
    #             "T3 Item 68 (Date of Birth): Year 6    must be larger than 1900.",
    #         ),
    #         ("t3_file_zero_filled_second", 1, 0, ""),
    #     ],
    # )
    # @pytest.mark.django_db(transaction=True)()
    # def test_go_misformatted_multi_records(
    #     self,
    #     file_fixture, result, number_of_errors, error_message, request, dfs
    # ):
    #     """Test that (not space filled) multi-records are caught."""
    #     file_fixture = request.getfixturevalue(file_fixture)
    #     dfs.datafile = file_fixture
    #     parse_datafile(dfs, file_fixture)
    #     parser_errors = ParserError.objects.filter(file=file_fixture)
    #     t3 = TANF_T3.objects.all()
    #     assert t3.count() == result

    #     parser_errors = ParserError.objects.all()
    #     assert parser_errors.count() == number_of_errors
    #     if number_of_errors > 0:
    #         error_messages = [parser_error.error_message for parser_error in parser_errors]
    #         assert error_message in error_messages

    #     parser_errors = (
    #         ParserError.objects.all()
    #         .exclude(
    #             # exclude extraneous cat 4 errors
    #             error_type=ParserErrorCategoryChoices.CASE_CONSISTENCY
    #         )
    #         .exclude(error_message="No records created.")
    #     )

    #     assert parser_errors.count() == number_of_errors

    @pytest.mark.django_db(transaction=True)()
    def test_go_empty_t4_t5_values(self, t4_t5_empty_values, dfs):
        """Test that empty field values for un-required fields parse."""
        dfs.datafile = t4_t5_empty_values
        parse_datafile(dfs, t4_t5_empty_values)
        parser_errors = ParserError.objects.filter(file=t4_t5_empty_values)
        t4 = TANF_T4.objects.filter(datafile=t4_t5_empty_values)
        t5 = TANF_T5.objects.filter(datafile=t4_t5_empty_values)
        assert t4.count() == 1
        assert t4[0].STRATUM is None
        logger.info(t4[0].__dict__)
        assert t5.count() == 1
        assert parser_errors[0].error_message == (
            "T4 Item 10: must be one of [1 2], got 3"
        )

    # Had to create new fixture file for this test. The go parser evaluates group/cat4 errors first now. Because of that
    # we get a cat4 error which rejects the record and stops other validation before the DOB checks.
    @pytest.mark.django_db(transaction=True)()
    def test_go_parse_t2_invalid_dob(self, t2_go_invalid_dob_file, dfs):
        """Test parsing a TANF T2 record with an invalid DOB."""
        dfs.datafile = t2_go_invalid_dob_file
        dfs.save()

        parse_datafile(dfs, t2_go_invalid_dob_file)

        parser_errors = ParserError.objects.filter(
            file=t2_go_invalid_dob_file
        ).order_by("error_message")

        month_error = parser_errors[4]
        year_error = parser_errors[6]
        digits_error = parser_errors[5]

        assert month_error.error_message == "T2 Item 32: month must be 1-12"
        assert year_error.error_message == "T2 Item 32: year must be larger than 1900"
        assert digits_error.error_message == "T2 Item 32: must be numeric"

    @pytest.mark.django_db(transaction=True)()
    def test_go_parse_tanf_section4_file_with_errors(
        self, tanf_section_4_file_with_errors, dfs
    ):
        """Test parsing TANF Section 4 submission."""
        tanf_section_4_file_with_errors.year = 2022
        tanf_section_4_file_with_errors.quarter = "Q1"
        dfs.datafile = tanf_section_4_file_with_errors

        parse_datafile(dfs, tanf_section_4_file_with_errors)

        dfs.status = dfs.get_status()
        dfs.case_aggregates = aggregates.total_errors_by_month(dfs.datafile, dfs.status)
        assert dfs.case_aggregates == {
            "months": [
                {"month": "Oct", "total_errors": 2},
                {"month": "Nov", "total_errors": 3},
                {"month": "Dec", "total_errors": 2},
            ]
        }

        assert dfs.get_status() == DataFileSummary.Status.ACCEPTED_WITH_ERRORS

        assert (
            TANF_T7.objects.filter(datafile=tanf_section_4_file_with_errors).count()
            == 18
        )

        parser_errors = ParserError.objects.filter(file=tanf_section_4_file_with_errors)

        assert parser_errors.count() == 7

        t7_objs = TANF_T7.objects.filter(
            datafile=tanf_section_4_file_with_errors
        ).order_by("FAMILIES_MONTH")

        first = t7_objs.first()
        sixth = t7_objs[5]

        assert first.RPT_MONTH_YEAR == 202111
        assert sixth.RPT_MONTH_YEAR == 202110

        assert first.TDRS_SECTION_IND == "1"
        assert sixth.TDRS_SECTION_IND == "1"

        assert first.FAMILIES_MONTH == 0
        assert sixth.FAMILIES_MONTH == 446

    @pytest.mark.django_db(transaction=True)()
    def test_go_parse_no_records_file(self, no_records_file, dfs):
        """Test parsing TANF Section 4 submission."""
        dfs.datafile = no_records_file
        parse_datafile(dfs, no_records_file)

        dfs.status = dfs.get_status()
        assert dfs.status == DataFileSummary.Status.REJECTED

        errors = ParserError.objects.filter(file=no_records_file)

        assert errors.count() == 2

        trailer_count_error = (
            "The number of records in the TRAILER row count: 1, does not match "
            "the number of records detected in the file: 0."
        )
        count_error = errors.get(error_message=trailer_count_error)
        assert count_error.error_type == ParserErrorCategoryChoices.PRE_CHECK
        assert count_error.content_type is None
        assert count_error.object_id is None

        no_records_error = errors.get(error_message="No records created.")
        assert no_records_error.error_type == ParserErrorCategoryChoices.PRE_CHECK
        assert no_records_error.content_type is None
        assert no_records_error.object_id is None

    @pytest.mark.django_db(transaction=True)
    def test_go_parse_aggregates_rejected_datafile(
        self, aggregates_rejected_datafile, dfs
    ):
        """Test record rejection counting when record has more than one preparsing error."""
        dfs.datafile = aggregates_rejected_datafile

        parse_datafile(dfs, aggregates_rejected_datafile)

        dfs.status = dfs.get_status()
        assert dfs.status == DataFileSummary.Status.REJECTED
        dfs.case_aggregates = aggregates.case_aggregates_by_month(
            dfs.datafile, dfs.status
        )
        assert dfs.case_aggregates == {
            "months": [
                {
                    "month": "Oct",
                    "accepted_without_errors": "N/A",
                    "accepted_with_errors": "N/A",
                },
                {
                    "month": "Nov",
                    "accepted_without_errors": "N/A",
                    "accepted_with_errors": "N/A",
                },
                {
                    "month": "Dec",
                    "accepted_without_errors": "N/A",
                    "accepted_with_errors": "N/A",
                },
            ],
            "rejected": 1,
        }

        # Again, group validators run first in the go parser and block other non precheck validation results. So we get
        # more errors since we always capture cat1/cat4 errors with the go parser.
        errors = ParserError.objects.filter(file=aggregates_rejected_datafile).order_by(
            "id"
        )

        assert errors.count() == 5
        record_precheck_errors = errors.filter(row_number=2)
        assert record_precheck_errors.count() == 4
        for error in record_precheck_errors:
            assert error.error_type in [
                ParserErrorCategoryChoices.RECORD_PRE_CHECK,
                ParserErrorCategoryChoices.CASE_CONSISTENCY,
            ]

        assert errors.last().error_type == ParserErrorCategoryChoices.PRE_CHECK

        assert (
            TANF_T2.objects.filter(datafile=aggregates_rejected_datafile).count() == 0
        )

    @pytest.mark.django_db(transaction=True)()
    def test_go_parse_tanf_section_1_file_with_bad_update_indicator(
        self, tanf_section_1_file_with_bad_update_indicator, dfs
    ):
        """Test parsing TANF Section 1 submission update indicator."""
        dfs.datafile = tanf_section_1_file_with_bad_update_indicator

        parse_datafile(dfs, tanf_section_1_file_with_bad_update_indicator)

        parser_errors = ParserError.objects.filter(
            file=tanf_section_1_file_with_bad_update_indicator,
        )

        assert dfs.get_status() == DataFileSummary.Status.ACCEPTED_WITH_ERRORS

        assert parser_errors.count() == 5

        error_messages = [error.error_message for error in parser_errors]

        assert (
            "HEADER Update Indicator must be set to D instead of U. Please review"
            + " Exporting Complete Data Using FTANF in the Knowledge Center."
            in error_messages
        )

    @pytest.mark.django_db(transaction=True)()
    def test_go_parse_tribal_section_4_bad_quarter(
        self, tribal_section_4_bad_quarter, dfs
    ):
        """Test handling invalid quarter value that raises a ValueError exception."""
        tribal_section_4_bad_quarter.year = 2021
        tribal_section_4_bad_quarter.quarter = "Q1"
        tribal_section_4_bad_quarter.save()
        dfs.datafile = tribal_section_4_bad_quarter

        parse_datafile(dfs, tribal_section_4_bad_quarter)
        parser_errors = ParserError.objects.filter(
            file=tribal_section_4_bad_quarter
        ).order_by("id")

        # We get 37 errors because go treats schema precheck validators as independent over each record/segment whereas
        # Python validates based on the raw row. There is a ticket in the backlog to enable go to behave like Python if
        # we want/need.
        assert parser_errors.count() == 37

        parser_errors.first().error_message == (
            "T7: 2020  is invalid. Calendar Quarter must be a numeric "
            "representing the Calendar Year and Quarter formatted as YYYYQ"
        )

        assert (
            Tribal_TANF_T7.objects.filter(datafile=tribal_section_4_bad_quarter).count()
            == 0
        )

    @pytest.mark.django_db(transaction=True)()
    def test_go_parse_t3_cat2_invalid_citizenship(
        self, t3_cat2_invalid_citizenship_file, dfs
    ):
        """Test parsing a TANF T3 record with an invalid CITIZENSHIP_STATUS."""
        dfs.datafile = t3_cat2_invalid_citizenship_file
        dfs.save()

        parse_datafile(dfs, t3_cat2_invalid_citizenship_file)

        exclusion = Query(
            error_type=ParserErrorCategoryChoices.CASE_CONSISTENCY
        ) | Query(error_type=ParserErrorCategoryChoices.PRE_CHECK)

        parser_errors = (
            ParserError.objects.filter(file=t3_cat2_invalid_citizenship_file)
            .exclude(exclusion)
            .order_by("pk")
        )

        # no errors expected as fields are not required
        assert parser_errors.count() == 0

    @pytest.mark.django_db(transaction=True)()
    def test_go_parse_m2_cat2_invalid_37_38_39_file(
        self, m2_cat2_invalid_37_38_39_file, dfs
    ):
        """Test parsing an SSP M2 file with an invalid EDUCATION_LEVEL, CITIZENSHIP_STATUS, COOPERATION_CHILD_SUPPORT."""
        dfs.datafile = m2_cat2_invalid_37_38_39_file
        m2_cat2_invalid_37_38_39_file.year = 2024
        m2_cat2_invalid_37_38_39_file.quarter = "Q1"
        dfs.save()

        parse_datafile(dfs, m2_cat2_invalid_37_38_39_file)

        exclusion = Query(
            error_type=ParserErrorCategoryChoices.CASE_CONSISTENCY
        ) | Query(error_type=ParserErrorCategoryChoices.PRE_CHECK)

        parser_errors = (
            ParserError.objects.filter(file=m2_cat2_invalid_37_38_39_file)
            .exclude(exclusion)
            .order_by("pk")
        )

        # no errors expected as fields are not required
        assert parser_errors.count() == 0

    # Had to create custom fixture here also since cat4 validation blocks the original fixture from ever hitting
    # cat2/3 validation
    @pytest.mark.django_db(transaction=True)()
    def test_go_parse_m3_cat2_invalid_68_69_file(
        self, m3_go_cat2_invalid_68_69_file, dfs
    ):
        """Test parsing an SSP M3 file with an invalid EDUCATION_LEVEL and CITIZENSHIP_STATUS."""
        dfs.datafile = m3_go_cat2_invalid_68_69_file
        dfs.save()

        parse_datafile(dfs, m3_go_cat2_invalid_68_69_file)

        exclusion = Query(
            error_type=ParserErrorCategoryChoices.CASE_CONSISTENCY
        ) | Query(error_type=ParserErrorCategoryChoices.PRE_CHECK)

        parser_errors = (
            ParserError.objects.filter(file=m3_go_cat2_invalid_68_69_file)
            .exclude(exclusion)
            .order_by("pk")
        )

        # One extra error for the new M1 record in the new fixture
        assert parser_errors.count() == 3
        for e in parser_errors[1:]:
            assert e.error_message == "M3 Item 68: must be 1-16 or 98-99, got 00"

    # Note: this says there should be failures but the python test originally also showed no errors?
    @pytest.mark.django_db(transaction=True)()
    def test_go_parse_m5_cat2_invalid_23_24_file(
        self, m5_go_cat2_invalid_23_24_file, dfs
    ):
        """Test parsing an SSP M5 file with an invalid EDUCATION_LEVEL and CITIZENSHIP_STATUS."""
        dfs.datafile = m5_go_cat2_invalid_23_24_file
        dfs.save()

        parse_datafile(dfs, m5_go_cat2_invalid_23_24_file)

        exclusion = Query(
            error_type=ParserErrorCategoryChoices.CASE_CONSISTENCY
        ) | Query(error_type=ParserErrorCategoryChoices.PRE_CHECK)

        parser_errors = (
            ParserError.objects.filter(file=m5_go_cat2_invalid_23_24_file)
            .exclude(exclusion)
            .order_by("pk")
        )

        assert parser_errors.count() == 0

    @pytest.mark.django_db(transaction=True)()
    def test_go_zero_filled_fips_code_file(self, test_file_zero_filled_fips_code, dfs):
        """Test parsing a file with zero filled FIPS code."""
        dfs.datafile = test_file_zero_filled_fips_code
        test_file_zero_filled_fips_code.save()

        parse_datafile(dfs, test_file_zero_filled_fips_code)

        parser_errors = ParserError.objects.filter(file=test_file_zero_filled_fips_code)

        assert (
            "T1 Item 2 (County FIPS Code): field is required but a value was not"
            + " provided."
            in [i.error_message for i in parser_errors]
        )

    @pytest.mark.parametrize(
        "file",
        [
            ("fra_bad_header_csv"),
            ("fra_bad_header_xlsx"),
        ],
    )
    @pytest.mark.django_db(transaction=True)()
    def test_go_parse_fra_bad_header(self, request, file, dfs):
        """Test parsing FRA files with bad header data."""
        datafile = request.getfixturevalue(file)
        datafile.year = 2024
        datafile.quarter = "Q1"
        datafile.version = datafile.pk
        datafile.save()

        dfs.datafile = datafile
        dfs.save()

        parse_datafile(dfs, datafile)

        assert TANF_Exiter1.objects.filter(datafile=datafile).count() == 0

        errors = ParserError.objects.filter(file=datafile).order_by("id")
        assert len(errors) == 1
        for e in errors:
            assert e.error_message == "File does not begin with FRA data."
            assert e.error_type == ParserErrorCategoryChoices.PRE_CHECK
        assert dfs.get_status() == DataFileSummary.Status.REJECTED

    @pytest.mark.parametrize(
        "file",
        [
            ("fra_empty_first_row_csv"),
            ("fra_empty_first_row_xlsx"),
        ],
    )
    @pytest.mark.django_db(transaction=True)()
    def test_go_parse_fra_empty_first_row(self, request, file, dfs):
        """Test parsing FRA files with an empty first row/no header data."""
        datafile = request.getfixturevalue(file)
        datafile.year = 2024
        datafile.quarter = "Q1"
        datafile.version = datafile.pk

        dfs.datafile = datafile
        dfs.save()

        parse_datafile(dfs, datafile)

        assert TANF_Exiter1.objects.filter(datafile=datafile).count() == 0

        errors = ParserError.objects.filter(file=datafile).order_by("id")
        assert len(errors) == 1
        for e in errors:
            assert e.error_message == "File does not begin with FRA data."
            assert e.error_type == ParserErrorCategoryChoices.PRE_CHECK
        assert dfs.get_status() == DataFileSummary.Status.REJECTED

    @pytest.mark.parametrize(
        "file",
        [
            ("fra_work_outcome_exiter_csv_file"),
            ("fra_work_outcome_exiter_xlsx_file"),
        ],
    )
    @pytest.mark.django_db(transaction=True)
    def test_go_parse_fra_work_outcome_exiters(self, request, file, dfs):
        """Test parsing FRA Work Outcome Exiters files."""
        datafile = request.getfixturevalue(file)
        datafile.year = 2024
        datafile.quarter = "Q2"
        datafile.version = datafile.pk
        datafile.save()

        dfs.datafile = datafile
        dfs.save()

        parse_datafile(dfs, datafile)
        errors = ParserError.objects.filter(file=datafile).order_by("id")

        assert TANF_Exiter1.objects.filter(datafile=datafile).count() == 5

        errors = ParserError.objects.filter(file=datafile).order_by("id")
        assert errors.count() == 8
        for e in errors:
            assert e.error_type == ParserErrorCategoryChoices.CASE_CONSISTENCY
        # TODO: need to update go parser to handle updating the DFS' record counts
        # assert dfs.total_number_of_records_in_file == 11
        # assert dfs.total_number_of_records_created == 5
        assert dfs.get_status() == DataFileSummary.Status.PARTIALLY_ACCEPTED

    @pytest.mark.parametrize(
        "file",
        [
            ("fra_ofa_test_csv"),
            ("fra_ofa_test_xlsx"),
        ],
    )
    @pytest.mark.django_db(transaction=True)
    def test_go_parse_fra_ofa_test_cases(self, request, file, dfs):
        """Test parsing OFA FRA files."""
        datafile = request.getfixturevalue(file)
        datafile.year = 2025
        datafile.quarter = "Q3"
        datafile.version = datafile.pk
        datafile.save()

        dfs.datafile = datafile
        dfs.save()

        parse_datafile(dfs, datafile)

        errors = ParserError.objects.filter(file=datafile).order_by("row_number")
        for e in errors:
            assert e.error_type == ParserErrorCategoryChoices.CASE_CONSISTENCY

        # We get one extra duplicate that the Python parser doesn't detect! The Python parser hasn't been catching that
        # line 13 is a duplicate of line 3
        assert errors.count() == 24
        assert TANF_Exiter1.objects.filter(datafile=datafile).count() == 8
        # assert dfs.total_number_of_records_in_file == 28
        # assert dfs.total_number_of_records_created == 10
        assert dfs.get_status() == DataFileSummary.Status.PARTIALLY_ACCEPTED

    @pytest.mark.django_db(transaction=True)
    # TODO: Failing
    def test_go_parse_fra_formula_fields(self, fra_formula_fields_test_xlsx, dfs):
        """Test parsing a correct FRA file with formula fields."""
        datafile = fra_formula_fields_test_xlsx
        datafile.year = 2025
        datafile.quarter = "Q3"
        datafile.version = datafile.pk
        datafile.save()

        dfs.datafile = datafile
        dfs.save()

        parse_datafile(dfs, datafile)

        errors = ParserError.objects.filter(file=datafile).order_by("id")
        assert errors.count() == 0
        assert TANF_Exiter1.objects.filter(datafile=datafile).count() == 8
        # See above TODO
        # assert dfs.total_number_of_records_in_file == 8
        # assert dfs.total_number_of_records_created == 8
        assert dfs.get_status() == DataFileSummary.Status.ACCEPTED

    @pytest.mark.django_db(transaction=True)()
    def test_go_parse_fra_decoder_unknown(self, fra_decoder_unknown, dfs):
        """Test parsing a FRA file with bad encoding."""
        datafile = fra_decoder_unknown
        datafile.year = 2025
        datafile.quarter = "Q3"
        datafile.version = datafile.pk
        datafile.save()

        dfs.datafile = datafile
        dfs.save()

        parse_datafile(dfs, datafile)

        errors = ParserError.objects.filter(file=datafile).order_by("id")
        assert errors.count() == 1
        assert errors.first().error_type == ParserErrorCategoryChoices.PRE_CHECK
        assert errors.first().error_message == (
            "Could not determine encoding of FRA file. If the file is an XLSX file, "
            "ensure it can be opened in Excel. If the file is a CSV, ensure it can be "
            "opened in a text editor and is UTF-8 encoded."
        )
        assert dfs.get_status() == DataFileSummary.Status.REJECTED

    @pytest.mark.django_db(transaction=True)()
    def test_go_parse_section2_no_records(self, section2_no_records, dfs):
        """Test parsing valid section 2 file with no records."""
        datafile = section2_no_records
        dfs.datafile = datafile
        dfs.save()

        parse_datafile(dfs, datafile)

        errors = ParserError.objects.filter(file=datafile)
        assert errors.count() == 0
        assert dfs.get_status() == DataFileSummary.Status.ACCEPTED

    @pytest.mark.django_db(transaction=True)
    def test_go_parse_tanf_s1_federally_funded_recipients(
        self, tanf_s1_federally_funded_recipients, dfs
    ):
        """Test parsing file that generates the tanf_s1_federally_funded_recipients error."""
        dfs.datafile = tanf_s1_federally_funded_recipients

        parse_datafile(dfs, tanf_s1_federally_funded_recipients)

        errors = ParserError.objects.filter(
            file=tanf_s1_federally_funded_recipients
        ).order_by("error_message")

        dfs.status = dfs.get_status()
        assert dfs.status == DataFileSummary.Status.ACCEPTED_WITH_ERRORS
        assert errors.first().error_message == (
            "Federally funded recipients must have a valid Social Security number."
        )

    @pytest.mark.django_db(transaction=True)
    def test_go_parse_case_aggregates_edge_case(self, case_aggregates_edge_case, dfs):
        """Test parsing of cases_across_months_with_error.txt."""
        case_aggregates_edge_case.year = 2026
        case_aggregates_edge_case.quarter = "Q1"
        case_aggregates_edge_case.save()

        dfs.datafile = case_aggregates_edge_case

        parse_datafile(dfs, case_aggregates_edge_case)

        dfs.status = dfs.get_status()
        assert dfs.status == DataFileSummary.Status.PARTIALLY_ACCEPTED

        dfs.case_aggregates = aggregates.case_aggregates_by_month(
            dfs.datafile, dfs.status
        )

        assert dfs.case_aggregates == {
            "months": [
                {
                    "month": "Oct",
                    "accepted_without_errors": 1,
                    "accepted_with_errors": 0,
                },
                {
                    "month": "Nov",
                    "accepted_without_errors": 1,
                    "accepted_with_errors": 0,
                },
                {
                    "month": "Dec",
                    "accepted_without_errors": 0,
                    "accepted_with_errors": 1,
                },
            ],
            "rejected": 2,
        }

        assert TANF_T1.objects.filter(datafile=case_aggregates_edge_case).count() == 3
        assert TANF_T2.objects.filter(datafile=case_aggregates_edge_case).count() == 3
        assert TANF_T3.objects.filter(datafile=case_aggregates_edge_case).count() == 6

    @pytest.mark.django_db(transaction=True)
    @pytest.mark.skip(reason="long runtime")
    def test_go_parse_super_big_s1_file(self, super_big_s1_file, dfs):
        """Test parsing super_big_s1_file and validate all records are created."""
        super_big_s1_file.year = 2023
        super_big_s1_file.quarter = "Q2"
        super_big_s1_file.version = super_big_s1_file.pk
        super_big_s1_file.save()

        dfs.datafile = super_big_s1_file
        dfs.save()

        parse_datafile(
            dfs,
            super_big_s1_file,
            timeout_seconds=GO_PARSE_LARGE_FILE_TIMEOUT_SECONDS,
        )
        expected_t1_record_count = 96497
        expected_t2_record_count = 112622
        expected_t3_record_count = 172552

        assert (
            TANF_T1.objects.filter(datafile=super_big_s1_file).count()
            == expected_t1_record_count
        )
        assert (
            TANF_T2.objects.filter(datafile=super_big_s1_file).count()
            == expected_t2_record_count
        )
        assert (
            TANF_T3.objects.filter(datafile=super_big_s1_file).count()
            == expected_t3_record_count
        )

    @pytest.mark.django_db(transaction=True)
    def test_go_parse_big_s1_file_with_rollback(self, big_s1_rollback_file, dfs):
        """Test parsing big_s1_rollback_file with rollback on error."""
        big_s1_rollback_file.year = 2023
        big_s1_rollback_file.quarter = "Q2"
        big_s1_rollback_file.version = big_s1_rollback_file.pk
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

        assert TANF_T1.objects.filter(datafile=big_s1_rollback_file).count() == 0
        assert TANF_T2.objects.filter(datafile=big_s1_rollback_file).count() == 0
        assert TANF_T3.objects.filter(datafile=big_s1_rollback_file).count() == 0

    @pytest.mark.parametrize(
        "file, batch_size, model, record_type, num_errors",
        [
            ("tanf_s1_exact_dup_file", 10000, TANF_T1, "T1", 5),
            ("tanf_s1_exact_dup_file", 1, TANF_T1, "T1", 5),
            ("tanf_s2_exact_dup_file", 10000, TANF_T4, "T4", 3),
            ("tanf_s2_exact_dup_file", 1, TANF_T4, "T4", 3),
            ("tanf_s3_exact_dup_file", 10000, TANF_T6, "T6", 3),
            ("tanf_s3_exact_dup_file", 1, TANF_T6, "T6", 3),
            ("tanf_s4_exact_dup_file", 10000, TANF_T7, "T7", 18),
            ("tanf_s4_exact_dup_file", 1, TANF_T7, "T7", 18),
            ("ssp_s1_exact_dup_file", 10000, SSP_M1, "M1", 5),
            ("ssp_s1_exact_dup_file", 1, SSP_M1, "M1", 5),
            ("ssp_s2_exact_dup_file", 10000, SSP_M4, "M4", 3),
            ("ssp_s2_exact_dup_file", 1, SSP_M4, "M4", 3),
            ("ssp_s3_exact_dup_file", 10000, SSP_M6, "M6", 3),
            ("ssp_s3_exact_dup_file", 1, SSP_M6, "M6", 3),
            ("ssp_s4_exact_dup_file", 10000, SSP_M7, "M7", 12),
            ("ssp_s4_exact_dup_file", 1, SSP_M7, "M7", 12),
        ],
    )
    @pytest.mark.django_db(transaction=True)
    def test_go_parse_duplicate(
        self, file, batch_size, model, record_type, num_errors, dfs, request
    ):
        """Test cases for datafiles that have exact duplicate records."""
        datafile = request.getfixturevalue(file)
        datafile.version = datafile.pk
        datafile.save()
        dfs.datafile = datafile

        parse_datafile(dfs, datafile)

        parser_errors = ParserError.objects.filter(
            file=datafile, error_type=ParserErrorCategoryChoices.CASE_CONSISTENCY
        ).order_by("error_message")

        for e in parser_errors:
            assert e.error_type == ParserErrorCategoryChoices.CASE_CONSISTENCY
        assert parser_errors.count() == num_errors

        dup_error = parser_errors.first()

        assert (
            dup_error.error_message
            == f"Duplicate record detected with record type {record_type} at line 3. Record is a duplicate of the record at line number 2."
        )

        assert model.objects.filter(datafile=datafile).count() == 0

    @pytest.mark.parametrize(
        "file, batch_size, model, record_type, num_errors, err_msg",
        [
            (
                "tanf_s1_partial_dup_file",
                10000,
                TANF_T1,
                "T1",
                5,
                "Partial duplicate record detected with record type T1 at line 3.",
            ),
            (
                "tanf_s1_partial_dup_file",
                1,
                TANF_T1,
                "T1",
                5,
                "Partial duplicate record detected with record type T1 at line 3.",
            ),
            (
                "tanf_s2_partial_dup_file",
                10000,
                TANF_T5,
                "T5",
                3,
                "Partial duplicate record detected with record type T5 at line 3.",
            ),
            (
                "tanf_s2_partial_dup_file",
                1,
                TANF_T5,
                "T5",
                3,
                "Partial duplicate record detected with record type T5 at line 3.",
            ),
            (
                "ssp_s1_partial_dup_file",
                10000,
                SSP_M1,
                "M1",
                5,
                "Partial duplicate record detected with record type M1 at line 3.",
            ),
            (
                "ssp_s1_partial_dup_file",
                1,
                SSP_M1,
                "M1",
                5,
                "Partial duplicate record detected with record type M1 at line 3.",
            ),
            (
                "ssp_s2_partial_dup_file",
                10000,
                SSP_M5,
                "M5",
                3,
                "Partial duplicate record detected with record type M5 at line 3.",
            ),
            (
                "ssp_s2_partial_dup_file",
                1,
                SSP_M5,
                "M5",
                3,
                "Partial duplicate record detected with record type M5 at line 3.",
            ),
        ],
    )
    @pytest.mark.django_db(transaction=True)
    def test_go_parse_partial_duplicate(
        self, file, batch_size, model, record_type, num_errors, err_msg, dfs, request
    ):
        """Test cases for datafiles that have partial duplicate records."""
        datafile = request.getfixturevalue(file)
        datafile.version = datafile.pk
        datafile.save()
        expected_error_msg = err_msg

        dfs.datafile = datafile

        parse_datafile(dfs, datafile)

        parser_errors = ParserError.objects.filter(
            file=datafile, error_type=ParserErrorCategoryChoices.CASE_CONSISTENCY
        ).order_by("-error_message")
        for e in parser_errors:
            assert e.error_type == ParserErrorCategoryChoices.CASE_CONSISTENCY
        assert parser_errors.count() == num_errors

        dup_error = parser_errors.first()
        assert (
            expected_error_msg.format(record_type=record_type)
            in dup_error.error_message
        )

        assert model.objects.filter(datafile=datafile).count() == 0

    @pytest.mark.django_db(transaction=True)
    def test_go_parse_cat_4_edge_case_file(self, cat4_edge_case_file, dfs):
        """Test parsing file with a cat4 error edge case submission."""
        cat4_edge_case_file.year = 2024
        cat4_edge_case_file.quarter = "Q1"
        cat4_edge_case_file.save()

        dfs.datafile = cat4_edge_case_file
        dfs.save()

        parse_datafile(dfs, cat4_edge_case_file)

        parser_errors = (
            ParserError.objects.filter(file=cat4_edge_case_file)
            .filter(error_type=ParserErrorCategoryChoices.CASE_CONSISTENCY)
            .order_by("row_number", "id")
        )

        assert TANF_T1.objects.filter(datafile=cat4_edge_case_file).count() == 2
        assert TANF_T2.objects.filter(datafile=cat4_edge_case_file).count() == 2
        assert TANF_T3.objects.filter(datafile=cat4_edge_case_file).count() == 4

        # TODO
        # assert dfs.total_number_of_records_in_file == 17
        # assert dfs.total_number_of_records_created == 8

        err = parser_errors.first()
        assert err.error_message == (
            "Every T1 record should have at least one corresponding T2 or T3 record "
            "with the same RPT_MONTH_YEAR and CASE_NUMBER"
        )
        assert dfs.get_status() == DataFileSummary.Status.PARTIALLY_ACCEPTED
