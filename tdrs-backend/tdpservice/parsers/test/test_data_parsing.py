"""Test preparser functions and tanf_parser."""
import pytest
from functools import reduce
from pathlib import Path

from tdpservice.parsers import tanf_parser, preparser, util
from tdpservice.search_indexes.models import T1

import logging
logger = logging.getLogger(__name__)

# TODO: ORM mock for true data file factories
# https://stackoverflow.com/questions/1533861/testing-django-models-with-filefield

@pytest.fixture
def test_file():
    """Open file pointer to test file."""
    test_filepath = str(Path(__file__).parent.joinpath('data'))
    test_filename = test_filepath + "/small_correct_file"
    yield open(test_filename, 'rb')

@pytest.fixture
def test_big_file():
    """Open file pointer to test file."""
    test_filepath = str(Path(__file__).parent.joinpath('data'))
    test_filename = test_filepath + "/ADS.E2J.FTP1.TS06"
    yield open(test_filename, 'rb')

@pytest.fixture
def bad_test_file():
    """Open file pointer to bad test file."""
    test_filepath = str(Path(__file__).parent.joinpath('data'))
    test_filename = test_filepath + "/bad_TANF_S2.txt"
    yield open(test_filename, 'rb')

@pytest.fixture
def bad_file_missing_header():
    """Open file pointer to bad test file."""
    test_filepath = str(Path(__file__).parent.joinpath('data'))
    test_filename = test_filepath + "/bad_missing_header.txt"
    yield open(test_filename, 'rb')

@pytest.fixture
def bad_file_multiple_headers():
    """Open file pointer to bad test file."""
    test_filepath = str(Path(__file__).parent.joinpath('data'))
    test_filename = test_filepath + "/bad_two_headers.txt"
    yield open(test_filename, 'rb')

@pytest.fixture
def big_bad_test_file():
    """Open file pointer to bad test file."""
    test_filepath = str(Path(__file__).parent.joinpath('data'))
    test_filename = test_filepath + "/bad_TANF_S1.txt"
    yield open(test_filename, 'rb')

@pytest.fixture
def bad_trailer_file():
    """Open file pointer to bad test file."""
    test_filepath = str(Path(__file__).parent.joinpath('data'))
    test_filename = test_filepath + "/bad_trailer_1.txt"
    yield open(test_filename, 'rb')

@pytest.fixture
def bad_trailer_file_2():
    """Open file pointer to bad test file."""
    test_filepath = str(Path(__file__).parent.joinpath('data'))
    test_filename = test_filepath + "/bad_trailer_2.txt"
    yield open(test_filename, 'rb')

@pytest.fixture
def empty_file():
    """Open file pointer to bad test file."""
    test_filepath = str(Path(__file__).parent.joinpath('data'))
    test_filename = test_filepath + "/empty_file"
    yield open(test_filename, 'rb')

def test_preparser_header(test_file, bad_test_file):
    """Test header preparser."""
    logger.info("test_file type: %s", type(test_file))
    test_line = test_file.readline().decode()
    is_valid, validator = preparser.validate_header(test_line, 'TANF', 'Active Case Data')

    logger.info("is_valid: %s", is_valid)
    logger.info("errors: %s", validator.errors)
    assert is_valid is True
    assert validator.errors == {}
    assert validator.document['state_fips'] == '06'

    # negative case
    bad_line = bad_test_file.readline().decode()
    not_valid, not_validator = preparser.validate_header(bad_line, 'TANF', 'Active Case Data')
    assert not_valid is False
    assert not_validator.errors != {}

    # Inserting a bad section type
    with pytest.raises(ValueError) as e_info:
        preparser.validate_header(test_line, 'TANF', 'Active Casexs')
    assert str(e_info.value) == "Given section does not match header section."

    # Inserting a bad program type
    with pytest.raises(ValueError) as e_info:
        preparser.validate_header(test_line, 'GARBAGE', 'Active Case Data')
    assert str(e_info.value) == "Given data type does not match header program type."

def test_preparser_trailer(test_file):
    """Test trailer preparser."""
    for line in test_file:
        line = line.decode()
        if util.get_record_type(line) == 'TR':
            trailer_line = line
            break
    is_valid, validator = preparser.validate_trailer(trailer_line)
    assert is_valid
    assert validator.errors == {}

    logger.debug("validator: %s", validator)
    logger.debug("validator.document: %s", validator.document)
    assert validator.document['record_count'] == '0000001'

def test_preparser_trailer_bad(bad_trailer_file, bad_trailer_file_2, empty_file):
    """Test trailer preparser with malformed trailers."""
    status, err = preparser.get_trailer_line(empty_file)
    assert status is False
    assert err['preparsing'] == 'File too short or missing trailer.'

    status, err = preparser.get_trailer_line(bad_trailer_file)
    assert status is False
    assert err['preparsing'] == 'Trailer length incorrect.'

    with pytest.raises(ValueError) as e_info:
        logger.debug(preparser.get_trailer_line(bad_trailer_file_2))
    assert str(e_info.value) == 'Last line is not recognized as a trailer line.'

def spy_count_check(spies, expected_counts):
    """Run reduce against two lists, returning True if all functions were called the expected number of times."""
    return reduce(lambda carry, expected: carry == all(expected),
                  [zip([spy.call_count for spy in spies], expected_counts)],
                  True)
    # logger.debug("reduceVal: %s", reduceVal)
    # for spy, expected in zip(spies, expected_counts):
    #    logger.debug("%s: spy called %s times\texpected\t%s", spy, spy.call_count, expected)
    #    assert spy.call_count == expected

@pytest.mark.django_db
def test_preparser_body(test_file, mocker):
    """Test that preparse correctly calls lower parser functions...or doesn't."""
    spy_preparse = mocker.spy(preparser, 'preparse')
    spy_head = mocker.spy(preparser, 'validate_header')
    spy_tail = mocker.spy(preparser, 'validate_trailer')
    spy_parse = mocker.spy(tanf_parser, 'parse')
    spy_t1 = mocker.spy(tanf_parser, 'active_t1_parser')

    spies = [spy_preparse, spy_head, spy_tail, spy_parse, spy_t1]
    assert preparser.preparse(test_file, 'TANF', 'Active Case Data')

    assert spy_count_check(spies, [1, 1, 1, 1, 1])

@pytest.mark.django_db
def test_preparser_big_file(test_big_file, mocker):
    """Test the preparse correctly handles a large, correct file."""
    spy_preparse = mocker.spy(preparser, 'preparse')
    spy_head = mocker.spy(preparser, 'validate_header')
    spy_tail = mocker.spy(preparser, 'validate_trailer')
    spy_parse = mocker.spy(tanf_parser, 'parse')
    spy_t1 = mocker.spy(tanf_parser, 'active_t1_parser')

    spies = [spy_preparse, spy_head, spy_tail, spy_parse, spy_t1]
    assert preparser.preparse(test_big_file, 'TANF', 'Active Case Data')

    assert spy_count_check(spies, [1, 1, 1, 1, 815])

@pytest.mark.django_db
def test_preparser_bad_file(bad_test_file, bad_file_missing_header, bad_file_multiple_headers, mocker):
    """Test that preparse correctly catches issues in a bad file."""
    spy_preparse = mocker.spy(preparser, 'preparse')
    spy_head = mocker.spy(preparser, 'validate_header')
    spy_tail = mocker.spy(preparser, 'validate_trailer')
    spy_parse = mocker.spy(tanf_parser, 'parse')
    spy_t1 = mocker.spy(tanf_parser, 'active_t1_parser')

    spies = [spy_preparse, spy_head, spy_tail, spy_parse, spy_t1]
    with pytest.raises(ValueError) as e_info:
        is_valid, preparser_errors = preparser.preparse(bad_test_file, 'TANF', 'Active Case Data')
    assert str(e_info.value) == 'Header invalid, error: Header length incorrect.'

    assert spy_count_check(spies, [1, 0, 0, 0, 0])

    with pytest.raises(ValueError) as e_info:
        preparser.preparse(bad_file_missing_header, 'TANF', 'Active Case Data')
    assert str(e_info.value) == 'Header invalid, error: First line in file is not recognized as a valid header.'

    with pytest.raises(ValueError) as e_info:
        preparser.preparse(bad_file_multiple_headers, 'TANF', 'Active Case Data')
    assert str(e_info.value).startswith('Preparsing error: Multiple header lines found')

@pytest.mark.django_db
def test_preparser_bad_params(test_file, mocker):
    """Test that preparse correctly catches bad parameters."""
    spy_preparse = mocker.spy(preparser, 'preparse')
    spy_head = mocker.spy(preparser, 'validate_header')
    spy_tail = mocker.spy(preparser, 'validate_trailer')
    spy_parse = mocker.spy(tanf_parser, 'parse')
    spy_t1 = mocker.spy(tanf_parser, 'active_t1_parser')

    spies = [spy_preparse, spy_head, spy_tail, spy_parse, spy_t1]

    with pytest.raises(ValueError) as e_info:
        preparser.preparse(test_file, 'TANF', 'Garbage Cases')
    assert str(e_info.value) == 'Given section does not match header section.'
    logger.debug("test_preparser_bad_params::garbage section value:")
    for spy in spies:
        logger.debug("Spy: %s\tCount: %s", spy, spy.call_count)
    assert spy_count_check(spies, [1, 1, 0, 0, 0])

    with pytest.raises(ValueError) as e_info:
        preparser.preparse(test_file, 'GARBAGE', 'Active Case Data')
    assert str(e_info.value) == "Given data type does not match header program type."
    logger.debug("test_preparser_bad_params::wrong program_type value:")
    for spy in spies:
        logger.debug("Spy: %s\tCount: %s", spy, spy.call_count)
    assert spy_count_check(spies, [2, 2, 0, 0, 0])

    with pytest.raises(ValueError) as e_info:
        preparser.preparse(test_file, 1234, 'Active Case Data')
    assert str(e_info.value) == 'Given data type does not match header program type.'
    logger.debug("test_preparser_bad_params::wrong program_type type:")
    for spy in spies:
        logger.debug("Spy: %s\tCount: %s", spy, spy.call_count)
    assert spy_count_check(spies, [3, 3, 0, 0, 0])


@pytest.mark.django_db
def test_parsing_tanf_t1_active(test_file):
    """Test tanf_parser.active_t1_parser."""
    t1_count_before = T1.objects.count()
    assert t1_count_before == 0
    tanf_parser.parse(test_file)
    t1_count_after = T1.objects.count()
    assert t1_count_after == (t1_count_before + 1)

    # define expected values
    # we get back a parser log object for 1354
    # should we create a FK between parserlog and t1 model?

@pytest.mark.django_db
def test_parsing_tanf_t1_bad(bad_test_file, big_bad_test_file):
    """Test tanf_parser.active_case_data with bad data."""
    t1_count_before = T1.objects.count()
    logger.info("t1_count_before: %s", t1_count_before)

    tanf_parser.parse(bad_test_file)

    t1_count_after = T1.objects.count()
    logger.info("t1_count_after: %s", t1_count_after)
    assert t1_count_after == t1_count_before

    t1_count_before = T1.objects.count()
    logger.info("t1_count_before: %s", t1_count_before)

    tanf_parser.parse(big_bad_test_file)

    t1_count_after = T1.objects.count()
    logger.info("t1_count_after: %s", t1_count_after)
    assert t1_count_after == t1_count_before
