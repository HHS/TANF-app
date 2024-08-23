"""Test category3 validators."""


import pytest
import datetime
from .. import category3
from ..util import ValidationErrorArgs
from ...row_schema import RowSchema
from ...fields import Field

# export all error messages to file

test_schema = RowSchema(
    record_type="Test",
    document=None,
    preparsing_validators=[],
    postparsing_validators=[],
    fields=[],
)


def _make_eargs(val):
    return ValidationErrorArgs(
        value=val,
        row_schema=test_schema,
        friendly_name='test field',
        item_num='1'
    )


def _validate_and_assert(validator, val, exp_result, exp_message):
    result, msg = validator(val, _make_eargs(val))
    print(f'result: {result}; msg: {msg}')
    assert result == exp_result
    assert msg == exp_message


@pytest.mark.parametrize('val, option, kwargs, exp_result, exp_message', [
    (10, 10, {}, True, None),
    (1, 10, {}, False, 'must match 10'),
])
def test_isEqual(val, option, kwargs, exp_result, exp_message):
    """Test isEqual validator error messages."""
    _validator = category3.isEqual(option, **kwargs)
    _validate_and_assert(_validator, val, exp_result, exp_message)


@pytest.mark.parametrize('val, option, kwargs, exp_result, exp_message', [
    (1, 10, {}, True, None),
    (10, 10, {}, False, 'must not be equal to 10'),
])
def test_isNotEqual(val, option, kwargs, exp_result, exp_message):
    """Test isNotEqual validator error messages."""
    _validator = category3.isNotEqual(option, **kwargs)
    _validate_and_assert(_validator, val, exp_result, exp_message)


@pytest.mark.parametrize('val, options, kwargs, exp_result, exp_message', [
    (1, [1, 2, 3], {}, True, None),
    (1, [4, 5, 6], {}, False, 'must be one of [4, 5, 6]'),
])
def test_isOneOf(val, options, kwargs, exp_result, exp_message):
    """Test isOneOf validator error messages."""
    _validator = category3.isOneOf(options, **kwargs)
    _validate_and_assert(_validator, val, exp_result, exp_message)


@pytest.mark.parametrize('val, options, kwargs, exp_result, exp_message', [
    (1, [4, 5, 6], {}, True, None),
    (1, [1, 2, 3], {}, False, 'must not be one of [1, 2, 3]'),
])
def test_isNotOneOf(val, options, kwargs, exp_result, exp_message):
    """Test isNotOneOf validator error messages."""
    _validator = category3.isNotOneOf(options, **kwargs)
    _validate_and_assert(_validator, val, exp_result, exp_message)


@pytest.mark.parametrize('val, option, inclusive, kwargs, exp_result, exp_message', [
    (10, 5, True, {}, True, None),
    (10, 20, True, {}, False, 'must be greater than 20'),
    (10, 10, False, {}, False, 'must be greater than 10'),
])
def test_isGreaterThan(val, option, inclusive, kwargs, exp_result, exp_message):
    """Test isGreaterThan validator error messages."""
    _validator = category3.isGreaterThan(option, inclusive, **kwargs)
    _validate_and_assert(_validator, val, exp_result, exp_message)


@pytest.mark.parametrize('val, option, inclusive, kwargs, exp_result, exp_message', [
    (5, 10, True, {}, True, None),
    (5, 3, True, {}, False, 'must be less than 3'),
    (5, 5, False, {}, False, 'must be less than 5'),
])
def test_isLessThan(val, option, inclusive, kwargs, exp_result, exp_message):
    """Test isLessThan validator error messages."""
    _validator = category3.isLessThan(option, inclusive, **kwargs)
    _validate_and_assert(_validator, val, exp_result, exp_message)


@pytest.mark.parametrize('val, min, max, inclusive, kwargs, exp_result, exp_message', [
    (5, 1, 10, True, {}, True, None),
    (20, 1, 10, True, {}, False, 'must be between 1 and 10'),
    (5, 1, 10, False, {}, True, None),
    (20, 1, 10, False, {}, False, 'must be between 1 and 10'),
])
def test_isBetween(val, min, max, inclusive, kwargs, exp_result, exp_message):
    """Test isBetween validator error messages."""
    _validator = category3.isBetween(min, max, inclusive, **kwargs)
    _validate_and_assert(_validator, val, exp_result, exp_message)


@pytest.mark.parametrize('val, substr, kwargs, exp_result, exp_message', [
    ('abcdef', 'abc', {}, True, None),
    ('abcdef', 'xyz', {}, False, 'must start with xyz')
])
def test_startsWith(val, substr, kwargs, exp_result, exp_message):
    """Test startsWith validator error messages."""
    _validator = category3.startsWith(substr, **kwargs)
    _validate_and_assert(_validator, val, exp_result, exp_message)


@pytest.mark.parametrize('val, substr, kwargs, exp_result, exp_message', [
    ('abc123', 'c1', {}, True, None),
    ('abc123', 'xy', {}, False, 'must contain xy'),
])
def test_contains(val, substr, kwargs, exp_result, exp_message):
    """Test contains validator error messages."""
    _validator = category3.contains(substr, **kwargs)
    _validate_and_assert(_validator, val, exp_result, exp_message)


@pytest.mark.parametrize('val, kwargs, exp_result, exp_message', [
    (1001, {}, True, None),
    ('ABC', {}, False, 'must be a number'),
])
def test_isNumber(val, kwargs, exp_result, exp_message):
    """Test isNumber validator error messages."""
    _validator = category3.isNumber(**kwargs)
    _validate_and_assert(_validator, val, exp_result, exp_message)


@pytest.mark.parametrize('val, kwargs, exp_result, exp_message', [
    ('F*&k', {}, False, 'must be alphanumeric'),
    ('Fork', {}, True, None),
])
def test_isAlphaNumeric(val, kwargs, exp_result, exp_message):
    """Test isAlphaNumeric validator error messages."""
    _validator = category3.isAlphaNumeric(**kwargs)
    _validate_and_assert(_validator, val, exp_result, exp_message)


@pytest.mark.parametrize('val, start, end, kwargs, exp_result, exp_message', [
    ('   ', 0, 4, {}, True, None),
    ('1001', 0, 4, {}, False, 'must be empty'),
])
def test_isEmpty(val, start, end, kwargs, exp_result, exp_message):
    """Test isEmpty validator error messages."""
    _validator = category3.isEmpty(start, end, **kwargs)
    _validate_and_assert(_validator, val, exp_result, exp_message)


@pytest.mark.parametrize('val, start, end, kwargs, exp_result, exp_message', [
    ('1001', 0, 4, {}, True, None),
    ('    ', 0, 4, {}, False, 'must not be empty'),
])
def test_isNotEmpty(val, start, end, kwargs, exp_result, exp_message):
    """Test isNotEmpty validator error messages."""
    _validator = category3.isNotEmpty(start, end, **kwargs)
    _validate_and_assert(_validator, val, exp_result, exp_message)


@pytest.mark.parametrize('val, kwargs, exp_result, exp_message', [
    ('    ', {}, True, None),
    ('0000', {}, False, 'must be blank'),
])
def test_isBlank(val, kwargs, exp_result, exp_message):
    """Test isBlank validator error messages."""
    _validator = category3.isBlank(**kwargs)
    _validate_and_assert(_validator, val, exp_result, exp_message)


@pytest.mark.parametrize('val, length, kwargs, exp_result, exp_message', [
    ('123', 3, {}, True, None),
    ('123', 4, {}, False, 'must have length 4'),
])
def test_hasLength(val, length, kwargs, exp_result, exp_message):
    """Test hasLength validator error messages."""
    _validator = category3.hasLength(length, **kwargs)
    _validate_and_assert(_validator, val, exp_result, exp_message)


@pytest.mark.parametrize('val, length, inclusive, kwargs, exp_result, exp_message', [
    ('123', 3, True, {}, True, None),
    ('123', 3, False, {}, False, 'must have length greater than 3'),
])
def test_hasLengthGreaterThan(val, length, inclusive, kwargs, exp_result, exp_message):
    """Test hasLengthGreaterThan validator error messages."""
    _validator = category3.hasLengthGreaterThan(length, inclusive, **kwargs)
    _validate_and_assert(_validator, val, exp_result, exp_message)


@pytest.mark.parametrize('val, length, kwargs, exp_result, exp_message', [
    (101, 3, {}, True, None),
    (101, 2, {}, False, 'must have length 2'),
])
def test_intHasLength(val, length, kwargs, exp_result, exp_message):
    """Test intHasLength validator error messages."""
    _validator = category3.intHasLength(length, **kwargs)
    _validate_and_assert(_validator, val, exp_result, exp_message)


@pytest.mark.parametrize('val, number_of_zeros, kwargs, exp_result, exp_message', [
    ('111', 3, {}, True, None),
    ('000', 3, {}, False, 'must not be zero'),
])
def test_isNotZero(val, number_of_zeros, kwargs, exp_result, exp_message):
    """Test isNotZero validator error messages."""
    _validator = category3.isNotZero(number_of_zeros, **kwargs)
    _validate_and_assert(_validator, val, exp_result, exp_message)


@pytest.mark.parametrize('val, min_age, kwargs, exp_result, exp_message', [
    ('199510', 18, {}, True, None),
    (
        f'{datetime.date.today().year - 18}01', 18, {}, False,
        '2006 must be less than or equal to 2006 to meet the minimum age requirement.'
    ),
    (
        '202010', 18, {}, False,
        '2020 must be less than or equal to 2006 to meet the minimum age requirement.'
    ),
])
def test_isOlderThan(val, min_age, kwargs, exp_result, exp_message):
    """Test isOlderThan validator error messages."""
    _validator = category3.isOlderThan(min_age, **kwargs)
    _validate_and_assert(_validator, val, exp_result, exp_message)


@pytest.mark.parametrize('val, kwargs, exp_result, exp_message', [
    ('123456789', {}, True, None),
    ('987654321', {}, True, None),
    (
        '111111111', {}, False,
        "is in ['000000000', '111111111', '222222222', '333333333', "
        "'444444444', '555555555', '666666666', '777777777', '888888888', '999999999']."
        ),
    (
        '999999999', {}, False,
        "is in ['000000000', '111111111', '222222222', '333333333', "
        "'444444444', '555555555', '666666666', '777777777', '888888888', '999999999']."
    ),
    (
        '888888888', {}, False,
        "is in ['000000000', '111111111', '222222222', '333333333', "
        "'444444444', '555555555', '666666666', '777777777', '888888888', '999999999']."
    ),
])
def test_validateSSN(val, kwargs, exp_result, exp_message):
    """Test validateSSN validator error messages."""
    _validator = category3.validateSSN(**kwargs)
    _validate_and_assert(_validator, val, exp_result, exp_message)


@pytest.mark.parametrize('condition_val, result_val, exp_result, exp_message, exp_fields', [
    (1, 1, True, None, ['TestField3', 'TestField1']),  # condition fails, valid
    (10, 1, True, None, ['TestField1', 'TestField3']),  # condition pass, result pass
    # condition pass, result fail
    (
        10, 20, False,
        'Since Item 1 (test1) is 10, then Item 3 (test3) 20 must be less than 10',
        ['TestField1', 'TestField3']
    ),
])
def test_ifThenAlso(condition_val, result_val, exp_result, exp_message, exp_fields):
    """Test ifThenAlso validator error messages."""
    schema = RowSchema(
        fields=[
            Field(
                item='1',
                name='TestField1',
                friendly_name='test1',
                type='number',
                startIndex=0,
                endIndex=1
            ),
            Field(
                item='2',
                name='TestField2',
                friendly_name='test2',
                type='number',
                startIndex=1,
                endIndex=2
            ),
            Field(
                item='3',
                name='TestField3',
                friendly_name='test3',
                type='number',
                startIndex=2,
                endIndex=3
            )
        ]
    )
    instance = {
        'TestField1': condition_val,
        'TestField2': 1,
        'TestField3': result_val,
    }
    _validator = category3.ifThenAlso(
        condition_field_name='TestField1',
        condition_function=category3.isEqual(10),
        result_field_name='TestField3',
        result_function=category3.isLessThan(10)
    )
    is_valid, error_msg, fields = _validator(instance, schema)
    assert is_valid == exp_result
    assert error_msg == exp_message
    assert fields == exp_fields


@pytest.mark.parametrize('condition_val, result_val, exp_result, exp_message, exp_fields', [
    (1, 1, True, None, ['TestField3', 'TestField1']),  # condition fails, valid
    (10, 1, True, None, ['TestField1', 'TestField3']),  # condition pass, result pass
    (10, 110, True, None, ['TestField1', 'TestField3']),
    # condition pass, result fail
    (
        10, 20, False,
        'Since Item 1 (test1) is 10, then Item 3 (test3) 20 must be less than 10 or must be greater than 100.',
        ['TestField1', 'TestField3']
    ),
])
def test_ifThenAlso_or(condition_val, result_val, exp_result, exp_message, exp_fields):
    """Test ifThenAlso validator error messages."""
    schema = RowSchema(
        fields=[
            Field(
                item='1',
                name='TestField1',
                friendly_name='test1',
                type='number',
                startIndex=0,
                endIndex=1
            ),
            Field(
                item='2',
                name='TestField2',
                friendly_name='test2',
                type='number',
                startIndex=1,
                endIndex=2
            ),
            Field(
                item='3',
                name='TestField3',
                friendly_name='test3',
                type='number',
                startIndex=2,
                endIndex=3
            )
        ]
    )
    instance = {
        'TestField1': condition_val,
        'TestField2': 1,
        'TestField3': result_val,
    }
    _validator = category3.ifThenAlso(
        condition_field_name='TestField1',
        condition_function=category3.isEqual(10),
        result_field_name='TestField3',
        result_function=category3.orValidators([
            category3.isLessThan(10),
            category3.isGreaterThan(100)
        ], if_result=True)
    )
    is_valid, error_msg, fields = _validator(instance, schema)
    assert is_valid == exp_result
    assert error_msg == exp_message
    assert fields == exp_fields


@pytest.mark.parametrize('val, exp_result, exp_message', [
    (10, True, None),
    (3, True, None),
    (100, False, 'Item 1 (TestField1) 100 must match 10 or must be less than 5.'),
])
def test_orValidators(val, exp_result, exp_message):
    """Test orValidators error messages."""
    _validator = category3.orValidators([
        category3.isEqual(10),
        category3.isLessThan(5)
    ])

    eargs = ValidationErrorArgs(
        value=val,
        row_schema=RowSchema(),
        friendly_name='TestField1',
        item_num='1'
    )

    is_valid, error_msg = _validator(val, eargs)
    assert is_valid == exp_result
    assert error_msg == exp_message


def test_sumIsEqual():
    """Test sumIsEqual postparsing validator."""
    schema = RowSchema(
        fields=[
            Field(
                item='1',
                name='TestField1',
                friendly_name='test1',
                type='number',
                startIndex=0,
                endIndex=1
            ),
            Field(
                item='2',
                name='TestField2',
                friendly_name='test2',
                type='number',
                startIndex=1,
                endIndex=2
            ),
            Field(
                item='3',
                name='TestField3',
                friendly_name='test3',
                type='number',
                startIndex=2,
                endIndex=3
            )
        ]
    )
    instance = {
        'TestField1': 2,
        'TestField2': 1,
        'TestField3': 9,
    }
    result = category3.sumIsEqual('TestField2', ['TestField1', 'TestField3'])(instance, schema)
    assert result == (
        False,
        "T1: The sum of ['TestField1', 'TestField3'] does not equal TestField2 test2 Item 2.",
        ['TestField2', 'TestField1', 'TestField3']
    )
    instance['TestField2'] = 11
    result = category3.sumIsEqual('TestField2', ['TestField1', 'TestField3'])(instance, schema)
    assert result == (True, None, ['TestField2', 'TestField1', 'TestField3'])


def test_sumIsLarger():
    """Test sumIsLarger postparsing validator."""
    schema = RowSchema(
        fields=[
            Field(
                item='1',
                name='TestField1',
                friendly_name='test1',
                type='number',
                startIndex=0,
                endIndex=1
            ),
            Field(
                item='2',
                name='TestField2',
                friendly_name='test2',
                type='number',
                startIndex=1,
                endIndex=2
            ),
            Field(
                item='3',
                name='TestField3',
                friendly_name='test3',
                type='number',
                startIndex=2,
                endIndex=3
            )
        ]
    )
    instance = {
        'TestField1': 2,
        'TestField2': 1,
        'TestField3': 5,
    }
    result = category3.sumIsLarger(['TestField1', 'TestField3'], 10)(instance, schema)
    assert result == (
        False,
        "T1: The sum of ['TestField1', 'TestField3'] is not larger than 10.",
        ['TestField1', 'TestField3']
    )
    instance['TestField3'] = 9
    result = category3.sumIsLarger(['TestField1', 'TestField3'], 10)(instance, schema)
    assert result == (True, None, ['TestField1', 'TestField3'])


def test_validate__FAM_AFF__SSN():
    """Test `validate__FAM_AFF__SSN` gives a valid result."""
    schema = RowSchema(
        fields=[
            Field(
                item='1',
                name='FAMILY_AFFILIATION',
                friendly_name='family affiliation',
                type='number',
                startIndex=0,
                endIndex=1
            ),
            Field(
                item='2',
                name='CITIZENSHIP_STATUS',
                friendly_name='citizenship status',
                type='number',
                startIndex=1,
                endIndex=2
            ),
            Field(
                item='3',
                name='SSN',
                friendly_name='social security number',
                type='number',
                startIndex=2,
                endIndex=11
            )
        ]
    )
    instance = {
        'FAMILY_AFFILIATION': 2,
        'CITIZENSHIP_STATUS': 1,
        'SSN': '0'*9,
    }
    result = category3.validate__FAM_AFF__SSN()(instance, schema)
    assert result == (
        False,
        'T1: Since Item 1 (family affiliation) is 2 and Item 2 (citizenship status) is 1 or 2, '
        'then Item 3 (social security number) must not be in 000000000 -- 999999999.',
        ['FAMILY_AFFILIATION', 'CITIZENSHIP_STATUS', 'SSN']
    )
    instance['SSN'] = '1'*8 + '0'
    result = category3.validate__FAM_AFF__SSN()(instance, schema)
    assert result == (True, None, ['FAMILY_AFFILIATION', 'CITIZENSHIP_STATUS', 'SSN'])


def test_validate__WORK_ELIGIBLE_INDICATOR__HOH__AGE():
    """Test `validate__WORK_ELIGIBLE_INDICATOR__HOH__AGE` gives a valid result."""
    schema = RowSchema(
        fields=[
            Field(
                item='1',
                name='WORK_ELIGIBLE_INDICATOR',
                friendly_name='work eligible indicator',
                type='string',
                startIndex=0,
                endIndex=1
            ),
            Field(
                item='2',
                name='RELATIONSHIP_HOH',
                friendly_name='relationship w/ head of household',
                type='string',
                startIndex=1,
                endIndex=2
            ),
            Field(
                item='3',
                name='DATE_OF_BIRTH',
                friendly_name='date of birth',
                type='string',
                startIndex=2,
                endIndex=10
            ),
            Field(
                item='4',
                name='RPT_MONTH_YEAR',
                friendly_name='report month/year',
                type='string',
                startIndex=10,
                endIndex=16
            )
        ]
    )
    instance = {
        'WORK_ELIGIBLE_INDICATOR': '11',
        'RELATIONSHIP_HOH': '1',
        'DATE_OF_BIRTH': '20200101',
        'RPT_MONTH_YEAR': '202010',
    }
    result = category3.validate__WORK_ELIGIBLE_INDICATOR__HOH__AGE()(instance, schema)
    assert result == (
        False,
        'T1: Since Item 1 (work eligible indicator) is 11 and Item 3 (Age) is less than 19, '
        'then Item 2 (relationship w/ head of household) must not be 1.',
        ['WORK_ELIGIBLE_INDICATOR', 'RELATIONSHIP_HOH', 'DATE_OF_BIRTH']
    )
    instance['DATE_OF_BIRTH'] = '19950101'
    result = category3.validate__WORK_ELIGIBLE_INDICATOR__HOH__AGE()(instance, schema)
    assert result == (True, None, ['WORK_ELIGIBLE_INDICATOR', 'RELATIONSHIP_HOH', 'DATE_OF_BIRTH'])
