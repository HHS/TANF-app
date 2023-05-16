"""Test the implementation of the parse_file method with realistic datafiles."""


import pytest
from pathlib import Path
from .. import parse
from tdpservice.data_files.models import DataFile
from tdpservice.search_indexes.models.tanf import TANF_T1
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
    assert errors == {
        'document': ['Section does not match.']
    }


@pytest.mark.django_db
def test_parse_wrong_program_type(test_datafile):
    """Test parsing of small_correct_file where the DataFile program type doesn't match the rawfile."""
    test_datafile.section = 'SSP Active Case Data'
    test_datafile.save()
    errors = parse.parse_datafile(test_datafile)
    assert errors == {
        'document': ['Section does not match.']
    }


@pytest.fixture
def test_big_file(stt_user, stt):
    """Fixture for ADS.E2J.FTP1.TS06."""
    return create_test_datafile('ADS.E2J.FTP1.TS06', stt_user, stt)


@pytest.mark.django_db
def test_parse_big_file(test_big_file):
    """Test parsing of ADS.E2J.FTP1.TS06."""
    expected_errors_count = 1828
    expected_t1_record_count = 815

    errors = parse.parse_datafile(test_big_file)

    assert len(errors.keys()) == expected_errors_count
    assert TANF_T1.objects.count() == expected_t1_record_count


@pytest.fixture
def bad_test_file(stt_user, stt):
    """Fixture for bad_TANF_S2."""
    return create_test_datafile('bad_TANF_S2.txt', stt_user, stt)


@pytest.mark.django_db
def test_parse_bad_test_file(bad_test_file):
    """Test parsing of bad_TANF_S2."""
    errors = parse.parse_datafile(bad_test_file)
    assert errors == {
        'header': ['Value length 24 does not match 23.'],
    }


@pytest.fixture
def bad_file_missing_header(stt_user, stt):
    """Fixture for bad_missing_header."""
    return create_test_datafile('bad_missing_header.txt', stt_user, stt)


@pytest.mark.django_db
def test_parse_bad_file_missing_header(bad_file_missing_header):
    """Test parsing of bad_missing_header."""
    errors = parse.parse_datafile(bad_file_missing_header)
    assert errors == {
        'document': ['No headers found.'],
    }


@pytest.fixture
def bad_file_multiple_headers(stt_user, stt):
    """Fixture for bad_two_headers."""
    return create_test_datafile('bad_two_headers.txt', stt_user, stt)


@pytest.mark.django_db
def test_parse_bad_file_multiple_headers(bad_file_multiple_headers):
    """Test parsing of bad_two_headers."""
    errors = parse.parse_datafile(bad_file_multiple_headers)
    assert errors == {
        'document': ['Multiple headers found.'],
    }


@pytest.fixture
def big_bad_test_file(stt_user, stt):
    """Fixture for bad_TANF_S1."""
    return create_test_datafile('bad_TANF_S1.txt', stt_user, stt)


@pytest.mark.django_db
def test_parse_big_bad_test_file(big_bad_test_file):
    """Test parsing of bad_TANF_S1."""
    errors = parse.parse_datafile(big_bad_test_file)
    assert errors == {
        'document': ['Multiple trailers found.'],
    }


@pytest.fixture
def bad_trailer_file(stt_user, stt):
    """Fixture for bad_trailer_1."""
    return create_test_datafile('bad_trailer_1.txt', stt_user, stt)


@pytest.mark.django_db
def test_parse_bad_trailer_file(bad_trailer_file):
    """Test parsing bad_trailer_1."""
    errors = parse.parse_datafile(bad_trailer_file)
    assert errors == {
        'trailer': ['Value length 11 does not match 23.'],
        2: ['Value length 7 does not match 156.'],
    }


@pytest.fixture
def bad_trailer_file_2(stt_user, stt):
    """Fixture for bad_trailer_2."""
    return create_test_datafile('bad_trailer_2.txt', stt_user, stt)


@pytest.mark.django_db
def test_parse_bad_trailer_file2(bad_trailer_file_2):
    """Test parsing bad_trailer_2."""
    errors = parse.parse_datafile(bad_trailer_file_2)
    assert errors == {
        'trailer': [
            'Value length 7 does not match 23.',
            'T1trash does not start with TRAILER.'
        ],
        2: ['Value length 117 does not match 156.'],
        3: ['Value length 7 does not match 156.']
    }


@pytest.fixture
def empty_file(stt_user, stt):
    """Fixture for empty_file."""
    return create_test_datafile('empty_file', stt_user, stt)


@pytest.mark.django_db
def test_parse_empty_file(empty_file):
    """Test parsing of empty_file."""
    errors = parse.parse_datafile(empty_file)
    assert errors == {
        'document': ['No headers found.'],
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

    assert errors == {
        'trailer': ['Value length 15 does not match 23.']
    }
    assert SSP_M1.objects.count() == expected_m1_record_count
    assert SSP_M2.objects.count() == expected_m2_record_count
    assert SSP_M3.objects.count() == expected_m3_record_count


@pytest.fixture
def ssp_section1_datafile(stt_user, stt):
    """Fixture for ssp_section1_datafile."""
    return create_test_datafile('ssp_section1_datafile.txt', stt_user, stt, 'SSP Active Case Data')


@pytest.mark.django_db
def test_parse_ssp_section1_datafile(ssp_section1_datafile):
    """Test parsing ssp_section1_datafile."""
    expected_m1_record_count = 7849
    expected_m2_record_count = 9373
    expected_m3_record_count = 16764

    errors = parse.parse_datafile(ssp_section1_datafile)

    assert errors == {
        'trailer': ['Value length 14 does not match 23.'],
        12430: ['Value length 30 does not match 150.'],
        15573: ['Value length 30 does not match 150.'],
        15615: ['Value length 30 does not match 150.'],
        16004: ['Value length 30 does not match 150.'],
        19681: ['Value length 30 does not match 150.']
    }
    assert SSP_M1.objects.count() == expected_m1_record_count
    assert SSP_M2.objects.count() == expected_m2_record_count
    assert SSP_M3.objects.count() == expected_m3_record_count
