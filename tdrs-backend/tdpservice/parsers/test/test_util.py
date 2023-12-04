"""Test the methods of RowSchema to ensure parsing and validation work in all individual cases."""

import pytest
from ..fields import Field, value_is_empty
from ..row_schema import RowSchema
from ..util import SchemaManager, make_generate_parser_error, create_test_datafile


def passing_validator():
    """Fake validator that always returns valid."""
    return lambda _: (True, None)


def failing_validator():
    """Fake validator that always returns invalid."""
    return lambda _: (False, 'Value is not valid.')

def passing_postparsing_validator():
    """Fake validator that always returns valid."""
    return lambda _: (True, None, [])


def failing_postparsing_validator():
    """Fake validator that always returns invalid."""
    return lambda _: (False, 'Value is not valid.', [])

def error_func(schema, error_category, error_message, record, field):
    """Fake error func that returns an error_message."""
    return error_message


def test_run_preparsing_validators_returns_valid():
    """Test run_preparsing_validators executes all preparsing_validators provided in schema."""
    line = '12345'
    schema = RowSchema(
        preparsing_validators=[
            passing_validator()
        ]
    )

    is_valid, errors = schema.run_preparsing_validators(line, error_func)
    assert is_valid is True
    assert errors == []


def test_run_preparsing_validators_returns_invalid_and_errors():
    """Test that run_preparsing_validators executes all preparsing_validators provided in schema and returns errors."""
    line = '12345'
    schema = RowSchema(
        preparsing_validators=[
            passing_validator(),
            failing_validator()
        ]
    )

    is_valid, errors = schema.run_preparsing_validators(line, error_func)
    assert is_valid is False
    assert errors == ['Value is not valid.']


def test_parse_line_parses_line_from_schema_to_dict():
    """Test that parse_line parses a string into a dict given start and end indices for all fields."""
    line = '12345001'
    schema = RowSchema(
        model=dict,
        fields=[
            Field(item=1, name='first', friendly_name='first', type='string', startIndex=0, endIndex=3),
            Field(item=2, name='second', friendly_name='second', type='string', startIndex=3, endIndex=4),
            Field(item=3, name='third', friendly_name='third', type='string', startIndex=4, endIndex=5),
            Field(item=4, name='fourth', friendly_name='fourth', type='number', startIndex=5, endIndex=7),
            Field(item=5, name='fifth', friendly_name='fifth', type='number', startIndex=7, endIndex=8),
        ]
    )

    record = schema.parse_line(line)

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
    schema = RowSchema(
        model=TestModel,
        fields=[
            Field(item=1, name='first', friendly_name='first', type='string', startIndex=0, endIndex=3),
            Field(item=2, name='second', friendly_name='second', type='string', startIndex=3, endIndex=4),
            Field(item=3, name='third', friendly_name='third', type='string', startIndex=4, endIndex=5),
            Field(item=4, name='fourth', friendly_name='fourth', type='number', startIndex=5, endIndex=7),
            Field(item=5, name='fifth', friendly_name='fifth', type='number', startIndex=7, endIndex=8),
        ]
    )

    record = schema.parse_line(line)

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
    schema = RowSchema(
        model=dict,
        fields=[
            Field(item=1, name='first', friendly_name='first', type='string', startIndex=0, endIndex=3, validators=[
                passing_validator()
            ]),
            Field(item=2, name='second', friendly_name='second', type='string', startIndex=3, endIndex=4, validators=[
                passing_validator()
            ]),
            Field(item=3, name='third', friendly_name='third', type='string', startIndex=4, endIndex=5, validators=[
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

    instance = TestModel()
    instance.first = '123'
    instance.second = '4'
    instance.third = '5'

    schema = RowSchema(
        model=TestModel,
        fields=[
            Field(item=1, name='first', friendly_name='first', type='string', startIndex=0, endIndex=3, validators=[
                passing_validator()
            ]),
            Field(item=2, name='second', friendly_name='second', type='string', startIndex=3, endIndex=4, validators=[
                passing_validator()
            ]),
            Field(item=3, name='third', friendly_name='third', type='string', startIndex=4, endIndex=5, validators=[
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
    schema = RowSchema(
        model=dict,
        fields=[
            Field(item=1, name='first', friendly_name='first', type='string', startIndex=0, endIndex=3, validators=[
                passing_validator(),
                failing_validator()
            ]),
            Field(item=2, name='second', friendly_name='second', type='string', startIndex=3, endIndex=4, validators=[
                passing_validator()
            ]),
            Field(item=3, name='third', friendly_name='third', type='string', startIndex=4, endIndex=5, validators=[
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

    instance = TestModel()
    instance.first = '123'
    instance.second = '4'
    instance.third = '5'

    schema = RowSchema(
        model=TestModel,
        fields=[
            Field(item=1, name='first', friendly_name='first', type='string', startIndex=0, endIndex=3, validators=[
                passing_validator(),
                failing_validator()
            ]),
            Field(item=2, name='second', friendly_name='second', type='string', startIndex=3, endIndex=4, validators=[
                passing_validator()
            ]),
            Field(item=3, name='third', friendly_name='third', type='string', startIndex=4, endIndex=5, validators=[
                passing_validator()
            ]),
        ]
    )

    is_valid, errors = schema.run_field_validators(instance, error_func)
    assert is_valid is False
    assert errors == ['Value is not valid.']


@pytest.mark.parametrize('first,second', [
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
    schema = RowSchema(
        model=dict,
        fields=[
            Field(
                item=1,
                name='first',
                friendly_name='first',
                type='string',
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
                type='string',
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
        'first is required but a value was not provided.',
        'second is required but a value was not provided.'
    ]


@pytest.mark.parametrize('first, expected_valid, expected_errors', [
    ('   ', True, []),
    ('####', False, ['Value is not valid.']),
    (None, True, []),
])
def test_field_validators_blank_and_not_required_returns_valid(first, expected_valid, expected_errors):
    """Test not required field returns valid if value not provided (blank)."""
    instance = {
        'first': first,
    }
    schema = RowSchema(
        model=dict,
        fields=[
            Field(
                item=1,
                name='first',
                friendly_name='first',
                type='string',
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
    schema = RowSchema(
        postparsing_validators=[
            passing_postparsing_validator()
        ]
    )

    is_valid, errors = schema.run_postparsing_validators(instance, error_func)
    assert is_valid is True
    assert errors == []


def test_run_postparsing_validators_returns_invalid_and_errors():
    """Test run_postparsing_validators executes all postparsing_validators provided in schema and returns errors."""
    instance = {}
    schema = RowSchema(
        postparsing_validators=[
            passing_postparsing_validator(),
            failing_postparsing_validator()
        ]
    )

    is_valid, errors = schema.run_postparsing_validators(instance, error_func)
    assert is_valid is False
    assert errors == ['Value is not valid.']


@pytest.mark.parametrize("value,length", [
    (None, 0),
    (None, 10),
    ('     ', 5),
    ('###', 3)
])
def test_value_is_empty_returns_true(value, length):
    """Test value_is_empty returns valid."""
    result = value_is_empty(value, length)
    assert result is True


@pytest.mark.parametrize("value,length", [
    (0, 1),
    (1, 1),
    (10, 2),
    ('0', 1),
    ('0000', 4),
    ('1    ', 5),
    ('##3', 3)
])
def test_value_is_empty_returns_false(value, length):
    """Test value_is_empty returns invalid."""
    result = value_is_empty(value, length)
    assert result is False


def test_multi_record_schema_parses_and_validates():
    """Test SchemaManager parse_and_validate."""
    line = '12345'
    schema_manager = SchemaManager(
        schemas=[
            RowSchema(
                model=dict,
                preparsing_validators=[
                    passing_validator()
                ],
                postparsing_validators=[
                    failing_postparsing_validator()
                ],
                fields=[
                    Field(
                        item=1,
                        name='first',
                        friendly_name='first',
                        type='string',
                        startIndex=0,
                        endIndex=3,
                        validators=[passing_validator()]
                        ),
                ]
            ),
            RowSchema(
                model=dict,
                preparsing_validators=[
                    passing_validator()
                ],
                postparsing_validators=[
                    passing_postparsing_validator()
                ],
                fields=[
                    Field(
                        item=2,
                        name='second',
                        friendly_name='first',
                        type='string',
                        startIndex=2,
                        endIndex=4,
                        validators=[passing_validator()]),
                ]
            ),
            RowSchema(
                model=dict,
                preparsing_validators=[
                    failing_validator()
                ],
                postparsing_validators=[
                    passing_postparsing_validator()
                ],
                fields=[
                    Field(
                        item=3,
                        name='third',
                        friendly_name='first',
                        type='string',
                        startIndex=4,
                        endIndex=5,
                        validators=[passing_validator()]
                        ),
                ]
            ),
            RowSchema(
                model=dict,
                preparsing_validators=[
                    passing_validator()
                ],
                postparsing_validators=[
                    passing_postparsing_validator()
                ],
                fields=[
                    Field(
                        item=4,
                        name='fourth',
                        friendly_name='first',
                        type='string',
                        startIndex=4,
                        endIndex=5,
                        validators=[failing_validator()]
                        ),
                ]
            )
        ]
    )

    rs = schema_manager.parse_and_validate(line, error_func)

    r0_record, r0_is_valid, r0_errors = rs[0]
    r1_record, r1_is_valid, r1_errors = rs[1]
    r2_record, r2_is_valid, r2_errors = rs[2]
    r3_record, r3_is_valid, r3_errors = rs[3]

    assert r0_record == {'first': '123'}
    assert r0_is_valid is False
    assert r0_errors == ['Value is not valid.']

    assert r1_record == {'second': '34'}
    assert r1_is_valid is True
    assert r1_errors == []

    assert r2_record is None
    assert r2_is_valid is False
    assert r2_errors == ['Value is not valid.']

    assert r3_record == {'fourth': '5'}
    assert r3_is_valid is False
    assert r3_errors == ['Value is not valid.']

@pytest.fixture
def test_datafile_empty_file(stt_user, stt):
    """Fixture for small_correct_file."""
    return create_test_datafile('empty_file', stt_user, stt)

@pytest.mark.django_db()
def test_run_postparsing_validators_returns_frinedly_fieldnames(test_datafile_empty_file):
    """Test run_postparsing_validators executes all postparsing_validators provided in schema."""

    def postparse_validator():
        """Fake validator that always returns valid."""
        return lambda _: (False, "an Error", ["FIRST", "SECOND"])

    instance = {}
    schema = RowSchema(
        model=dict,
        postparsing_validators=[
            postparse_validator()
        ],
        fields=[
            Field(
                item=1,
                name='FIRST',
                friendly_name='first',
                type='string',
                startIndex=0,
                endIndex=3,
                required=False,
                validators=[]
            ),
            Field(
                item=2,
                name='SECOND',
                friendly_name='second',
                type='string',
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
    assert errors[0].fields_json == {'friendly_name': {'FIRST': 'first', 'SECOND': 'second'}}
    assert errors[0].error_message == "an Error"
