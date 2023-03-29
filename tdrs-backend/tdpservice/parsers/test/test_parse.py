"""Test the implementation of the parse_file method with realistic datafiles."""


import pytest
from pathlib import Path
from .. import parse
from tdpservice.data_files.models import DataFile


def create_test_datafile(filename, stt_user, stt):
    """Create a test DataFile instance with the given file attached."""
    path = str(Path(__file__).parent.joinpath('data')) + f'/{filename}'
    datafile = DataFile.create_new_version({
        'quarter': '4',
        'year': 2022,
        'section': 'Active Case Data',
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
    assert errors == {
        2: ['No schema selected.']
    }


@pytest.mark.django_db
def test_parse_section_mismatch(test_datafile):
    """Test parsing of small_correct_file where the DataFile section doesn't match the rawfile section."""
    test_datafile.section = 'Closed Case Data'
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
    expected_errors = {}
    for i in range(2, 2645):
        expected_errors[i] = ['No schema selected.']

    errors = parse.parse_datafile(test_big_file)
    assert errors == expected_errors


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
        # 'trailer': ['Value length 14 does not match 23.'],
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
        'document': ['Multiple headers found.'],
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
        2: ['No schema selected.'],
        3: ['Value length 11 does not match 23.'],
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
        2: ['No schema selected.'],
        3: ['No schema selected.'],
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
