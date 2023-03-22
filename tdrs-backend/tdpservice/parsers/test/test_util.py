"""Test the methods of RowSchema to ensure parsing and validation work in all individual cases."""


from ..util import RowSchema, Field


def passing_validator():
    """Fake validator that always returns valid."""
    return lambda _: (True, None)


def failing_validator():
    """Fake validator that always returns invalid."""
    return lambda _: (False, 'Value is not valid.')


def test_run_preparsing_validators_returns_valid():
    """Test run_preparsing_validators executes all preparsing_validators provided in schema."""
    line = '12345'
    schema = RowSchema(
        preparsing_validators=[
            passing_validator()
        ]
    )

    is_valid, errors = schema.run_preparsing_validators(line)
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

    is_valid, errors = schema.run_preparsing_validators(line)
    assert is_valid is False
    assert errors == ['Value is not valid.']


def test_parse_line_parses_line_from_schema_to_dict():
    """Test that parse_line parses a string into a dict given start and end indices for all fields."""
    line = '12345'
    schema = RowSchema(
        model=dict,
        fields=[
            Field(name='first', type='string', startIndex=0, endIndex=3),
            Field(name='second', type='string', startIndex=3, endIndex=4),
            Field(name='third', type='string', startIndex=4, endIndex=5),
        ]
    )

    record = schema.parse_line(line)

    assert record['first'] == '123'
    assert record['second'] == '4'
    assert record['third'] == '5'


def test_parse_line_parses_line_from_schema_to_object():
    """Test that parse_line parses a string into an object given start and end indices for all fields."""
    class TestModel:
        first = None
        second = None
        third = None

    line = '12345'
    schema = RowSchema(
        model=TestModel,
        fields=[
            Field(name='first', type='string', startIndex=0, endIndex=3),
            Field(name='second', type='string', startIndex=3, endIndex=4),
            Field(name='third', type='string', startIndex=4, endIndex=5),
        ]
    )

    record = schema.parse_line(line)

    assert record.first == '123'
    assert record.second == '4'
    assert record.third == '5'


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
            Field(name='first', type='string', startIndex=0, endIndex=3, validators=[
                passing_validator()
            ]),
            Field(name='second', type='string', startIndex=3, endIndex=4, validators=[
                passing_validator()
            ]),
            Field(name='third', type='string', startIndex=4, endIndex=5, validators=[
                passing_validator()
            ]),
        ]
    )

    is_valid, errors = schema.run_field_validators(instance)
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
            Field(name='first', type='string', startIndex=0, endIndex=3, validators=[
                passing_validator()
            ]),
            Field(name='second', type='string', startIndex=3, endIndex=4, validators=[
                passing_validator()
            ]),
            Field(name='third', type='string', startIndex=4, endIndex=5, validators=[
                passing_validator()
            ]),
        ]
    )

    is_valid, errors = schema.run_field_validators(instance)
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
            Field(name='first', type='string', startIndex=0, endIndex=3, validators=[
                passing_validator(),
                failing_validator()
            ]),
            Field(name='second', type='string', startIndex=3, endIndex=4, validators=[
                passing_validator()
            ]),
            Field(name='third', type='string', startIndex=4, endIndex=5, validators=[
                passing_validator()
            ]),
        ]
    )

    is_valid, errors = schema.run_field_validators(instance)
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
            Field(name='first', type='string', startIndex=0, endIndex=3, validators=[
                passing_validator(),
                failing_validator()
            ]),
            Field(name='second', type='string', startIndex=3, endIndex=4, validators=[
                passing_validator()
            ]),
            Field(name='third', type='string', startIndex=4, endIndex=5, validators=[
                passing_validator()
            ]),
        ]
    )

    is_valid, errors = schema.run_field_validators(instance)
    assert is_valid is False
    assert errors == ['Value is not valid.']


def test_field_validators_blank_and_required_returns_error():
    """Test required field returns error if value not provided (blank)."""
    instance = {
        'first': ' ',
    }
    schema = RowSchema(
        model=dict,
        fields=[
            Field(name='first', type='string', startIndex=0, endIndex=3, required=True, validators=[
                passing_validator(),
            ]),
        ]
    )

    is_valid, errors = schema.run_field_validators(instance)
    assert is_valid is False
    assert errors == ['first is required but a value was not provided.']


def test_field_validators_blank_and_not_required_returns_valid():
    """Test not required field returns valid if value not provided (blank)."""
    instance = {
        'first': ' ',
    }
    schema = RowSchema(
        model=dict,
        fields=[
            Field(name='first', type='string', startIndex=0, endIndex=3, required=False, validators=[
                passing_validator(),
                failing_validator()
            ]),
        ]
    )

    is_valid, errors = schema.run_field_validators(instance)
    assert is_valid is True
    assert errors == []


def test_run_postparsing_validators_returns_valid():
    """Test run_postparsing_validators executes all postparsing_validators provided in schema."""
    instance = {}
    schema = RowSchema(
        postparsing_validators=[
            passing_validator()
        ]
    )

    is_valid, errors = schema.run_postparsing_validators(instance)
    assert is_valid is True
    assert errors == []


def test_run_postparsing_validators_returns_invalid_and_errors():
    """Test run_postparsing_validators executes all postparsing_validators provided in schema and returns errors."""
    instance = {}
    schema = RowSchema(
        postparsing_validators=[
            passing_validator(),
            failing_validator()
        ]
    )

    is_valid, errors = schema.run_postparsing_validators(instance)
    assert is_valid is False
    assert errors == ['Value is not valid.']
