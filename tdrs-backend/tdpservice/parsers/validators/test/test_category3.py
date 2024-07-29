import pytest
import datetime
from ..category3 import ComposableValidators, ComposableFieldValidators
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


class TestComposableFieldValidators:
    @pytest.mark.parametrize('val, option, kwargs, exp_result, exp_message', [
        (10, 10, {}, True, None),
        (1, 10, {}, False, 'Test Item 1 (test field): 1 does not match 10.'),
    ])
    def test_isEqual(self, val, option, kwargs, exp_result, exp_message):
        _validator = ComposableFieldValidators.isEqual(option, **kwargs)
        _validate_and_assert(_validator, val, exp_result, exp_message)

    @pytest.mark.parametrize('val, option, kwargs, exp_result, exp_message', [
        (1, 10, {}, True, None),
        (10, 10, {}, False, 'Test Item 1 (test field): 10 matches 10.'),
    ])
    def test_isNotEqual(self, val, option, kwargs, exp_result, exp_message):
        _validator = ComposableFieldValidators.isNotEqual(option, **kwargs)
        _validate_and_assert(_validator, val, exp_result, exp_message)

    @pytest.mark.parametrize('val, options, kwargs, exp_result, exp_message', [
        (1, [1, 2, 3], {}, True, None),
        (1, [4, 5, 6], {}, False, 'Test Item 1 (test field): 1 is not in [4, 5, 6].'),
    ])
    def test_isOneOf(self, val, options, kwargs, exp_result, exp_message):
        _validator = ComposableFieldValidators.isOneOf(options, **kwargs)
        _validate_and_assert(_validator, val, exp_result, exp_message)

    @pytest.mark.parametrize('val, options, kwargs, exp_result, exp_message', [
        (1, [4, 5, 6], {}, True, None),
        (1, [1, 2, 3], {}, False, 'Test Item 1 (test field): 1 is in [1, 2, 3].'),
    ])
    def test_isNotOneOf(self, val, options, kwargs, exp_result, exp_message):
        _validator = ComposableFieldValidators.isNotOneOf(options, **kwargs)
        _validate_and_assert(_validator, val, exp_result, exp_message)

    @pytest.mark.parametrize('val, option, inclusive, kwargs, exp_result, exp_message', [
        (10, 5, True, {}, True, None),
        (10, 20, True, {}, False, 'Test Item 1 (test field): 10 is not larger than 20.'),
        (10, 10, False, {}, False, 'Test Item 1 (test field): 10 is not larger than 10.'),
    ])
    def test_isGreaterThan(self, val, option, inclusive, kwargs, exp_result, exp_message):
        _validator = ComposableFieldValidators.isGreaterThan(option, inclusive, **kwargs)
        _validate_and_assert(_validator, val, exp_result, exp_message)

    @pytest.mark.parametrize('val, option, inclusive, kwargs, exp_result, exp_message', [
        (5, 10, True, {}, True, None),
        (5, 3, True, {}, False, 'Test Item 1 (test field): 5 is not smaller than 3.'),
        (5, 5, False, {}, False, 'Test Item 1 (test field): 5 is not smaller than 5.'),
    ])
    def test_isLessThan(self, val, option, inclusive, kwargs, exp_result, exp_message):
        _validator = ComposableFieldValidators.isLessThan(option, inclusive, **kwargs)
        _validate_and_assert(_validator, val, exp_result, exp_message)

    @pytest.mark.parametrize('val, min, max, inclusive, kwargs, exp_result, exp_message', [
        (5, 1, 10, True, {}, True, None),
        (20, 1, 10, True, {}, False, 'Test Item 1 (test field): 20 is not in range [1, 10].'),
        (5, 1, 10, False, {}, True, None),
        (20, 1, 10, False, {}, False, 'Test Item 1 (test field): 20 is not between 1 and 10.'),
    ])
    def test_isBetween(self, val, min, max, inclusive, kwargs, exp_result, exp_message):
        _validator = ComposableFieldValidators.isBetween(min, max, inclusive, **kwargs)
        _validate_and_assert(_validator, val, exp_result, exp_message)

    @pytest.mark.parametrize('val, substr, kwargs, exp_result, exp_message', [
        ('abcdef', 'abc', {}, True, None),
        ('abcdef', 'xyz', {}, False, 'Test Item 1 (test field): abcdef does not start with xyz.')
    ])
    def test_startsWith(self, val, substr, kwargs, exp_result, exp_message):
        _validator = ComposableFieldValidators.startsWith(substr, **kwargs)
        _validate_and_assert(_validator, val, exp_result, exp_message)

    @pytest.mark.parametrize('val, substr, kwargs, exp_result, exp_message', [
        ('abc123', 'c1', {}, True, None),
        ('abc123', 'xy', {}, False, 'Test Item 1 (test field): abc123 does not contain xy.'),
    ])
    def test_contains(self, val, substr, kwargs, exp_result, exp_message):
        _validator = ComposableFieldValidators.contains(substr, **kwargs)
        _validate_and_assert(_validator, val, exp_result, exp_message)

    @pytest.mark.parametrize('val, kwargs, exp_result, exp_message', [
        (1001, {}, True, None),
        ('ABC', {}, False, 'Test Item 1 (test field): ABC is not a number.'),
    ])
    def test_isNumber(self, val, kwargs, exp_result, exp_message):
        _validator = ComposableFieldValidators.isNumber(**kwargs)
        _validate_and_assert(_validator, val, exp_result, exp_message)

    @pytest.mark.parametrize('val, kwargs, exp_result, exp_message', [
        ('F*&k', {}, False, 'Test Item 1 (test field): F*&k is not alphanumeric.'),
        ('Fork', {}, True, None),
    ])
    def test_isAlphaNumeric(self, val, kwargs, exp_result, exp_message):
        _validator = ComposableFieldValidators.isAlphaNumeric(**kwargs)
        _validate_and_assert(_validator, val, exp_result, exp_message)

    @pytest.mark.parametrize('val, start, end, kwargs, exp_result, exp_message', [
        ('   ', 0, 4, {}, True, None),
        ('1001', 0, 4, {}, False, 'Test Item 1 (test field): 1001 is not blank between positions 0 and 4.'),
    ])
    def test_isEmpty(self, val, start, end, kwargs, exp_result, exp_message):
        _validator = ComposableFieldValidators.isEmpty(start, end, **kwargs)
        _validate_and_assert(_validator, val, exp_result, exp_message)

    @pytest.mark.parametrize('val, start, end, kwargs, exp_result, exp_message', [
        ('1001', 0, 4, {}, True, None),
        ('    ', 0, 4, {}, False, 'Test Item 1 (test field):      contains blanks between positions 0 and 4.'),
    ])
    def test_isNotEmpty(self, val, start, end, kwargs, exp_result, exp_message):
        _validator = ComposableFieldValidators.isNotEmpty(start, end, **kwargs)
        _validate_and_assert(_validator, val, exp_result, exp_message)

    @pytest.mark.parametrize('val, kwargs, exp_result, exp_message', [
        ('    ', {}, True, None),
        ('0000', {}, False, 'Test Item 1 (test field): 0000 is not blank.'),
    ])
    def test_isBlank(self, val, kwargs, exp_result, exp_message):
        _validator = ComposableFieldValidators.isBlank(**kwargs)
        _validate_and_assert(_validator, val, exp_result, exp_message)

    @pytest.mark.parametrize('val, length, kwargs, exp_result, exp_message', [
        ('123', 3, {}, True, None),
        ('123', 4, {}, False, 'Test Item 1 (test field): field length is 3 characters but must be 4.'),
    ])
    def test_hasLength(self, val, length, kwargs, exp_result, exp_message):
        _validator = ComposableFieldValidators.hasLength(length, **kwargs)
        _validate_and_assert(_validator, val, exp_result, exp_message)

    @pytest.mark.parametrize('val, length, inclusive, kwargs, exp_result, exp_message', [
        ('123', 3, True, {}, True, None),
        ('123', 3, False, {}, False, 'Test Item 1 (test field): Value length 3 is not greater than 3.'),
    ])
    def test_hasLengthGreaterThan(self, val, length, inclusive, kwargs, exp_result, exp_message):
        _validator = ComposableFieldValidators.hasLengthGreaterThan(length, inclusive, **kwargs)
        _validate_and_assert(_validator, val, exp_result, exp_message)

    @pytest.mark.parametrize('val, length, kwargs, exp_result, exp_message', [
        (101, 3, {}, True, None),
        (101, 2, {}, False, 'Test Item 1 (test field): 101 does not have exactly 2 digits.'),
    ])
    def test_intHasLength(self, val, length, kwargs, exp_result, exp_message):
        _validator = ComposableFieldValidators.intHasLength(length, **kwargs)
        _validate_and_assert(_validator, val, exp_result, exp_message)

    @pytest.mark.parametrize('val, number_of_zeros, kwargs, exp_result, exp_message', [
        ('111', 3, {}, True, None),
        ('000', 3, {}, False, 'Test Item 1 (test field): 000 is zero.'),
    ])
    def test_isNotZero(self, val, number_of_zeros, kwargs, exp_result, exp_message):
        _validator = ComposableFieldValidators.isNotZero(number_of_zeros, **kwargs)
        _validate_and_assert(_validator, val, exp_result, exp_message)

    @pytest.mark.parametrize('val, min_age, kwargs, exp_result, exp_message', [
        ('199510', 18, {}, True, None),
        (
            f'{datetime.date.today().year - 18}01', 18, {}, False, 
            'Item 1 (test field) 2006 must be less than or equal to 2006 to meet the minimum age requirement.'
        ),
        (
            '202010', 18, {}, False,
            'Item 1 (test field) 2020 must be less than or equal to 2006 to meet the minimum age requirement.'
        ),
    ])
    def test_isOlderThan(self, val, min_age, kwargs, exp_result, exp_message):
        _validator = ComposableFieldValidators.isOlderThan(min_age, **kwargs)
        _validate_and_assert(_validator, val, exp_result, exp_message)

    @pytest.mark.parametrize('val, kwargs, exp_result, exp_message', [
        ('123456789', {}, True, None),
        ('987654321', {}, True, None),
        (
            '111111111', {}, False,
            "Item 1 (test field) 111111111 is in ['000000000', '111111111', '222222222', '333333333', "
            "'444444444', '555555555', '666666666', '777777777', '888888888', '999999999']."
         ),
        (
            '999999999', {}, False,
            "Item 1 (test field) 999999999 is in ['000000000', '111111111', '222222222', '333333333', "
            "'444444444', '555555555', '666666666', '777777777', '888888888', '999999999']."
        ),
        (
            '888888888', {}, False,
            "Item 1 (test field) 888888888 is in ['000000000', '111111111', '222222222', '333333333', "
            "'444444444', '555555555', '666666666', '777777777', '888888888', '999999999']."
        ),
    ])
    def test_validateSSN(self, val, kwargs, exp_result, exp_message):
        _validator = ComposableFieldValidators.validateSSN(**kwargs)
        _validate_and_assert(_validator, val, exp_result, exp_message)


class TestComposableValidators:
    def test_validate__FAM_AFF__SSN(self):
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
        result = ComposableValidators.validate__FAM_AFF__SSN()(instance, schema)
        assert result == (
            False,
            'T1: If FAMILY_AFFILIATION ==2 and CITIZENSHIP_STATUS==1 or 2, ' +
            'then SSN != 000000000 -- 999999999.',
            ['FAMILY_AFFILIATION', 'CITIZENSHIP_STATUS', 'SSN']
        )
        instance['SSN'] = '1'*8 + '0'
        result = ComposableValidators.validate__FAM_AFF__SSN()(instance, schema)
        assert result == (True, None, ['FAMILY_AFFILIATION', 'CITIZENSHIP_STATUS', 'SSN'])

    def test_validate__WORK_ELIGIBLE_INDICATOR__HOH__AGE(self):
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
        result = ComposableValidators.validate__WORK_ELIGIBLE_INDICATOR__HOH__AGE()(instance, schema)
        assert result == (
            False,
            'T1: If WORK_ELIGIBLE_INDICATOR == 11 and AGE < 19, then RELATIONSHIP_HOH != 1',
            ['WORK_ELIGIBLE_INDICATOR', 'RELATIONSHIP_HOH', 'DATE_OF_BIRTH']
        )
        instance['DATE_OF_BIRTH'] = '19950101'
        result = ComposableValidators.validate__WORK_ELIGIBLE_INDICATOR__HOH__AGE()(instance, schema)
        assert result == (True, None, ['WORK_ELIGIBLE_INDICATOR', 'RELATIONSHIP_HOH', 'DATE_OF_BIRTH'])
