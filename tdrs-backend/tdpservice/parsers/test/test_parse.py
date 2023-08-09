"""Test the implementation of the parse_file method with realistic datafiles."""


import pytest
from .. import parse
from ..models import ParserError, ParserErrorCategoryChoices, DataFileSummary
from tdpservice.search_indexes.models.tanf import TANF_T1, TANF_T2, TANF_T3, TANF_T4, TANF_T5
from tdpservice.search_indexes.models.ssp import SSP_M1, SSP_M2, SSP_M3
from .factories import DataFileSummaryFactory
from tdpservice.data_files.models import DataFile
from .. import schema_defs, util

import logging

es_logger = logging.getLogger('elasticsearch')
es_logger.setLevel(logging.WARNING)


@pytest.fixture
def test_datafile(stt_user, stt):
    """Fixture for small_correct_file."""
    return util.create_test_datafile('small_correct_file', stt_user, stt)

@pytest.fixture
def dfs():
    """Fixture for DataFileSummary."""
    return DataFileSummaryFactory.create()

@pytest.mark.django_db
def test_parse_small_correct_file(test_datafile, dfs):
    """Test parsing of small_correct_file."""
    dfs.datafile = test_datafile
    dfs.save()

    errors = parse.parse_datafile(test_datafile)
    dfs.status = dfs.get_status()
    dfs.case_aggregates = util.case_aggregates_by_month(dfs.datafile, dfs.status)
    assert dfs.case_aggregates == {'rejected': 0,
                                   'months': [
                                       {'accepted_without_errors': 1, 'accepted_with_errors': 0, 'month': 'Oct'},
                                       {'accepted_without_errors': 0, 'accepted_with_errors': 0, 'month': 'Nov'},
                                       {'accepted_without_errors': 0, 'accepted_with_errors': 0, 'month': 'Dec'}
                                    ]}

    assert errors == {}
    assert dfs.get_status() == DataFileSummary.Status.ACCEPTED
    assert TANF_T1.objects.count() == 1
    assert ParserError.objects.filter(file=test_datafile).count() == 0

    # spot check
    t1 = TANF_T1.objects.all().first()
    assert t1.RPT_MONTH_YEAR == 202010
    assert t1.CASE_NUMBER == '11111111112'
    assert t1.COUNTY_FIPS_CODE == '230'
    assert t1.ZIP_CODE == '40336'
    assert t1.FUNDING_STREAM == 1
    assert t1.NBR_FAMILY_MEMBERS == 2
    assert t1.RECEIVES_SUB_CC == 3
    assert t1.CASH_AMOUNT == 873
    assert t1.SANC_REDUCTION_AMT == 0
    assert t1.FAMILY_NEW_CHILD == 2

@pytest.mark.django_db
def test_parse_section_mismatch(test_datafile, dfs):
    """Test parsing of small_correct_file where the DataFile section doesn't match the rawfile section."""
    test_datafile.section = 'Closed Case Data'
    test_datafile.save()

    dfs.datafile = test_datafile
    dfs.save()

    errors = parse.parse_datafile(test_datafile)
    dfs.status = dfs.get_status()
    assert dfs.status == DataFileSummary.Status.REJECTED
    parser_errors = ParserError.objects.filter(file=test_datafile)
    dfs.case_aggregates = util.case_aggregates_by_month(dfs.datafile, dfs.status)
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
def test_parse_wrong_program_type(test_datafile, dfs):
    """Test parsing of small_correct_file where the DataFile program type doesn't match the rawfile."""
    test_datafile.section = 'SSP Active Case Data'
    test_datafile.save()

    dfs.datafile = test_datafile
    dfs.save()
    errors = parse.parse_datafile(test_datafile)
    assert dfs.get_status() == DataFileSummary.Status.REJECTED

    parser_errors = ParserError.objects.filter(file=test_datafile)
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


@pytest.fixture
def test_big_file(stt_user, stt):
    """Fixture for ADS.E2J.FTP1.TS06."""
    return util.create_test_datafile('ADS.E2J.FTP1.TS06', stt_user, stt)

@pytest.mark.django_db
@pytest.mark.big_files
def test_parse_big_file(test_big_file, dfs):
    """Test parsing of ADS.E2J.FTP1.TS06."""
    expected_t1_record_count = 815
    expected_t2_record_count = 882
    expected_t3_record_count = 1376

    dfs.datafile = test_big_file
    dfs.save()

    errors = parse.parse_datafile(test_big_file)
    dfs.status = dfs.get_status()
    assert dfs.status == DataFileSummary.Status.ACCEPTED_WITH_ERRORS
    dfs.case_aggregates = util.case_aggregates_by_month(dfs.datafile, dfs.status)
    assert dfs.case_aggregates == {'rejected': 0,
                                   'months': [
                                       {'accepted_without_errors': 171, 'accepted_with_errors': 99, 'month': 'Oct'},
                                       {'accepted_without_errors': 169, 'accepted_with_errors': 104, 'month': 'Nov'},
                                       {'accepted_without_errors': 166, 'accepted_with_errors': 106, 'month': 'Dec'}
                                    ]}

    parser_errors = ParserError.objects.filter(file=test_big_file)
    assert parser_errors.count() == 355
    assert len(errors) == 334

    row_18_error = parser_errors.get(row_number=18)
    assert row_18_error.error_type == ParserErrorCategoryChoices.FIELD_VALUE
    assert row_18_error.error_message == 'MONTHS_FED_TIME_LIMIT is required but a value was not provided.'
    assert row_18_error.content_type.model == 'tanf_t2'
    assert row_18_error.object_id is not None

    assert errors[18] == [row_18_error]

    assert TANF_T1.objects.count() == expected_t1_record_count
    assert TANF_T2.objects.count() == expected_t2_record_count
    assert TANF_T3.objects.count() == expected_t3_record_count


@pytest.fixture
def bad_test_file(stt_user, stt):
    """Fixture for bad_TANF_S2."""
    return util.create_test_datafile('bad_TANF_S2.txt', stt_user, stt)


@pytest.mark.django_db
def test_parse_bad_test_file(bad_test_file, dfs):
    """Test parsing of bad_TANF_S2."""
    errors = parse.parse_datafile(bad_test_file)

    parser_errors = ParserError.objects.filter(file=bad_test_file)
    assert parser_errors.count() == 1

    err = parser_errors.first()

    assert err.row_number == 1
    assert err.error_type == ParserErrorCategoryChoices.PRE_CHECK
    assert err.error_message == 'Header length is 24 but must be 23 characters.'
    assert err.content_type is None
    assert err.object_id is None
    assert errors == {
        'header': [err]
    }


@pytest.fixture
def bad_file_missing_header(stt_user, stt):
    """Fixture for bad_missing_header."""
    return util.create_test_datafile('bad_missing_header.txt', stt_user, stt)

@pytest.mark.django_db
def test_parse_bad_file_missing_header(bad_file_missing_header, dfs):
    """Test parsing of bad_missing_header."""
    errors = parse.parse_datafile(bad_file_missing_header)
    dfs.datafile = bad_file_missing_header
    dfs.save()
    assert dfs.get_status() == DataFileSummary.Status.REJECTED

    parser_errors = ParserError.objects.filter(file=bad_file_missing_header)

    assert parser_errors.count() == 2

    err = parser_errors.first()

    assert err.row_number == 1
    assert err.error_type == ParserErrorCategoryChoices.PRE_CHECK
    assert err.error_message == 'Header length is 14 but must be 23 characters.'
    assert err.content_type is None
    assert err.object_id is None
    assert errors == {
        'header': [parser_errors[1], parser_errors[0]]
    }


@pytest.fixture
def bad_file_multiple_headers(stt_user, stt):
    """Fixture for bad_two_headers."""
    return util.create_test_datafile('bad_two_headers.txt', stt_user, stt)


@pytest.mark.django_db
def test_parse_bad_file_multiple_headers(bad_file_multiple_headers, dfs):
    """Test parsing of bad_two_headers."""
    errors = parse.parse_datafile(bad_file_multiple_headers)
    dfs.datafile = bad_file_multiple_headers
    dfs.save()
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


@pytest.fixture
def big_bad_test_file(stt_user, stt):
    """Fixture for bad_TANF_S1."""
    return util.create_test_datafile('bad_TANF_S1.txt', stt_user, stt)


@pytest.mark.django_db
def test_parse_big_bad_test_file(big_bad_test_file, dfs):
    """Test parsing of bad_TANF_S1."""
    parse.parse_datafile(big_bad_test_file)

    parser_errors = ParserError.objects.filter(file=big_bad_test_file)
    assert parser_errors.count() == 1

    err = parser_errors.first()

    assert err.row_number == 3679
    assert err.error_type == ParserErrorCategoryChoices.PRE_CHECK
    assert err.error_message == 'Multiple headers found.'
    assert err.content_type is None
    assert err.object_id is None


@pytest.fixture
def bad_trailer_file(stt_user, stt):
    """Fixture for bad_trailer_1."""
    return util.create_test_datafile('bad_trailer_1.txt', stt_user, stt)

@pytest.mark.django_db
def test_parse_bad_trailer_file(bad_trailer_file, dfs):
    """Test parsing bad_trailer_1."""
    dfs.datafile = bad_trailer_file
    dfs.save()

    errors = parse.parse_datafile(bad_trailer_file)

    parser_errors = ParserError.objects.filter(file=bad_trailer_file)
    assert parser_errors.count() == 2

    trailer_error = parser_errors.get(row_number=3)
    assert trailer_error.error_type == ParserErrorCategoryChoices.PRE_CHECK
    assert trailer_error.error_message == 'Trailer length is 11 but must be 23 characters.'
    assert trailer_error.content_type is None
    assert trailer_error.object_id is None

    row_error = parser_errors.get(row_number=2)
    assert row_error.error_type == ParserErrorCategoryChoices.PRE_CHECK
    assert row_error.error_message == 'Value length 7 does not match 156.'
    assert row_error.content_type is None
    assert row_error.object_id is None

    assert errors == {
        'trailer': [trailer_error],
        2: [row_error]
    }


@pytest.fixture
def bad_trailer_file_2(stt_user, stt):
    """Fixture for bad_trailer_2."""
    return util.create_test_datafile('bad_trailer_2.txt', stt_user, stt)


@pytest.mark.django_db()
def test_parse_bad_trailer_file2(bad_trailer_file_2):
    """Test parsing bad_trailer_2."""
    errors = parse.parse_datafile(bad_trailer_file_2)

    parser_errors = ParserError.objects.filter(file=bad_trailer_file_2)
    assert parser_errors.count() == 4

    trailer_errors = parser_errors.filter(row_number=3)

    trailer_error_1 = trailer_errors.first()
    assert trailer_error_1.error_type == ParserErrorCategoryChoices.PRE_CHECK
    assert trailer_error_1.error_message == 'Trailer length is 7 but must be 23 characters.'
    assert trailer_error_1.content_type is None
    assert trailer_error_1.object_id is None

    trailer_error_2 = trailer_errors[1]
    assert trailer_error_2.error_type == ParserErrorCategoryChoices.PRE_CHECK
    assert trailer_error_2.error_message == 'T1trash does not start with TRAILER.'
    assert trailer_error_2.content_type is None
    assert trailer_error_2.object_id is None

    row_2_error = parser_errors.get(row_number=2)
    assert row_2_error.error_type == ParserErrorCategoryChoices.PRE_CHECK
    assert row_2_error.error_message == 'Value length 117 does not match 156.'
    assert row_2_error.content_type is None
    assert row_2_error.object_id is None

    row_3_error = trailer_errors[2]
    assert row_3_error.error_type == ParserErrorCategoryChoices.PRE_CHECK
    assert row_3_error.error_message == 'Value length 7 does not match 156.'
    assert row_3_error.content_type is None
    assert row_3_error.object_id is None

    assert errors == {
        2: [row_2_error],
        3: [row_3_error],
        "trailer": [trailer_error_1, trailer_error_2],
    }


@pytest.fixture
def empty_file(stt_user, stt):
    """Fixture for empty_file."""
    return util.create_test_datafile('empty_file', stt_user, stt)


@pytest.mark.django_db
def test_parse_empty_file(empty_file, dfs):
    """Test parsing of empty_file."""
    dfs.datafile = empty_file
    dfs.save()
    errors = parse.parse_datafile(empty_file)

    dfs.status = dfs.get_status()
    dfs.case_aggregates = util.case_aggregates_by_month(empty_file, dfs.status)

    assert dfs.status == DataFileSummary.Status.REJECTED
    assert dfs.case_aggregates == {'rejected': 2,
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

    parser_errors = ParserError.objects.filter(file=empty_file)
    assert parser_errors.count() == 2

    err = parser_errors.first()

    assert err.row_number == 1
    assert err.error_type == ParserErrorCategoryChoices.PRE_CHECK
    assert err.error_message == 'Header length is 0 but must be 23 characters.'
    assert err.content_type is None
    assert err.object_id is None
    assert errors == {
        'header': list(parser_errors),
    }


@pytest.fixture
def small_ssp_section1_datafile(stt_user, stt):
    """Fixture for small_ssp_section1."""
    return util.create_test_datafile('small_ssp_section1.txt', stt_user, stt, 'SSP Active Case Data')


@pytest.mark.django_db
def test_parse_small_ssp_section1_datafile(small_ssp_section1_datafile, dfs):
    """Test parsing small_ssp_section1_datafile."""
    expected_m1_record_count = 5
    expected_m2_record_count = 6
    expected_m3_record_count = 8

    small_ssp_section1_datafile.year = 2019
    small_ssp_section1_datafile.quarter = 'Q1'
    small_ssp_section1_datafile.save()

    dfs.datafile = small_ssp_section1_datafile
    dfs.save()

    errors = parse.parse_datafile(small_ssp_section1_datafile)

    dfs.status = dfs.get_status()
    assert dfs.status == DataFileSummary.Status.ACCEPTED_WITH_ERRORS
    dfs.case_aggregates = util.case_aggregates_by_month(dfs.datafile, dfs.status)
    assert dfs.case_aggregates == {'rejected': 1,
                                   'months': [
                                       {'accepted_without_errors': 5, 'accepted_with_errors': 0, 'month': 'Oct'},
                                       {'accepted_without_errors': 0, 'accepted_with_errors': 0, 'month': 'Nov'},
                                       {'accepted_without_errors': 0, 'accepted_with_errors': 0, 'month': 'Dec'}
                                    ]}

    parser_errors = ParserError.objects.filter(file=small_ssp_section1_datafile)
    assert parser_errors.count() == 1

    err = parser_errors.first()

    assert err.row_number == 20
    assert err.error_type == ParserErrorCategoryChoices.PRE_CHECK
    assert err.error_message == 'Trailer length is 15 but must be 23 characters.'
    assert err.content_type is None
    assert err.object_id is None
    assert errors == {
        'trailer': [err]
    }
    assert SSP_M1.objects.count() == expected_m1_record_count
    assert SSP_M2.objects.count() == expected_m2_record_count
    assert SSP_M3.objects.count() == expected_m3_record_count


@pytest.fixture
def ssp_section1_datafile(stt_user, stt):
    """Fixture for ssp_section1_datafile."""
    return util.create_test_datafile('ssp_section1_datafile.txt', stt_user, stt, 'SSP Active Case Data')


@pytest.mark.django_db()
def test_parse_ssp_section1_datafile(ssp_section1_datafile):
    """Test parsing ssp_section1_datafile."""
    expected_m1_record_count = 7849
    expected_m2_record_count = 9373
    expected_m3_record_count = 16764

    parse.parse_datafile(ssp_section1_datafile)

    parser_errors = ParserError.objects.filter(file=ssp_section1_datafile)
    assert parser_errors.count() == 10

    err = parser_errors.first()

    assert err.row_number == 10339
    assert err.error_type == ParserErrorCategoryChoices.FIELD_VALUE
    assert err.error_message == 'EARNED_INCOME is required but a value was not provided.'
    assert err.content_type is not None
    assert err.object_id is not None

    assert SSP_M1.objects.count() == expected_m1_record_count
    assert SSP_M2.objects.count() == expected_m2_record_count
    assert SSP_M3.objects.count() == expected_m3_record_count

@pytest.fixture
def small_tanf_section1_datafile(stt_user, stt):
    """Fixture for small_tanf_section1."""
    return util.create_test_datafile('small_tanf_section1.txt', stt_user, stt)

@pytest.mark.django_db
def test_parse_tanf_section1_datafile(small_tanf_section1_datafile, dfs):
    """Test parsing of small_tanf_section1_datafile and validate T2 model data."""
    dfs.datafile = small_tanf_section1_datafile
    dfs.save()

    errors = parse.parse_datafile(small_tanf_section1_datafile)

    dfs.status = dfs.get_status()
    assert dfs.status == DataFileSummary.Status.ACCEPTED
    dfs.case_aggregates = util.case_aggregates_by_month(dfs.datafile, dfs.status)
    assert dfs.case_aggregates == {'rejected': 0,
                                   'months': [
                                       {'accepted_without_errors': 5, 'accepted_with_errors': 0, 'month': 'Oct'},
                                       {'accepted_without_errors': 0, 'accepted_with_errors': 0, 'month': 'Nov'},
                                       {'accepted_without_errors': 0, 'accepted_with_errors': 0, 'month': 'Dec'}
                                    ]}

    assert errors == {}
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
def test_parse_tanf_section1_datafile_obj_counts(small_tanf_section1_datafile):
    """Test parsing of small_tanf_section1_datafile in general."""
    parse.parse_datafile(small_tanf_section1_datafile)

#     assert errors == {}
#     assert TANF_T1.objects.count() == 5
#     assert TANF_T2.objects.count() == 5
#     assert TANF_T3.objects.count() == 6

@pytest.mark.django_db()
def test_parse_tanf_section1_datafile_t3s(small_tanf_section1_datafile):
    """Test parsing of small_tanf_section1_datafile and validate T3 model data."""
    parse.parse_datafile(small_tanf_section1_datafile)

#     assert errors == {}
#     assert TANF_T3.objects.count() == 6

#     t3_models = TANF_T3.objects.all()
#     t3_1 = t3_models[0]
#     assert t3_1.RPT_MONTH_YEAR == 202010
#     assert t3_1.CASE_NUMBER == '11111111112'
#     assert t3_1.FAMILY_AFFILIATION == 1
#     assert t3_1.GENDER == 2
#     assert t3_1.EDUCATION_LEVEL == '98'

#     t3_6 = t3_models[5]
#     assert t3_6.RPT_MONTH_YEAR == 202010
#     assert t3_6.CASE_NUMBER == '11111111151'
#     assert t3_6.FAMILY_AFFILIATION == 1
#     assert t3_6.GENDER == 2
#     assert t3_6.EDUCATION_LEVEL == '98'

@pytest.fixture
def super_big_s1_file(stt_user, stt):
    """Fixture for ADS.E2J.NDM1.TS53_fake."""
    return util.create_test_datafile('ADS.E2J.NDM1.TS53_fake', stt_user, stt)


@pytest.mark.django_db()
def test_parse_super_big_s1_file(super_big_s1_file):
    """Test parsing of super_big_s1_file and validate all T1/T2/T3 records are created."""
    parse.parse_datafile(super_big_s1_file)

    parser_errors = ParserError.objects.filter(file=super_big_s1_file)
    assert parser_errors.count() == 13

    assert TANF_T1.objects.count() == 96642
    assert TANF_T2.objects.count() == 112794
    assert TANF_T3.objects.count() == 172595

@pytest.fixture
def super_big_s1_rollback_file(stt_user, stt):
    """Fixture for ADS.E2J.NDM1.TS53_fake.rollback."""
    return util.create_test_datafile('ADS.E2J.NDM1.TS53_fake.rollback', stt_user, stt)

@pytest.mark.django_db()
@pytest.mark.big_files
def test_parse_super_big_s1_file_with_rollback(super_big_s1_rollback_file):
    """Test parsing of super_big_s1_rollback_file.

    Validate all T1/T2/T3 records are not created due to multiple headers.
    """
    parse.parse_datafile(super_big_s1_rollback_file)

    parser_errors = ParserError.objects.filter(file=super_big_s1_rollback_file)
    assert parser_errors.count() == 1

    err = parser_errors.first()

    assert err.row_number == 50022
    assert err.error_type == ParserErrorCategoryChoices.PRE_CHECK
    assert err.error_message == 'Multiple headers found.'
    assert err.content_type is None
    assert err.object_id is None

    assert TANF_T1.objects.count() == 0
    assert TANF_T2.objects.count() == 0
    assert TANF_T3.objects.count() == 0


@pytest.fixture
def bad_tanf_s1__row_missing_required_field(stt_user, stt):
    """Fixture for small_tanf_section1."""
    return util.create_test_datafile('small_bad_tanf_s1', stt_user, stt)


@pytest.mark.django_db
def test_parse_bad_tfs1_missing_required(bad_tanf_s1__row_missing_required_field, dfs):
    """Test parsing a bad TANF Section 1 submission where a row is missing required data."""
    dfs.datafile = bad_tanf_s1__row_missing_required_field
    dfs.save()

    errors = parse.parse_datafile(bad_tanf_s1__row_missing_required_field)

    assert dfs.get_status() == DataFileSummary.Status.ACCEPTED_WITH_ERRORS

    parser_errors = ParserError.objects.filter(file=bad_tanf_s1__row_missing_required_field)
    assert parser_errors.count() == 4
    # for e in parser_errors:
    #    print(e.error_type, e.error_message)

    row_2_error = parser_errors.get(row_number=2)
    assert row_2_error.error_type == ParserErrorCategoryChoices.FIELD_VALUE
    assert row_2_error.error_message == 'RPT_MONTH_YEAR is required but a value was not provided.'
    assert row_2_error.content_type.model == 'tanf_t1'
    assert row_2_error.object_id is not None

    row_3_error = parser_errors.get(row_number=3)
    assert row_3_error.error_type == ParserErrorCategoryChoices.FIELD_VALUE
    assert row_3_error.error_message == 'RPT_MONTH_YEAR is required but a value was not provided.'
    assert row_3_error.content_type.model == 'tanf_t2'
    assert row_3_error.object_id is not None

    row_4_error = parser_errors.get(row_number=4)
    assert row_4_error.error_type == ParserErrorCategoryChoices.FIELD_VALUE
    assert row_4_error.error_message == 'RPT_MONTH_YEAR is required but a value was not provided.'
    assert row_4_error.content_type.model == 'tanf_t3'
    assert row_4_error.object_id is not None

    row_5_error = parser_errors.get(row_number=5)
    assert row_5_error.error_type == ParserErrorCategoryChoices.PRE_CHECK
    assert row_5_error.error_message == 'Unknown Record_Type was found.'
    assert row_5_error.content_type is None
    assert row_5_error.object_id is None

    assert errors == {
        2: [row_2_error],
        3: [row_3_error],
        4: [row_4_error],
        5: [row_5_error],
    }


@pytest.fixture
def bad_ssp_s1__row_missing_required_field(stt_user, stt):
    """Fixture for ssp_section1_datafile."""
    return util.create_test_datafile('small_bad_ssp_s1', stt_user, stt, 'SSP Active Case Data')


@pytest.mark.django_db()
def test_parse_bad_ssp_s1_missing_required(bad_ssp_s1__row_missing_required_field):
    """Test parsing a bad TANF Section 1 submission where a row is missing required data."""
    errors = parse.parse_datafile(bad_ssp_s1__row_missing_required_field)

    parser_errors = ParserError.objects.filter(file=bad_ssp_s1__row_missing_required_field)
    print(parser_errors.values())
    assert parser_errors.count() == 5

    row_2_error = parser_errors.get(row_number=2)
    assert row_2_error.error_type == ParserErrorCategoryChoices.FIELD_VALUE
    assert row_2_error.error_message == 'RPT_MONTH_YEAR is required but a value was not provided.'
    assert row_2_error.content_type.model == 'ssp_m1'
    assert row_2_error.object_id is not None

    row_3_error = parser_errors.get(row_number=3)
    assert row_3_error.error_type == ParserErrorCategoryChoices.FIELD_VALUE
    assert row_3_error.error_message == 'RPT_MONTH_YEAR is required but a value was not provided.'
    assert row_3_error.content_type.model == 'ssp_m2'
    assert row_3_error.object_id is not None

    row_4_error = parser_errors.get(row_number=4)
    assert row_4_error.error_type == ParserErrorCategoryChoices.FIELD_VALUE
    assert row_4_error.error_message == 'RPT_MONTH_YEAR is required but a value was not provided.'
    assert row_4_error.content_type.model == 'ssp_m3'
    assert row_4_error.object_id is not None

    row_5_error = parser_errors.get(row_number=5)
    assert row_5_error.error_type == ParserErrorCategoryChoices.PRE_CHECK
    assert row_5_error.error_message == 'Unknown Record_Type was found.'
    assert row_5_error.content_type is None
    assert row_5_error.object_id is None

    trailer_error = parser_errors.get(row_number=6)
    assert trailer_error.error_type == ParserErrorCategoryChoices.PRE_CHECK
    assert trailer_error.error_message == 'Trailer length is 15 but must be 23 characters.'
    assert trailer_error.content_type is None
    assert trailer_error.object_id is None

    assert errors == {
        2: [row_2_error],
        3: [row_3_error],
        4: [row_4_error],
        5: [row_5_error],
        'trailer': [trailer_error],
    }

@pytest.mark.django_db
def test_dfs_set_case_aggregates(test_datafile, dfs):
    """Test that the case aggregates are set correctly."""
    test_datafile.section = 'Active Case Data'
    test_datafile.save()
    parse.parse_datafile(test_datafile)  # this still needs to execute to create db objects to be queried
    dfs.file = test_datafile
    dfs.save()
    dfs.status = dfs.get_status()
    dfs.case_aggregates = util.case_aggregates_by_month(test_datafile, dfs.status)
    dfs.save()

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
    # get schema
    schema = util.get_schema('T3', 'A', 'TAN')
    assert schema == schema_defs.tanf.t3

    # get model
    models = util.get_program_models('TAN', 'A')
    assert models == {
                    'T1': schema_defs.tanf.t1,
                    'T2': schema_defs.tanf.t2,
                    'T3': schema_defs.tanf.t3,
                }

    model = util.get_program_model('TAN', 'A', 'T1')
    assert model == schema_defs.tanf.t1
    # get section
    section = util.get_section_reference('TAN', 'C')
    assert section == DataFile.Section.CLOSED_CASE_DATA

    # from datafile:
    # get model(s)
    # get section str

    # from model:
    # get text
    # get section str
    # get ref section

@pytest.fixture
def small_tanf_section2_file(stt_user, stt):
    """Fixture for ssp_section1_datafile."""
    return create_test_datafile('small_tanf_section2.txt', stt_user, stt, 'Closed Case Data')

@pytest.mark.django_db()
def test_parse_small_tanf_section2_file(small_tanf_section2_file):
    """Test parsing a bad TANF Section 1 submission where a row is missing required data."""
    parse.parse_datafile(small_tanf_section2_file)

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

@pytest.fixture
def tanf_section2_file(stt_user, stt):
    """Fixture for ssp_section1_datafile."""
    return create_test_datafile('ADS.E2J.FTP2.TS06', stt_user, stt, 'Closed Case Data')

@pytest.mark.django_db()
def test_parse_tanf_section2_file(tanf_section2_file):
    """Test parsing a bad TANF Section 1 submission where a row is missing required data."""
    parse.parse_datafile(tanf_section2_file)

    assert TANF_T4.objects.all().count() == 223
    assert TANF_T5.objects.all().count() == 605

    parser_errors = ParserError.objects.filter(file=tanf_section2_file)
    assert parser_errors.count() == 2681
    err = parser_errors.first()
    assert err.error_type == ParserErrorCategoryChoices.FIELD_VALUE
    assert err.error_message == "REC_OASDI_INSURANCE is required but a value was not provided."
    assert err.content_type.model == "tanf_t5"
    assert err.object_id is not None
