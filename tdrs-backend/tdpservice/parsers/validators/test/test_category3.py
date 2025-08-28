"""Test category3 validators."""

import datetime

from django.conf import settings

import pytest

from tdpservice.data_files.models import DataFile
from tdpservice.parsers.dataclasses import FieldType, ValidationErrorArgs
from tdpservice.parsers.fields import Field
from tdpservice.parsers.row_schema import TanfDataReportSchema
from tdpservice.parsers.validators import category3
from tdpservice.parsers.validators.util import deprecate_call
from tdpservice.stts.models import STT

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


def _validate_and_assert(validator, val, exp_result, exp_message):
    result = validator(val, _make_eargs(val))
    assert result.valid == exp_result
    assert result.error_message == exp_message
    assert result.deprecated is False


@pytest.mark.parametrize(
    "val, option, kwargs, exp_result, exp_message",
    [
        (10, 10, {}, True, None),
        (1, 10, {}, False, "must match 10"),
    ],
)
def test_isEqual(val, option, kwargs, exp_result, exp_message):
    """Test isEqual validator error messages."""
    _validator = category3.isEqual(option, **kwargs)
    _validate_and_assert(_validator, val, exp_result, exp_message)


@pytest.mark.parametrize(
    "val, option, kwargs, exp_result, exp_message",
    [
        (1, 10, {}, True, None),
        (10, 10, {}, False, "must not be equal to 10"),
    ],
)
def test_isNotEqual(val, option, kwargs, exp_result, exp_message):
    """Test isNotEqual validator error messages."""
    _validator = category3.isNotEqual(option, **kwargs)
    _validate_and_assert(_validator, val, exp_result, exp_message)


@pytest.mark.parametrize(
    "val, options, kwargs, exp_result, exp_message",
    [
        (1, [1, 2, 3], {}, True, None),
        (1, [4, 5, 6], {}, False, "must be one of [4, 5, 6]"),
    ],
)
def test_isOneOf(val, options, kwargs, exp_result, exp_message):
    """Test isOneOf validator error messages."""
    _validator = category3.isOneOf(options, **kwargs)
    _validate_and_assert(_validator, val, exp_result, exp_message)


@pytest.mark.parametrize(
    "val, options, kwargs, exp_result, exp_message",
    [
        (1, [4, 5, 6], {}, True, None),
        (1, [1, 2, 3], {}, False, "must not be one of [1, 2, 3]"),
    ],
)
def test_isNotOneOf(val, options, kwargs, exp_result, exp_message):
    """Test isNotOneOf validator error messages."""
    _validator = category3.isNotOneOf(options, **kwargs)
    _validate_and_assert(_validator, val, exp_result, exp_message)


@pytest.mark.parametrize(
    "val, option, inclusive, kwargs, exp_result, exp_message",
    [
        (10, 5, True, {}, True, None),
        (10, 20, True, {}, False, "must be greater than 20"),
        (10, 10, False, {}, False, "must be greater than 10"),
    ],
)
def test_isGreaterThan(val, option, inclusive, kwargs, exp_result, exp_message):
    """Test isGreaterThan validator error messages."""
    _validator = category3.isGreaterThan(option, inclusive, **kwargs)
    _validate_and_assert(_validator, val, exp_result, exp_message)


@pytest.mark.parametrize(
    "val, option, inclusive, kwargs, exp_result, exp_message",
    [
        (5, 10, True, {}, True, None),
        (5, 3, True, {}, False, "must be less than 3"),
        (5, 5, False, {}, False, "must be less than 5"),
    ],
)
def test_isLessThan(val, option, inclusive, kwargs, exp_result, exp_message):
    """Test isLessThan validator error messages."""
    _validator = category3.isLessThan(option, inclusive, **kwargs)
    _validate_and_assert(_validator, val, exp_result, exp_message)


@pytest.mark.parametrize(
    "val, min, max, inclusive, kwargs, exp_result, exp_message",
    [
        (5, 1, 10, True, {}, True, None),
        (20, 1, 10, True, {}, False, "must be between 1 and 10"),
        (5, 1, 10, False, {}, True, None),
        (20, 1, 10, False, {}, False, "must be between 1 and 10"),
    ],
)
def test_isBetween(val, min, max, inclusive, kwargs, exp_result, exp_message):
    """Test isBetween validator error messages."""
    _validator = category3.isBetween(min, max, inclusive, **kwargs)
    _validate_and_assert(_validator, val, exp_result, exp_message)


@pytest.mark.parametrize(
    "val, substr, kwargs, exp_result, exp_message",
    [
        ("abcdef", "abc", {}, True, None),
        ("abcdef", "xyz", {}, False, "must start with xyz"),
    ],
)
def test_startsWith(val, substr, kwargs, exp_result, exp_message):
    """Test startsWith validator error messages."""
    _validator = category3.startsWith(substr, **kwargs)
    _validate_and_assert(_validator, val, exp_result, exp_message)


@pytest.mark.parametrize(
    "val, substr, kwargs, exp_result, exp_message",
    [
        ("abc123", "c1", {}, True, None),
        ("abc123", "xy", {}, False, "must contain xy"),
    ],
)
def test_contains(val, substr, kwargs, exp_result, exp_message):
    """Test contains validator error messages."""
    _validator = category3.contains(substr, **kwargs)
    _validate_and_assert(_validator, val, exp_result, exp_message)


@pytest.mark.parametrize(
    "val, kwargs, exp_result, exp_message",
    [
        (1001, {}, True, None),
        ("ABC", {}, False, "must be a number"),
    ],
)
def test_isNumber(val, kwargs, exp_result, exp_message):
    """Test isNumber validator error messages."""
    _validator = category3.isNumber(**kwargs)
    _validate_and_assert(_validator, val, exp_result, exp_message)


@pytest.mark.parametrize(
    "val, kwargs, exp_result, exp_message",
    [
        ("F*&k", {}, False, "must be alphanumeric"),
        ("Fork", {}, True, None),
    ],
)
def test_isAlphaNumeric(val, kwargs, exp_result, exp_message):
    """Test isAlphaNumeric validator error messages."""
    _validator = category3.isAlphaNumeric(**kwargs)
    _validate_and_assert(_validator, val, exp_result, exp_message)


@pytest.mark.parametrize(
    "val, start, end, kwargs, exp_result, exp_message",
    [
        ("   ", 0, 4, {}, True, None),
        ("1001", 0, 4, {}, False, "must be empty"),
    ],
)
def test_isEmpty(val, start, end, kwargs, exp_result, exp_message):
    """Test isEmpty validator error messages."""
    _validator = category3.isEmpty(start, end, **kwargs)
    _validate_and_assert(_validator, val, exp_result, exp_message)


@pytest.mark.parametrize(
    "val, start, end, kwargs, exp_result, exp_message",
    [
        ("1001", 0, 4, {}, True, None),
        ("    ", 0, 4, {}, False, "must not be empty"),
    ],
)
def test_isNotEmpty(val, start, end, kwargs, exp_result, exp_message):
    """Test isNotEmpty validator error messages."""
    _validator = category3.isNotEmpty(start, end, **kwargs)
    _validate_and_assert(_validator, val, exp_result, exp_message)


@pytest.mark.parametrize(
    "val, kwargs, exp_result, exp_message",
    [
        ("    ", {}, True, None),
        ("0000", {}, False, "must be blank"),
    ],
)
def test_isBlank(val, kwargs, exp_result, exp_message):
    """Test isBlank validator error messages."""
    _validator = category3.isBlank(**kwargs)
    _validate_and_assert(_validator, val, exp_result, exp_message)


@pytest.mark.parametrize(
    "val, length, kwargs, exp_result, exp_message",
    [
        ("123", 3, {}, True, None),
        ("123", 4, {}, False, "must have length 4"),
    ],
)
def test_hasLength(val, length, kwargs, exp_result, exp_message):
    """Test hasLength validator error messages."""
    _validator = category3.hasLength(length, **kwargs)
    _validate_and_assert(_validator, val, exp_result, exp_message)


@pytest.mark.parametrize(
    "val, length, inclusive, kwargs, exp_result, exp_message",
    [
        ("123", 3, True, {}, True, None),
        ("123", 3, False, {}, False, "must have length greater than 3"),
    ],
)
def test_hasLengthGreaterThan(val, length, inclusive, kwargs, exp_result, exp_message):
    """Test hasLengthGreaterThan validator error messages."""
    _validator = category3.hasLengthGreaterThan(length, inclusive, **kwargs)
    _validate_and_assert(_validator, val, exp_result, exp_message)


@pytest.mark.parametrize(
    "val, length, kwargs, exp_result, exp_message",
    [
        (101, 3, {}, True, None),
        (101, 2, {}, False, "must have length 2"),
    ],
)
def test_intHasLength(val, length, kwargs, exp_result, exp_message):
    """Test intHasLength validator error messages."""
    _validator = category3.intHasLength(length, **kwargs)
    _validate_and_assert(_validator, val, exp_result, exp_message)


@pytest.mark.parametrize(
    "val, number_of_zeros, kwargs, exp_result, exp_message",
    [
        ("111", 3, {}, True, None),
        ("000", 3, {}, False, "must not be zero"),
    ],
)
def test_isNotZero(val, number_of_zeros, kwargs, exp_result, exp_message):
    """Test isNotZero validator error messages."""
    _validator = category3.isNotZero(number_of_zeros, **kwargs)
    _validate_and_assert(_validator, val, exp_result, exp_message)


@pytest.mark.parametrize(
    "val, min_age, kwargs, exp_result, exp_message",
    [
        ("199510", 18, {}, True, None),
        (
            f"{datetime.date.today().year - 18}01",
            18,
            {},
            False,
            (
                f"{datetime.date.today().year - 18} must be less than or equal to "
                f"{datetime.date.today().year - 18} to meet the minimum age requirement."
            ),
        ),
        (
            "202010",
            18,
            {},
            False,
            (
                f"2020 must be less than or equal to {datetime.date.today().year - 18} "
                "to meet the minimum age requirement."
            ),
        ),
    ],
)
def test_isOlderThan(val, min_age, kwargs, exp_result, exp_message):
    """Test isOlderThan validator error messages."""
    _validator = category3.isOlderThan(min_age, **kwargs)
    _validate_and_assert(_validator, val, exp_result, exp_message)


@pytest.mark.parametrize(
    "val, kwargs, exp_result, exp_message",
    [
        ("123456789", {}, True, None),
        ("987654321", {}, True, None),
        (
            "111111111",
            {},
            False,
            "is in ['000000000', '111111111', '222222222', '333333333', "
            "'444444444', '555555555', '666666666', '777777777', '888888888', '999999999'].",
        ),
        (
            "999999999",
            {},
            False,
            "is in ['000000000', '111111111', '222222222', '333333333', "
            "'444444444', '555555555', '666666666', '777777777', '888888888', '999999999'].",
        ),
        (
            "888888888",
            {},
            False,
            "is in ['000000000', '111111111', '222222222', '333333333', "
            "'444444444', '555555555', '666666666', '777777777', '888888888', '999999999'].",
        ),
    ],
)
def test_validateSSN(val, kwargs, exp_result, exp_message):
    """Test validateSSN validator error messages."""
    _validator = category3.validateSSN(**kwargs)
    _validate_and_assert(_validator, val, exp_result, exp_message)


@pytest.mark.parametrize(
    "condition_val, result_val, exp_result, exp_message, exp_fields",
    [
        (1, 1, True, None, ["TestField3", "TestField1"]),  # condition fails, valid
        (
            10,
            1,
            True,
            None,
            ["TestField1", "TestField3"],
        ),  # condition pass, result pass
        # condition pass, result fail
        (
            10,
            20,
            False,
            "Since Item 1 (test1) is 10, then Item 3 (test3) 20 must be less than 10",
            ["TestField1", "TestField3"],
        ),
    ],
)
def test_ifThenAlso(condition_val, result_val, exp_result, exp_message, exp_fields):
    """Test ifThenAlso validator error messages."""
    schema = TanfDataReportSchema(
        fields=[
            Field(
                item="1",
                name="TestField1",
                friendly_name="test1",
                type=FieldType.NUMERIC,
                startIndex=0,
                endIndex=1,
            ),
            Field(
                item="2",
                name="TestField2",
                friendly_name="test2",
                type=FieldType.NUMERIC,
                startIndex=1,
                endIndex=2,
            ),
            Field(
                item="3",
                name="TestField3",
                friendly_name="test3",
                type=FieldType.NUMERIC,
                startIndex=2,
                endIndex=3,
            ),
        ]
    )
    instance = {
        "TestField1": condition_val,
        "TestField2": 1,
        "TestField3": result_val,
    }
    _validator = category3.ifThenAlso(
        condition_field_name="TestField1",
        condition_function=category3.isEqual(10),
        result_field_name="TestField3",
        result_function=category3.isLessThan(10),
    )
    result = _validator(instance, schema)
    assert result.valid == exp_result
    assert result.error_message == exp_message
    assert result.field_names == exp_fields


@pytest.mark.parametrize(
    "condition_val, result_val, exp_result, exp_message, exp_fields",
    [
        (1, 1, True, None, ["TestField3", "TestField1"]),  # condition fails, valid
        (
            10,
            1,
            True,
            None,
            ["TestField1", "TestField3"],
        ),  # condition pass, result pass
        (10, 110, True, None, ["TestField1", "TestField3"]),
        # condition pass, result fail
        (
            10,
            20,
            False,
            "Since Item 1 (test1) is 10, then Item 3 (test3) 20 must be less than 10 or must be greater than 100.",
            ["TestField1", "TestField3"],
        ),
    ],
)
def test_ifThenAlso_or(condition_val, result_val, exp_result, exp_message, exp_fields):
    """Test ifThenAlso validator error messages."""
    schema = TanfDataReportSchema(
        fields=[
            Field(
                item="1",
                name="TestField1",
                friendly_name="test1",
                type=FieldType.NUMERIC,
                startIndex=0,
                endIndex=1,
            ),
            Field(
                item="2",
                name="TestField2",
                friendly_name="test2",
                type=FieldType.NUMERIC,
                startIndex=1,
                endIndex=2,
            ),
            Field(
                item="3",
                name="TestField3",
                friendly_name="test3",
                type=FieldType.NUMERIC,
                startIndex=2,
                endIndex=3,
            ),
        ]
    )
    instance = {
        "TestField1": condition_val,
        "TestField2": 1,
        "TestField3": result_val,
    }
    _validator = category3.ifThenAlso(
        condition_field_name="TestField1",
        condition_function=category3.isEqual(10),
        result_field_name="TestField3",
        result_function=category3.orValidators(
            [category3.isLessThan(10), category3.isGreaterThan(100)], if_result=True
        ),
    )
    result = _validator(instance, schema)
    assert result.valid == exp_result
    assert result.error_message == exp_message
    assert result.field_names == exp_fields


@pytest.mark.parametrize(
    "val, exp_result, exp_message",
    [
        (10, True, None),
        (3, True, None),
        (100, False, "Item 1 (TestField1) 100 must match 10 or must be less than 5."),
    ],
)
def test_orValidators(val, exp_result, exp_message):
    """Test orValidators error messages."""
    _validator = category3.orValidators(
        [category3.isEqual(10), category3.isLessThan(5)]
    )

    eargs = ValidationErrorArgs(
        value=val,
        row_schema=TanfDataReportSchema(),
        friendly_name="TestField1",
        item_num="1",
    )

    result = _validator(val, eargs)
    assert result.valid == exp_result
    assert result.error_message == exp_message


def test_sumIsEqual():
    """Test sumIsEqual postparsing validator."""
    schema = TanfDataReportSchema(
        fields=[
            Field(
                item="1",
                name="TestField1",
                friendly_name="test1",
                type=FieldType.NUMERIC,
                startIndex=0,
                endIndex=1,
            ),
            Field(
                item="2",
                name="TestField2",
                friendly_name="test2",
                type=FieldType.NUMERIC,
                startIndex=1,
                endIndex=2,
            ),
            Field(
                item="3",
                name="TestField3",
                friendly_name="test3",
                type=FieldType.NUMERIC,
                startIndex=2,
                endIndex=3,
            ),
        ]
    )
    instance = {
        "TestField1": 2,
        "TestField2": 1,
        "TestField3": 9,
    }
    result = category3.sumIsEqual("TestField2", ["TestField1", "TestField3"])(
        instance, schema
    )
    assert result.valid is False
    assert (
        result.error_message
        == "The sum of TestField1, TestField3 does not equal TestField2 test2 Item 2."
    )
    assert result.field_names == ["TestField2", "TestField1", "TestField3"]

    instance["TestField2"] = 11
    result = category3.sumIsEqual("TestField2", ["TestField1", "TestField3"])(
        instance, schema
    )
    assert result.valid is True
    assert result.error_message is None
    assert result.field_names == ["TestField2", "TestField1", "TestField3"]


def test_sumIsLarger():
    """Test sumIsLarger postparsing validator."""
    schema = TanfDataReportSchema(
        fields=[
            Field(
                item="1",
                name="TestField1",
                friendly_name="test1",
                type=FieldType.NUMERIC,
                startIndex=0,
                endIndex=1,
            ),
            Field(
                item="2",
                name="TestField2",
                friendly_name="test2",
                type=FieldType.NUMERIC,
                startIndex=1,
                endIndex=2,
            ),
            Field(
                item="3",
                name="TestField3",
                friendly_name="test3",
                type=FieldType.NUMERIC,
                startIndex=2,
                endIndex=3,
            ),
        ]
    )
    instance = {
        "TestField1": 2,
        "TestField2": 1,
        "TestField3": 5,
    }
    result = category3.sumIsLarger(["TestField1", "TestField3"], 10)(instance, schema)
    assert result.valid is False
    assert result.error_message == (
        "No benefit amounts detected for this case. The total sum of TestField1, TestField3 must be greater than 10."
    )
    assert result.field_names == ["TestField1", "TestField3"]

    instance["TestField3"] = 9
    result = category3.sumIsLarger(["TestField1", "TestField3"], 10)(instance, schema)
    assert result.valid is True
    assert result.error_message is None
    assert result.field_names == ["TestField1", "TestField3"]


def test_suppress_for_fra_pilot_state():
    """Test `suppress_for_fra_pilot_state` suppresses validation logic."""
    stt = STT(type="state", postal_code="AZ")
    datafile = DataFile(stt=stt)
    schema = TanfDataReportSchema(
        fields=[
            Field(
                item="1",
                name="WORK_ELIGIBLE_INDICATOR",
                friendly_name="Work-Eligible Individual Indicator",
                type=FieldType.ALPHA_NUMERIC,
                startIndex=0,
                endIndex=1,
            ),
            Field(
                item="2",
                name="WORK_PART_STATUS",
                friendly_name="Work Participation Status",
                type=FieldType.ALPHA_NUMERIC,
                startIndex=1,
                endIndex=2,
            ),
        ],
    )
    schema.prepare(datafile)

    record = {
        "WORK_ELIGIBLE_INDICATOR": "1",
        "WORK_PART_STATUS": "99",
    }

    validate = category3.suppress_for_fra_pilot_state(
        "WORK_ELIGIBLE_INDICATOR",
        "WORK_PART_STATUS",
        category3.ifThenAlso(
            condition_field_name="WORK_ELIGIBLE_INDICATOR",
            condition_function=category3.isBetween(1, 5, inclusive=True, cast=int),
            result_field_name="WORK_PART_STATUS",
            result_function=category3.isNotEqual("99"),
        ),
    )

    settings.FRA_PILOT_STATES = ["AZ"]

    result = validate(record, schema)
    assert result.valid
    assert result.error_message is None


def test_validate__WORK_ELIGIBLE_INDICATOR__HOH__AGE():
    """Test `validate__WORK_ELIGIBLE_INDICATOR__HOH__AGE` gives a valid result."""
    schema = TanfDataReportSchema(
        fields=[
            Field(
                item="1",
                name="WORK_ELIGIBLE_INDICATOR",
                friendly_name="work eligible indicator",
                type=FieldType.ALPHA_NUMERIC,
                startIndex=0,
                endIndex=1,
            ),
            Field(
                item="2",
                name="RELATIONSHIP_HOH",
                friendly_name="relationship w/ head of household",
                type=FieldType.ALPHA_NUMERIC,
                startIndex=1,
                endIndex=2,
            ),
            Field(
                item="3",
                name="DATE_OF_BIRTH",
                friendly_name="date of birth",
                type=FieldType.ALPHA_NUMERIC,
                startIndex=2,
                endIndex=10,
            ),
            Field(
                item="4",
                name="RPT_MONTH_YEAR",
                friendly_name="report month/year",
                type=FieldType.ALPHA_NUMERIC,
                startIndex=10,
                endIndex=16,
            ),
        ]
    )
    instance = {
        "WORK_ELIGIBLE_INDICATOR": "11",
        "RELATIONSHIP_HOH": "1",
        "DATE_OF_BIRTH": "20200101",
        "RPT_MONTH_YEAR": "202010",
    }
    result = category3.validate__WORK_ELIGIBLE_INDICATOR__HOH__AGE()(instance, schema)
    assert result.valid is False
    assert result.error_message == (
        "T1: Since Item 1 (work eligible indicator) is 11 and Item 3 (Age) is less than 19, "
        "then Item 2 (relationship w/ head of household) must not be 1."
    )
    assert result.field_names == [
        "WORK_ELIGIBLE_INDICATOR",
        "RELATIONSHIP_HOH",
        "DATE_OF_BIRTH",
    ]

    instance["DATE_OF_BIRTH"] = "19950101"
    result = category3.validate__WORK_ELIGIBLE_INDICATOR__HOH__AGE()(instance, schema)
    assert result.valid is True
    assert result.error_message is None
    assert result.field_names == [
        "WORK_ELIGIBLE_INDICATOR",
        "RELATIONSHIP_HOH",
        "DATE_OF_BIRTH",
    ]


def test_deprecate__WORK_ELIGIBLE_INDICATOR__HOH__AGE():
    """Test deprecated `validate__WORK_ELIGIBLE_INDICATOR__HOH__AGE` gives a valid result."""
    schema = TanfDataReportSchema(
        fields=[
            Field(
                item="1",
                name="WORK_ELIGIBLE_INDICATOR",
                friendly_name="work eligible indicator",
                type=FieldType.ALPHA_NUMERIC,
                startIndex=0,
                endIndex=1,
            ),
            Field(
                item="2",
                name="RELATIONSHIP_HOH",
                friendly_name="relationship w/ head of household",
                type=FieldType.ALPHA_NUMERIC,
                startIndex=1,
                endIndex=2,
            ),
            Field(
                item="3",
                name="DATE_OF_BIRTH",
                friendly_name="date of birth",
                type=FieldType.ALPHA_NUMERIC,
                startIndex=2,
                endIndex=10,
            ),
            Field(
                item="4",
                name="RPT_MONTH_YEAR",
                friendly_name="report month/year",
                type=FieldType.ALPHA_NUMERIC,
                startIndex=10,
                endIndex=16,
            ),
        ]
    )
    instance = {
        "WORK_ELIGIBLE_INDICATOR": "11",
        "RELATIONSHIP_HOH": "1",
        "DATE_OF_BIRTH": "20200101",
        "RPT_MONTH_YEAR": "202010",
    }
    result = deprecate_call(category3.validate__WORK_ELIGIBLE_INDICATOR__HOH__AGE())(
        instance, schema
    )
    assert result.valid is False
    assert result.error_message == (
        "T1: Since Item 1 (work eligible indicator) is 11 and Item 3 (Age) is less than 19, "
        "then Item 2 (relationship w/ head of household) must not be 1."
    )
    assert result.field_names == [
        "WORK_ELIGIBLE_INDICATOR",
        "RELATIONSHIP_HOH",
        "DATE_OF_BIRTH",
    ]
    assert result.deprecated is True

    instance["DATE_OF_BIRTH"] = "19950101"
    result = category3.validate__WORK_ELIGIBLE_INDICATOR__HOH__AGE()(instance, schema)
    assert result.valid is True
    assert result.error_message is None
    assert result.field_names == [
        "WORK_ELIGIBLE_INDICATOR",
        "RELATIONSHIP_HOH",
        "DATE_OF_BIRTH",
    ]
    assert result.deprecated is False


@pytest.mark.parametrize(
    "condition_val, result_val, exp_result, exp_message, exp_fields",
    [
        (1, 1, True, None, ["TestField3", "TestField1"]),  # condition fails, valid
        (
            10,
            1,
            True,
            None,
            ["TestField1", "TestField3"],
        ),  # condition pass, result pass
        # condition pass, result fail
        (
            10,
            20,
            False,
            "Since Item 1 (test1) is 10, then Item 3 (test3) 20 must be less than 10",
            ["TestField1", "TestField3"],
        ),
    ],
)
def test_deprecate_ifThenAlso(
    condition_val, result_val, exp_result, exp_message, exp_fields
):
    """Test deprecate ifThenAlso validator error messages."""
    schema = TanfDataReportSchema(
        fields=[
            Field(
                item="1",
                name="TestField1",
                friendly_name="test1",
                type=FieldType.NUMERIC,
                startIndex=0,
                endIndex=1,
            ),
            Field(
                item="2",
                name="TestField2",
                friendly_name="test2",
                type=FieldType.NUMERIC,
                startIndex=1,
                endIndex=2,
            ),
            Field(
                item="3",
                name="TestField3",
                friendly_name="test3",
                type=FieldType.NUMERIC,
                startIndex=2,
                endIndex=3,
            ),
        ]
    )
    instance = {
        "TestField1": condition_val,
        "TestField2": 1,
        "TestField3": result_val,
    }
    _validator = deprecate_call(
        category3.ifThenAlso(
            condition_field_name="TestField1",
            condition_function=category3.isEqual(10),
            result_field_name="TestField3",
            result_function=category3.isLessThan(10),
        )
    )
    result = _validator(instance, schema)
    assert result.valid == exp_result
    assert result.error_message == exp_message
    assert result.field_names == exp_fields
    assert result.deprecated is True
