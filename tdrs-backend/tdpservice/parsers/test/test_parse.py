"""Test the implementation of the parse_file method with realistic datafiles."""


import pytest
from django.contrib.admin.models import LogEntry
from django.conf import settings
from django.db.models import Q as Query
from .. import parse
from ..models import ParserError, ParserErrorCategoryChoices, DataFileSummary
from tdpservice.search_indexes.models.tanf import TANF_T1, TANF_T2, TANF_T3, TANF_T4, TANF_T5, TANF_T6, TANF_T7
from tdpservice.search_indexes.models.tribal import Tribal_TANF_T1, Tribal_TANF_T2, Tribal_TANF_T3, Tribal_TANF_T4
from tdpservice.search_indexes.models.tribal import Tribal_TANF_T5, Tribal_TANF_T6, Tribal_TANF_T7
from tdpservice.search_indexes.models.ssp import SSP_M1, SSP_M2, SSP_M3, SSP_M4, SSP_M5, SSP_M6, SSP_M7
from tdpservice.search_indexes import documents
from tdpservice.parsers.test.factories import DataFileSummaryFactory, ParsingFileFactory
from tdpservice.data_files.models import DataFile
from tdpservice.parsers import util
from .. import schema_defs, aggregates
from elasticsearch.helpers.errors import BulkIndexError
import logging
logger = logging.getLogger(__name__)


es_logger = logging.getLogger('elasticsearch')
es_logger.setLevel(logging.WARNING)

settings.GENERATE_TRAILER_ERRORS = True

@pytest.fixture
def test_datafile(stt_user, stt):
    """Fixture for small_correct_file."""
    return util.create_test_datafile('small_correct_file.txt', stt_user, stt)


@pytest.fixture
def test_header_datafile(stt_user, stt):
    """Fixture for header test."""
    return util.create_test_datafile('tanf_section1_header_test.txt', stt_user, stt)


@pytest.fixture
def dfs():
    """Fixture for DataFileSummary."""
    return DataFileSummaryFactory.build()


@pytest.fixture
def t2_invalid_dob_file():
    """Fixture for T2 file with an invalid DOB."""
    parsing_file = ParsingFileFactory(
        year=2021,
        quarter='Q1',
        file__name='t2_invalid_dob_file.txt',
        file__section='Active Case Data',
        file__data=(b'HEADER20204A25   TAN1ED\n'
                    b'T22020101111111111212Q897$9 3WTTTTTY@W222122222222101221211001472201140000000000000000000000000'
                    b'0000000000000000000000000000000000000000000000000000000000291\n'
                    b'TRAILER0000001         ')
    )
    return parsing_file

# TODO: the name of this test doesn't make perfect sense anymore since it will always have errors now.
# TODO: parametrize and merge with test_zero_filled_fips_code_file
@pytest.mark.django_db
def test_parse_small_correct_file(small_correct_file, dfs):
    """Test parsing of small_correct_file."""
    small_correct_file.year = 2021
    small_correct_file.quarter = 'Q1'
    small_correct_file.save()
    dfs.datafile = small_correct_file

    parse.parse_datafile(small_correct_file, dfs)

    errors = ParserError.objects.filter(file=small_correct_file).order_by('id')
    assert errors.count() == 2
    assert errors.first().error_type == ParserErrorCategoryChoices.CASE_CONSISTENCY

    dfs.status = dfs.get_status()
    dfs.case_aggregates = aggregates.case_aggregates_by_month(dfs.datafile, dfs.status)
    assert dfs.case_aggregates == {'rejected': 1,
                                   'months': [
                                       {'accepted_without_errors': 'N/A',
                                        'accepted_with_errors': 'N/A',
                                        'month': 'Oct'},
                                       {'accepted_without_errors': 'N/A',
                                        'accepted_with_errors': 'N/A',
                                        'month': 'Nov'},
                                       {'accepted_without_errors': 'N/A',
                                        'accepted_with_errors': 'N/A',
                                        'month': 'Dec'}
                                   ]}

    assert dfs.get_status() == DataFileSummary.Status.REJECTED
    assert TANF_T1.objects.count() == 0


@pytest.mark.django_db
def test_parse_section_mismatch(small_correct_file, dfs):
    """Test parsing of small_correct_file where the DataFile section doesn't match the rawfile section."""
    small_correct_file.section = 'Closed Case Data'
    small_correct_file.save()

    dfs.datafile = small_correct_file

    errors = parse.parse_datafile(small_correct_file, dfs)
    dfs.status = dfs.get_status()
    assert dfs.status == DataFileSummary.Status.REJECTED
    parser_errors = ParserError.objects.filter(file=small_correct_file)
    dfs.case_aggregates = aggregates.case_aggregates_by_month(
        dfs.datafile, dfs.status)
    assert dfs.case_aggregates == {'rejected': 1,
                                   'months': [
                                       {'accepted_without_errors': 'N/A',
                                        'accepted_with_errors': 'N/A',
                                        'month': 'Oct'},
                                       {'accepted_without_errors': 'N/A',
                                        'accepted_with_errors': 'N/A',
                                        'month': 'Nov'},
                                       {'accepted_without_errors': 'N/A',
                                        'accepted_with_errors': 'N/A',
                                        'month': 'Dec'}
                                   ]}
    assert parser_errors.count() == 1

    err = parser_errors.first()

    assert err.row_number == 1
    assert err.error_type == ParserErrorCategoryChoices.PRE_CHECK
    assert err.error_message == 'Data does not match the expected layout for Closed Case Data.'
    assert err.content_type is None
    assert err.object_id is None
    assert errors == {
        'document': [err]
    }


@pytest.mark.django_db
def test_parse_wrong_program_type(small_correct_file, dfs):
    """Test parsing of small_correct_file where the DataFile program type doesn't match the rawfile."""
    small_correct_file.section = 'SSP Active Case Data'
    small_correct_file.save()

    dfs.datafile = small_correct_file
    dfs.save()
    errors = parse.parse_datafile(small_correct_file, dfs)
    assert dfs.get_status() == DataFileSummary.Status.REJECTED

    parser_errors = ParserError.objects.filter(file=small_correct_file)
    assert parser_errors.count() == 1

    err = parser_errors.first()

    assert err.row_number == 1
    assert err.error_type == ParserErrorCategoryChoices.PRE_CHECK
    assert err.error_message == 'Data does not match the expected layout for SSP Active Case Data.'
    assert err.content_type is None
    assert err.object_id is None
    assert errors == {
        'document': [err]
    }

@pytest.mark.django_db
def test_parse_big_file(big_file, dfs):
    """Test parsing of ADS.E2J.FTP1.TS06."""
    expected_t1_record_count = 815
    expected_t2_record_count = 882
    expected_t3_record_count = 1376

    dfs.datafile = big_file

    parse.parse_datafile(big_file, dfs)
    dfs.status = dfs.get_status()
    assert dfs.status == DataFileSummary.Status.ACCEPTED_WITH_ERRORS
    dfs.case_aggregates = aggregates.case_aggregates_by_month(
        dfs.datafile, dfs.status)
    assert dfs.case_aggregates == {'months': [
        {'month': 'Oct', 'accepted_without_errors': 25, 'accepted_with_errors': 245},
        {'month': 'Nov', 'accepted_without_errors': 18, 'accepted_with_errors': 255},
        {'month': 'Dec', 'accepted_without_errors': 27, 'accepted_with_errors': 245}],
        'rejected': 0}

    assert TANF_T1.objects.count() == expected_t1_record_count
    assert TANF_T2.objects.count() == expected_t2_record_count
    assert TANF_T3.objects.count() == expected_t3_record_count

    search = documents.tanf.TANF_T1DataSubmissionDocument.search().query(
        'match',
        datafile__id=big_file.id
    )
    assert search.count() == expected_t1_record_count
    search.delete()

    search = documents.tanf.TANF_T2DataSubmissionDocument.search().query(
        'match',
        datafile__id=big_file.id
    )
    assert search.count() == expected_t2_record_count
    search.delete()

    search = documents.tanf.TANF_T3DataSubmissionDocument.search().query(
        'match',
        datafile__id=big_file.id
    )
    assert search.count() == expected_t3_record_count
    search.delete()


@pytest.mark.django_db
def test_parse_bad_test_file(bad_test_file, dfs):
    """Test parsing of bad_TANF_S2."""
    errors = parse.parse_datafile(bad_test_file, dfs)

    parser_errors = ParserError.objects.filter(file=bad_test_file)
    assert parser_errors.count() == 1

    err = parser_errors.first()

    assert err.row_number == 1
    assert err.error_type == ParserErrorCategoryChoices.PRE_CHECK
    assert err.error_message == 'HEADER: record length is 24 characters but must be 23.'
    assert err.content_type is None
    assert err.object_id is None
    assert errors == {
        'header': [err]
    }


@pytest.mark.django_db
def test_parse_bad_file_missing_header(bad_file_missing_header, dfs):
    """Test parsing of bad_missing_header."""
    errors = parse.parse_datafile(bad_file_missing_header, dfs)
    dfs.datafile = bad_file_missing_header
    assert dfs.get_status() == DataFileSummary.Status.REJECTED

    parser_errors = ParserError.objects.filter(file=bad_file_missing_header).order_by('created_at')

    assert parser_errors.count() == 2

    err = parser_errors.first()

    assert err.row_number == 1
    assert err.error_type == ParserErrorCategoryChoices.PRE_CHECK
    assert err.error_message == 'HEADER: record length is 14 characters but must be 23.'
    assert err.content_type is None
    assert err.object_id is None
    assert errors == {
        'header': list(parser_errors)
    }


@pytest.mark.django_db
def test_parse_bad_file_multiple_headers(bad_file_multiple_headers, dfs):
    """Test parsing of bad_two_headers."""
    bad_file_multiple_headers.year = 2024
    bad_file_multiple_headers.quarter = 'Q1'
    bad_file_multiple_headers.save()
    errors = parse.parse_datafile(bad_file_multiple_headers, dfs)
    dfs.datafile = bad_file_multiple_headers
    assert dfs.get_status() == DataFileSummary.Status.REJECTED

    parser_errors = ParserError.objects.filter(file=bad_file_multiple_headers)
    assert parser_errors.count() == 1

    err = parser_errors.first()

    assert err.row_number == 9
    assert err.error_type == ParserErrorCategoryChoices.PRE_CHECK
    assert err.error_message == "Multiple headers found."
    assert err.content_type is None
    assert err.object_id is None
    assert errors['document'] == ['Multiple headers found.']


@pytest.mark.django_db
def test_parse_big_bad_test_file(big_bad_test_file, dfs):
    """Test parsing of bad_TANF_S1."""
    big_bad_test_file.year = 2022
    big_bad_test_file.quarter = 'Q1'
    parse.parse_datafile(big_bad_test_file, dfs)

    parser_errors = ParserError.objects.filter(file=big_bad_test_file)
    assert parser_errors.count() == 1

    err = parser_errors.first()

    assert err.row_number == 3679
    assert err.error_type == ParserErrorCategoryChoices.PRE_CHECK
    assert err.error_message == 'Multiple headers found.'
    assert err.content_type is None
    assert err.object_id is None


@pytest.mark.django_db
def test_parse_bad_trailer_file(bad_trailer_file, dfs):
    """Test parsing bad_trailer_1."""
    bad_trailer_file.year = 2021
    bad_trailer_file.quarter = 'Q1'
    dfs.datafile = bad_trailer_file

    errors = parse.parse_datafile(bad_trailer_file, dfs)

    parser_errors = ParserError.objects.filter(file=bad_trailer_file)
    assert parser_errors.count() == 5

    trailer_error = parser_errors.get(row_number=3)
    assert trailer_error.error_type == ParserErrorCategoryChoices.PRE_CHECK
    assert trailer_error.error_message == 'TRAILER: record length is 11 characters but must be 23.'
    assert trailer_error.content_type is None
    assert trailer_error.object_id is None

    # reporting month/year test
    row_errors = parser_errors.filter(row_number=2)
    row_errors_list = []
    for row_error in row_errors:
        row_errors_list.append(row_error)
        assert row_error.error_type == ParserErrorCategoryChoices.PRE_CHECK
        assert trailer_error.error_message in [
            'TRAILER: record length is 11 characters but must be 23.',
            'T1: Reporting month year None does not match file reporting year:2021, quarter:Q1.']
        assert row_error.content_type is None
        assert row_error.object_id is None

    assert errors['trailer'] == [trailer_error]

    # case number validators
    for error_2_0 in errors["2_0"]:
        assert error_2_0 in row_errors_list

    row_errors = list(parser_errors.filter(row_number=2).order_by("id"))
    length_error = row_errors[0]
    assert length_error.error_type == ParserErrorCategoryChoices.PRE_CHECK
    assert length_error.error_message == "T1: record length of 7 characters is not in the range [117, 156]."
    assert length_error.content_type is None
    assert length_error.object_id is None
    assert errors == {
        'trailer': [trailer_error],
        "2_0": row_errors
    }


@pytest.mark.django_db()
def test_parse_bad_trailer_file2(bad_trailer_file_2, dfs):
    """Test parsing bad_trailer_2."""
    dfs.datafile = bad_trailer_file_2
    dfs.save()

    bad_trailer_file_2.year = 2021
    bad_trailer_file_2.quarter = 'Q1'
    errors = parse.parse_datafile(bad_trailer_file_2, dfs)

    parser_errors = ParserError.objects.filter(file=bad_trailer_file_2)
    assert parser_errors.count() == 9

    trailer_errors = list(parser_errors.filter(row_number=3).order_by('id'))

    trailer_error_1 = trailer_errors[0]
    assert trailer_error_1.error_type == ParserErrorCategoryChoices.PRE_CHECK
    assert trailer_error_1.error_message == 'TRAILER: record length is 7 characters but must be 23.'
    assert trailer_error_1.content_type is None
    assert trailer_error_1.object_id is None

    trailer_error_2 = trailer_errors[1]
    assert trailer_error_2.error_type == ParserErrorCategoryChoices.PRE_CHECK
    assert trailer_error_2.error_message == "Your file does not end with a TRAILER record."
    assert trailer_error_2.content_type is None
    assert trailer_error_2.object_id is None

    row_2_errors = parser_errors.filter(row_number=2).order_by('id')
    row_2_error = row_2_errors.first()
    assert row_2_error.error_type == ParserErrorCategoryChoices.FIELD_VALUE
    assert row_2_error.error_message == (
        'T1 Item 13 (Receives Subsidized Housing): 3 is not '
        'larger or equal to 1 and smaller or equal to 2.'
    )

    # catch-rpt-month-year-mismatches
    row_3_errors = parser_errors.filter(row_number=3)
    row_3_error_list = []

    for row_3_error in row_3_errors:
        row_3_error_list.append(row_3_error)
        assert row_3_error.error_type == ParserErrorCategoryChoices.PRE_CHECK
        assert row_3_error.error_message in {
            'T1: record length of 7 characters is not in the range [117, 156].',
            'T1: Reporting month year None does not match file reporting year:2021, quarter:Q1.',
            'TRAILER: record length is 7 characters but must be 23.',
            'T1: Case number T1trash cannot contain blanks.',
            'Your file does not end with a TRAILER record.'}
        assert row_3_error.content_type is None
        assert row_3_error.object_id is None

    errors_2_0 = errors["2_0"]
    errors_3_0 = errors["3_0"]
    error_trailer = errors["trailer"]
    row_2_error_set = set(row_2_errors)
    for error_2_0 in errors_2_0:
        assert error_2_0 in row_2_error_set
    for error_3_0 in errors_3_0:
        assert error_3_0 in row_3_error_list
    assert error_trailer == [trailer_error_1, trailer_error_2]

    # case number validators
    row_3_errors = [trailer_errors[2], trailer_errors[3]]
    length_error = row_3_errors[0]
    assert length_error.error_type == ParserErrorCategoryChoices.PRE_CHECK
    assert length_error.error_message == 'T1: record length of 7 characters is not in the range [117, 156].'
    assert length_error.content_type is None
    assert length_error.object_id is None

    trailer_error_3 = trailer_errors[3]
    assert trailer_error_3.error_type == ParserErrorCategoryChoices.PRE_CHECK
    assert trailer_error_3.error_message == 'T1: Case number T1trash cannot contain blanks.'
    assert trailer_error_3.content_type is None
    assert trailer_error_3.object_id is None

    trailer_error_4 = trailer_errors[4]
    assert trailer_error_4.error_type == ParserErrorCategoryChoices.PRE_CHECK
    assert trailer_error_4.error_message == ('T1: Reporting month year None does not '
                                             'match file reporting year:2021, quarter:Q1.')
    assert trailer_error_4.content_type is None
    assert trailer_error_4.object_id is None


@pytest.mark.django_db
def test_parse_empty_file(empty_file, dfs):
    """Test parsing of empty_file."""
    dfs.datafile = empty_file
    dfs.save()
    errors = parse.parse_datafile(empty_file, dfs)

    dfs.status = dfs.get_status()
    dfs.case_aggregates = aggregates.case_aggregates_by_month(empty_file, dfs.status)

    assert dfs.status == DataFileSummary.Status.REJECTED
    assert dfs.case_aggregates == {'rejected': 1,
                                   'months': [
                                       {'accepted_without_errors': 'N/A',
                                        'accepted_with_errors': 'N/A',
                                        'month': 'Oct'},
                                       {'accepted_without_errors': 'N/A',
                                        'accepted_with_errors': 'N/A',
                                        'month': 'Nov'},
                                       {'accepted_without_errors': 'N/A',
                                        'accepted_with_errors': 'N/A',
                                        'month': 'Dec'}
                                   ]}

    parser_errors = ParserError.objects.filter(file=empty_file).order_by('id')

    assert parser_errors.count() == 2

    err = parser_errors.first()

    assert err.row_number == 1
    assert err.error_type == ParserErrorCategoryChoices.PRE_CHECK
    assert err.error_message == 'HEADER: record length is 0 characters but must be 23.'
    assert err.content_type is None
    assert err.object_id is None
    assert errors == {
        'header': list(parser_errors)
    }


@pytest.mark.django_db
def test_parse_small_ssp_section1_datafile(small_ssp_section1_datafile, dfs):
    """Test parsing small_ssp_section1_datafile."""
    small_ssp_section1_datafile.year = 2024
    small_ssp_section1_datafile.quarter = 'Q1'

    expected_m1_record_count = 5
    expected_m2_record_count = 6
    expected_m3_record_count = 8

    dfs.datafile = small_ssp_section1_datafile
    dfs.save()
    parse.parse_datafile(small_ssp_section1_datafile, dfs)

    parser_errors = ParserError.objects.filter(file=small_ssp_section1_datafile)
    dfs.status = dfs.get_status()
    assert dfs.status == DataFileSummary.Status.ACCEPTED_WITH_ERRORS
    dfs.case_aggregates = aggregates.case_aggregates_by_month(
        dfs.datafile, dfs.status)
    assert dfs.case_aggregates["rejected"] == 1
    for month in dfs.case_aggregates['months']:
        if month['month'] == 'Oct':
            assert month['accepted_without_errors'] == 0
            assert month['accepted_with_errors'] == 5
        else:
            assert month['accepted_without_errors'] == 0
            assert month['accepted_with_errors'] == 0

    parser_errors = ParserError.objects.filter(file=small_ssp_section1_datafile)
    assert parser_errors.count() == 16
    assert SSP_M1.objects.count() == expected_m1_record_count
    assert SSP_M2.objects.count() == expected_m2_record_count
    assert SSP_M3.objects.count() == expected_m3_record_count


@pytest.mark.django_db()
def test_parse_ssp_section1_datafile(ssp_section1_datafile, dfs):
    """Test parsing ssp_section1_datafile."""
    ssp_section1_datafile.year = 2019
    ssp_section1_datafile.quarter = 'Q1'

    expected_m1_record_count = 818
    expected_m2_record_count = 989
    expected_m3_record_count = 1748

    dfs.datafile = ssp_section1_datafile
    dfs.save()

    parse.parse_datafile(ssp_section1_datafile, dfs)

    parser_errors = ParserError.objects.filter(file=ssp_section1_datafile)

    err = parser_errors.first()

    assert err.row_number == 2
    assert err.error_type == ParserErrorCategoryChoices.FIELD_VALUE
    assert err.error_message == (
        'M1 Item 11 (Receives Subsidized Housing): 3 is not larger or equal to 1 and smaller or equal to 2.'
    )
    assert err.content_type is not None
    assert err.object_id is not None

    dup_errors = parser_errors.filter(error_type=ParserErrorCategoryChoices.CASE_CONSISTENCY).order_by("id")
    assert dup_errors.count() == 2
    assert dup_errors[0].error_message == "Duplicate record detected with record type M3 at line 453. " + \
        "Record is a duplicate of the record at line number 452."
    assert dup_errors[1].error_message == "Duplicate record detected with record type M3 at line 3273. " + \
        "Record is a duplicate of the record at line number 3272."

    assert parser_errors.count() == 32488

    assert SSP_M1.objects.count() == expected_m1_record_count
    assert SSP_M2.objects.count() == expected_m2_record_count
    assert SSP_M3.objects.count() == expected_m3_record_count


@pytest.mark.django_db
def test_parse_tanf_section1_datafile(small_tanf_section1_datafile, dfs):
    """Test parsing of small_tanf_section1_datafile and validate T2 model data."""
    small_tanf_section1_datafile.year = 2021
    small_tanf_section1_datafile.quarter = 'Q1'
    dfs.datafile = small_tanf_section1_datafile

    parse.parse_datafile(small_tanf_section1_datafile, dfs)

    dfs.status = dfs.get_status()
    assert dfs.status == DataFileSummary.Status.ACCEPTED_WITH_ERRORS
    dfs.case_aggregates = aggregates.case_aggregates_by_month(
        dfs.datafile, dfs.status)
    assert dfs.case_aggregates == {'months': [
        {'month': 'Oct', 'accepted_without_errors': 4, 'accepted_with_errors': 1},
        {'month': 'Nov', 'accepted_without_errors': 0, 'accepted_with_errors': 0},
        {'month': 'Dec', 'accepted_without_errors': 0, 'accepted_with_errors': 0}],
        'rejected': 0}

    assert TANF_T2.objects.count() == 5

    t2_models = TANF_T2.objects.all()

    t2 = t2_models[0]
    assert t2.RPT_MONTH_YEAR == 202010
    assert t2.CASE_NUMBER == '11111111112'
    assert t2.FAMILY_AFFILIATION == 1
    assert t2.OTHER_UNEARNED_INCOME == '0291'

    t2_2 = t2_models[1]
    assert t2_2.RPT_MONTH_YEAR == 202010
    assert t2_2.CASE_NUMBER == '11111111115'
    assert t2_2.FAMILY_AFFILIATION == 2
    assert t2_2.OTHER_UNEARNED_INCOME == '0000'


@pytest.mark.django_db()
def test_parse_tanf_section1_datafile_obj_counts(small_tanf_section1_datafile, dfs):
    """Test parsing of small_tanf_section1_datafile in general."""
    small_tanf_section1_datafile.year = 2021
    small_tanf_section1_datafile.quarter = 'Q1'

    dfs.datafile = small_tanf_section1_datafile
    dfs.save()

    parse.parse_datafile(small_tanf_section1_datafile, dfs)

    assert TANF_T1.objects.count() == 5
    assert TANF_T2.objects.count() == 5
    assert TANF_T3.objects.count() == 6


@pytest.mark.django_db()
def test_parse_tanf_section1_datafile_t3s(small_tanf_section1_datafile, dfs):
    """Test parsing of small_tanf_section1_datafile and validate T3 model data."""
    small_tanf_section1_datafile.year = 2021
    small_tanf_section1_datafile.quarter = 'Q1'

    dfs.datafile = small_tanf_section1_datafile
    dfs.save()

    parse.parse_datafile(small_tanf_section1_datafile, dfs)

    assert TANF_T3.objects.count() == 6

    t3_models = TANF_T3.objects.all()
    t3_1 = t3_models[0]
    assert t3_1.RPT_MONTH_YEAR == 202010
    assert t3_1.CASE_NUMBER == '11111111112'
    assert t3_1.FAMILY_AFFILIATION == 1
    assert t3_1.GENDER == 2
    assert t3_1.EDUCATION_LEVEL == '98'

    t3_5 = t3_models[4]
    assert t3_5.RPT_MONTH_YEAR == 202010
    assert t3_5.CASE_NUMBER == '11111111151'
    assert t3_5.FAMILY_AFFILIATION == 1
    assert t3_5.GENDER == 1
    assert t3_5.EDUCATION_LEVEL == '98'


@pytest.mark.django_db()
@pytest.mark.skip(reason="long runtime")  # big_files
def test_parse_super_big_s1_file(super_big_s1_file, dfs):
    """Test parsing of super_big_s1_file and validate all T1/T2/T3 records are created."""
    super_big_s1_file.year = 2023
    super_big_s1_file.quarter = 'Q2'
    super_big_s1_file.save()

    dfs.datafile = super_big_s1_file
    dfs.save()

    parse.parse_datafile(super_big_s1_file, dfs)
    expected_t1_record_count = 96607
    expected_t2_record_count = 112753
    expected_t3_record_count = 172525

    assert TANF_T1.objects.count() == expected_t1_record_count
    assert TANF_T2.objects.count() == expected_t2_record_count
    assert TANF_T3.objects.count() == expected_t3_record_count

    search = documents.tanf.TANF_T1DataSubmissionDocument.search().query(
        'match',
        datafile__id=super_big_s1_file.id
    )
    assert search.count() == expected_t1_record_count
    search.delete()

    search = documents.tanf.TANF_T2DataSubmissionDocument.search().query(
        'match',
        datafile__id=super_big_s1_file.id
    )
    assert search.count() == expected_t2_record_count
    search.delete()

    search = documents.tanf.TANF_T3DataSubmissionDocument.search().query(
        'match',
        datafile__id=super_big_s1_file.id
    )
    assert search.count() == expected_t3_record_count
    search.delete()


@pytest.mark.django_db()
def test_parse_big_s1_file_with_rollback(big_s1_rollback_file, dfs):
    """Test parsing of big_s1_rollback_file.

    Validate all T1/T2/T3 records are not created due to multiple headers.
    """
    big_s1_rollback_file.year = 2023
    big_s1_rollback_file.quarter = 'Q2'
    big_s1_rollback_file.save()

    dfs.datafile = big_s1_rollback_file
    dfs.save()

    parse.parse_datafile(big_s1_rollback_file, dfs)

    parser_errors = ParserError.objects.filter(file=big_s1_rollback_file)
    assert parser_errors.count() == 1

    err = parser_errors.first()

    assert err.row_number == 13609
    assert err.error_type == ParserErrorCategoryChoices.PRE_CHECK
    assert err.error_message == 'Multiple headers found.'
    assert err.content_type is None
    assert err.object_id is None

    assert TANF_T1.objects.count() == 0
    assert TANF_T2.objects.count() == 0
    assert TANF_T3.objects.count() == 0

    search = documents.tanf.TANF_T1DataSubmissionDocument.search().query(
        'match',
        datafile__id=big_s1_rollback_file.id
    )
    assert search.count() == 0

    search = documents.tanf.TANF_T2DataSubmissionDocument.search().query(
        'match',
        datafile__id=big_s1_rollback_file.id
    )
    assert search.count() == 0

    search = documents.tanf.TANF_T3DataSubmissionDocument.search().query(
        'match',
        datafile__id=big_s1_rollback_file.id
    )
    assert search.count() == 0


@pytest.mark.django_db
def test_parse_bad_tfs1_missing_required(bad_tanf_s1__row_missing_required_field, dfs):
    """Test parsing a bad TANF Section 1 submission where a row is missing required data."""
    bad_tanf_s1__row_missing_required_field.year = 2021
    bad_tanf_s1__row_missing_required_field.quarter = 'Q1'

    dfs.datafile = bad_tanf_s1__row_missing_required_field
    dfs.save()

    parse.parse_datafile(bad_tanf_s1__row_missing_required_field, dfs)

    assert dfs.get_status() == DataFileSummary.Status.REJECTED

    parser_errors = ParserError.objects.filter(
        file=bad_tanf_s1__row_missing_required_field)

    assert parser_errors.count() == 5

    error_message = 'T1: Reporting month year None does not match file reporting year:2021, quarter:Q1.'
    row_2_error = parser_errors.get(row_number=2, error_message=error_message)
    assert row_2_error.error_type == ParserErrorCategoryChoices.PRE_CHECK
    assert row_2_error.error_message == error_message

    error_message = 'T2: Reporting month year None does not match file reporting year:2021, quarter:Q1.'
    row_3_error = parser_errors.get(row_number=3, error_message=error_message)
    assert row_3_error.error_type == ParserErrorCategoryChoices.PRE_CHECK
    assert row_3_error.error_message == error_message

    error_message = 'T3: Reporting month year None does not match file reporting year:2021, quarter:Q1.'
    row_4_error = parser_errors.get(row_number=4, error_message=error_message)
    assert row_4_error.error_type == ParserErrorCategoryChoices.PRE_CHECK
    assert row_4_error.error_message == error_message

    error_message = 'Unknown Record_Type was found.'
    row_5_error = parser_errors.get(row_number=5, error_message=error_message)
    assert row_5_error.error_type == ParserErrorCategoryChoices.PRE_CHECK
    assert row_5_error.error_message == error_message
    assert row_5_error.content_type is None
    assert row_5_error.object_id is None


@pytest.mark.django_db()
def test_parse_bad_ssp_s1_missing_required(bad_ssp_s1__row_missing_required_field, dfs):
    """Test parsing a bad TANF Section 1 submission where a row is missing required data."""
    bad_ssp_s1__row_missing_required_field.year = 2019
    bad_ssp_s1__row_missing_required_field.quarter = 'Q1'

    dfs.datafile = bad_ssp_s1__row_missing_required_field
    dfs.save()

    parse.parse_datafile(bad_ssp_s1__row_missing_required_field, dfs)

    parser_errors = ParserError.objects.filter(file=bad_ssp_s1__row_missing_required_field)
    assert parser_errors.count() == 6

    row_2_error = parser_errors.get(
        row_number=2,
        error_message__contains='Reporting month year None does not match file reporting year:2019, quarter:Q1.'
    )
    assert row_2_error.error_type == ParserErrorCategoryChoices.PRE_CHECK

    row_3_error = parser_errors.get(
        row_number=3,
        error_message__contains='Reporting month year None does not match file reporting year:2019, quarter:Q1.'
    )
    assert row_3_error.error_type == ParserErrorCategoryChoices.PRE_CHECK

    row_4_error = parser_errors.get(
        row_number=4,
        error_message__contains='Reporting month year None does not match file reporting year:2019, quarter:Q1.'
    )
    assert row_4_error.error_type == ParserErrorCategoryChoices.PRE_CHECK

    error_message = 'Reporting month year None does not match file reporting year:2019, quarter:Q1.'
    rpt_month_errors = parser_errors.filter(error_message__contains=error_message)
    assert len(rpt_month_errors) == 3
    for i, e in enumerate(rpt_month_errors):
        assert e.error_type == ParserErrorCategoryChoices.PRE_CHECK
        assert error_message.format(i + 1) in e.error_message
        assert e.object_id is None

    row_5_error = parser_errors.get(
        row_number=5,
        error_message='Unknown Record_Type was found.'
    )
    assert row_5_error.error_type == ParserErrorCategoryChoices.PRE_CHECK
    assert row_5_error.content_type is None
    assert row_5_error.object_id is None

    trailer_error = parser_errors.get(
        row_number=6,
        error_message='TRAILER: record length is 15 characters but must be 23.'
    )
    assert trailer_error.error_type == ParserErrorCategoryChoices.PRE_CHECK
    assert trailer_error.content_type is None
    assert trailer_error.object_id is None

@pytest.mark.django_db
def test_dfs_set_case_aggregates(small_correct_file, dfs):
    """Test that the case aggregates are set correctly."""
    small_correct_file.year = 2020
    small_correct_file.quarter = 'Q3'
    small_correct_file.section = 'Active Case Data'
    small_correct_file.save()
    # this still needs to execute to create db objects to be queried
    parse.parse_datafile(small_correct_file, dfs)
    dfs.file = small_correct_file
    dfs.status = dfs.get_status()
    dfs.case_aggregates = aggregates.case_aggregates_by_month(
        small_correct_file, dfs.status)

    for month in dfs.case_aggregates['months']:
        if month['month'] == 'Oct':
            assert month['accepted_without_errors'] == 1
            assert month['accepted_with_errors'] == 0


@pytest.mark.django_db
def test_get_schema_options(dfs):
    """Test use-cases for translating strings to named object references."""
    '''
    text -> section
    text -> models{} YES
    text -> model YES
    datafile -> model
        ^ section -> program -> model
    datafile -> text
    model -> text YES
    section -> text

    text**: input string from the header/file
    '''

    # from text:
    schema = parse.get_schema_manager('T1xx', 'A', 'TAN')
    assert isinstance(schema, aggregates.SchemaManager)
    assert schema == schema_defs.tanf.t1

    # get model
    models = schema_defs.utils.get_program_models('TAN', 'A')
    assert models == {
        'T1': schema_defs.tanf.t1,
        'T2': schema_defs.tanf.t2,
        'T3': schema_defs.tanf.t3,
    }

    model = schema_defs.utils.get_program_model('TAN', 'A', 'T1')
    assert model == schema_defs.tanf.t1
    # get section
    section = schema_defs.utils.get_section_reference('TAN', 'C')
    assert section == DataFile.Section.CLOSED_CASE_DATA

    # from datafile:
    # get model(s)
    # get section str

    # from model:
    # get text
    # get section str
    # get ref section


@pytest.mark.django_db()
def test_parse_small_tanf_section2_file(small_tanf_section2_file, dfs):
    """Test parsing a small TANF Section 2 submission."""
    small_tanf_section2_file.year = 2021
    small_tanf_section2_file.quarter = 'Q1'

    dfs.datafile = small_tanf_section2_file
    dfs.save()

    parse.parse_datafile(small_tanf_section2_file, dfs)

    assert TANF_T4.objects.all().count() == 1
    assert TANF_T5.objects.all().count() == 1

    parser_errors = ParserError.objects.filter(file=small_tanf_section2_file)

    assert parser_errors.count() == 0

    t4 = TANF_T4.objects.first()
    t5 = TANF_T5.objects.first()

    assert t4.DISPOSITION == 1
    assert t4.REC_SUB_CC == 3

    assert t5.GENDER == 2
    assert t5.AMOUNT_UNEARNED_INCOME == '0000'


@pytest.mark.django_db()
def test_parse_tanf_section2_file(tanf_section2_file, dfs):
    """Test parsing TANF Section 2 submission."""
    tanf_section2_file.year = 2021
    tanf_section2_file.quarter = 'Q1'

    dfs.datafile = tanf_section2_file
    dfs.save()

    parse.parse_datafile(tanf_section2_file, dfs)

    assert TANF_T4.objects.all().count() == 206
    assert TANF_T5.objects.all().count() == 548

    parser_errors = ParserError.objects.filter(file=tanf_section2_file)

    err = parser_errors.first()
    assert err.error_type == ParserErrorCategoryChoices.FIELD_VALUE
    assert err.error_message == (
        "T4 Item 10 (Received Subsidized Housing): 3 "
        "is not larger or equal to 1 and smaller or equal to 2."
    )
    assert err.content_type.model == "tanf_t4"
    assert err.object_id is not None


@pytest.mark.django_db()
def test_parse_tanf_section3_file(tanf_section3_file, dfs):
    """Test parsing TANF Section 3 submission."""
    tanf_section3_file.year = 2022
    tanf_section3_file.quarter = 'Q1'

    dfs.datafile = tanf_section3_file

    parse.parse_datafile(tanf_section3_file, dfs)

    dfs.status = dfs.get_status()
    dfs.case_aggregates = aggregates.total_errors_by_month(
        dfs.datafile, dfs.status)
    assert dfs.case_aggregates == {"months": [
        {"month": "Oct", "total_errors": 0},
        {"month": "Nov", "total_errors": 0},
        {"month": "Dec", "total_errors": 0}
    ]}

    assert dfs.get_status() == DataFileSummary.Status.ACCEPTED

    assert TANF_T6.objects.all().count() == 3

    parser_errors = ParserError.objects.filter(file=tanf_section3_file)
    assert parser_errors.count() == 0

    t6_objs = TANF_T6.objects.all().order_by('NUM_APPROVED')

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
def test_parse_tanf_section1_blanks_file(tanf_section1_file_with_blanks, dfs):
    """Test section 1 fields that are allowed to have blanks."""
    tanf_section1_file_with_blanks.year = 2021
    tanf_section1_file_with_blanks.quarter = 'Q1'

    dfs.datafile = tanf_section1_file_with_blanks
    dfs.save()

    parse.parse_datafile(tanf_section1_file_with_blanks, dfs)

    parser_errors = ParserError.objects.filter(file=tanf_section1_file_with_blanks)

    assert parser_errors.count() == 22

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
def test_parse_tanf_section4_file(tanf_section4_file, dfs):
    """Test parsing TANF Section 4 submission."""
    tanf_section4_file.year = 2022
    tanf_section4_file.quarter = 'Q1'

    dfs.datafile = tanf_section4_file

    parse.parse_datafile(tanf_section4_file, dfs)

    dfs.status = dfs.get_status()
    dfs.case_aggregates = aggregates.total_errors_by_month(
        dfs.datafile, dfs.status)
    assert dfs.case_aggregates == {"months": [
        {"month": "Oct", "total_errors": 0},
        {"month": "Nov", "total_errors": 0},
        {"month": "Dec", "total_errors": 0}
    ]}

    assert dfs.get_status() == DataFileSummary.Status.ACCEPTED

    assert TANF_T7.objects.all().count() == 18

    parser_errors = ParserError.objects.filter(file=tanf_section4_file)
    assert parser_errors.count() == 0

    t7_objs = TANF_T7.objects.all().order_by('FAMILIES_MONTH')

    first = t7_objs.first()
    sixth = t7_objs[5]

    assert first.RPT_MONTH_YEAR == 202111
    assert sixth.RPT_MONTH_YEAR == 202112

    assert first.TDRS_SECTION_IND == '2'
    assert sixth.TDRS_SECTION_IND == '2'

    assert first.FAMILIES_MONTH == 274
    assert sixth.FAMILIES_MONTH == 499


@pytest.mark.django_db()
def test_parse_bad_tanf_section4_file(bad_tanf_section4_file, dfs):
    """Test parsing TANF Section 4 submission when no records are created."""
    bad_tanf_section4_file.year = 2021
    bad_tanf_section4_file.quarter = 'Q1'

    dfs.datafile = bad_tanf_section4_file

    parse.parse_datafile(bad_tanf_section4_file, dfs)

    dfs.status = dfs.get_status()
    dfs.case_aggregates = aggregates.total_errors_by_month(dfs.datafile, dfs.status)

    assert dfs.case_aggregates == {'months': [
        {'month': 'Oct', 'total_errors': 'N/A'},
        {'month': 'Nov', 'total_errors': 'N/A'},
        {'month': 'Dec', 'total_errors': 'N/A'}
    ]}

    assert dfs.get_status() == DataFileSummary.Status.REJECTED

    assert TANF_T7.objects.all().count() == 0

    parser_errors = ParserError.objects.filter(file=bad_tanf_section4_file).order_by('id')
    assert parser_errors.count() == 2

    error = parser_errors.first()
    error.error_message == "Value length 151 does not match 247."
    error.error_type == ParserErrorCategoryChoices.PRE_CHECK

    error = parser_errors[1]
    error.error_message == "No records created."
    error.error_type == ParserErrorCategoryChoices.PRE_CHECK


@pytest.mark.django_db()
def test_parse_ssp_section4_file(ssp_section4_file, dfs):
    """Test parsing SSP Section 4 submission."""
    ssp_section4_file.year = 2022
    ssp_section4_file.quarter = 'Q1'

    dfs.datafile = ssp_section4_file

    parse.parse_datafile(ssp_section4_file, dfs)

    m7_objs = SSP_M7.objects.all().order_by('FAMILIES_MONTH')

    dfs.status = dfs.get_status()
    dfs.case_aggregates = aggregates.total_errors_by_month(
        dfs.datafile, dfs.status)
    assert dfs.case_aggregates == {"months": [
        {"month": "Oct", "total_errors": 0},
        {"month": "Nov", "total_errors": 0},
        {"month": "Dec", "total_errors": 0}
    ]}

    assert m7_objs.count() == 12

    first = m7_objs.first()
    assert first.RPT_MONTH_YEAR == 202110
    assert first.FAMILIES_MONTH == 748


@pytest.mark.django_db()
def test_parse_ssp_section2_rec_oadsi_file(ssp_section2_rec_oadsi_file, dfs):
    """Test parsing SSP Section 2 REC_OADSI."""
    ssp_section2_rec_oadsi_file.year = 2019
    ssp_section2_rec_oadsi_file.quarter = 'Q1'

    dfs.datafile = ssp_section2_rec_oadsi_file

    parse.parse_datafile(ssp_section2_rec_oadsi_file, dfs)
    parser_errors = ParserError.objects.filter(file=ssp_section2_rec_oadsi_file)

    assert parser_errors.count() == 0


@pytest.mark.django_db()
def test_parse_ssp_section2_file(ssp_section2_file, dfs):
    """Test parsing SSP Section 2 submission."""
    ssp_section2_file.year = 2019
    ssp_section2_file.quarter = 'Q1'

    dfs.datafile = ssp_section2_file

    parse.parse_datafile(ssp_section2_file, dfs)

    dfs.status = dfs.get_status()
    dfs.case_aggregates = aggregates.case_aggregates_by_month(
        dfs.datafile, dfs.status)
    for dfs_case_aggregate in dfs.case_aggregates['months']:
        assert dfs_case_aggregate['accepted_without_errors'] == 0
        assert dfs_case_aggregate['accepted_with_errors'] in [75, 78]
        assert dfs_case_aggregate['month'] in ['Oct', 'Nov', 'Dec']
    assert dfs.get_status() == DataFileSummary.Status.PARTIALLY_ACCEPTED

    m4_objs = SSP_M4.objects.all().order_by('id')
    m5_objs = SSP_M5.objects.all().order_by('AMOUNT_EARNED_INCOME')

    expected_m4_count = 231
    expected_m5_count = 703

    assert SSP_M4.objects.count() == expected_m4_count
    assert SSP_M5.objects.count() == expected_m5_count

    search = documents.ssp.SSP_M4DataSubmissionDocument.search().query(
        'match',
        datafile__id=ssp_section2_file.id
    )
    assert search.count() == expected_m4_count
    search.delete()

    search = documents.ssp.SSP_M5DataSubmissionDocument.search().query(
        'match',
        datafile__id=ssp_section2_file.id
    )
    assert search.count() == expected_m5_count
    search.delete()

    m4 = m4_objs.first()
    assert m4.DISPOSITION == 1
    assert m4.REC_SUB_CC == 3

    m5 = m5_objs.first()
    assert m5.FAMILY_AFFILIATION == 1
    assert m5.AMOUNT_EARNED_INCOME == '0000'
    assert m5.AMOUNT_UNEARNED_INCOME == '0000'


@pytest.mark.django_db()
def test_parse_ssp_section3_file(ssp_section3_file, dfs):
    """Test parsing TANF Section 3 submission."""
    ssp_section3_file.year = 2022
    ssp_section3_file.quarter = 'Q1'

    dfs.datafile = ssp_section3_file

    parse.parse_datafile(ssp_section3_file, dfs)

    dfs.status = dfs.get_status()
    dfs.case_aggregates = aggregates.total_errors_by_month(
        dfs.datafile, dfs.status)
    assert dfs.case_aggregates == {"months": [
        {"month": "Oct", "total_errors": 0},
        {"month": "Nov", "total_errors": 0},
        {"month": "Dec", "total_errors": 0}
    ]}

    assert dfs.get_status() == DataFileSummary.Status.ACCEPTED

    m6_objs = SSP_M6.objects.all().order_by('RPT_MONTH_YEAR')
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
def test_rpt_month_year_mismatch(header_datafile, dfs):
    """Test that the rpt_month_year mismatch error is raised."""
    datafile = header_datafile

    datafile.section = 'Active Case Data'
    # test_datafile fixture uses create_test_data_file which assigns
    # a default year / quarter of 2021 / Q1
    datafile.year = 2021
    datafile.quarter = 'Q1'
    datafile.save()

    dfs.datafile = header_datafile
    dfs.save()

    parse.parse_datafile(datafile, dfs)

    parser_errors = ParserError.objects.filter(file=datafile)
    assert parser_errors.count() == 2
    assert parser_errors.first().error_type == ParserErrorCategoryChoices.CASE_CONSISTENCY

    datafile.year = 2023
    datafile.save()

    parse.parse_datafile(datafile, dfs)

    parser_errors = ParserError.objects.filter(file=datafile).order_by('-id')
    assert parser_errors.count() == 3

    err = parser_errors.first()
    assert err.error_type == ParserErrorCategoryChoices.PRE_CHECK
    assert err.error_message == "Submitted reporting year:2020, quarter:Q4 doesn't" + \
        " match file reporting year:2023, quarter:Q1."


@pytest.mark.django_db()
def test_parse_tribal_section_1_file(tribal_section_1_file, dfs):
    """Test parsing Tribal TANF Section 1 submission."""
    tribal_section_1_file.year = 2022
    tribal_section_1_file.quarter = 'Q1'
    tribal_section_1_file.save()

    dfs.datafile = tribal_section_1_file

    parse.parse_datafile(tribal_section_1_file, dfs)

    dfs.status = dfs.get_status()
    assert dfs.status == DataFileSummary.Status.ACCEPTED
    dfs.case_aggregates = aggregates.case_aggregates_by_month(
        dfs.datafile, dfs.status)
    assert dfs.case_aggregates == {'rejected': 0,
                                   'months': [{'month': 'Oct', 'accepted_without_errors': 1, 'accepted_with_errors': 0},
                                              {'month': 'Nov', 'accepted_without_errors': 0, 'accepted_with_errors': 0},
                                              {'month': 'Dec', 'accepted_without_errors': 0, 'accepted_with_errors': 0}
                                              ]}

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
    assert t2.MONTHS_FED_TIME_LIMIT == '  0'
    assert t3.EDUCATION_LEVEL == '98'


@pytest.mark.django_db()
def test_parse_tribal_section_1_inconsistency_file(tribal_section_1_inconsistency_file, dfs):
    """Test parsing inconsistent Tribal TANF Section 1 submission."""
    parse.parse_datafile(tribal_section_1_inconsistency_file, dfs)

    assert Tribal_TANF_T1.objects.all().count() == 0

    parser_errors = ParserError.objects.filter(file=tribal_section_1_inconsistency_file)
    assert parser_errors.count() == 1

    assert parser_errors.first().error_message == "Tribe Code (142) inconsistency with Program Type (TAN) " + \
        "and FIPS Code (01)."


@pytest.mark.django_db()
def test_parse_tribal_section_2_file(tribal_section_2_file, dfs):
    """Test parsing Tribal TANF Section 2 submission."""
    tribal_section_2_file.year = 2020
    tribal_section_2_file.quarter = 'Q1'

    dfs.datafile = tribal_section_2_file

    parse.parse_datafile(tribal_section_2_file, dfs)

    dfs.status = dfs.get_status()
    dfs.case_aggregates = aggregates.case_aggregates_by_month(
        dfs.datafile, dfs.status)
    assert dfs.case_aggregates == {'rejected': 0,
                                   'months': [
                                       {'accepted_without_errors': 3,
                                           'accepted_with_errors': 0, 'month': 'Oct'},
                                       {'accepted_without_errors': 3,
                                           'accepted_with_errors': 0, 'month': 'Nov'},
                                       {'accepted_without_errors': 0,
                                           'accepted_with_errors': 0, 'month': 'Dec'}
                                   ]}

    assert dfs.get_status() == DataFileSummary.Status.ACCEPTED

    assert Tribal_TANF_T4.objects.all().count() == 6
    assert Tribal_TANF_T5.objects.all().count() == 13

    t4_objs = Tribal_TANF_T4.objects.all().order_by("CLOSURE_REASON")
    t5_objs = Tribal_TANF_T5.objects.all().order_by("COUNTABLE_MONTH_FED_TIME")

    t4 = t4_objs.first()
    t5 = t5_objs.last()

    assert t4.CLOSURE_REASON == '15'
    assert t5.COUNTABLE_MONTH_FED_TIME == '  8'


@pytest.mark.django_db()
def test_parse_tribal_section_3_file(tribal_section_3_file, dfs):
    """Test parsing Tribal TANF Section 3 submission."""
    tribal_section_3_file.year = 2022
    tribal_section_3_file.quarter = 'Q1'

    dfs.datafile = tribal_section_3_file

    parse.parse_datafile(tribal_section_3_file, dfs)

    dfs.status = dfs.get_status()
    dfs.case_aggregates = aggregates.total_errors_by_month(
        dfs.datafile, dfs.status)
    assert dfs.case_aggregates == {"months": [
        {"month": "Oct", "total_errors": 0},
        {"month": "Nov", "total_errors": 0},
        {"month": "Dec", "total_errors": 0}
    ]}

    assert dfs.get_status() == DataFileSummary.Status.ACCEPTED

    assert Tribal_TANF_T6.objects.all().count() == 3

    t6_objs = Tribal_TANF_T6.objects.all().order_by("NUM_APPLICATIONS")

    t6 = t6_objs.first()

    assert t6.NUM_APPLICATIONS == 1
    assert t6.NUM_FAMILIES == 41
    assert t6.NUM_CLOSED_CASES == 3


@pytest.mark.django_db()
def test_parse_tribal_section_4_file(tribal_section_4_file, dfs):
    """Test parsing Tribal TANF Section 4 submission."""
    tribal_section_4_file.year = 2022
    tribal_section_4_file.quarter = 'Q1'

    dfs.datafile = tribal_section_4_file

    parse.parse_datafile(tribal_section_4_file, dfs)

    dfs.status = dfs.get_status()
    dfs.case_aggregates = aggregates.total_errors_by_month(
        dfs.datafile, dfs.status)
    assert dfs.case_aggregates == {"months": [
        {"month": "Oct", "total_errors": 0},
        {"month": "Nov", "total_errors": 0},
        {"month": "Dec", "total_errors": 0}
    ]}

    assert Tribal_TANF_T7.objects.all().count() == 18

    t7_objs = Tribal_TANF_T7.objects.all().order_by('FAMILIES_MONTH')

    first = t7_objs.first()
    sixth = t7_objs[5]

    assert first.RPT_MONTH_YEAR == 202111
    assert sixth.RPT_MONTH_YEAR == 202112

    assert first.TDRS_SECTION_IND == '2'
    assert sixth.TDRS_SECTION_IND == '2'

    assert first.FAMILIES_MONTH == 274
    assert sixth.FAMILIES_MONTH == 499


@pytest.mark.parametrize('file_fixture, result, number_of_errors, error_message',
                         [('second_child_only_space_t3_file', 1, 0, ''),
                          ('one_child_t3_file', 1, 0, ''),
                          ('t3_file', 1, 0, ''),
                          ('t3_file_two_child', 1, 1,
                           'The second child record is too short at 97 characters' +
                           ' and must be at least 101 characters.'),
                          ('t3_file_two_child_with_space_filled', 2, 0, ''),
                          ('two_child_second_filled', 2, 8,
                           'T3 Item 68 (Date of Birth): Year 6    must be larger than 1900.'),
                          ('t3_file_zero_filled_second', 1, 0, '')])
@pytest.mark.django_db()
def test_misformatted_multi_records(file_fixture, result, number_of_errors, error_message, request, dfs):
    """Test that (not space filled) multi-records are caught."""
    file_fixture = request.getfixturevalue(file_fixture)
    dfs.datafile = file_fixture
    parse.parse_datafile(file_fixture, dfs)
    parser_errors = ParserError.objects.filter(file=file_fixture)
    t3 = TANF_T3.objects.all()
    assert t3.count() == result

    parser_errors = ParserError.objects.all()
    assert parser_errors.count() == number_of_errors
    if number_of_errors > 0:
        error_messages = [parser_error.error_message for parser_error in parser_errors]
        assert error_message in error_messages

    parser_errors = ParserError.objects.all().exclude(
        # exclude extraneous cat 4 errors
        error_type=ParserErrorCategoryChoices.CASE_CONSISTENCY
    ).exclude(error_message="No records created.")

    assert parser_errors.count() == number_of_errors


@pytest.mark.django_db()
def test_empty_t4_t5_values(t4_t5_empty_values, dfs):
    """Test that empty field values for un-required fields parse."""
    dfs.datafile = t4_t5_empty_values
    parse.parse_datafile(t4_t5_empty_values, dfs)
    parser_errors = ParserError.objects.filter(file=t4_t5_empty_values)
    t4 = TANF_T4.objects.all()
    t5 = TANF_T5.objects.all()
    assert t4.count() == 1
    assert t4[0].STRATUM is None
    logger.info(t4[0].__dict__)
    assert t5.count() == 1
    assert parser_errors[0].error_message == (
        "T4 Item 10 (Received Subsidized Housing): 3 is "
        "not larger or equal to 1 and smaller or equal to 2."
    )


@pytest.mark.django_db()
def test_parse_t2_invalid_dob(t2_invalid_dob_file, dfs):
    """Test parsing a TANF T2 record with an invalid DOB."""
    dfs.datafile = t2_invalid_dob_file
    t2_invalid_dob_file.year = 2021
    t2_invalid_dob_file.quarter = 'Q1'
    dfs.save()

    parse.parse_datafile(t2_invalid_dob_file, dfs)

    parser_errors = ParserError.objects.filter(file=t2_invalid_dob_file).order_by("pk")

    month_error = parser_errors[2]
    year_error = parser_errors[1]
    digits_error = parser_errors[0]

    assert month_error.error_message == "T2 Item 32 (Date of Birth): $9 is not a valid month."
    assert year_error.error_message == "T2 Item 32 (Date of Birth): Year Q897 must be larger than 1900."
    assert digits_error.error_message == "T2 Item 32 (Date of Birth): Q897$9 3 does not have exactly 8 digits."

@pytest.mark.django_db
def test_bulk_create_returns_rollback_response_on_bulk_index_exception(small_correct_file, mocker, dfs):
    """Test bulk_create_records returns (False, [unsaved_records]) on BulkIndexException."""
    mocker.patch(
        'tdpservice.search_indexes.documents.tanf.TANF_T1DataSubmissionDocument.update',
        side_effect=BulkIndexError('indexing exception')
    )

    # create some records, don't save them
    records = {
        documents.tanf.TANF_T1DataSubmissionDocument(): [TANF_T1()],
        documents.tanf.TANF_T2DataSubmissionDocument(): [TANF_T2()],
        documents.tanf.TANF_T3DataSubmissionDocument(): [TANF_T3()]
    }

    all_created, unsaved_records = parse.bulk_create_records(
        records,
        line_number=1,
        header_count=1,
        datafile=small_correct_file,
        dfs=dfs,
        flush=True
    )

    assert LogEntry.objects.all().count() == 1

    log = LogEntry.objects.get()
    assert log.change_message == "Encountered error while indexing datafile documents: indexing exception"

    assert all_created is True
    assert len(unsaved_records.items()) == 0
    assert TANF_T1.objects.all().count() == 1
    assert TANF_T2.objects.all().count() == 1
    assert TANF_T3.objects.all().count() == 1


@pytest.mark.django_db()
def test_parse_tanf_section4_file_with_errors(tanf_section_4_file_with_errors, dfs):
    """Test parsing TANF Section 4 submission."""
    tanf_section_4_file_with_errors.year = 2022
    tanf_section_4_file_with_errors.quarter = 'Q1'
    dfs.datafile = tanf_section_4_file_with_errors

    parse.parse_datafile(tanf_section_4_file_with_errors, dfs)

    dfs.status = dfs.get_status()
    dfs.case_aggregates = aggregates.total_errors_by_month(
        dfs.datafile, dfs.status)
    assert dfs.case_aggregates == {"months": [
        {"month": "Oct", "total_errors": 2},
        {"month": "Nov", "total_errors": 2},
        {"month": "Dec", "total_errors": 2}
    ]}

    assert dfs.get_status() == DataFileSummary.Status.ACCEPTED_WITH_ERRORS

    assert TANF_T7.objects.all().count() == 18

    parser_errors = ParserError.objects.filter(file=tanf_section_4_file_with_errors)

    assert parser_errors.count() == 6

    t7_objs = TANF_T7.objects.all().order_by('FAMILIES_MONTH')

    first = t7_objs.first()
    sixth = t7_objs[5]

    assert first.RPT_MONTH_YEAR == 202111
    assert sixth.RPT_MONTH_YEAR == 202110

    assert first.TDRS_SECTION_IND == '1'
    assert sixth.TDRS_SECTION_IND == '1'

    assert first.FAMILIES_MONTH == 0
    assert sixth.FAMILIES_MONTH == 446


@pytest.mark.django_db()
def test_parse_no_records_file(no_records_file, dfs):
    """Test parsing TANF Section 4 submission."""
    dfs.datafile = no_records_file
    parse.parse_datafile(no_records_file, dfs)

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
def test_parse_aggregates_rejected_datafile(aggregates_rejected_datafile, dfs):
    """Test record rejection counting when record has more than one preparsing error."""
    aggregates_rejected_datafile.year = 2021
    aggregates_rejected_datafile.quarter = 'Q1'
    dfs.datafile = aggregates_rejected_datafile

    parse.parse_datafile(aggregates_rejected_datafile, dfs)

    dfs.status = dfs.get_status()
    assert dfs.status == DataFileSummary.Status.REJECTED
    dfs.case_aggregates = aggregates.case_aggregates_by_month(
        dfs.datafile, dfs.status)
    assert dfs.case_aggregates == {'months': [
        {'month': 'Oct', 'accepted_without_errors': "N/A", 'accepted_with_errors': "N/A"},
        {'month': 'Nov', 'accepted_without_errors': "N/A", 'accepted_with_errors': "N/A"},
        {'month': 'Dec', 'accepted_without_errors': "N/A", 'accepted_with_errors': "N/A"}],
        'rejected': 1}

    errors = ParserError.objects.filter(file=aggregates_rejected_datafile)

    assert errors.count() == 3
    for error in errors:
        assert error.error_type == ParserErrorCategoryChoices.PRE_CHECK
    assert errors.filter(row_number=2).count() == 2

    assert TANF_T2.objects.count() == 0

@pytest.mark.django_db()
def test_parse_tanf_section_1_file_with_bad_update_indicator(tanf_section_1_file_with_bad_update_indicator, dfs):
    """Test parsing TANF Section 1 submission update indicator."""
    dfs.datafile = tanf_section_1_file_with_bad_update_indicator

    parse.parse_datafile(tanf_section_1_file_with_bad_update_indicator, dfs)

    parser_errors = ParserError.objects.filter(file=tanf_section_1_file_with_bad_update_indicator)

    assert parser_errors.count() == 1

    error = parser_errors.first()

    assert error.error_type == ParserErrorCategoryChoices.FIELD_VALUE
    assert error.error_message == "HEADER Item 10 (update indicator): U does not match D."


@pytest.mark.django_db()
def test_parse_tribal_section_4_bad_quarter(tribal_section_4_bad_quarter, dfs):
    """Test handling invalid quarter value that raises a ValueError exception."""
    tribal_section_4_bad_quarter.year = 2021
    tribal_section_4_bad_quarter.quarter = 'Q1'
    dfs.datafile = tribal_section_4_bad_quarter

    parse.parse_datafile(tribal_section_4_bad_quarter, dfs)
    parser_errors = ParserError.objects.filter(file=tribal_section_4_bad_quarter).order_by('id')

    assert parser_errors.count() == 3

    parser_errors.first().error_message == "T7: 2020  is invalid. Calendar Quarter must be a numeric" + \
        "representing the Calendar Year and Quarter formatted as YYYYQ"

    Tribal_TANF_T7.objects.count() == 0

@pytest.mark.django_db()
def test_parse_t3_cat2_invalid_citizenship(t3_cat2_invalid_citizenship_file, dfs):
    """Test parsing a TANF T3 record with an invalid CITIZENSHIP_STATUS."""
    dfs.datafile = t3_cat2_invalid_citizenship_file
    t3_cat2_invalid_citizenship_file.year = 2021
    t3_cat2_invalid_citizenship_file.quarter = 'Q1'
    dfs.save()

    parse.parse_datafile(t3_cat2_invalid_citizenship_file, dfs)

    exclusion = Query(error_type=ParserErrorCategoryChoices.CASE_CONSISTENCY) | \
        Query(error_type=ParserErrorCategoryChoices.PRE_CHECK)

    parser_errors = ParserError.objects.filter(file=t3_cat2_invalid_citizenship_file).exclude(exclusion).order_by("pk")

    assert parser_errors.count() == 2

    for e in parser_errors:
        assert e.error_message == "T3 Item 76 (Citizenship/Immigration Status): 0 is not in [1, 2, 9]."


@pytest.mark.django_db()
def test_parse_m2_cat2_invalid_37_38_39_file(m2_cat2_invalid_37_38_39_file, dfs):
    """Test parsing an SSP M2 file with an invalid EDUCATION_LEVEL, CITIZENSHIP_STATUS, COOPERATION_CHILD_SUPPORT."""
    dfs.datafile = m2_cat2_invalid_37_38_39_file
    m2_cat2_invalid_37_38_39_file.year = 2024
    m2_cat2_invalid_37_38_39_file.quarter = 'Q1'
    dfs.save()

    parse.parse_datafile(m2_cat2_invalid_37_38_39_file, dfs)

    exclusion = Query(error_type=ParserErrorCategoryChoices.CASE_CONSISTENCY) | \
        Query(error_type=ParserErrorCategoryChoices.PRE_CHECK)

    parser_errors = ParserError.objects.filter(file=m2_cat2_invalid_37_38_39_file).exclude(exclusion).order_by("pk")

    assert parser_errors.count() == 3

    error_msgs = {
        "Item 37 (Educational Level) 00 is not in range [1, 16]. or "
        "Item 37 (Educational Level) 00 is not in range [98, 99].",
        "M2 Item 38 (Citizenship/Immigration Status): 0 is not in [1, 2, 3, 9].",
        "M2 Item 39 (Cooperated with Child Support): 0 is not in [1, 2, 9]."
    }
    for e in parser_errors:
        assert e.error_message in error_msgs

@pytest.mark.django_db()
def test_parse_m3_cat2_invalid_68_69_file(m3_cat2_invalid_68_69_file, dfs):
    """Test parsing an SSP M3 file with an invalid EDUCATION_LEVEL and CITIZENSHIP_STATUS."""
    dfs.datafile = m3_cat2_invalid_68_69_file
    m3_cat2_invalid_68_69_file.year = 2024
    m3_cat2_invalid_68_69_file.quarter = 'Q1'
    dfs.save()

    parse.parse_datafile(m3_cat2_invalid_68_69_file, dfs)

    exclusion = Query(error_type=ParserErrorCategoryChoices.CASE_CONSISTENCY) | \
        Query(error_type=ParserErrorCategoryChoices.PRE_CHECK)

    parser_errors = ParserError.objects.filter(file=m3_cat2_invalid_68_69_file).exclude(exclusion).order_by("pk")

    assert parser_errors.count() == 4

    error_msgs = {"Item 68 (Educational Level) 00 is not in range [1, 16]. or Item 68 (Educational Level) " +
                  "00 is not in range [98, 99].",
                  "M3 Item 69 (Citizenship/Immigration Status): 0 is not in [1, 2, 3, 9].",
                  "Item 68 (Educational Level) 00 is not in range [1, 16]. or Item 68 (Educational Level) " +
                  "00 is not in range [98, 99].",
                  "M3 Item 69 (Citizenship/Immigration Status): 0 is not in [1, 2, 3, 9]."}

    for e in parser_errors:
        assert e.error_message in error_msgs

@pytest.mark.django_db()
def test_parse_m5_cat2_invalid_23_24_file(m5_cat2_invalid_23_24_file, dfs):
    """Test parsing an SSP M5 file with an invalid EDUCATION_LEVEL and CITIZENSHIP_STATUS."""
    dfs.datafile = m5_cat2_invalid_23_24_file
    m5_cat2_invalid_23_24_file.year = 2019
    m5_cat2_invalid_23_24_file.quarter = 'Q1'
    dfs.save()

    parse.parse_datafile(m5_cat2_invalid_23_24_file, dfs)

    exclusion = Query(error_type=ParserErrorCategoryChoices.CASE_CONSISTENCY) | \
        Query(error_type=ParserErrorCategoryChoices.PRE_CHECK)

    parser_errors = ParserError.objects.filter(file=m5_cat2_invalid_23_24_file).exclude(exclusion).order_by("pk")

    assert parser_errors.count() == 2

    error_msgs = {"M5 Item 23 (Educational Level): 00 matches 00.",
                  "M5 Item 24 (Citizenship/Immigration Status): 0 is not in [1, 2, 3, 9]."}

    for e in parser_errors:
        assert e.error_message in error_msgs


@pytest.fixture
def test_file_zero_filled_fips_code():
    """Fixture for T1 file with an invalid CITIZENSHIP_STATUS."""
    parsing_file = ParsingFileFactory(
        year=2021,
        quarter='Q1',
        file__name='t3_invalid_citizenship_file.txt',
        file__section='Active Case Data',
        file__data=(b'HEADER20241A01000TAN2ED\n'
                    b'T1202401    2132333   0140951112 43312   03   0   0   2 554145' +
                    b'   0 0  0   0  0   0  0   0  0   0222222   0   02229 22    \n' +
                    b'T2202401    21323333219550117WT@TB9BT92122222222223 1329911 34' +
                    b'  32 699 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0' +
                    b' 0 0 0 0   0   01623   0   0   0\n' +
                    b'T2202401    21323333219561102WTT@WBP992122221222222 2329911 28' +
                    b'  32 699 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0' +
                    b' 0 0 0 0   0   01432   0   0   0\n' +
                    b'T3202401    2132333120070906WT@@#ZY@W212222122 63981   0   012' +
                    b'0050201WTTYT#TT0212222122 63981   0   0                      \n' +
                    b'TRAILER      4         ')
    )
    return parsing_file


@pytest.mark.django_db()
def test_zero_filled_fips_code_file(test_file_zero_filled_fips_code, dfs):
    """Test parsing a file with zero filled FIPS code."""
    # TODO: this test can be merged as parametrized test with  "test_parse_small_correct_file"
    dfs.datafile = test_file_zero_filled_fips_code
    test_file_zero_filled_fips_code.year = 2024
    test_file_zero_filled_fips_code.quarter = 'Q2'
    test_file_zero_filled_fips_code.save()

    parse.parse_datafile(test_file_zero_filled_fips_code, dfs)

    parser_errors = ParserError.objects.filter(file=test_file_zero_filled_fips_code)
    assert 'T1 Item 2 (County FIPS Code): field is required but a value was not' + \
           ' provided.' in [i.error_message for i in parser_errors]


@pytest.mark.parametrize("file, batch_size, model, record_type, num_errors", [
    ('tanf_s1_exact_dup_file', 10000, TANF_T1, "T1", 3),
    ('tanf_s1_exact_dup_file', 1, TANF_T1, "T1", 3),  # This forces an in memory and database deletion of records.
    ('tanf_s2_exact_dup_file', 10000, TANF_T4, "T4", 3),
    ('tanf_s2_exact_dup_file', 1, TANF_T4, "T4", 3),  # This forces an in memory and database deletion of records.
    ('tanf_s3_exact_dup_file', 10000, TANF_T6, "T6", 1),
    ('tanf_s3_exact_dup_file', 1, TANF_T6, "T6", 1),  # This forces an in memory and database deletion of records.
    ('tanf_s4_exact_dup_file', 10000, TANF_T7, "T7", 1),
    ('tanf_s4_exact_dup_file', 1, TANF_T7, "T7", 1),  # This forces an in memory and database deletion of records.
    ('ssp_s1_exact_dup_file', 10000, SSP_M1, "M1", 3),
    ('ssp_s1_exact_dup_file', 1, SSP_M1, "M1", 3),  # This forces an in memory and database deletion of records.
    ('ssp_s2_exact_dup_file', 10000, SSP_M4, "M4", 3),
    ('ssp_s2_exact_dup_file', 1, SSP_M4, "M4", 3),  # This forces an in memory and database deletion of records.
    ('ssp_s3_exact_dup_file', 10000, SSP_M6, "M6", 1),
    ('ssp_s3_exact_dup_file', 1, SSP_M6, "M6", 1),  # This forces an in memory and database deletion of records.
    ('ssp_s4_exact_dup_file', 10000, SSP_M7, "M7", 1),
    ('ssp_s4_exact_dup_file', 1, SSP_M7, "M7", 1),  # This forces an in memory and database deletion of records.
])
@pytest.mark.django_db()
def test_parse_duplicate(file, batch_size, model, record_type, num_errors, dfs, request):
    """Test cases for datafiles that have exact duplicate records."""
    datafile = request.getfixturevalue(file)
    dfs.datafile = datafile

    settings.BULK_CREATE_BATCH_SIZE = batch_size

    parse.parse_datafile(datafile, dfs)
    parser_errors = ParserError.objects.filter(file=datafile,
                                               error_type=ParserErrorCategoryChoices.CASE_CONSISTENCY).order_by('id')
    for e in parser_errors:
        assert e.error_type == ParserErrorCategoryChoices.CASE_CONSISTENCY
    assert parser_errors.count() == num_errors

    dup_error = parser_errors.first()
    assert dup_error.error_message == f"Duplicate record detected with record type {record_type} at line 3. " + \
        "Record is a duplicate of the record at line number 2."

    model.objects.count() == 0

@pytest.mark.parametrize("file, batch_size, model, record_type, num_errors, err_msg", [
    ('tanf_s1_partial_dup_file', 10000, TANF_T1, "T1", 3, "partial_dup_t1_err_msg"),
    # This forces an in memory and database deletion of records.
    ('tanf_s1_partial_dup_file', 1, TANF_T1, "T1", 3, "partial_dup_t1_err_msg"),
    ('tanf_s2_partial_dup_file', 10000, TANF_T5, "T5", 3, "partial_dup_t5_err_msg"),
    # This forces an in memory and database deletion of records.
    ('tanf_s2_partial_dup_file', 1, TANF_T5, "T5", 3, "partial_dup_t5_err_msg"),
    ('tanf_s3_partial_dup_file', 10000, TANF_T6, "T6", 1, "partial_dup_s3_s4_err_msg"),
    # This forces an in memory and database deletion of records.
    ('tanf_s3_partial_dup_file', 1, TANF_T6, "T6", 1, "partial_dup_s3_s4_err_msg"),
    ('tanf_s4_partial_dup_file', 10000, TANF_T7, "T7", 1, "partial_dup_s3_s4_err_msg"),
    # This forces an in memory and database deletion of records.
    ('tanf_s4_partial_dup_file', 1, TANF_T7, "T7", 1, "partial_dup_s3_s4_err_msg"),
    ('ssp_s1_partial_dup_file', 10000, SSP_M1, "M1", 3, "partial_dup_t1_err_msg"),
    # This forces an in memory and database deletion of records.
    ('ssp_s1_partial_dup_file', 1, SSP_M1, "M1", 3, "partial_dup_t1_err_msg"),
    ('ssp_s2_partial_dup_file', 10000, SSP_M5, "M5", 3, "partial_dup_t5_err_msg"),
    # This forces an in memory and database deletion of records.
    ('ssp_s2_partial_dup_file', 1, SSP_M5, "M5", 3, "partial_dup_t5_err_msg"),
])
@pytest.mark.django_db()
def test_parse_partial_duplicate(file, batch_size, model, record_type, num_errors, err_msg, dfs, request):
    """Test cases for datafiles that have partial duplicate records."""
    datafile = request.getfixturevalue(file)
    expected_error_msg = request.getfixturevalue(err_msg)

    dfs.datafile = datafile

    settings.BULK_CREATE_BATCH_SIZE = batch_size

    parse.parse_datafile(datafile, dfs)
    parser_errors = ParserError.objects.filter(file=datafile,
                                               error_type=ParserErrorCategoryChoices.CASE_CONSISTENCY).order_by('id')
    for e in parser_errors:
        assert e.error_type == ParserErrorCategoryChoices.CASE_CONSISTENCY
    assert parser_errors.count() == num_errors

    dup_error = parser_errors.first()
    assert dup_error.error_message == expected_error_msg.format(record_type=record_type)

    model.objects.count() == 0

@pytest.mark.django_db()
def test_parse_cat_4_edge_case_file(cat4_edge_case_file, dfs):
    """Test parsing file with a cat4 error edge case submission."""
    cat4_edge_case_file.year = 2024
    cat4_edge_case_file.quarter = 'Q1'

    dfs.datafile = cat4_edge_case_file
    dfs.save()

    settings.BULK_CREATE_BATCH_SIZE = 1

    parse.parse_datafile(cat4_edge_case_file, dfs)

    parser_errors = ParserError.objects.filter(file=cat4_edge_case_file).filter(
        error_type=ParserErrorCategoryChoices.CASE_CONSISTENCY)

    assert TANF_T1.objects.all().count() == 2
    assert TANF_T2.objects.all().count() == 2
    assert TANF_T3.objects.all().count() == 4

    assert dfs.total_number_of_records_in_file == 17
    assert dfs.total_number_of_records_created == 8

    err = parser_errors.first()
    assert err.error_message == ("Every T1 record should have at least one corresponding T2 or T3 record with the "
                                 "same RPT_MONTH_YEAR and CASE_NUMBER.")
