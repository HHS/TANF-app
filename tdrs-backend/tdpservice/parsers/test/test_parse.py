"""Test the implementation of the parse_file method with realistic datafiles."""


import pytest
from pathlib import Path
from .. import parse
from ..models import ParserError, ParserErrorCategoryChoices
from tdpservice.data_files.models import DataFile
from tdpservice.search_indexes.models.tanf import TANF_T1, TANF_T2, TANF_T3
from tdpservice.search_indexes.models.ssp import SSP_M1, SSP_M2, SSP_M3


def create_test_datafile(filename, stt_user, stt, section='Active Case Data'):
    """Create a test DataFile instance with the given file attached."""
    path = str(Path(__file__).parent.joinpath('data')) + f'/{filename}'
    datafile = DataFile.create_new_version({
        'quarter': '4',
        'year': 2022,
        'section': section,
        'user': stt_user,
        'stt': stt
    })

    with open(path, 'rb') as file:
        datafile.file.save(filename, file)

    return datafile


@pytest.fixture
def test_datafile(stt_user, stt):
    """Fixture for small_correct_file."""
    return create_test_datafile('small_correct_file', stt_user, stt)


@pytest.mark.django_db
def test_parse_small_correct_file(test_datafile):
    """Test parsing of small_correct_file."""
    errors = parse.parse_datafile(test_datafile)

    assert errors == {}
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
def test_parse_section_mismatch(test_datafile):
    """Test parsing of small_correct_file where the DataFile section doesn't match the rawfile section."""
    test_datafile.section = 'Closed Case Data'
    test_datafile.save()

    errors = parse.parse_datafile(test_datafile)

    parser_errors = ParserError.objects.filter(file=test_datafile)
    assert parser_errors.count() == 1

    err = parser_errors.first()

    assert err.row_number == 1
    assert err.error_type == ParserErrorCategoryChoices.PRE_CHECK
    assert err.error_message == 'Section does not match.'
    assert errors == {
        'document': [err]
    }


@pytest.mark.django_db
def test_parse_wrong_program_type(test_datafile):
    """Test parsing of small_correct_file where the DataFile program type doesn't match the rawfile."""
    test_datafile.section = 'SSP Active Case Data'
    test_datafile.save()

    errors = parse.parse_datafile(test_datafile)

    parser_errors = ParserError.objects.filter(file=test_datafile)
    assert parser_errors.count() == 1

    err = parser_errors.first()

    assert err.row_number == 1
    assert err.error_type == ParserErrorCategoryChoices.PRE_CHECK
    assert err.error_message == 'Section does not match.'
    assert errors == {
        'document': [err]
    }


@pytest.fixture
def test_big_file(stt_user, stt):
    """Fixture for ADS.E2J.FTP1.TS06."""
    return create_test_datafile('ADS.E2J.FTP1.TS06', stt_user, stt)


@pytest.mark.django_db
def test_parse_big_file(test_big_file):
    """Test parsing of ADS.E2J.FTP1.TS06."""
    expected_t1_record_count = 815
    expected_t2_record_count = 882
    expected_t3_record_count = 1376
    errors = parse.parse_datafile(test_big_file)
    parser_errors = ParserError.objects.filter(file=test_big_file)

    assert errors == {}
    assert TANF_T1.objects.count() == expected_t1_record_count
    assert TANF_T2.objects.count() == expected_t2_record_count
    assert TANF_T3.objects.count() == expected_t3_record_count


@pytest.fixture
def bad_test_file(stt_user, stt):
    """Fixture for bad_TANF_S2."""
    return create_test_datafile('bad_TANF_S2.txt', stt_user, stt)


@pytest.mark.django_db
def test_parse_bad_test_file(bad_test_file):
    """Test parsing of bad_TANF_S2."""
    errors = parse.parse_datafile(bad_test_file)

    parser_errors = ParserError.objects.filter(file=bad_test_file)
    assert parser_errors.count() == 1

    err = parser_errors.first()

    assert err.row_number == 1
    assert err.error_type == ParserErrorCategoryChoices.PRE_CHECK
    assert err.error_message == 'Value length 24 does not match 23.'
    assert errors == {
        'header': [err]
    }


@pytest.fixture
def bad_file_missing_header(stt_user, stt):
    """Fixture for bad_missing_header."""
    return create_test_datafile('bad_missing_header.txt', stt_user, stt)


@pytest.mark.django_db
def test_parse_bad_file_missing_header(bad_file_missing_header):
    """Test parsing of bad_missing_header."""
    errors = parse.parse_datafile(bad_file_missing_header)

    parser_errors = ParserError.objects.filter(file=bad_file_missing_header)
    assert parser_errors.count() == 1

    err = parser_errors.first()

    assert err.row_number == 1
    assert err.error_type == ParserErrorCategoryChoices.PRE_CHECK
    assert err.error_message == 'No headers found.'
    assert errors == {
        'document': [err]
    }


@pytest.fixture
def bad_file_multiple_headers(stt_user, stt):
    """Fixture for bad_two_headers."""
    return create_test_datafile('bad_two_headers.txt', stt_user, stt)


@pytest.mark.django_db
def test_parse_bad_file_multiple_headers(bad_file_multiple_headers):
    """Test parsing of bad_two_headers."""
    errors = parse.parse_datafile(bad_file_multiple_headers)

    parser_errors = ParserError.objects.filter(file=bad_file_multiple_headers)
    assert parser_errors.count() == 1

    err = parser_errors.first()

    assert err.row_number == 9
    assert err.error_type == ParserErrorCategoryChoices.PRE_CHECK
    assert err.error_message == 'Multiple headers found.'
    assert errors == {
        'document': [err]
    }


@pytest.fixture
def big_bad_test_file(stt_user, stt):
    """Fixture for bad_TANF_S1."""
    return create_test_datafile('bad_TANF_S1.txt', stt_user, stt)


@pytest.mark.django_db
def test_parse_big_bad_test_file(big_bad_test_file):
    """Test parsing of bad_TANF_S1."""
    errors = parse.parse_datafile(big_bad_test_file)

    parser_errors = ParserError.objects.filter(file=big_bad_test_file)
    assert parser_errors.count() == 1

    err = parser_errors.first()

    assert err.row_number == 7204
    assert err.error_type == ParserErrorCategoryChoices.PRE_CHECK
    assert err.error_message == 'Multiple trailers found.'
    assert errors == {
        'document': [err]
    }


@pytest.fixture
def bad_trailer_file(stt_user, stt):
    """Fixture for bad_trailer_1."""
    return create_test_datafile('bad_trailer_1.txt', stt_user, stt)


@pytest.mark.django_db
def test_parse_bad_trailer_file(bad_trailer_file):
    """Test parsing bad_trailer_1."""
    errors = parse.parse_datafile(bad_trailer_file)

    parser_errors = ParserError.objects.filter(file=bad_trailer_file)
    assert parser_errors.count() == 2

    trailer_error = parser_errors.get(row_number=-1)
    assert trailer_error.error_type == ParserErrorCategoryChoices.PRE_CHECK
    assert trailer_error.error_message == 'Value length 11 does not match 23.'

    row_error = parser_errors.get(row_number=2)
    assert row_error.error_type == ParserErrorCategoryChoices.PRE_CHECK
    assert row_error.error_message == 'Value length 7 does not match 156.'

    assert errors == {
        'trailer': [trailer_error],
        2: [row_error]
    }


@pytest.fixture
def bad_trailer_file_2(stt_user, stt):
    """Fixture for bad_trailer_2."""
    return create_test_datafile('bad_trailer_2.txt', stt_user, stt)


@pytest.mark.django_db
def test_parse_bad_trailer_file2(bad_trailer_file_2):
    """Test parsing bad_trailer_2."""
    errors = parse.parse_datafile(bad_trailer_file_2)

    parser_errors = ParserError.objects.filter(file=bad_trailer_file_2)
    assert parser_errors.count() == 4

    trailer_errors = parser_errors.filter(row_number=-1)

    trailer_error_1 = trailer_errors.first()
    assert trailer_error_1.error_type == ParserErrorCategoryChoices.PRE_CHECK
    assert trailer_error_1.error_message == 'Value length 7 does not match 23.'

    trailer_error_2 = trailer_errors.last()
    assert trailer_error_2.error_type == ParserErrorCategoryChoices.PRE_CHECK
    assert trailer_error_2.error_message == 'T1trash does not start with TRAILER.'

    row_2_error = parser_errors.get(row_number=2)
    assert row_2_error.error_type == ParserErrorCategoryChoices.PRE_CHECK
    assert row_2_error.error_message == 'Value length 117 does not match 156.'

    row_3_error = parser_errors.get(row_number=3)
    assert row_3_error.error_type == ParserErrorCategoryChoices.PRE_CHECK
    assert row_3_error.error_message == 'Value length 7 does not match 156.'

    assert errors == {
        'trailer': [
            trailer_error_1,
            trailer_error_2
        ],
        2: [row_2_error],
        3: [row_3_error]
    }


@pytest.fixture
def empty_file(stt_user, stt):
    """Fixture for empty_file."""
    return create_test_datafile('empty_file', stt_user, stt)


@pytest.mark.django_db
def test_parse_empty_file(empty_file):
    """Test parsing of empty_file."""
    errors = parse.parse_datafile(empty_file)

    parser_errors = ParserError.objects.filter(file=empty_file)
    assert parser_errors.count() == 1

    err = parser_errors.first()

    assert err.row_number == 0
    assert err.error_type == ParserErrorCategoryChoices.PRE_CHECK
    assert err.error_message == 'No headers found.'
    assert errors == {
        'document': [err]
    }


@pytest.fixture
def small_ssp_section1_datafile(stt_user, stt):
    """Fixture for small_ssp_section1."""
    return create_test_datafile('small_ssp_section1.txt', stt_user, stt, 'SSP Active Case Data')


@pytest.mark.django_db
def test_parse_small_ssp_section1_datafile(small_ssp_section1_datafile):
    """Test parsing small_ssp_section1_datafile."""
    expected_m1_record_count = 5
    expected_m2_record_count = 6
    expected_m3_record_count = 8

    errors = parse.parse_datafile(small_ssp_section1_datafile)

    parser_errors = ParserError.objects.filter(file=small_ssp_section1_datafile)
    assert parser_errors.count() == 1

    err = parser_errors.first()

    assert err.row_number == -1
    assert err.error_type == ParserErrorCategoryChoices.PRE_CHECK
    assert err.error_message == 'Value length 15 does not match 23.'
    assert errors == {
        'trailer': [err]
    }
    assert SSP_M1.objects.count() == expected_m1_record_count
    assert SSP_M2.objects.count() == expected_m2_record_count
    assert SSP_M3.objects.count() == expected_m3_record_count


@pytest.fixture
def ssp_section1_datafile(stt_user, stt):
    """Fixture for ssp_section1_datafile."""
    return create_test_datafile('ssp_section1_datafile.txt', stt_user, stt, 'SSP Active Case Data')


# @pytest.mark.django_db
# def test_parse_ssp_section1_datafile(ssp_section1_datafile):
    # """Test parsing ssp_section1_datafile."""
#     expected_m1_record_count = 7849
#     expected_m2_record_count = 9373
#     expected_m3_record_count = 16764

#     errors = parse.parse_datafile(ssp_section1_datafile)

#     parser_errors = ParserError.objects.filter(file=ssp_section1_datafile)
#     assert parser_errors.count() == 6

#     trailer_error = parser_errors.get(row_number=-1)
#     assert trailer_error.error_type == ParserErrorCategoryChoices.PRE_CHECK
#     assert trailer_error.error_message == 'Value length 14 does not match 23.'

#     row_12430_error = parser_errors.get(row_number=12430)
#     assert row_12430_error.error_type == ParserErrorCategoryChoices.PRE_CHECK
#     assert row_12430_error.error_message == 'Value length 30 does not match 150.'

#     row_15573_error = parser_errors.get(row_number=15573)
#     assert row_15573_error.error_type == ParserErrorCategoryChoices.PRE_CHECK
#     assert row_15573_error.error_message == 'Value length 30 does not match 150.'

#     row_15615_error = parser_errors.get(row_number=15615)
#     assert row_15615_error.error_type == ParserErrorCategoryChoices.PRE_CHECK
#     assert row_15615_error.error_message == 'Value length 30 does not match 150.'

#     row_16004_error = parser_errors.get(row_number=16004)
#     assert row_16004_error.error_type == ParserErrorCategoryChoices.PRE_CHECK
#     assert row_16004_error.error_message == 'Value length 30 does not match 150.'

#     row_19681_error = parser_errors.get(row_number=19681)
#     assert row_19681_error.error_type == ParserErrorCategoryChoices.PRE_CHECK
#     assert row_19681_error.error_message == 'Value length 30 does not match 150.'

#     assert errors == {
#         'trailer': [trailer_error],
#         12430: [row_12430_error],
#         15573: [row_15573_error],
#         15615: [row_15615_error],
#         16004: [row_16004_error],
#         19681: [row_19681_error]
#     }
#     assert SSP_M1.objects.count() == expected_m1_record_count
#     assert SSP_M2.objects.count() == expected_m2_record_count
#     assert SSP_M3.objects.count() == expected_m3_record_count

@pytest.fixture
def small_tanf_section1_datafile(stt_user, stt):
    """Fixture for small_tanf_section1."""
    return create_test_datafile('small_tanf_section1.txt', stt_user, stt)

@pytest.mark.django_db
def test_parse_tanf_section1_datafile(small_tanf_section1_datafile):
    """Test parsing of small_tanf_section1_datafile and validate T2 model data."""
    errors = parse.parse_datafile(small_tanf_section1_datafile)

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

@pytest.mark.django_db
def test_parse_tanf_section1_datafile_obj_counts(small_tanf_section1_datafile):
    """Test parsing of small_tanf_section1_datafile in general."""
    errors = parse.parse_datafile(small_tanf_section1_datafile)

    assert errors == {}
    assert TANF_T1.objects.count() == 5
    assert TANF_T2.objects.count() == 5
    assert TANF_T3.objects.count() == 6

@pytest.mark.django_db
def test_parse_tanf_section1_datafile_t3s(small_tanf_section1_datafile):
    """Test parsing of small_tanf_section1_datafile and validate T3 model data."""
    errors = parse.parse_datafile(small_tanf_section1_datafile)

    assert errors == {}
    assert TANF_T3.objects.count() == 6

    t3_models = TANF_T3.objects.all()
    t3_1 = t3_models[0]
    assert t3_1.RPT_MONTH_YEAR == 202010
    assert t3_1.CASE_NUMBER == '11111111112'
    assert t3_1.FAMILY_AFFILIATION == 1
    assert t3_1.GENDER == 2
    assert t3_1.EDUCATION_LEVEL == '98'

    t3_6 = t3_models[5]
    assert t3_6.RPT_MONTH_YEAR == 202010
    assert t3_6.CASE_NUMBER == '11111111151'
    assert t3_6.FAMILY_AFFILIATION == 1
    assert t3_6.GENDER == 2
    assert t3_6.EDUCATION_LEVEL == '98'
