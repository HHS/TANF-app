"""Test the implementation of the parse_file method with realistic datafiles."""

import logging
from django.conf import settings
from django.db.models import Q as Query

import pytest

from tdpservice.parsers import aggregates, util
from tdpservice.parsers.test.helpers import parse_datafile
from tdpservice.parsers.models import (
    DataFileSummary,
    ParserError,
    ParserErrorCategoryChoices,
)
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

settings.GENERATE_TRAILER_ERRORS = True
# TODO: the name of this test doesn't make perfect sense anymore since it will always have errors now.
# TODO: parametrize and merge with test_zero_filled_fips_code_file


class TestParse:
    """Tests for parse and validation flows."""

    @pytest.fixture
    def parsed_small_correct_file(self, small_correct_file, dfs):
        """Return parsed small_correct_file and its DataFileSummary."""
        small_correct_file.year = 2021
        small_correct_file.quarter = "Q1"
        small_correct_file.save()

        parse_datafile(dfs, small_correct_file)

        return small_correct_file, dfs

    @pytest.fixture
    def parsed_bad_trailer_file(self, bad_trailer_file, dfs):
        """Return parsed bad_trailer_file and its errors."""
        bad_trailer_file.year = 2021
        bad_trailer_file.quarter = "Q1"

        parse_datafile(dfs, bad_trailer_file)

        parser_errors = ParserError.objects.filter(file=bad_trailer_file)
        return bad_trailer_file, dfs, parser_errors

    @pytest.fixture
    def parsed_bad_trailer_file_2(self, bad_trailer_file_2, dfs):
        """Return parsed bad_trailer_file_2 and its errors."""
        dfs.datafile = bad_trailer_file_2
        dfs.save()

        bad_trailer_file_2.year = 2021
        bad_trailer_file_2.quarter = "Q1"

        parse_datafile(dfs, bad_trailer_file_2)

        parser_errors = ParserError.objects.filter(file=bad_trailer_file_2)
        return bad_trailer_file_2, dfs, parser_errors

    @pytest.mark.django_db
    def test_small_correct_file_case_consistency_error(
        self, parsed_small_correct_file
    ):
        """Test case consistency errors are recorded for small_correct_file."""
        datafile, _dfs = parsed_small_correct_file
        errors = ParserError.objects.filter(file=datafile).order_by("id")
        assert errors.count() == 2
        assert errors.first().error_type == ParserErrorCategoryChoices.CASE_CONSISTENCY

    @pytest.mark.django_db
    def test_small_correct_file_case_aggregates_rejected(
        self, parsed_small_correct_file
    ):
        """Test case aggregates for rejected small_correct_file."""
        _datafile, dfs = parsed_small_correct_file
        dfs.status = dfs.get_status()
        dfs.case_aggregates = aggregates.case_aggregates_by_month(dfs.datafile, dfs.status)
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

    @pytest.mark.django_db
    def test_small_correct_file_no_records_created(self, parsed_small_correct_file):
        """Test that small_correct_file does not create records when rejected."""
        _datafile, _dfs = parsed_small_correct_file
        assert TANF_T1.objects.count() == 0

    @pytest.mark.django_db
    @pytest.mark.parametrize(
        "section, expected_message, expected_aggregates, save_dfs",
        [
            (
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
            ),
            (
                "SSP Active Case Data",
                "Data does not match the expected layout for "
                "SSP Active Case Data.",
                None,
                True,
            ),
        ],
    )
    def test_parse_section_mismatch_variants(
        self,
        small_correct_file,
        dfs,
        section,
        expected_message,
        expected_aggregates,
        save_dfs,
    ):
        """Test parsing when file metadata does not match the raw data layout."""
        small_correct_file.section = section
        small_correct_file.save()

        dfs.datafile = small_correct_file
        if save_dfs:
            dfs.save()

        parse_datafile(dfs, small_correct_file)

        dfs.status = dfs.get_status()
        assert dfs.status == DataFileSummary.Status.REJECTED
        parser_errors = ParserError.objects.filter(file=small_correct_file)
        assert parser_errors.count() == 1

        if expected_aggregates is not None:
            dfs.case_aggregates = aggregates.case_aggregates_by_month(
                dfs.datafile, dfs.status
            )
            assert dfs.case_aggregates == expected_aggregates

        err = parser_errors.first()
        assert err.row_number == 1
        assert err.error_type == ParserErrorCategoryChoices.PRE_CHECK
        assert err.error_message == expected_message
        assert err.content_type is None
        assert err.object_id is None

    @pytest.mark.django_db
    @pytest.mark.parametrize(
        "fixture_name, updates, expected",
        [
            (
                "bad_test_file",
                {},
                {
                    "count": 1,
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
                    "error_message": (
                        "HEADER: record length is 14 characters but must be 23."
                    ),
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
    def test_parse_precheck_header_errors(self, request, fixture_name, updates, expected, dfs):
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

    @pytest.mark.django_db
    def test_bad_trailer_file_trailer_error(self, parsed_bad_trailer_file):
        """Test trailer errors for bad_trailer_1."""
        _datafile, _dfs, parser_errors = parsed_bad_trailer_file
        assert parser_errors.count() == 5

        trailer_error = parser_errors.get(row_number=3)
        assert trailer_error.error_type == ParserErrorCategoryChoices.RECORD_PRE_CHECK
        assert (
            trailer_error.error_message
            == "TRAILER: record length is 11 characters but must be 23."
        )
        assert trailer_error.content_type is None
        assert trailer_error.object_id is None

    @pytest.mark.django_db
    def test_bad_trailer_file_row_errors(self, parsed_bad_trailer_file):
        """Test row-level errors for bad_trailer_1."""
        _datafile, _dfs, parser_errors = parsed_bad_trailer_file

        # reporting month/year test
        row_errors = parser_errors.filter(row_number=2)
        row_errors_list = []
        for row_error in row_errors:
            row_errors_list.append(row_error)
            assert row_error.error_type == ParserErrorCategoryChoices.RECORD_PRE_CHECK
            assert row_error.error_message in [
                "TRAILER: record length is 11 characters but must be 23.",
                "T1: Case number T1trash cannot contain blanks.",
                "T1: record length should be at least 117 characters but it is 7 characters.",
                "T1: Reporting month year None does not match file reporting year:2021, quarter:Q1.",
            ]
            assert row_error.content_type is None
            assert row_error.object_id is None

        row_errors = list(parser_errors.filter(row_number=2).order_by("id"))
        length_error = row_errors[0]
        assert length_error.error_type == ParserErrorCategoryChoices.RECORD_PRE_CHECK
        assert (
            length_error.error_message
            == "T1: record length should be at least 117 characters but it is 7 characters."
        )
        assert length_error.content_type is None
        assert length_error.object_id is None

    @pytest.mark.django_db
    def test_bad_trailer_file2_trailer_errors(self, parsed_bad_trailer_file_2):
        """Test trailer errors for bad_trailer_2."""
        _datafile, _dfs, parser_errors = parsed_bad_trailer_file_2
        assert parser_errors.count() == 9

        parser_errors = parser_errors.exclude(
            error_type=ParserErrorCategoryChoices.CASE_CONSISTENCY
        )
        trailer_errors = list(parser_errors.filter(row_number=3).order_by("id"))

        trailer_error_1 = trailer_errors[0]
        assert trailer_error_1.error_type == ParserErrorCategoryChoices.RECORD_PRE_CHECK
        assert (
            trailer_error_1.error_message
            == "TRAILER: record length is 7 characters but must be 23."
        )
        assert trailer_error_1.content_type is None
        assert trailer_error_1.object_id is None

        trailer_error_2 = trailer_errors[1]
        assert trailer_error_2.error_type == ParserErrorCategoryChoices.RECORD_PRE_CHECK
        assert (
            trailer_error_2.error_message
            == "Your file does not end with a TRAILER record."
        )
        assert trailer_error_2.content_type is None
        assert trailer_error_2.object_id is None

    @pytest.mark.django_db
    def test_bad_trailer_file2_row_2_error(self, parsed_bad_trailer_file_2):
        """Test row 2 validation error for bad_trailer_2."""
        _datafile, _dfs, parser_errors = parsed_bad_trailer_file_2

        parser_errors = parser_errors.exclude(
            error_type=ParserErrorCategoryChoices.CASE_CONSISTENCY
        )
        row_2_errors = parser_errors.filter(row_number=2).order_by("id")
        row_2_error = row_2_errors.first()
        assert row_2_error.error_type == ParserErrorCategoryChoices.FIELD_VALUE
        assert row_2_error.error_message == (
            "T1 Item 13 (Receives Subsidized Housing): 3 is not in range [1, 2]."
        )

    @pytest.mark.django_db
    def test_bad_trailer_file2_row_3_errors(self, parsed_bad_trailer_file_2):
        """Test row 3 errors and case number validation for bad_trailer_2."""
        _datafile, _dfs, parser_errors = parsed_bad_trailer_file_2

        parser_errors = parser_errors.exclude(
            error_type=ParserErrorCategoryChoices.CASE_CONSISTENCY
        )
        trailer_errors = list(parser_errors.filter(row_number=3).order_by("id"))

        # catch-rpt-month-year-mismatches
        row_3_errors = parser_errors.filter(row_number=3)
        row_3_error_list = []

        for row_3_error in row_3_errors:
            row_3_error_list.append(row_3_error)
            assert row_3_error.error_type == ParserErrorCategoryChoices.RECORD_PRE_CHECK
            assert row_3_error.error_message in {
                "T1: record length should be at least 117 characters but it is 7 characters.",
                "T1: Reporting month year None does not match file reporting year:2021, quarter:Q1.",
                "TRAILER: record length is 7 characters but must be 23.",
                "T1: Case number T1trash cannot contain blanks.",
                "Your file does not end with a TRAILER record.",
            }
            assert row_3_error.content_type is None
            assert row_3_error.object_id is None

        # case number validators
        row_3_errors = [trailer_errors[2], trailer_errors[3]]
        length_error = row_3_errors[0]
        assert length_error.error_type == ParserErrorCategoryChoices.RECORD_PRE_CHECK
        assert (
            length_error.error_message
            == "T1: record length should be at least 117 characters but it is 7 characters."
        )
        assert length_error.content_type is None
        assert length_error.object_id is None

        trailer_error_3 = trailer_errors[3]
        assert trailer_error_3.error_type == ParserErrorCategoryChoices.RECORD_PRE_CHECK
        assert (
            trailer_error_3.error_message
            == "T1: Case number T1trash cannot contain blanks."
        )
        assert trailer_error_3.content_type is None
        assert trailer_error_3.object_id is None

        trailer_error_4 = trailer_errors[4]
        assert trailer_error_4.error_type == ParserErrorCategoryChoices.RECORD_PRE_CHECK
        assert trailer_error_4.error_message == (
            "T1: Reporting month year None does not "
            "match file reporting year:2021, quarter:Q1."
        )
        assert trailer_error_4.content_type is None
        assert trailer_error_4.object_id is None

    @pytest.mark.django_db
    def test_parse_empty_file(self, empty_file, dfs):
        """Test parsing of empty_file."""
        dfs.datafile = empty_file
        dfs.save()
        parse_datafile(dfs, empty_file)

        dfs.status = dfs.get_status()
        dfs.case_aggregates = aggregates.case_aggregates_by_month(empty_file, dfs.status)

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

        assert parser_errors.count() == 2

        err = parser_errors.first()

        assert err.row_number == 1
        assert err.error_type == ParserErrorCategoryChoices.PRE_CHECK
        assert err.error_message == "HEADER: record length is 0 characters but must be 23."
        assert err.content_type is None
        assert err.object_id is None

    @pytest.mark.django_db
    def test_parse_small_ssp_section1_datafile(self, small_ssp_section1_datafile, dfs):
        """Test parsing small_ssp_section1_datafile."""
        small_ssp_section1_datafile.year = 2024
        small_ssp_section1_datafile.quarter = "Q1"

        expected_m1_record_count = 5
        expected_m2_record_count = 6
        expected_m3_record_count = 8

        dfs.datafile = small_ssp_section1_datafile
        dfs.save()
        parse_datafile(dfs, small_ssp_section1_datafile)

        parser_errors = ParserError.objects.filter(file=small_ssp_section1_datafile)
        dfs.status = dfs.get_status()
        assert dfs.status == DataFileSummary.Status.PARTIALLY_ACCEPTED
        dfs.case_aggregates = aggregates.case_aggregates_by_month(dfs.datafile, dfs.status)

        assert dfs.case_aggregates["rejected"] == 1
        for month in dfs.case_aggregates["months"]:
            if month["month"] == "Oct":
                assert month["accepted_without_errors"] == 0
                assert month["accepted_with_errors"] == 5
            else:
                assert month["accepted_without_errors"] == 0
                assert month["accepted_with_errors"] == 0

        parser_errors = ParserError.objects.filter(file=small_ssp_section1_datafile)
        assert parser_errors.count() == 9
        assert SSP_M1.objects.count() == expected_m1_record_count
        assert SSP_M2.objects.count() == expected_m2_record_count
        assert SSP_M3.objects.count() == expected_m3_record_count

    @pytest.mark.django_db()
    def test_parse_ssp_section1_datafile(self, ssp_section1_datafile, dfs):
        """Test parsing ssp_section1_datafile."""
        ssp_section1_datafile.year = 2019
        ssp_section1_datafile.quarter = "Q1"

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
        assert err.error_message == (
            "M1 Item 11 (Receives Subsidized Housing): 3 is not in range [1, 2]."
        )
        assert err.content_type is not None
        assert err.object_id is not None

        cat4_errors = parser_errors.filter(
            error_type=ParserErrorCategoryChoices.CASE_CONSISTENCY
        ).order_by("id")

        assert cat4_errors.count() == 3
        assert (
            cat4_errors[0].error_message
            == "Duplicate record detected with record type M3 at line 453. "
            + "Record is a duplicate of the record at line number 452."
        )
        assert (
            cat4_errors[1].error_message
            == "Duplicate record detected with record type M3 at line 3273. "
            + "Record is a duplicate of the record at line number 3272."
        )
        assert (
            cat4_errors[2].error_message
            == "Partial duplicate record detected with record type M3 at line 3275. "
            + "Record is a partial duplicate of the record at line number 3274. Duplicated fields "
            + "causing error: Item 0 (Record Type), Item 3 (Reporting Year and Month), Item 5 (Case Number), "
            + "Item 60 (Family Affiliation), Item 61 (Date of Birth), and Item 62 (Social Security Number)."
        )

        assert parser_errors.count() == 31726

        assert SSP_M1.objects.count() == expected_m1_record_count
        assert SSP_M2.objects.count() == expected_m2_record_count
        assert SSP_M3.objects.count() == expected_m3_record_count

    @pytest.mark.django_db
    def test_parse_tanf_section1_datafile(self, small_tanf_section1_datafile, dfs):
        """Test parsing of small_tanf_section1_datafile and validate T2 model data."""
        small_tanf_section1_datafile.year = 2021
        small_tanf_section1_datafile.quarter = "Q1"
        dfs.datafile = small_tanf_section1_datafile

        parse_datafile(dfs, small_tanf_section1_datafile)

        dfs.status = dfs.get_status()
        assert dfs.status == DataFileSummary.Status.ACCEPTED_WITH_ERRORS
        dfs.case_aggregates = aggregates.case_aggregates_by_month(dfs.datafile, dfs.status)
        assert dfs.case_aggregates == {
            "months": [
                {"month": "Oct", "accepted_without_errors": 1, "accepted_with_errors": 4},
                {"month": "Nov", "accepted_without_errors": 0, "accepted_with_errors": 0},
                {"month": "Dec", "accepted_without_errors": 0, "accepted_with_errors": 0},
            ],
            "rejected": 0,
        }

        assert TANF_T2.objects.count() == 5

        t2_models = TANF_T2.objects.all()

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

    @pytest.mark.django_db()
    def test_parse_tanf_section1_datafile_obj_counts(self, small_tanf_section1_datafile, dfs):
        """Test parsing of small_tanf_section1_datafile in general."""
        small_tanf_section1_datafile.year = 2021
        small_tanf_section1_datafile.quarter = "Q1"

        dfs.datafile = small_tanf_section1_datafile
        dfs.save()

        parse_datafile(dfs, small_tanf_section1_datafile)

        assert TANF_T1.objects.count() == 5
        assert TANF_T2.objects.count() == 5
        assert TANF_T3.objects.count() == 6

    @pytest.mark.django_db()
    def test_parse_tanf_section1_datafile_t3s(self, small_tanf_section1_datafile, dfs):
        """Test parsing of small_tanf_section1_datafile and validate T3 model data."""
        small_tanf_section1_datafile.year = 2021
        small_tanf_section1_datafile.quarter = "Q1"

        dfs.datafile = small_tanf_section1_datafile
        dfs.save()

        parse_datafile(dfs, small_tanf_section1_datafile)

        assert TANF_T3.objects.count() == 6

        t3_models = TANF_T3.objects.all()
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

    @pytest.mark.django_db
    def test_parse_bad_tfs1_missing_required(self, bad_tanf_s1__row_missing_required_field, dfs):
        """Test parsing a bad TANF Section 1 submission where a row is missing required data."""
        bad_tanf_s1__row_missing_required_field.year = 2021
        bad_tanf_s1__row_missing_required_field.quarter = "Q1"

        dfs.datafile = bad_tanf_s1__row_missing_required_field
        dfs.save()

        parse_datafile(dfs, bad_tanf_s1__row_missing_required_field)

        assert dfs.get_status() == DataFileSummary.Status.REJECTED

        parser_errors = ParserError.objects.filter(
            file=bad_tanf_s1__row_missing_required_field
        )

        assert parser_errors.count() == 5

        error_message = "T1: Reporting month year None does not match file reporting year:2021, quarter:Q1."
        row_2_error = parser_errors.get(row_number=2, error_message=error_message)
        assert row_2_error.error_type == ParserErrorCategoryChoices.RECORD_PRE_CHECK
        assert row_2_error.error_message == error_message

        error_message = "T2: Reporting month year None does not match file reporting year:2021, quarter:Q1."
        row_3_error = parser_errors.get(row_number=3, error_message=error_message)
        assert row_3_error.error_type == ParserErrorCategoryChoices.RECORD_PRE_CHECK
        assert row_3_error.error_message == error_message

        error_message = "T3: Reporting month year None does not match file reporting year:2021, quarter:Q1."
        row_4_error = parser_errors.get(row_number=4, error_message=error_message)
        assert row_4_error.error_type == ParserErrorCategoryChoices.RECORD_PRE_CHECK
        assert row_4_error.error_message == error_message

        error_message = "Unknown Record_Type was found."
        row_5_error = parser_errors.get(row_number=5, error_message=error_message)
        assert row_5_error.error_type == ParserErrorCategoryChoices.RECORD_PRE_CHECK
        assert row_5_error.error_message == error_message
        assert row_5_error.content_type is None
        assert row_5_error.object_id is None

    @pytest.mark.django_db()
    def test_parse_bad_ssp_s1_missing_required(self, bad_ssp_s1__row_missing_required_field, dfs):
        """Test parsing a bad TANF Section 1 submission where a row is missing required data."""
        bad_ssp_s1__row_missing_required_field.year = 2019
        bad_ssp_s1__row_missing_required_field.quarter = "Q1"

        dfs.datafile = bad_ssp_s1__row_missing_required_field
        dfs.save()

        parse_datafile(dfs, bad_ssp_s1__row_missing_required_field)

        parser_errors = ParserError.objects.filter(
            file=bad_ssp_s1__row_missing_required_field
        )
        assert parser_errors.count() == 6

        row_2_error = parser_errors.get(
            row_number=2,
            error_message__contains="Reporting month year None does not match file reporting year:2019, quarter:Q1.",
        )
        assert row_2_error.error_type == ParserErrorCategoryChoices.RECORD_PRE_CHECK

        row_3_error = parser_errors.get(
            row_number=3,
            error_message__contains="Reporting month year None does not match file reporting year:2019, quarter:Q1.",
        )
        assert row_3_error.error_type == ParserErrorCategoryChoices.RECORD_PRE_CHECK

        row_4_error = parser_errors.get(
            row_number=4,
            error_message__contains="Reporting month year None does not match file reporting year:2019, quarter:Q1.",
        )
        assert row_4_error.error_type == ParserErrorCategoryChoices.RECORD_PRE_CHECK

        error_message = (
            "Reporting month year None does not match file reporting year:2019, quarter:Q1."
        )
        rpt_month_errors = parser_errors.filter(error_message__contains=error_message)
        assert len(rpt_month_errors) == 3
        for i, e in enumerate(rpt_month_errors):
            assert e.error_type == ParserErrorCategoryChoices.RECORD_PRE_CHECK
            assert error_message.format(i + 1) in e.error_message
            assert e.object_id is None

        row_5_error = parser_errors.get(
            row_number=5, error_message="Unknown Record_Type was found."
        )
        assert row_5_error.error_type == ParserErrorCategoryChoices.RECORD_PRE_CHECK
        assert row_5_error.content_type is None
        assert row_5_error.object_id is None

        trailer_error = parser_errors.get(
            row_number=6,
            error_message="TRAILER: record length is 15 characters but must be 23.",
        )
        assert trailer_error.error_type == ParserErrorCategoryChoices.RECORD_PRE_CHECK
        assert trailer_error.content_type is None
        assert trailer_error.object_id is None

    @pytest.mark.django_db
    def test_dfs_set_case_aggregates(self, small_correct_file, dfs):
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

    @pytest.mark.django_db()
    def test_parse_small_tanf_section2_file(self, small_tanf_section2_file, dfs):
        """Test parsing a small TANF Section 2 submission."""
        small_tanf_section2_file.year = 2021
        small_tanf_section2_file.quarter = "Q1"

        dfs.datafile = small_tanf_section2_file
        dfs.save()

        parse_datafile(dfs, small_tanf_section2_file)

        assert TANF_T4.objects.all().count() == 1
        assert TANF_T5.objects.all().count() == 1

        parser_errors = ParserError.objects.filter(file=small_tanf_section2_file)

        assert parser_errors.count() == 0

        t4 = TANF_T4.objects.first()
        t5 = TANF_T5.objects.first()

        assert t4.DISPOSITION == 1
        assert t4.REC_SUB_CC == 3

        assert t5.SEX == 2
        assert t5.AMOUNT_UNEARNED_INCOME == "0000"

    @pytest.mark.django_db()
    def test_parse_tanf_section2_file(self, tanf_section2_file, dfs):
        """Test parsing TANF Section 2 submission."""
        tanf_section2_file.year = 2022
        tanf_section2_file.quarter = "Q1"

        dfs.datafile = tanf_section2_file
        dfs.save()

        parse_datafile(dfs, tanf_section2_file)

        assert TANF_T4.objects.all().count() == 223
        assert TANF_T5.objects.all().count() == 605

        parser_errors = ParserError.objects.filter(file=tanf_section2_file)

        err = parser_errors.first()
        assert err.error_type == ParserErrorCategoryChoices.FIELD_VALUE
        assert err.error_message == (
            "T4 Item 10 (Received Subsidized Housing): 3 is not in range [1, 2]."
        )
        assert err.content_type.model == "tanf_t4"
        assert err.object_id is not None

    @pytest.mark.django_db()
    def test_parse_tanf_section3_file(self, tanf_section3_file, dfs):
        """Test parsing TANF Section 3 submission."""
        tanf_section3_file.year = 2022
        tanf_section3_file.quarter = "Q1"

        dfs.datafile = tanf_section3_file

        parse_datafile(dfs, tanf_section3_file)

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

        assert TANF_T6.objects.all().count() == 3

        parser_errors = ParserError.objects.filter(file=tanf_section3_file)
        assert parser_errors.count() == 0

        t6_objs = TANF_T6.objects.all().order_by("NUM_APPROVED")

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

    @pytest.mark.django_db()
    def test_parse_tanf_section1_blanks_file(self, tanf_section1_file_with_blanks, dfs):
        """Test section 1 fields that are allowed to have blanks."""
        tanf_section1_file_with_blanks.year = 2021
        tanf_section1_file_with_blanks.quarter = "Q1"

        dfs.datafile = tanf_section1_file_with_blanks
        dfs.save()

        parse_datafile(dfs, tanf_section1_file_with_blanks)

        parser_errors = ParserError.objects.filter(file=tanf_section1_file_with_blanks)

        assert parser_errors.count() == 23

        # Should only be cat3 validator errors
        for error in parser_errors:
            assert error.error_type == ParserErrorCategoryChoices.VALUE_CONSISTENCY

        t1 = TANF_T1.objects.first()
        t2 = TANF_T2.objects.first()
        t3 = TANF_T3.objects.first()

        assert t1.FAMILY_SANC_ADULT is None
        assert t2.MARITAL_STATUS is None
        assert t3.CITIZENSHIP_STATUS is None

    @pytest.mark.django_db()
    def test_parse_tanf_section4_file(self, tanf_section4_file, dfs):
        """Test parsing TANF Section 4 submission."""
        tanf_section4_file.year = 2022
        tanf_section4_file.quarter = "Q1"

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

        assert TANF_T7.objects.all().count() == 18

        parser_errors = ParserError.objects.filter(file=tanf_section4_file)
        assert parser_errors.count() == 0

        t7_objs = TANF_T7.objects.all().order_by("FAMILIES_MONTH")

        first = t7_objs.first()
        sixth = t7_objs[5]

        assert first.RPT_MONTH_YEAR == 202111
        assert sixth.RPT_MONTH_YEAR == 202112

        assert first.TDRS_SECTION_IND == "2"
        assert sixth.TDRS_SECTION_IND == "2"

        assert first.FAMILIES_MONTH == 274
        assert sixth.FAMILIES_MONTH == 499

    @pytest.mark.django_db()
    def test_parse_bad_tanf_section4_file(self, bad_tanf_section4_file, dfs):
        """Test parsing TANF Section 4 submission when no records are created."""
        bad_tanf_section4_file.year = 2021
        bad_tanf_section4_file.quarter = "Q1"

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

        assert TANF_T7.objects.all().count() == 0

        parser_errors = ParserError.objects.filter(file=bad_tanf_section4_file).order_by(
            "id"
        )
        assert parser_errors.count() == 2

        error = parser_errors.first()
        error.error_message == "Value length 151 does not match 247."
        error.error_type == ParserErrorCategoryChoices.PRE_CHECK

        error = parser_errors[1]
        error.error_message == "No records created."
        error.error_type == ParserErrorCategoryChoices.PRE_CHECK

    @pytest.mark.django_db()
    def test_parse_ssp_section4_file(self, ssp_section4_file, dfs):
        """Test parsing SSP Section 4 submission."""
        ssp_section4_file.year = 2022
        ssp_section4_file.quarter = "Q1"

        dfs.datafile = ssp_section4_file

        parse_datafile(dfs, ssp_section4_file)

        m7_objs = SSP_M7.objects.all().order_by("FAMILIES_MONTH")

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

    @pytest.mark.django_db()
    def test_parse_ssp_section2_rec_oadsi_file(self, ssp_section2_rec_oadsi_file, dfs):
        """Test parsing SSP Section 2 REC_OADSI."""
        ssp_section2_rec_oadsi_file.year = 2019
        ssp_section2_rec_oadsi_file.quarter = "Q1"

        dfs.datafile = ssp_section2_rec_oadsi_file

        parse_datafile(dfs, ssp_section2_rec_oadsi_file)
        parser_errors = ParserError.objects.filter(file=ssp_section2_rec_oadsi_file)

        assert parser_errors.count() == 0

    @pytest.mark.django_db()
    def test_parse_ssp_section2_file(self, ssp_section2_file, dfs):
        """Test parsing SSP Section 2 submission."""
        ssp_section2_file.year = 2019
        ssp_section2_file.quarter = "Q1"

        dfs.datafile = ssp_section2_file

        parse_datafile(dfs, ssp_section2_file)

        dfs.status = dfs.get_status()
        dfs.case_aggregates = aggregates.case_aggregates_by_month(dfs.datafile, dfs.status)
        for dfs_case_aggregate in dfs.case_aggregates["months"]:
            assert dfs_case_aggregate["accepted_without_errors"] == 0
            assert dfs_case_aggregate["accepted_with_errors"] in [75, 78]
            assert dfs_case_aggregate["month"] in ["Oct", "Nov", "Dec"]
        assert dfs.get_status() == DataFileSummary.Status.PARTIALLY_ACCEPTED

        m4_objs = SSP_M4.objects.all().order_by("id")
        m5_objs = SSP_M5.objects.all().order_by("AMOUNT_EARNED_INCOME")

        expected_m4_count = 231
        expected_m5_count = 703

        assert SSP_M4.objects.count() == expected_m4_count
        assert SSP_M5.objects.count() == expected_m5_count

        m4 = m4_objs.first()
        assert m4.DISPOSITION == 1
        assert m4.REC_SUB_CC == 3

        m5 = m5_objs.first()
        assert m5.FAMILY_AFFILIATION == 1
        assert m5.AMOUNT_EARNED_INCOME == "0000"
        assert m5.AMOUNT_UNEARNED_INCOME == "0000"

    @pytest.mark.django_db()
    def test_parse_ssp_section3_file(self, ssp_section3_file, dfs):
        """Test parsing TANF Section 3 submission."""
        ssp_section3_file.year = 2022
        ssp_section3_file.quarter = "Q1"

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

        m6_objs = SSP_M6.objects.all().order_by("RPT_MONTH_YEAR")
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

    @pytest.mark.django_db
    def test_rpt_month_year_mismatch(self, header_datafile, dfs):
        """Test that the rpt_month_year mismatch error is raised."""
        datafile = header_datafile

        datafile.section = "Active Case Data"
        # test_datafile fixture uses create_test_data_file which assigns
        # a default year / quarter of 2021 / Q1
        datafile.year = 2021
        datafile.quarter = "Q1"
        datafile.save()

        dfs.datafile = header_datafile
        dfs.save()

        parse_datafile(dfs, datafile)

        parser_errors = ParserError.objects.filter(file=datafile)
        assert parser_errors.count() == 2
        assert (
            parser_errors.first().error_type == ParserErrorCategoryChoices.CASE_CONSISTENCY
        )

        datafile.year = 2023
        datafile.save()

        parse_datafile(dfs, datafile)

        parser_errors = ParserError.objects.filter(file=datafile).order_by("-id")
        assert parser_errors.count() == 3

        err = parser_errors.first()
        assert err.error_type == ParserErrorCategoryChoices.PRE_CHECK
        assert (
            err.error_message
            == "Submitted reporting year:2020, quarter:Q4 doesn't"
            + " match file reporting year:2023, quarter:Q1."
        )

    @pytest.mark.django_db()
    def test_parse_tribal_section_1_file(self, tribal_section_1_file, dfs):
        """Test parsing Tribal TANF Section 1 submission."""
        tribal_section_1_file.year = 2022
        tribal_section_1_file.quarter = "Q1"
        tribal_section_1_file.save()

        dfs.datafile = tribal_section_1_file

        parse_datafile(dfs, tribal_section_1_file)

        dfs.status = dfs.get_status()
        assert dfs.status == DataFileSummary.Status.ACCEPTED
        dfs.case_aggregates = aggregates.case_aggregates_by_month(dfs.datafile, dfs.status)
        assert dfs.case_aggregates == {
            "rejected": 0,
            "months": [
                {"month": "Oct", "accepted_without_errors": 1, "accepted_with_errors": 0},
                {"month": "Nov", "accepted_without_errors": 0, "accepted_with_errors": 0},
                {"month": "Dec", "accepted_without_errors": 0, "accepted_with_errors": 0},
            ],
        }

        assert Tribal_TANF_T1.objects.all().count() == 1
        assert Tribal_TANF_T2.objects.all().count() == 1
        assert Tribal_TANF_T3.objects.all().count() == 2

        t1_objs = Tribal_TANF_T1.objects.all().order_by("CASH_AMOUNT")
        t2_objs = Tribal_TANF_T2.objects.all().order_by("MONTHS_FED_TIME_LIMIT")
        t3_objs = Tribal_TANF_T3.objects.all().order_by("EDUCATION_LEVEL")

        t1 = t1_objs.first()
        t2 = t2_objs.first()
        t3 = t3_objs.last()

        assert t1.CASH_AMOUNT == 502
        assert t2.MONTHS_FED_TIME_LIMIT == "  0"
        assert t3.EDUCATION_LEVEL == "98"

    @pytest.mark.django_db()
    def test_parse_tribal_section_1_inconsistency_file(
        self,
        tribal_section_1_inconsistency_file, dfs
    ):
        """Test parsing inconsistent Tribal TANF Section 1 submission."""
        parse_datafile(dfs, tribal_section_1_inconsistency_file)

        assert Tribal_TANF_T1.objects.all().count() == 0

        parser_errors = ParserError.objects.filter(file=tribal_section_1_inconsistency_file)
        assert parser_errors.count() == 1

        assert (
            parser_errors.first().error_message
            == "Tribe Code (142) inconsistency with Program Type (TAN) "
            + "and FIPS Code (01)."
        )

    @pytest.mark.django_db()
    def test_parse_tribal_section_2_file(self, tribal_section_2_file, dfs):
        """Test parsing Tribal TANF Section 2 submission."""
        tribal_section_2_file.year = 2020
        tribal_section_2_file.quarter = "Q1"

        dfs.datafile = tribal_section_2_file

        parse_datafile(dfs, tribal_section_2_file)

        dfs.status = dfs.get_status()
        dfs.case_aggregates = aggregates.case_aggregates_by_month(dfs.datafile, dfs.status)
        assert dfs.case_aggregates == {
            "rejected": 0,
            "months": [
                {"accepted_without_errors": 3, "accepted_with_errors": 0, "month": "Oct"},
                {"accepted_without_errors": 3, "accepted_with_errors": 0, "month": "Nov"},
                {"accepted_without_errors": 0, "accepted_with_errors": 0, "month": "Dec"},
            ],
        }

        assert dfs.get_status() == DataFileSummary.Status.ACCEPTED

        assert Tribal_TANF_T4.objects.all().count() == 6
        assert Tribal_TANF_T5.objects.all().count() == 13

        t4_objs = Tribal_TANF_T4.objects.all().order_by("CLOSURE_REASON")
        t5_objs = Tribal_TANF_T5.objects.all().order_by("COUNTABLE_MONTH_FED_TIME")

        t4 = t4_objs.first()
        t5 = t5_objs.last()

        assert t4.CLOSURE_REASON == "15"
        assert t5.COUNTABLE_MONTH_FED_TIME == "  8"

    @pytest.mark.django_db()
    def test_parse_tribal_section_3_file(self, tribal_section_3_file, dfs):
        """Test parsing Tribal TANF Section 3 submission."""
        tribal_section_3_file.year = 2022
        tribal_section_3_file.quarter = "Q1"

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

        assert Tribal_TANF_T6.objects.all().count() == 3

        t6_objs = Tribal_TANF_T6.objects.all().order_by("NUM_APPLICATIONS")

        t6 = t6_objs.first()

        assert t6.NUM_APPLICATIONS == 1
        assert t6.NUM_FAMILIES == 41
        assert t6.NUM_CLOSED_CASES == 3

    @pytest.mark.django_db()
    def test_parse_tribal_section_4_file(self, tribal_section_4_file, dfs):
        """Test parsing Tribal TANF Section 4 submission."""
        tribal_section_4_file.year = 2022
        tribal_section_4_file.quarter = "Q1"

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

        assert Tribal_TANF_T7.objects.all().count() == 18

        t7_objs = Tribal_TANF_T7.objects.all().order_by("FAMILIES_MONTH")

        first = t7_objs.first()
        sixth = t7_objs[5]

        assert first.RPT_MONTH_YEAR == 202111
        assert sixth.RPT_MONTH_YEAR == 202112

        assert first.TDRS_SECTION_IND == "2"
        assert sixth.TDRS_SECTION_IND == "2"

        assert first.FAMILIES_MONTH == 274
        assert sixth.FAMILIES_MONTH == 499

    @pytest.mark.parametrize(
        "file_fixture, result, number_of_errors, error_message",
        [
            ("second_child_only_space_t3_file", 1, 0, ""),
            ("one_child_t3_file", 1, 0, ""),
            ("t3_file", 1, 0, ""),
            (
                "t3_file_two_child",
                1,
                1,
                "The second child record is too short at 97 characters"
                + " and must be at least 101 characters.",
            ),
            ("t3_file_two_child_with_space_filled", 2, 0, ""),
            (
                "two_child_second_filled",
                2,
                8,
                "T3 Item 68 (Date of Birth): Year 6    must be larger than 1900.",
            ),
            ("t3_file_zero_filled_second", 1, 0, ""),
        ],
    )
    @pytest.mark.django_db()
    def test_misformatted_multi_records(
        self,
        file_fixture, result, number_of_errors, error_message, request, dfs
    ):
        """Test that (not space filled) multi-records are caught."""
        file_fixture = request.getfixturevalue(file_fixture)
        dfs.datafile = file_fixture
        parse_datafile(dfs, file_fixture)
        parser_errors = ParserError.objects.filter(file=file_fixture)
        t3 = TANF_T3.objects.all()
        assert t3.count() == result

        parser_errors = ParserError.objects.all()
        assert parser_errors.count() == number_of_errors
        if number_of_errors > 0:
            error_messages = [parser_error.error_message for parser_error in parser_errors]
            assert error_message in error_messages

        parser_errors = (
            ParserError.objects.all()
            .exclude(
                # exclude extraneous cat 4 errors
                error_type=ParserErrorCategoryChoices.CASE_CONSISTENCY
            )
            .exclude(error_message="No records created.")
        )

        assert parser_errors.count() == number_of_errors

    @pytest.mark.django_db()
    def test_empty_t4_t5_values(self, t4_t5_empty_values, dfs):
        """Test that empty field values for un-required fields parse."""
        dfs.datafile = t4_t5_empty_values
        parse_datafile(dfs, t4_t5_empty_values)
        parser_errors = ParserError.objects.filter(file=t4_t5_empty_values)
        t4 = TANF_T4.objects.all()
        t5 = TANF_T5.objects.all()
        assert t4.count() == 1
        assert t4[0].STRATUM is None
        logger.info(t4[0].__dict__)
        assert t5.count() == 1
        assert parser_errors[0].error_message == (
            "T4 Item 10 (Received Subsidized Housing): 3 is not in range [1, 2]."
        )

    @pytest.mark.django_db()
    def test_parse_t2_invalid_dob(self, t2_invalid_dob_file, dfs):
        """Test parsing a TANF T2 record with an invalid DOB."""
        dfs.datafile = t2_invalid_dob_file
        t2_invalid_dob_file.year = 2021
        t2_invalid_dob_file.quarter = "Q1"
        dfs.save()

        parse_datafile(dfs, t2_invalid_dob_file)

        parser_errors = ParserError.objects.filter(file=t2_invalid_dob_file).order_by("pk")

        month_error = parser_errors[2]
        year_error = parser_errors[1]
        digits_error = parser_errors[0]

        assert (
            month_error.error_message
            == "T2 Item 32 (Date of Birth): $9 is not a valid month."
        )
        assert (
            year_error.error_message
            == "T2 Item 32 (Date of Birth): Year Q897 must be larger than 1900."
        )
        assert (
            digits_error.error_message
            == "T2 Item 32 (Date of Birth): Q897$9 3 does not have exactly 8 digits."
        )

    @pytest.mark.django_db()
    def test_parse_tanf_section4_file_with_errors(self, tanf_section_4_file_with_errors, dfs):
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

        assert TANF_T7.objects.all().count() == 18

        parser_errors = ParserError.objects.filter(file=tanf_section_4_file_with_errors)

        assert parser_errors.count() == 7

        t7_objs = TANF_T7.objects.all().order_by("FAMILIES_MONTH")

        first = t7_objs.first()
        sixth = t7_objs[5]

        assert first.RPT_MONTH_YEAR == 202111
        assert sixth.RPT_MONTH_YEAR == 202110

        assert first.TDRS_SECTION_IND == "1"
        assert sixth.TDRS_SECTION_IND == "1"

        assert first.FAMILIES_MONTH == 0
        assert sixth.FAMILIES_MONTH == 446

    @pytest.mark.django_db()
    def test_parse_no_records_file(self, no_records_file, dfs):
        """Test parsing TANF Section 4 submission."""
        dfs.datafile = no_records_file
        parse_datafile(dfs, no_records_file)

        dfs.status = dfs.get_status()
        assert dfs.status == DataFileSummary.Status.REJECTED

        errors = ParserError.objects.filter(file=no_records_file)

        assert errors.count() == 1

        error = errors.first()
        assert error.error_message == "No records created."
        assert error.error_type == ParserErrorCategoryChoices.PRE_CHECK
        assert error.content_type is None
        assert error.object_id is None

    @pytest.mark.django_db
    def test_parse_aggregates_rejected_datafile(self, aggregates_rejected_datafile, dfs):
        """Test record rejection counting when record has more than one preparsing error."""
        aggregates_rejected_datafile.year = 2021
        aggregates_rejected_datafile.quarter = "Q1"

        print(aggregates_rejected_datafile)

        dfs.datafile = aggregates_rejected_datafile

        parse_datafile(dfs, aggregates_rejected_datafile)

        dfs.status = dfs.get_status()
        assert dfs.status == DataFileSummary.Status.REJECTED
        dfs.case_aggregates = aggregates.case_aggregates_by_month(dfs.datafile, dfs.status)
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

        errors = ParserError.objects.filter(file=aggregates_rejected_datafile).order_by(
            "id"
        )

        assert errors.count() == 3
        record_precheck_errors = errors.filter(row_number=2)
        assert record_precheck_errors.count() == 2
        for error in record_precheck_errors:
            assert error.error_type == ParserErrorCategoryChoices.RECORD_PRE_CHECK

        assert errors.last().error_type == ParserErrorCategoryChoices.PRE_CHECK

        assert TANF_T2.objects.count() == 0

    @pytest.mark.django_db()
    def test_parse_tanf_section_1_file_with_bad_update_indicator(
        self,
        tanf_section_1_file_with_bad_update_indicator, dfs
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

    @pytest.mark.django_db()
    def test_parse_tribal_section_4_bad_quarter(self, tribal_section_4_bad_quarter, dfs):
        """Test handling invalid quarter value that raises a ValueError exception."""
        tribal_section_4_bad_quarter.year = 2021
        tribal_section_4_bad_quarter.quarter = "Q1"
        dfs.datafile = tribal_section_4_bad_quarter

        parse_datafile(dfs, tribal_section_4_bad_quarter)
        parser_errors = ParserError.objects.filter(
            file=tribal_section_4_bad_quarter
        ).order_by("id")

        assert parser_errors.count() == 3

        parser_errors.first().error_message == (
            "T7: 2020  is invalid. Calendar Quarter must be a numeric "
            "representing the Calendar Year and Quarter formatted as YYYYQ"
        )

        Tribal_TANF_T7.objects.count() == 0

    @pytest.mark.django_db()
    def test_parse_t3_cat2_invalid_citizenship(self, t3_cat2_invalid_citizenship_file, dfs):
        """Test parsing a TANF T3 record with an invalid CITIZENSHIP_STATUS."""
        dfs.datafile = t3_cat2_invalid_citizenship_file
        t3_cat2_invalid_citizenship_file.year = 2021
        t3_cat2_invalid_citizenship_file.quarter = "Q1"
        dfs.save()

        parse_datafile(dfs, t3_cat2_invalid_citizenship_file)

        exclusion = Query(error_type=ParserErrorCategoryChoices.CASE_CONSISTENCY) | Query(
            error_type=ParserErrorCategoryChoices.PRE_CHECK
        )

        parser_errors = (
            ParserError.objects.filter(file=t3_cat2_invalid_citizenship_file)
            .exclude(exclusion)
            .order_by("pk")
        )

        # no errors expected as fields are not required
        assert parser_errors.count() == 0

    @pytest.mark.django_db()
    def test_parse_m2_cat2_invalid_37_38_39_file(self, m2_cat2_invalid_37_38_39_file, dfs):
        """Test parsing an SSP M2 file with an invalid EDUCATION_LEVEL, CITIZENSHIP_STATUS, COOPERATION_CHILD_SUPPORT."""
        dfs.datafile = m2_cat2_invalid_37_38_39_file
        m2_cat2_invalid_37_38_39_file.year = 2024
        m2_cat2_invalid_37_38_39_file.quarter = "Q1"
        dfs.save()

        parse_datafile(dfs, m2_cat2_invalid_37_38_39_file)

        exclusion = Query(error_type=ParserErrorCategoryChoices.CASE_CONSISTENCY) | Query(
            error_type=ParserErrorCategoryChoices.PRE_CHECK
        )

        parser_errors = (
            ParserError.objects.filter(file=m2_cat2_invalid_37_38_39_file)
            .exclude(exclusion)
            .order_by("pk")
        )

        # no errors expected as fields are not required
        assert parser_errors.count() == 0

    @pytest.mark.django_db()
    def test_parse_m3_cat2_invalid_68_69_file(self, m3_cat2_invalid_68_69_file, dfs):
        """Test parsing an SSP M3 file with an invalid EDUCATION_LEVEL and CITIZENSHIP_STATUS."""
        dfs.datafile = m3_cat2_invalid_68_69_file
        m3_cat2_invalid_68_69_file.year = 2024
        m3_cat2_invalid_68_69_file.quarter = "Q1"
        dfs.save()

        parse_datafile(dfs, m3_cat2_invalid_68_69_file)

        exclusion = Query(error_type=ParserErrorCategoryChoices.CASE_CONSISTENCY) | Query(
            error_type=ParserErrorCategoryChoices.PRE_CHECK
        )

        parser_errors = (
            ParserError.objects.filter(file=m3_cat2_invalid_68_69_file)
            .exclude(exclusion)
            .order_by("pk")
        )

        assert parser_errors.count() == 2

        error_msgs = {
            "Item 68 (Educational Level) 00 must be between 1 and 16 or must be between 98 and 99.",
            "Item 68 (Educational Level) 00 must be between 1 and 16 or must be between 98 and 99.",
        }

        for e in parser_errors:
            assert e.error_message in error_msgs

    @pytest.mark.django_db()
    def test_parse_m5_cat2_invalid_23_24_file(self, m5_cat2_invalid_23_24_file, dfs):
        """Test parsing an SSP M5 file with an invalid EDUCATION_LEVEL and CITIZENSHIP_STATUS."""
        dfs.datafile = m5_cat2_invalid_23_24_file
        m5_cat2_invalid_23_24_file.year = 2019
        m5_cat2_invalid_23_24_file.quarter = "Q1"
        dfs.save()

        parse_datafile(dfs, m5_cat2_invalid_23_24_file)

        exclusion = Query(error_type=ParserErrorCategoryChoices.CASE_CONSISTENCY) | Query(
            error_type=ParserErrorCategoryChoices.PRE_CHECK
        )

        parser_errors = (
            ParserError.objects.filter(file=m5_cat2_invalid_23_24_file)
            .exclude(exclusion)
            .order_by("pk")
        )

        assert parser_errors.count() == 0

    @pytest.mark.django_db()
    def test_zero_filled_fips_code_file(self, test_file_zero_filled_fips_code, dfs):
        """Test parsing a file with zero filled FIPS code."""
        # TODO: this test can be merged as parametrized test with  "test_parse_small_correct_file"
        dfs.datafile = test_file_zero_filled_fips_code
        test_file_zero_filled_fips_code.year = 2024
        test_file_zero_filled_fips_code.quarter = "Q2"
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
    @pytest.mark.django_db()
    def test_parse_fra_bad_header(self, request, file, dfs):
        """Test parsing FRA files with bad header data."""
        datafile = request.getfixturevalue(file)
        datafile.year = 2024
        datafile.quarter = "Q1"

        dfs.datafile = datafile
        dfs.save()

        parse_datafile(dfs, datafile)

        assert TANF_Exiter1.objects.all().count() == 0

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
    @pytest.mark.django_db()
    def test_parse_fra_empty_first_row(self, request, file, dfs):
        """Test parsing FRA files with an empty first row/no header data."""
        datafile = request.getfixturevalue(file)
        datafile.year = 2024
        datafile.quarter = "Q1"

        dfs.datafile = datafile
        dfs.save()

        parse_datafile(dfs, datafile)

        assert TANF_Exiter1.objects.all().count() == 0

        errors = ParserError.objects.filter(file=datafile).order_by("id")
        assert len(errors) == 1
        for e in errors:
            assert e.error_message == "File does not begin with FRA data."
            assert e.error_type == ParserErrorCategoryChoices.PRE_CHECK
        assert dfs.get_status() == DataFileSummary.Status.REJECTED

    @pytest.mark.django_db()
    def test_parse_fra_decoder_unknown(self, fra_decoder_unknown, dfs):
        """Test parsing a FRA file with bad encoding."""
        datafile = fra_decoder_unknown
        datafile.year = 2025
        datafile.quarter = "Q3"

        dfs.datafile = datafile
        dfs.save()

        try:
            parse_datafile(dfs, datafile)
        except util.DecoderUnknownException:
            pass

        errors = ParserError.objects.filter(file=datafile).order_by("id")
        assert errors.count() == 1
        assert errors.first().error_type == ParserErrorCategoryChoices.PRE_CHECK
        assert errors.first().error_message == (
            "Could not determine encoding of FRA file. If the file is an XLSX file, "
            "ensure it can be opened in Excel. If the file is a CSV, ensure it can be "
            "opened in a text editor and is UTF-8 encoded."
        )
        assert dfs.get_status() == DataFileSummary.Status.REJECTED

    @pytest.mark.django_db()
    def test_parse_section2_no_records(self, section2_no_records, dfs):
        """Test parsing valid section 2 file with no records."""
        datafile = section2_no_records
        dfs.datafile = datafile
        dfs.save()

        parse_datafile(dfs, datafile)

        errors = ParserError.objects.filter(file=datafile).order_by("id")
        assert errors.count() == 0
        assert dfs.get_status() == DataFileSummary.Status.ACCEPTED

    @pytest.mark.django_db
    def test_parse_tanf_s1_federally_funded_recipients(
        self,
        tanf_s1_federally_funded_recipients, dfs
    ):
        """Test parsing file that generates the tanf_s1_federally_funded_recipients error."""
        dfs.datafile = tanf_s1_federally_funded_recipients

        parse_datafile(dfs, tanf_s1_federally_funded_recipients)

        errors = ParserError.objects.filter(
            file=tanf_s1_federally_funded_recipients
        ).order_by("id")

        dfs.status = dfs.get_status()
        assert dfs.status == DataFileSummary.Status.ACCEPTED_WITH_ERRORS
        assert errors.last().error_message == (
            "Federally funded recipients must have a valid Social Security number."
        )
