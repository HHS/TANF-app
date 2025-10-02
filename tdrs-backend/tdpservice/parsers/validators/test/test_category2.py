"""Test category2 validators."""

import pytest

from tdpservice.parsers.dataclasses import ValidationErrorArgs
from tdpservice.parsers.row_schema import TanfDataReportSchema
from tdpservice.parsers.validators import category2
from tdpservice.parsers.validators.util import deprecate_call

test_schema = TanfDataReportSchema(
    record_type="Test",
    model=None,
    preparsing_validators=[],
    postparsing_validators=[],
    fields=[],
)


def _make_eargs(val):
    return ValidationErrorArgs(
        value=val, row_schema=test_schema, friendly_name="test field", item_num="1"
    )


def _validate_and_assert(validator, val, exp_result, exp_message, exp_deprecated=False):
    result = validator(val, _make_eargs(val))
    assert result.valid == exp_result
    assert result.error_message == exp_message
    assert result.deprecated == exp_deprecated


@pytest.mark.parametrize(
    "val, option, kwargs, exp_result, exp_message",
    [
        (10, 10, {}, True, None),
        (1, 10, {}, False, "Test Item 1 (test field): 1 does not match 10."),
    ],
)
def test_isEqual(val, option, kwargs, exp_result, exp_message):
    """Test isEqual validator error messages."""
    _validator = category2.isEqual(option, **kwargs)
    _validate_and_assert(_validator, val, exp_result, exp_message)


@pytest.mark.parametrize(
    "val, option, kwargs, exp_result, exp_message",
    [
        (1, 10, {}, True, None),
        (10, 10, {}, False, "Test Item 1 (test field): 10 matches 10."),
    ],
)
def test_isNotEqual(val, option, kwargs, exp_result, exp_message):
    """Test isNotEqual validator error messages."""
    _validator = category2.isNotEqual(option, **kwargs)
    _validate_and_assert(_validator, val, exp_result, exp_message)


@pytest.mark.parametrize(
    "val, options, kwargs, exp_result, exp_message",
    [
        (1, [1, 2, 3], {}, True, None),
        (1, [4, 5, 6], {}, False, "Test Item 1 (test field): 1 is not in [4, 5, 6]."),
    ],
)
def test_isOneOf(val, options, kwargs, exp_result, exp_message):
    """Test isOneOf validator error messages."""
    _validator = category2.isOneOf(options, **kwargs)
    _validate_and_assert(_validator, val, exp_result, exp_message)


@pytest.mark.parametrize(
    "val, options, kwargs, exp_result, exp_message",
    [
        (1, [4, 5, 6], {}, True, None),
        (1, [1, 2, 3], {}, False, "Test Item 1 (test field): 1 is in [1, 2, 3]."),
    ],
)
def test_isNotOneOf(val, options, kwargs, exp_result, exp_message):
    """Test isNotOneOf validator error messages."""
    _validator = category2.isNotOneOf(options, **kwargs)
    _validate_and_assert(_validator, val, exp_result, exp_message)


@pytest.mark.parametrize(
    "val, option, inclusive, kwargs, exp_result, exp_message",
    [
        (10, 5, True, {}, True, None),
        (
            10,
            20,
            True,
            {},
            False,
            "Test Item 1 (test field): 10 is not larger than 20.",
        ),
        (
            10,
            10,
            False,
            {},
            False,
            "Test Item 1 (test field): 10 is not larger than 10.",
        ),
    ],
)
def test_isGreaterThan(val, option, inclusive, kwargs, exp_result, exp_message):
    """Test isGreaterThan validator error messages."""
    _validator = category2.isGreaterThan(option, inclusive, **kwargs)
    _validate_and_assert(_validator, val, exp_result, exp_message)


@pytest.mark.parametrize(
    "val, option, inclusive, kwargs, exp_result, exp_message",
    [
        (5, 10, True, {}, True, None),
        (5, 3, True, {}, False, "Test Item 1 (test field): 5 is not smaller than 3."),
        (5, 5, False, {}, False, "Test Item 1 (test field): 5 is not smaller than 5."),
    ],
)
def test_isLessThan(val, option, inclusive, kwargs, exp_result, exp_message):
    """Test isLessThan validator error messages."""
    _validator = category2.isLessThan(option, inclusive, **kwargs)
    _validate_and_assert(_validator, val, exp_result, exp_message)


@pytest.mark.parametrize(
    "val, min, max, inclusive, kwargs, exp_result, exp_message",
    [
        (5, 1, 10, True, {}, True, None),
        (
            20,
            1,
            10,
            True,
            {},
            False,
            "Test Item 1 (test field): 20 is not in range [1, 10].",
        ),
        (5, 1, 10, False, {}, True, None),
        (
            20,
            1,
            10,
            False,
            {},
            False,
            "Test Item 1 (test field): 20 is not between 1 and 10.",
        ),
    ],
)
def test_isBetween(val, min, max, inclusive, kwargs, exp_result, exp_message):
    """Test isBetween validator error messages."""
    _validator = category2.isBetween(min, max, inclusive, **kwargs)
    _validate_and_assert(_validator, val, exp_result, exp_message)


@pytest.mark.parametrize(
    "val, substr, kwargs, exp_result, exp_message",
    [
        ("abcdef", "abc", {}, True, None),
        (
            "abcdef",
            "xyz",
            {},
            False,
            "Test Item 1 (test field): abcdef does not start with xyz.",
        ),
    ],
)
def test_startsWith(val, substr, kwargs, exp_result, exp_message):
    """Test startsWith validator error messages."""
    _validator = category2.startsWith(substr, **kwargs)
    _validate_and_assert(_validator, val, exp_result, exp_message)


@pytest.mark.parametrize(
    "val, substr, kwargs, exp_result, exp_message",
    [
        ("abc123", "c1", {}, True, None),
        (
            "abc123",
            "xy",
            {},
            False,
            "Test Item 1 (test field): abc123 does not contain xy.",
        ),
    ],
)
def test_contains(val, substr, kwargs, exp_result, exp_message):
    """Test contains validator error messages."""
    _validator = category2.contains(substr, **kwargs)
    _validate_and_assert(_validator, val, exp_result, exp_message)


@pytest.mark.parametrize(
    "val, kwargs, exp_result, exp_message",
    [
        (1001, {}, True, None),
        ("ABC", {}, False, "Test Item 1 (test field): ABC is not a number."),
    ],
)
def test_isNumber(val, kwargs, exp_result, exp_message):
    """Test isNumber validator error messages."""
    _validator = category2.isNumber(**kwargs)
    _validate_and_assert(_validator, val, exp_result, exp_message)


@pytest.mark.parametrize(
    "val, kwargs, exp_result, exp_message",
    [
        ("F*&k", {}, False, "Test Item 1 (test field): F*&k is not alphanumeric."),
        ("Fork", {}, True, None),
    ],
)
def test_isAlphaNumeric(val, kwargs, exp_result, exp_message):
    """Test isAlphaNumeric validator error messages."""
    _validator = category2.isAlphaNumeric(**kwargs)
    _validate_and_assert(_validator, val, exp_result, exp_message)


@pytest.mark.parametrize(
    "val, start, end, kwargs, exp_result, exp_message",
    [
        ("   ", 0, 4, {}, True, None),
        (
            "1001",
            0,
            4,
            {},
            False,
            "Test Item 1 (test field): 1001 is not blank between positions 0 and 4.",
        ),
    ],
)
def test_isEmpty(val, start, end, kwargs, exp_result, exp_message):
    """Test isEmpty validator error messages."""
    _validator = category2.isEmpty(start, end, **kwargs)
    _validate_and_assert(_validator, val, exp_result, exp_message)


@pytest.mark.parametrize(
    "val, start, end, kwargs, exp_result, exp_message",
    [
        ("1001", 0, 4, {}, True, None),
        (
            "    ",
            0,
            4,
            {},
            False,
            "Test Item 1 (test field):      contains blanks between positions 0 and 4.",
        ),
    ],
)
def test_isNotEmpty(val, start, end, kwargs, exp_result, exp_message):
    """Test isNotEmpty validator error messages."""
    _validator = category2.isNotEmpty(start, end, **kwargs)
    _validate_and_assert(_validator, val, exp_result, exp_message)


@pytest.mark.parametrize(
    "val, kwargs, exp_result, exp_message",
    [
        ("    ", {}, True, None),
        ("0000", {}, False, "Test Item 1 (test field): 0000 is not blank."),
    ],
)
def test_isBlank(val, kwargs, exp_result, exp_message):
    """Test isBlank validator error messages."""
    _validator = category2.isBlank(**kwargs)
    _validate_and_assert(_validator, val, exp_result, exp_message)


@pytest.mark.parametrize(
    "val, length, kwargs, exp_result, exp_message",
    [
        ("123", 3, {}, True, None),
        (
            "123",
            4,
            {},
            False,
            "Test Item 1 (test field): field length is 3 characters but must be 4.",
        ),
    ],
)
def test_hasLength(val, length, kwargs, exp_result, exp_message):
    """Test hasLength validator error messages."""
    _validator = category2.hasLength(length, **kwargs)
    _validate_and_assert(_validator, val, exp_result, exp_message)


@pytest.mark.parametrize(
    "val, length, inclusive, kwargs, exp_result, exp_message",
    [
        ("123", 3, True, {}, True, None),
        (
            "123",
            3,
            False,
            {},
            False,
            "Test Item 1 (test field): Value length 3 is not greater than 3.",
        ),
    ],
)
def test_hasLengthGreaterThan(val, length, inclusive, kwargs, exp_result, exp_message):
    """Test hasLengthGreaterThan validator error messages."""
    _validator = category2.hasLengthGreaterThan(length, inclusive, **kwargs)
    _validate_and_assert(_validator, val, exp_result, exp_message)


@pytest.mark.parametrize(
    "val, length, kwargs, exp_result, exp_message",
    [
        (101, 3, {}, True, None),
        (
            101,
            2,
            {},
            False,
            "Test Item 1 (test field): 101 does not have exactly 2 digits.",
        ),
    ],
)
def test_intHasLength(val, length, kwargs, exp_result, exp_message):
    """Test intHasLength validator error messages."""
    _validator = category2.intHasLength(length, **kwargs)
    _validate_and_assert(_validator, val, exp_result, exp_message)


@pytest.mark.parametrize(
    "val, number_of_zeros, kwargs, exp_result, exp_message",
    [
        ("111", 3, {}, True, None),
        ("000", 3, {}, False, "Test Item 1 (test field): 000 is zero."),
    ],
)
def test_isNotZero(val, number_of_zeros, kwargs, exp_result, exp_message):
    """Test isNotZero validator error messages."""
    _validator = category2.isNotZero(number_of_zeros, **kwargs)
    _validate_and_assert(_validator, val, exp_result, exp_message)


@pytest.mark.parametrize(
    "val, year, kwargs, exp_result, exp_message",
    [
        ("202201", 2020, {}, True, None),
        (
            "201001",
            2020,
            {},
            False,
            "Test Item 1 (test field): Year 2010 must be larger than 2020.",
        ),
        (
            "202001",
            2020,
            {},
            False,
            "Test Item 1 (test field): Year 2020 must be larger than 2020.",
        ),
    ],
)
def test_dateYearIsLargerThan(val, year, kwargs, exp_result, exp_message):
    """Test dateYearIsLargerThan validator error messages."""
    _validator = category2.dateYearIsLargerThan(year, **kwargs)
    _validate_and_assert(_validator, val, exp_result, exp_message)


@pytest.mark.parametrize(
    "val, year, month, kwargs, exp_result, exp_message",
    [
        (
            "201001",
            2010,
            2,
            {},
            False,
            "Test Item 1 (test field): If year equals 2010 month must be larger than 2.",
        ),
        (
            "202010",
            2010,
            8,
            {},
            True,
            None,
        ),
        (
            "200901",
            2010,
            2,
            {},
            False,
            "Test Item 1 (test field): Must be larger than 201002.",
        ),
        (
            "202001",
            2010,
            8,
            {},
            True,
            None,
        ),
    ],
)
def test_dateYearMonthIsLargerThan(val, year, month, kwargs, exp_result, exp_message):
    """Test dateYearMonthIsLargerThan validator error messages."""
    _validator = category2.dateYearMonthIsLargerThan(year, month, **kwargs)
    _validate_and_assert(_validator, val, exp_result, exp_message)


@pytest.mark.parametrize(
    "val, month, kwargs, exp_result, exp_message",
    [
        (
            "201001",
            2,
            {},
            False,
            "Test Item 1 (test field): Month 01 must be larger than 2.",
        ),
        (
            "202010",
            8,
            {},
            True,
            None,
        ),
    ],
)
def test_dateMonthIsLargerThan(val, month, kwargs, exp_result, exp_message):
    """Test dateMonthIsLargerThan validator error messages."""
    _validator = category2.dateMonthIsLargerThan(month, **kwargs)
    _validate_and_assert(_validator, val, exp_result, exp_message)


@pytest.mark.parametrize(
    "val, kwargs, exp_result, exp_message",
    [
        ("202010", {}, True, None),
        ("202001", {}, True, None),
        ("202012", {}, True, None),
        ("202015", {}, False, "Test Item 1 (test field): 15 is not a valid month."),
    ],
)
def test_dateMonthIsValid(val, kwargs, exp_result, exp_message):
    """Test dateMonthIsValid validator error messages."""
    _validator = category2.dateMonthIsValid(**kwargs)
    _validate_and_assert(_validator, val, exp_result, exp_message)


@pytest.mark.parametrize(
    "val, kwargs, exp_result, exp_message",
    [
        ("20201001", {}, True, None),
        ("20201031", {}, True, None),
        ("20201032", {}, False, "Test Item 1 (test field): 32 is not a valid day."),
        ("20201050", {}, False, "Test Item 1 (test field): 50 is not a valid day."),
    ],
)
def test_dateDayIsValid(val, kwargs, exp_result, exp_message):
    """Test dateDayIsValid validator error messages."""
    _validator = category2.dateDayIsValid(**kwargs)
    _validate_and_assert(_validator, val, exp_result, exp_message)


@pytest.mark.parametrize(
    "val, kwargs, exp_result, exp_message",
    [
        ("20201", {}, True, None),
        ("20204", {}, True, None),
        ("20200", {}, False, "Test Item 1 (test field): 0 is not a valid quarter."),
        ("20205", {}, False, "Test Item 1 (test field): 5 is not a valid quarter."),
        ("20207", {}, False, "Test Item 1 (test field): 7 is not a valid quarter."),
    ],
)
def test_quarterIsValid(val, kwargs, exp_result, exp_message):
    """Test quarterIsValid validator error messages."""
    _validator = category2.quarterIsValid(**kwargs)
    _validate_and_assert(_validator, val, exp_result, exp_message)


@pytest.mark.parametrize(
    "val, validator, kwargs, exp_result, exp_message",
    [
        (4, category2.isEqual, {"option": 4}, True, None),
        (
            "    ",
            category2.isOneOf,
            {"options": [1, 2]},
            False,
            "Test Item 1 (test field):      is not in [1, 2].",
        ),
        (
            "1  4",
            category2.validateHeaderUpdateIndicator,
            {},
            False,
            (
                "HEADER Update Indicator must be set to D instead "
                "of 1  4. Please review Exporting Complete Data "
                "Using FTANF in the Knowledge Center."
            ),
        ),
    ],
)
def test_deprecated_cat2_validator(val, validator, kwargs, exp_result, exp_message):
    """Test deprecated cat2 validators."""
    deprecated_validator = deprecate_call(validator(**kwargs))
    _validate_and_assert(
        deprecated_validator, val, exp_result, exp_message, exp_deprecated=True
    )
