"""Test the methods of TanfDataReportSchema to ensure parsing and validation work in all individual cases."""

import pytest
from datetime import datetime
from ..fields import Field
from ..row_schema import TanfDataReportSchema
from ..util import (
    make_generate_parser_error,
    create_test_datafile,
    get_years_apart,
    clean_options_string,
    generate_t2_t3_t5_hashes)
from ..validators.category3 import ifThenAlso
from ..validators.util import deprecate_call, deprecate_validator, make_validator
from tdpservice.parsers.dataclasses import FieldType, RawRow
import logging

def passing_validator():
    """Fake validator that always returns valid."""
    return make_validator(lambda _, : True,
                          lambda _, : "Failed.")

def failing_validator():
    """Fake validator that always returns invalid."""
    return make_validator(lambda _, : False,
                          lambda _, : "Value is not valid.")

def error_func(schema, error_category, error_message, record, field, deprecated=False):
    """Fake error func that returns an error_message."""
    return error_message

def deprecated_error_func(schema, error_category, error_message, record, field, deprecated=False):
    """Fake error func that returns an error_message and if the validator is deprecated."""
    return (error_message, deprecated)


@deprecate_validator
def deprecated_validator():
    """Fake validator that is false and is deprecated."""
    return make_validator(lambda _, : False,
                          lambda _, : "Failed.")

def validator_to_deprecate():
    """Fake validator that is False and becomes deprecated when invoked."""
    return make_validator(lambda _, : False,
                          lambda _, : "Failed.")


def test_deprecate_validator():
    """Test completely deprecated validator."""
    line = '12345'
    schema = TanfDataReportSchema(
        model=None,
        preparsing_validators=[
            deprecated_validator()
        ]
    )

    is_valid, errors = schema.run_preparsing_validators(line, None, deprecated_error_func)
    assert is_valid is False
    assert len(errors) == 1

    error = errors[0]
    assert error[0] == "Failed."
    assert error[1] is True


def test_deprecate_call():
    """Test deprecated invocation of a validator."""
    line = '12345'
    schema = TanfDataReportSchema(
        model=None,
        preparsing_validators=[
            deprecate_call(validator_to_deprecate()),
            passing_validator()
        ]
    )

    is_valid, errors = schema.run_preparsing_validators(line, None, deprecated_error_func)
    assert is_valid is False
    assert len(errors) == 1

    error = errors[0]
    assert error[0] == "Failed."
    assert error[1] is True


def test_run_preparsing_validators_returns_valid():
    """Test run_preparsing_validators executes all preparsing_validators provided in schema."""
    line = '12345'
    schema = TanfDataReportSchema(
        model=None,
        preparsing_validators=[
            passing_validator()
        ]
    )

    is_valid, errors = schema.run_preparsing_validators(line, None, error_func)
    assert is_valid is True
    assert errors == []


def test_run_preparsing_validators_returns_invalid_and_errors():
    """Test that run_preparsing_validators executes all preparsing_validators provided in schema and returns errors."""
    line = '12345'
    schema = TanfDataReportSchema(
        model=None,
        preparsing_validators=[
            passing_validator(),
            failing_validator()
        ]
    )

    is_valid, errors = schema.run_preparsing_validators(line, None, error_func)
    assert is_valid is False
    assert errors == ['Value is not valid.']


def test_parse_line_parses_line_from_schema_to_dict():
    """Test that parse_line parses a string into a dict given start and end indices for all fields."""
    line = '12345001'
    schema = TanfDataReportSchema(
        model=dict,
        fields=[
            Field(item=1, name='first', friendly_name='first', type=FieldType.ALPHA_NUMERIC,
                  startIndex=0, endIndex=3),
            Field(item=2, name='second', friendly_name='second', type=FieldType.ALPHA_NUMERIC,
                  startIndex=3, endIndex=4),
            Field(item=3, name='third', friendly_name='third', type=FieldType.ALPHA_NUMERIC,
                  startIndex=4, endIndex=5),
            Field(item=4, name='fourth', friendly_name='fourth', type=FieldType.NUMERIC,
                  startIndex=5, endIndex=7),
            Field(item=5, name='fifth', friendly_name='fifth', type=FieldType.NUMERIC,
                  startIndex=7, endIndex=8),
        ]
    )

    length = len(line)
    row = RawRow(data=line, raw_len=length, decoded_len=length, row_num=1, record_type="")
    record = schema.parse_row(row)

    assert record['first'] == '123'
    assert record['second'] == '4'
    assert record['third'] == '5'
    assert record['fourth'] == 0
    assert record['fifth'] == 1


def test_parse_line_parses_line_from_schema_to_object():
    """Test that parse_line parses a string into an object given start and end indices for all fields."""
    class TestModel:
        first = None
        second = None
        third = None
        fourth = None
        fifth = None

    line = '12345001'
    schema = TanfDataReportSchema(
        model=TestModel,
        fields=[
            Field(item=1, name='first', friendly_name='first', type=FieldType.ALPHA_NUMERIC,
                  startIndex=0, endIndex=3),
            Field(item=2, name='second', friendly_name='second', type=FieldType.ALPHA_NUMERIC,
                  startIndex=3, endIndex=4),
            Field(item=3, name='third', friendly_name='third', type=FieldType.ALPHA_NUMERIC,
                  startIndex=4, endIndex=5),
            Field(item=4, name='fourth', friendly_name='fourth', type=FieldType.NUMERIC,
                  startIndex=5, endIndex=7),
            Field(item=5, name='fifth', friendly_name='fifth', type=FieldType.NUMERIC,
                  startIndex=7, endIndex=8),
        ]
    )

    length = len(line)
    row = RawRow(data=line, raw_len=length, decoded_len=length, row_num=1, record_type="")
    record = schema.parse_row(row)

    assert record.first == '123'
    assert record.second == '4'
    assert record.third == '5'
    assert record.fourth == 0
    assert record.fifth == 1


def test_run_field_validators_returns_valid_with_dict():
    """Test that run_field_validators can validate all fields against parsed data dict."""
    instance = {
        'first': '123',
        'second': '4',
        'third': '5'
    }
    schema = TanfDataReportSchema(
        model=None,
        fields=[
            Field(item=1, name='first', friendly_name='first', type=FieldType.ALPHA_NUMERIC,
                  startIndex=0, endIndex=3, validators=[
                      passing_validator()
                      ]),
            Field(item=2, name='second', friendly_name='second', type=FieldType.ALPHA_NUMERIC,
                  startIndex=3, endIndex=4, validators=[
                      passing_validator()
                      ]),
            Field(item=3, name='third', friendly_name='third', type=FieldType.ALPHA_NUMERIC,
                  startIndex=4, endIndex=5, validators=[
                      passing_validator()
                      ]),
        ]
    )

    is_valid, errors = schema.run_field_validators(instance, error_func)
    assert is_valid is True
    assert errors == []


def test_run_field_validators_returns_valid_with_object():
    """Test that run_field_validators can validate all fields against parsed data object."""
    class TestModel:
        first = None
        second = None
        third = None

    instance = TestModel
    instance.first = '123'
    instance.second = '4'
    instance.third = '5'

    model = instance

    schema = TanfDataReportSchema(
        model=model,
        fields=[
            Field(item=1, name='first', friendly_name='first', type=FieldType.ALPHA_NUMERIC,
                  startIndex=0, endIndex=3, validators=[
                      passing_validator()
                      ]),
            Field(item=2, name='second', friendly_name='second', type=FieldType.ALPHA_NUMERIC,
                  startIndex=3, endIndex=4, validators=[
                      passing_validator()
                      ]),
            Field(item=3, name='third', friendly_name='third', type=FieldType.ALPHA_NUMERIC,
                  startIndex=4, endIndex=5, validators=[
                      passing_validator()
                      ]),
        ]
    )

    is_valid, errors = schema.run_field_validators(instance, error_func)
    assert is_valid is True
    assert errors == []


def test_run_field_validators_returns_invalid_with_dict():
    """Test that run_field_validators can validate all fields against parsed data dict and return errors."""
    instance = {
        'first': '123',
        'second': '4',
        'third': '5'
    }
    schema = TanfDataReportSchema(
        model=None,
        fields=[
            Field(item=1, name='first', friendly_name='first', type=FieldType.ALPHA_NUMERIC,
                  startIndex=0, endIndex=3, validators=[
                      passing_validator(),
                      failing_validator()
                      ]),
            Field(item=2, name='second', friendly_name='second', type=FieldType.ALPHA_NUMERIC,
                  startIndex=3, endIndex=4, validators=[
                      passing_validator()
                      ]),
            Field(item=3, name='third', friendly_name='third', type=FieldType.ALPHA_NUMERIC,
                  startIndex=4, endIndex=5, validators=[
                      passing_validator()
                      ]),
        ]
    )

    is_valid, errors = schema.run_field_validators(instance, error_func)
    assert is_valid is False
    assert errors == ['Value is not valid.']


def test_run_field_validators_returns_invalid_with_object():
    """Test that run_field_validators can validate all fields against parsed data object and return errors."""
    class TestModel:
        first = None
        second = None
        third = None

    instance = TestModel
    instance.first = '123'
    instance.second = '4'
    instance.third = '5'

    model = instance

    schema = TanfDataReportSchema(
        model=model,
        fields=[
            Field(item=1, name='first', friendly_name='first', type=FieldType.ALPHA_NUMERIC,
                  startIndex=0, endIndex=3, validators=[
                      passing_validator(),
                      failing_validator()
                      ]),
            Field(item=2, name='second', friendly_name='second', type=FieldType.ALPHA_NUMERIC,
                  startIndex=3, endIndex=4, validators=[
                      passing_validator()
                      ]),
            Field(item=3, name='third', friendly_name='third', type=FieldType.ALPHA_NUMERIC,
                  startIndex=4, endIndex=5, validators=[
                      passing_validator()
                      ]),
        ]
    )

    is_valid, errors = schema.run_field_validators(instance, error_func)
    assert is_valid is False
    assert errors == ['Value is not valid.']


@pytest.mark.parametrize('first,second', [
    ('', ''),
    (' ', '  '),
    ('#', '##'),
    (None, None),
])
def test_field_validators_blank_and_required_returns_error(first, second):
    """Test required field returns error if value not provided (blank)."""
    instance = {
        'first': first,
        'second': second,
    }
    schema = TanfDataReportSchema(
        model=None,
        fields=[
            Field(
                item=1,
                name='first',
                friendly_name='first',
                type=FieldType.ALPHA_NUMERIC,
                startIndex=0,
                endIndex=1,
                required=True,
                validators=[
                    passing_validator(),
                ]
            ),
            Field(
                item=2,
                name='second',
                friendly_name='second',
                type=FieldType.ALPHA_NUMERIC,
                startIndex=1,
                endIndex=3,
                required=True,
                validators=[
                    passing_validator(),
                ]
            ),
        ]
    )

    is_valid, errors = schema.run_field_validators(instance, error_func)
    assert is_valid is False
    assert errors == [
        'T1 Item 1 (first): field is required but a value was not provided.',
        'T1 Item 2 (second): field is required but a value was not provided.'
    ]


@pytest.mark.parametrize('first, expected_valid, expected_errors', [
    ('   ', True, []),
    ('####', True, []),
    (None, True, []),
])
def test_field_validators_blank_and_not_required_returns_valid(first, expected_valid, expected_errors):
    """Test not required field returns valid if value not provided (blank)."""
    instance = {
        'first': first,
    }
    schema = TanfDataReportSchema(
        model=None,
        fields=[
            Field(
                item=1,
                name='first',
                friendly_name='first',
                type=FieldType.ALPHA_NUMERIC,
                startIndex=0,
                endIndex=3,
                required=False,
                validators=[
                    passing_validator(),
                    failing_validator()
                ]
            ),
        ]
    )

    is_valid, errors = schema.run_field_validators(instance, error_func)
    assert is_valid is expected_valid
    assert errors == expected_errors


def test_run_postparsing_validators_returns_valid():
    """Test run_postparsing_validators executes all postparsing_validators provided in schema."""
    instance = {}
    schema = TanfDataReportSchema(
        model=None,
        postparsing_validators=[
            passing_validator()
        ]
    )

    is_valid, errors = schema.run_postparsing_validators(instance, error_func)
    assert is_valid is True
    assert errors == []


def test_run_postparsing_validators_returns_invalid_and_errors():
    """Test run_postparsing_validators executes all postparsing_validators provided in schema and returns errors."""
    instance = {}
    schema = TanfDataReportSchema(
        model=None,
        postparsing_validators=[
            passing_validator(),
            failing_validator()
        ]
    )

    is_valid, errors = schema.run_postparsing_validators(instance, error_func)
    assert is_valid is False
    assert errors == ['Value is not valid.']


@pytest.fixture
def test_datafile_empty_file(stt_user, stt):
    """Fixture for empty_file."""
    return create_test_datafile('empty_file', stt_user, stt)

@pytest.mark.django_db()
def test_run_postparsing_validators_returns_frinedly_fieldnames(test_datafile_empty_file):
    """Test run_postparsing_validators executes all postparsing_validators provided in schema."""
    instance = {}
    schema = TanfDataReportSchema(
        model=None,
        postparsing_validators=[
            ifThenAlso("FIRST", passing_validator(),
                       "SECOND", failing_validator())
        ],
        fields=[
            Field(
                item=1,
                name='FIRST',
                friendly_name='first',
                type=FieldType.ALPHA_NUMERIC,
                startIndex=0,
                endIndex=3,
                required=False,
                validators=[]
            ),
            Field(
                item=2,
                name='SECOND',
                friendly_name='second',
                type=FieldType.ALPHA_NUMERIC,
                startIndex=3,
                endIndex=4,
                required=False,
                validators=[]
            ),
        ]
    )

    is_valid, errors = schema.run_postparsing_validators(instance, make_generate_parser_error(
        test_datafile_empty_file, 10
    ))
    assert is_valid is False
    assert errors[0].fields_json == {
        "friendly_name": {"FIRST": "first", "SECOND": "second"},
        "item_numbers": {"FIRST": 1, "SECOND": 2},
    }
    assert errors[0].error_message == "Since Item 1 (first) is None, then Item 2 (second) None Value is not valid."


@pytest.mark.parametrize("rpt_date_str,date_str,expected", [
    ('20200102', '20100101', 10),
    ('20200102', '20100106', 9),
    ('20200101', '20200102', 0),
    ('20200101', '20210102', -1),
])
def test_get_years_apart(rpt_date_str, date_str, expected):
    """Test the get_years_apart util function."""
    rpt_date = datetime.strptime(rpt_date_str, '%Y%m%d')
    date = datetime.strptime(date_str, '%Y%m%d')
    assert int(get_years_apart(rpt_date, date)) == expected


@pytest.mark.parametrize('options, expected', [
    ([1, 2, 3, 4], '[1, 2, 3, 4]'),
    (['1', '2', '3', '4'], '[1, 2, 3, 4]'),
    (['a', 'b', 'c', 'd'], '[a, b, c, d]'),
    (('a', 'b', 'c', 'd'), '[a, b, c, d]'),
    (["'a'", "'b'", "'c'", "'d'"], "['a', 'b', 'c', 'd']"),
    (['words', 'are very', 'weird'], '[words, are very, weird]'),
])
def test_clean_options_string(options, expected):
    """Test `clean_options_string` util func."""
    result = clean_options_string(options)
    assert result == expected


@pytest.mark.django_db()
def test_empty_SSN_DOB_space_filled(caplog):
    """Test empty_SSN_DOB_space_filled."""
    line = 'fake_line'

    class record:
        CASE_NUMBER = 'fake_case_number'
        SSN = None
        DATE_OF_BIRTH = None
        FAMILY_AFFILIATION = 'fake_family_affiliation'
        RPT_MONTH_YEAR = '202310'
        RecordType = 'T2'

    with caplog.at_level(logging.ERROR):
        generate_t2_t3_t5_hashes(line, record)
    assert caplog.text == ''
