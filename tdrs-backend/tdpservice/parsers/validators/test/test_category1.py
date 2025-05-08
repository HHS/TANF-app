"""Test category1 validators."""

import pytest
from tdpservice.parsers.validators import category1
from tdpservice.parsers.validators.util import deprecate_call
from tdpservice.parsers.row_schema import TanfDataReportSchema
from tdpservice.parsers.dataclasses import ValidationErrorArgs

test_schema = TanfDataReportSchema(
    record_type="Test",
    model=None,
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


def _validate_and_assert(validator, line, exp_result, exp_message, exp_deprecated=False):
    result = validator(line, _make_eargs(line))
    assert result.valid == exp_result
    assert result.error == exp_message
    assert result.deprecated == exp_deprecated


@pytest.mark.parametrize('line, kwargs, exp_result, exp_message', [
    ('asdfasdf', {}, True, None),
    ('00000000', {}, True, None),
    ('########', {}, False, 'Test Item 1 (test field): ######## contains blanks between positions 0 and 8.'),
    ('        ', {}, False, 'Test Item 1 (test field):          contains blanks between positions 0 and 8.'),
])
def test_recordIsNotEmpty(line, kwargs, exp_result, exp_message):
    """Test recordIsNotEmpty error messages."""
    _validator = category1.recordIsNotEmpty(**kwargs)
    _validate_and_assert(_validator, line, exp_result, exp_message)


@pytest.mark.parametrize('line, length, kwargs, exp_result, exp_message', [
    ('1234', 4, {}, True, None),
    ('12345', 4, {}, False, 'Test: record length is 5 characters but must be 4.'),
    ('123', 4, {}, False, 'Test: record length is 3 characters but must be 4.'),
])
def test_recordHasLength(line, length, kwargs, exp_result, exp_message):
    """Test recordHasLength error messages."""
    _validator = category1.recordHasLength(length, **kwargs)
    _validate_and_assert(_validator, line, exp_result, exp_message)

@pytest.mark.parametrize('line, length, kwargs, exp_result, exp_message', [
    ('1234', 4, {}, True, None),
    ('12345            ', 10, {}, True, None),
    ('123', 4, {}, False, 'Test: record length should be at least 4 characters but it is 3 characters.'),
])
def test_recordHasLengthOfAtLeast(line, length, kwargs, exp_result, exp_message):
    """Test recordHasLengthOfAtLeast error messages."""
    _validator = category1.recordHasLengthOfAtLeast(length, **kwargs)
    _validate_and_assert(_validator, line, exp_result, exp_message)


@pytest.mark.parametrize('line, min, max, kwargs, exp_result, exp_message', [
    ('1234', 2, 6, {}, True, None),
    ('1234', 2, 4, {}, True, None),
    ('1234', 4, 6, {}, True, None),
    ('1234', 1, 2, {}, False, 'Test: record length of 4 characters is not in the range [1, 2].'),
    ('1234', 6, 8, {}, False, 'Test: record length of 4 characters is not in the range [6, 8].'),
])
def test_recordHasLengthBetween(line, min, max, kwargs, exp_result, exp_message):
    """Test recordHasLengthBetween error messages."""
    _validator = category1.recordHasLengthBetween(min, max, **kwargs)
    _validate_and_assert(_validator, line, exp_result, exp_message)


@pytest.mark.parametrize('line, substr, kwargs, exp_result, exp_message', [
    ('12345', '12', {}, True, None),
    ('ABC123', 'ABC', {}, True, None),
    ('ABC123', 'abc', {}, False, 'ABC123 must start with abc.'),
    ('12345', 'abc', {}, False, '12345 must start with abc.'),
])
def test_recordStartsWith(line, substr, kwargs, exp_result, exp_message):
    """Test recordStartsWith error messages."""
    _validator = category1.recordStartsWith(substr, **kwargs)
    _validate_and_assert(_validator, line, exp_result, exp_message)


@pytest.mark.parametrize('line, start, end, kwargs, exp_result, exp_message', [
    ('1234', 1, 3, {}, True, None),
    ('1004', 1, 3, {}, True, None),
    ('1  4', 1, 3, {}, False, 'Test: Case number 1  4 cannot contain blanks.'),
    ('1##4', 1, 3, {}, False, 'Test: Case number 1##4 cannot contain blanks.'),
])
def test_caseNumberNotEmpty(line, start, end, kwargs, exp_result, exp_message):
    """Test caseNumberNotEmpty error messages."""
    _validator = category1.caseNumberNotEmpty(start, end, **kwargs)
    _validate_and_assert(_validator, line, exp_result, exp_message)


@pytest.mark.parametrize('line, validator, kwargs, exp_result, exp_message', [
    ('1234', category1.recordHasLength, {"length": 4}, True, None),
    ('    ', category1.recordIsNotEmpty, {}, False, ('Test Item 1 (test field):      contains blanks '
                                                     'between positions 0 and 4.')),
    ('1  4', category1.recordStartsWith, {"substr": "x"}, False, '1  4 must start with x.'),
])
def test_deprecated_cat1_validator(line, validator, kwargs, exp_result, exp_message):
    """Test deprecated cat1 validators."""
    deprecated_validator = deprecate_call(validator(**kwargs))
    _validate_and_assert(deprecated_validator, line, exp_result, exp_message, exp_deprecated=True)
