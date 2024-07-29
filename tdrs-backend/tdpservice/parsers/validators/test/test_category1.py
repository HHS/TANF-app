import pytest
from ..category1 import PreparsingValidators
from ..util import ValidationErrorArgs
from ...row_schema import RowSchema

test_schema = RowSchema(
    record_type="Test",
    document=None,
    preparsing_validators=[],
    postparsing_validators=[],
    fields=[],
)


def _make_eargs(line):
    return ValidationErrorArgs(
        value=line,
        row_schema=test_schema,
        friendly_name='test field',
        item_num='1'
    )


def _validate_and_assert(validator, line, exp_result, exp_message):
    result, msg = validator(line, _make_eargs(line))
    assert result == exp_result
    assert msg == exp_message


class TestPreparsingValidators:
    @pytest.mark.parametrize('line, kwargs, exp_result, exp_message', [
        ('asdfasdf', {}, True, None),
        ('00000000', {}, True, None),
        ('########', {}, False, 'Test Item 1 (test field): ######## contains blanks between positions 0 and 8.'),
        ('        ', {}, False, 'Test Item 1 (test field):          contains blanks between positions 0 and 8.'),
    ])
    def test_recordIsNotEmpty(self, line, kwargs, exp_result, exp_message):
        _validator = PreparsingValidators.recordIsNotEmpty(**kwargs)
        _validate_and_assert(_validator, line, exp_result, exp_message)

    @pytest.mark.parametrize('line, length, kwargs, exp_result, exp_message', [
        ('1234', 4, {}, True, None),
        ('12345', 4, {}, False, 'Test: record length is 5 characters but must be 4.'),
        ('123', 4, {}, False, 'Test: record length is 3 characters but must be 4.'),
    ])
    def test_recordHasLength(self, line, length, kwargs, exp_result, exp_message):
        _validator = PreparsingValidators.recordHasLength(length, **kwargs)
        _validate_and_assert(_validator, line, exp_result, exp_message)

    @pytest.mark.parametrize('line, min, max, kwargs, exp_result, exp_message', [
        ('1234', 2, 6, {}, True, None),
        ('1234', 2, 4, {}, True, None),
        ('1234', 4, 6, {}, True, None),
        ('1234', 1, 2, {}, False, 'Test: record length of 4 characters is not in the range [1, 2].'),
        ('1234', 6, 8, {}, False, 'Test: record length of 4 characters is not in the range [6, 8].'),
    ])
    def test_recordHasLengthBetween(self, line, min, max, kwargs, exp_result, exp_message):
        _validator = PreparsingValidators.recordHasLengthBetween(min, max, **kwargs)
        _validate_and_assert(_validator, line, exp_result, exp_message)

    @pytest.mark.parametrize('line, substr, kwargs, exp_result, exp_message', [
        ('12345', '12', {}, True, None),
        ('ABC123', 'ABC', {}, True, None),
        ('ABC123', 'abc', {}, False, 'ABC123 must start with abc.'),
        ('12345', 'abc', {}, False, '12345 must start with abc.'),
    ])
    def test_recordStartsWith(self, line, substr, kwargs, exp_result, exp_message):
        _validator = PreparsingValidators.recordStartsWith(substr, **kwargs)
        _validate_and_assert(_validator, line, exp_result, exp_message)

    @pytest.mark.parametrize('line, start, end, kwargs, exp_result, exp_message', [
        ('1234', 1, 3, {}, True, None),
        ('1004', 1, 3, {}, True, None),
        ('1  4', 1, 3, {}, False, 'Test: Case number 1  4 cannot contain blanks.'),
        ('1##4', 1, 3, {}, False, 'Test: Case number 1##4 cannot contain blanks.'),
    ])
    def test_caseNumberNotEmpty(self, line, start, end, kwargs, exp_result, exp_message):
        _validator = PreparsingValidators.caseNumberNotEmpty(start, end, **kwargs)
        _validate_and_assert(_validator, line, exp_result, exp_message)
