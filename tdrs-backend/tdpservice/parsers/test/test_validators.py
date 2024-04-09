"""Tests for generic validator functions."""

import pytest
import logging
from datetime import date
from .. import validators
from ..case_consistency_validator import CaseConsistencyValidator
from .. import schema_defs, util
from ..row_schema import RowSchema
from tdpservice.parsers.test.factories import TanfT1Factory, TanfT2Factory, TanfT3Factory, TanfT5Factory, TanfT6Factory

from tdpservice.parsers.test.factories import SSPM5Factory

logger = logging.getLogger(__name__)

@pytest.mark.parametrize("value,length", [
    (None, 0),
    (None, 10),
    ('     ', 5),
    ('###', 3),
    ('', 0),
    ('', 10),
])
def test_value_is_empty_returns_true(value, length):
    """Test value_is_empty returns valid."""
    result = validators.value_is_empty(value, length)
    assert result is True


@pytest.mark.parametrize("value,length", [
    (0, 1),
    (1, 1),
    (10, 2),
    ('0', 1),
    ('0000', 4),
    ('1    ', 5),
    ('##3', 3),
])
def test_value_is_empty_returns_false(value, length):
    """Test value_is_empty returns invalid."""
    result = validators.value_is_empty(value, length)
    assert result is False


def test_or_validators():
    """Test `or_validators` gives a valid result."""
    value = "2"
    validator = validators.or_validators(validators.matches(("2")), validators.matches(("3")))
    assert validator(value, RowSchema(), "friendly_name", "item_no") == (True, None)
    assert validator("3", RowSchema(), "friendly_name", "item_no") == (True, None)
    assert validator("5", RowSchema(), "friendly_name", "item_no") == (False,
                                                                       "T1: 5 does not match 2. or T1: 5 does not "
                                                                       "match 3.")

    validator = validators.or_validators(validators.matches(("2")), validators.matches(("3")),
                                         validators.matches(("4")))
    assert validator(value, RowSchema(), "friendly_name", "item_no") == (True, None)

    value = "3"
    assert validator(value, RowSchema(), "friendly_name", "item_no") == (True, None)

    value = "4"
    assert validator(value, RowSchema(), "friendly_name", "item_no") == (True, None)

    value = "5"
    assert validator(value, RowSchema(), "friendly_name", "item_no") == (False,
                                                                         "T1: 5 does not match 2. or T1: 5 does not "
                                                                         "match 3. or T1: 5 does not match 4.")

    validator = validators.or_validators(validators.matches((2)), validators.matches((3)), validators.isLargerThan(4))
    assert validator(5, RowSchema(), "friendly_name", "item_no") == (True, None)
    assert validator(1, RowSchema(), "friendly_name", "item_no") == (False,
                                                                     "T1: 1 does not match 2. or T1: 1 does not "
                                                                     "match 3. or T1: 1 is not larger than 4.")

def test_if_validators():
    """Test `if_then_validator` gives a valid result."""
    value = {"Field1": "1", "Field2": "2"}
    validator = validators.if_then_validator(
          condition_field_name="Field1", condition_function=validators.matches('1'),
          result_field_name="Field2", result_function=validators.matches('2'),
      )
    assert validator(value, RowSchema()) == (True, None, ['Field1', 'Field2'])

    validator = validator = validators.if_then_validator(
          condition_field_name="Field1", condition_function=validators.matches('1'),
          result_field_name="Field2", result_function=validators.matches('1'),
      )
    result = validator(value, RowSchema())
    assert result == (False, 'if Field1 :1 validator1 passed then Field2 T1: 2 does not match 1.', ['Field1', 'Field2'])


def test_and_validators():
    """Test `and_validators` gives a valid result."""
    validator = validators.and_validators(validators.isLargerThan(2), validators.isLargerThan(0))
    assert validator(1, RowSchema(), "friendly_name", "item_no") == (False, 'T1: 1 is not larger than 2.')
    assert validator(3, RowSchema(), "friendly_name", "item_no") == (True, None)


def test_validate__FAM_AFF__SSN():
    """Test `validate__FAM_AFF__SSN` gives a valid result."""
    instance = {
        'FAMILY_AFFILIATION': 2,
        'CITIZENSHIP_STATUS': 1,
        'SSN': '0'*9,
    }
    result = validators.validate__FAM_AFF__SSN()(instance, RowSchema())
    assert result == (False,
                      'T1: If FAMILY_AFFILIATION ==2 and CITIZENSHIP_STATUS==1 or 2, ' +
                      'then SSN != 000000000 -- 999999999.',
                      ['FAMILY_AFFILIATION', 'CITIZENSHIP_STATUS', 'SSN'])
    instance['SSN'] = '1'*8 + '0'
    result = validators.validate__FAM_AFF__SSN()(instance, RowSchema())
    assert result == (True, None, ['FAMILY_AFFILIATION', 'CITIZENSHIP_STATUS', 'SSN'])

def test_quarterIsValid():
    """Test `quarterIsValid`."""
    value = "20204"
    val = validators.quarterIsValid()
    result = val(value)
    assert result == (True, None)

    value = "20205"
    result = val(value, RowSchema(), "friendly_name", "item_no")
    assert result == (False, "T1: 5 is not a valid quarter.")

def test_validateSSN():
    """Test `validateSSN`."""
    value = "123456789"
    val = validators.validateSSN()
    result = val(value)
    assert result == (True, None)

    value = "111111111"
    options = [str(i) * 9 for i in range(0, 10)]
    result = val(value, RowSchema(), "friendly_name", "item_no")
    assert result == (False, f"T1: {value} is in {options}.")

def test_validateRace():
    """Test `validateRace`."""
    value = 1
    val = validators.validateRace()
    result = val(value)
    assert result == (True, None)

    value = 3
    result = val(value, RowSchema(), "friendly_name", "item_no")
    assert result == (False, f"T1: {value} is not greater than or equal to 0 or smaller than or equal to 2.")

def test_validateRptMonthYear():
    """Test `validateRptMonthYear`."""
    value = "T1202012"
    val = validators.validateRptMonthYear()
    result = val(value)
    assert result == (True, None)

    value = "T1      "
    result = val(value, RowSchema(), "friendly_name", "item_no")
    assert result == (False, f"T1: The value: {value[2:8]}, does not follow the YYYYMM format for Reporting Year and "
                      "Month.")

    value = "T1189912"
    result = val(value, RowSchema(), "friendly_name", "item_no")
    assert result == (False, f"T1: The value: {value[2:8]}, does not follow the YYYYMM format for Reporting Year and "
                      "Month.")

    value = "T1202013"
    result = val(value, RowSchema(), "friendly_name", "item_no")
    assert result == (False, f"T1: The value: {value[2:8]}, does not follow the YYYYMM format for Reporting Year and "
                      "Month.")

def test_matches_returns_valid():
    """Test `matches` gives a valid result."""
    value = 'TEST'

    validator = validators.matches('TEST')
    is_valid, error = validator(value)

    assert is_valid is True
    assert error is None


def test_matches_returns_invalid():
    """Test `matches` gives an invalid result."""
    value = 'TEST'

    validator = validators.matches('test')
    is_valid, error = validator(value, RowSchema(), "friendly_name", "item_no")

    assert is_valid is False
    assert error == 'T1: TEST does not match test.'


def test_oneOf_returns_valid():
    """Test `oneOf` gives a valid result."""
    value = 17
    options = [17, 24, 36]

    validator = validators.oneOf(options)
    is_valid, error = validator(value)

    assert is_valid is True
    assert error is None


def test_oneOf_returns_invalid():
    """Test `oneOf` gives an invalid result."""
    value = 64
    options = [17, 24, 36]

    validator = validators.oneOf(options)
    is_valid, error = validator(value, RowSchema(), "friendly_name", "item_no")

    assert is_valid is False
    assert error == 'T1: 64 is not in [17, 24, 36].'


def test_between_returns_valid():
    """Test `between` gives a valid result for integers."""
    value = 47

    validator = validators.between(3, 400)
    is_valid, error = validator(value)

    assert is_valid is True
    assert error is None


def test_between_returns_valid_for_string_value():
    """Test `between` gives a valid result for strings."""
    value = '047'

    validator = validators.between(3, 400)
    is_valid, error = validator(value)

    assert is_valid is True
    assert error is None


def test_between_returns_invalid():
    """Test `between` gives an invalid result for integers."""
    value = 47

    validator = validators.between(48, 400)
    is_valid, error = validator(value, RowSchema(), "friendly_name", "item_no")

    assert is_valid is False
    assert error == 'T1: 47 is not between 48 and 400.'


def test_date_month_is_valid_returns_valid():
    """Test `dateMonthIsValid` gives a valid result."""
    value = '20191027'
    validator = validators.dateMonthIsValid()
    is_valid, error = validator(value)
    assert is_valid is True
    assert error is None


def test_date_month_is_valid_returns_invalid():
    """Test `dateMonthIsValid` gives an invalid result."""
    value = '20191327'
    validator = validators.dateMonthIsValid()
    is_valid, error = validator(value, RowSchema(), "friendly_name", "item_no")
    assert is_valid is False
    assert error == 'T1: 13 is not a valid month.'


def test_date_day_is_valid_returns_valid():
    """Test `dateDayIsValid` gives a valid result."""
    value = '20191027'
    validator = validators.dateDayIsValid()
    is_valid, error = validator(value)
    assert is_valid is True
    assert error is None


def test_date_day_is_valid_returns_invalid():
    """Test `dateDayIsValid` gives an invalid result."""
    value = '20191132'
    validator = validators.dateDayIsValid()
    is_valid, error = validator(value, RowSchema(), "friendly_name", "item_no")
    assert is_valid is False
    assert error == 'T1: 32 is not a valid day.'


def test_olderThan():
    """Test `olderThan`."""
    min_age = 18
    value = 19830223
    validator = validators.olderThan(min_age)
    assert validator(value) == (True, None)

    value = 20240101
    result = validator(value, RowSchema(), "friendly_name", "item_no")
    assert result == (False, (f"T1: {str(value)[:4]} must be less than or equal to {date.today().year - min_age} "
                              "to meet the minimum age requirement."))


def test_dateYearIsLargerThan():
    """Test `dateYearIsLargerThan`."""
    year = 1900
    value = 19830223
    validator = validators.dateYearIsLargerThan(year)
    assert validator(value) == (True, None)

    value = 18990101
    assert validator(value, RowSchema(), "friendly_name", "item_no") == (False,
                                                                         f"T1: Year {str(value)[:4]} must be larger "
                                                                         f"than {year}.")


def test_between_returns_invalid_for_string_value():
    """Test `between` gives an invalid result for strings."""
    value = '047'

    validator = validators.between(100, 400)
    is_valid, error = validator(value, RowSchema(), "friendly_name", "item_no")

    assert is_valid is False
    assert error == 'T1: 047 is not between 100 and 400.'


def test_recordHasLength_returns_valid():
    """Test `recordHasLength` gives a valid result."""
    value = 'abcd123'

    validator = validators.recordHasLength(7)
    is_valid, error = validator(value)

    assert is_valid is True
    assert error is None


def test_recordHasLength_returns_invalid():
    """Test `recordHasLength` gives an invalid result."""
    value = 'abcd123'

    validator = validators.recordHasLength(22)
    is_valid, error = validator(value, RowSchema(), "friendly_name", "item_no")

    assert is_valid is False
    assert error == 'T1 record length is 7 characters but must be 22.'


def test_intHasLength_returns_valid():
    """Test `intHasLength` gives a valid result."""
    value = '123'

    validator = validators.intHasLength(3)
    is_valid, error = validator(value)

    assert is_valid is True
    assert error is None


def test_intHasLength_returns_invalid():
    """Test `intHasLength` gives an invalid result."""
    value = '1a3'

    validator = validators.intHasLength(22)
    is_valid, error = validator(value, RowSchema(), "friendly_name", "item_no")

    assert is_valid is False
    assert error == 'T1: 1a3 does not have exactly 22 digits.'


def test_contains_returns_valid():
    """Test `contains` gives a valid result."""
    value = '12345abcde'

    validator = validators.contains('2345')
    is_valid, error = validator(value)

    assert is_valid is True
    assert error is None


def test_contains_returns_invalid():
    """Test `contains` gives an invalid result."""
    value = '12345abcde'

    validator = validators.contains('6789')
    is_valid, error = validator(value, RowSchema(), "friendly_name", "item_no")

    assert is_valid is False
    assert error == 'T1: 12345abcde does not contain 6789.'


def test_startsWith_returns_valid():
    """Test `startsWith` gives a valid result."""
    value = '12345abcde'

    validator = validators.startsWith('1234')
    is_valid, error = validator(value)

    assert is_valid is True
    assert error is None


def test_startsWith_returns_invalid():
    """Test `startsWith` gives an invalid result."""
    value = '12345abcde'

    validator = validators.startsWith('abc')
    is_valid, error = validator(value, RowSchema(), "friendly_name", "item_no")

    assert is_valid is False
    assert error == 'T1: 12345abcde does not start with abc.'


def test_notEmpty_returns_valid_full_string():
    """Test `notEmpty` gives a valid result for a full string."""
    value = '1        '

    validator = validators.notEmpty()
    is_valid, error = validator(value)

    assert is_valid is True
    assert error is None


def test_notEmpty_returns_invalid_full_string():
    """Test `notEmpty` gives an invalid result for a full string."""
    value = '         '

    validator = validators.notEmpty()
    is_valid, error = validator(value, RowSchema(), "friendly_name", "item_no")

    assert is_valid is False
    assert error == 'T1:           contains blanks between positions 0 and 9.'


def test_notEmpty_returns_valid_substring():
    """Test `notEmpty` gives a valid result for a partial string."""
    value = '11122333'

    validator = validators.notEmpty(start=3, end=5)
    is_valid, error = validator(value)

    assert is_valid is True
    assert error is None


def test_notEmpty_returns_invalid_substring():
    """Test `notEmpty` gives an invalid result for a partial string."""
    value = '111  333'

    validator = validators.notEmpty(start=3, end=5)
    is_valid, error = validator(value, RowSchema(), "friendly_name", "item_no")

    assert is_valid is False
    assert error == "T1: 111  333 contains blanks between positions 3 and 5."


def test_notEmpty_returns_nonexistent_substring():
    """Test `notEmpty` gives an invalid result for a nonexistent substring."""
    value = '111  333'

    validator = validators.notEmpty(start=10, end=12)
    is_valid, error = validator(value, RowSchema(), "friendly_name", "item_no")

    assert is_valid is False
    assert error == "T1: 111  333 contains blanks between positions 10 and 12."

@pytest.mark.usefixtures('db')
class TestCat3ValidatorsBase:
    """A base test class for tests that evaluate category three validators."""

    @pytest.fixture
    def record(self):
        """Record instance that returns a valid Section 1 record.

        This fixture must be overridden in all child classes.
        """
        raise NotImplementedError()


class TestT1Cat3Validators(TestCat3ValidatorsBase):
    """Test category three validators for TANF T1 records."""

    @pytest.fixture
    def record(self):
        """Override default record with TANF T1 record."""
        return TanfT1Factory.create()

    def test_validate_food_stamps(self, record):
        """Test cat3 validator for food stamps."""
        val = validators.if_then_validator(
          condition_field_name='RECEIVES_FOOD_STAMPS', condition_function=validators.matches(1),
          result_field_name='AMT_FOOD_STAMP_ASSISTANCE', result_function=validators.isLargerThan(0),
        )
        record.RECEIVES_FOOD_STAMPS = 1
        record.AMT_FOOD_STAMP_ASSISTANCE = 1
        result = val(record, RowSchema())
        assert result == (True, None, ['RECEIVES_FOOD_STAMPS', 'AMT_FOOD_STAMP_ASSISTANCE'])

        record.AMT_FOOD_STAMP_ASSISTANCE = 0
        result = val(record, RowSchema())
        assert result[0] is False

    def test_validate_subsidized_child_care(self, record):
        """Test cat3 validator for subsidized child care."""
        val = validators.if_then_validator(
          condition_field_name='RECEIVES_SUB_CC', condition_function=validators.notMatches(3),
          result_field_name='AMT_SUB_CC', result_function=validators.isLargerThan(0),
        )
        record.RECEIVES_SUB_CC = 4
        record.AMT_SUB_CC = 1
        result = val(record, RowSchema())
        assert result == (True, None, ['RECEIVES_SUB_CC', 'AMT_SUB_CC'])

        record.RECEIVES_SUB_CC = 4
        record.AMT_SUB_CC = 0
        result = val(record, RowSchema())
        assert result[0] is False

    def test_validate_cash_amount_and_nbr_months(self, record):
        """Test cat3 validator for cash amount and number of months."""
        val = validators.if_then_validator(
          condition_field_name='CASH_AMOUNT', condition_function=validators.isLargerThan(0),
          result_field_name='NBR_MONTHS', result_function=validators.isLargerThan(0),
        )
        result = val(record, RowSchema())
        assert result == (True, None, ['CASH_AMOUNT', 'NBR_MONTHS'])

        record.CASH_AMOUNT = 1
        record.NBR_MONTHS = -1
        result = val(record, RowSchema())
        assert result[0] is False

    def test_validate_child_care(self, record):
        """Test cat3 validator for child care."""
        val = validators.if_then_validator(
          condition_field_name='CC_AMOUNT', condition_function=validators.isLargerThan(0),
          result_field_name='CHILDREN_COVERED', result_function=validators.isLargerThan(0),
        )
        result = val(record, RowSchema())
        assert result == (True, None, ['CC_AMOUNT', 'CHILDREN_COVERED'])

        record.CC_AMOUNT = 1
        record.CHILDREN_COVERED = -1
        result = val(record, RowSchema())
        assert result[0] is False

        val = validators.if_then_validator(
          condition_field_name='CC_AMOUNT', condition_function=validators.isLargerThan(0),
          result_field_name='CC_NBR_MONTHS', result_function=validators.isLargerThan(0),
        )
        record.CC_AMOUNT = 10
        record.CC_NBR_MONTHS = -1
        result = val(record, RowSchema())
        assert result[0] is False

    def test_validate_transportation(self, record):
        """Test cat3 validator for transportation."""
        val = validators.if_then_validator(
          condition_field_name='TRANSP_AMOUNT', condition_function=validators.isLargerThan(0),
          result_field_name='TRANSP_NBR_MONTHS', result_function=validators.isLargerThan(0),
        )
        result = val(record, RowSchema())
        assert result == (True, None, ['TRANSP_AMOUNT', 'TRANSP_NBR_MONTHS'])

        record.TRANSP_AMOUNT = 1
        record.TRANSP_NBR_MONTHS = -1
        result = val(record, RowSchema())
        assert result[0] is False

    def test_validate_transitional_services(self, record):
        """Test cat3 validator for transitional services."""
        val = validators.if_then_validator(
          condition_field_name='TRANSITION_SERVICES_AMOUNT', condition_function=validators.isLargerThan(0),
          result_field_name='TRANSITION_NBR_MONTHS', result_function=validators.isLargerThan(0),
        )
        result = val(record, RowSchema())
        assert result == (True, None, ['TRANSITION_SERVICES_AMOUNT', 'TRANSITION_NBR_MONTHS'])

        record.TRANSITION_SERVICES_AMOUNT = 1
        record.TRANSITION_NBR_MONTHS = -1
        result = val(record, RowSchema())
        assert result[0] is False

    def test_validate_other(self, record):
        """Test cat3 validator for other."""
        val = validators.if_then_validator(
          condition_field_name='OTHER_AMOUNT', condition_function=validators.isLargerThan(0),
          result_field_name='OTHER_NBR_MONTHS', result_function=validators.isLargerThan(0),
        )
        result = val(record, RowSchema())
        assert result == (True, None, ['OTHER_AMOUNT', 'OTHER_NBR_MONTHS'])

        record.OTHER_AMOUNT = 1
        record.OTHER_NBR_MONTHS = -1
        result = val(record, RowSchema())
        assert result[0] is False

    def test_validate_reasons_for_amount_of_assistance_reductions(self, record):
        """Test cat3 validator for assistance reductions."""
        val = validators.if_then_validator(
          condition_field_name='SANC_REDUCTION_AMT', condition_function=validators.isLargerThan(0),
          result_field_name='WORK_REQ_SANCTION', result_function=validators.oneOf((1, 2)),
        )
        record.SANC_REDUCTION_AMT = 1
        result = val(record, RowSchema())
        assert result == (True, None, ['SANC_REDUCTION_AMT', 'WORK_REQ_SANCTION'])

        record.SANC_REDUCTION_AMT = 10
        record.WORK_REQ_SANCTION = -1
        result = val(record, RowSchema())
        assert result[0] is False

    def test_validate_sum(self, record):
        """Test cat3 validator for sum of cash fields."""
        val = validators.sumIsLarger(("AMT_FOOD_STAMP_ASSISTANCE", "AMT_SUB_CC", "CC_AMOUNT", "TRANSP_AMOUNT",
                                      "TRANSITION_SERVICES_AMOUNT", "OTHER_AMOUNT"), 0)
        result = val(record, RowSchema())
        assert result == (True, None, ['AMT_FOOD_STAMP_ASSISTANCE', 'AMT_SUB_CC', 'CC_AMOUNT', 'TRANSP_AMOUNT',
                                       'TRANSITION_SERVICES_AMOUNT', 'OTHER_AMOUNT'])

        record.AMT_FOOD_STAMP_ASSISTANCE = 0
        record.AMT_SUB_CC = 0
        record.CC_AMOUNT = 0
        record.TRANSP_AMOUNT = 0
        record.TRANSITION_SERVICES_AMOUNT = 0
        record.OTHER_AMOUNT = 0
        result = val(record, RowSchema())
        assert result[0] is False


class TestT2Cat3Validators(TestCat3ValidatorsBase):
    """Test category three validators for TANF T2 records."""

    @pytest.fixture
    def record(self):
        """Override default record with TANF T2 record."""
        return TanfT2Factory.create()

    def test_validate_ssn(self, record):
        """Test cat3 validator for social security number."""
        val = validators.if_then_validator(
                  condition_field_name='FAMILY_AFFILIATION', condition_function=validators.oneOf((1, 2)),
                  result_field_name='SSN', result_function=validators.notOneOf(("000000000", "111111111", "222222222",
                                                                                "333333333", "444444444", "555555555",
                                                                                "666666666", "777777777", "888888888",
                                                                                "999999999")),
            )
        record.SSN = "999989999"
        record.FAMILY_AFFILIATION = 1
        result = val(record, RowSchema())
        assert result == (True, None, ['FAMILY_AFFILIATION', 'SSN'])

        record.FAMILY_AFFILIATION = 1
        record.SSN = "999999999"
        result = val(record, RowSchema())
        assert result[0] is False

    def test_validate_race_ethnicity(self, record):
        """Test cat3 validator for race/ethnicity."""
        races = ["RACE_HISPANIC", "RACE_AMER_INDIAN", "RACE_ASIAN", "RACE_BLACK", "RACE_HAWAIIAN", "RACE_WHITE"]
        record.FAMILY_AFFILIATION = 1
        for race in races:
            val = validators.if_then_validator(
                  condition_field_name='FAMILY_AFFILIATION', condition_function=validators.oneOf((1, 2, 3)),
                  result_field_name=race, result_function=validators.isInLimits(1, 2),
            )
            result = val(record, RowSchema())
            assert result == (True, None, ['FAMILY_AFFILIATION', race])

        record.FAMILY_AFFILIATION = 0
        for race in races:
            val = validators.if_then_validator(
                  condition_field_name='FAMILY_AFFILIATION', condition_function=validators.oneOf((1, 2, 3)),
                  result_field_name=race, result_function=validators.isInLimits(1, 2)
            )
            result = val(record, RowSchema())
            assert result == (True, None, ['FAMILY_AFFILIATION', race])

    def test_validate_marital_status(self, record):
        """Test cat3 validator for marital status."""
        val = validators.if_then_validator(
                        condition_field_name='FAMILY_AFFILIATION', condition_function=validators.isInLimits(1, 3),
                        result_field_name='MARITAL_STATUS', result_function=validators.isInLimits(1, 5),
                    )
        record.FAMILY_AFFILIATION = 1
        result = val(record, RowSchema())
        assert result == (True, None, ['FAMILY_AFFILIATION', 'MARITAL_STATUS'])

        record.FAMILY_AFFILIATION = 3
        record.MARITAL_STATUS = 0
        result = val(record, RowSchema())
        assert result[0] is False

    def test_validate_parent_with_minor(self, record):
        """Test cat3 validator for parent with a minor child."""
        val = validators.if_then_validator(
                        condition_field_name='FAMILY_AFFILIATION', condition_function=validators.isInLimits(1, 3),
                        result_field_name='PARENT_MINOR_CHILD', result_function=validators.isInLimits(1, 3),
                    )
        result = val(record, RowSchema())
        assert result == (True, None, ['FAMILY_AFFILIATION', 'PARENT_MINOR_CHILD'])

        record.PARENT_MINOR_CHILD = 0
        result = val(record, RowSchema())
        assert result[0] is False

    def test_validate_education_level(self, record):
        """Test cat3 validator for education level."""
        val = validators.if_then_validator(
                      condition_field_name='FAMILY_AFFILIATION', condition_function=validators.oneOf((1, 2, 3)),
                      result_field_name='EDUCATION_LEVEL', result_function=validators.oneOf(("01", "02", "03", "04",
                                                                                             "05", "06", "07", "08",
                                                                                             "09", "10", "11", "12",
                                                                                             "13", "14", "15", "16",
                                                                                             "98", "99")),
                )
        record.FAMILY_AFFILIATION = 3
        result = val(record, RowSchema())
        assert result == (True, None, ['FAMILY_AFFILIATION', 'EDUCATION_LEVEL'])

        record.FAMILY_AFFILIATION = 1
        record.EDUCATION_LEVEL = "00"
        result = val(record, RowSchema())
        assert result[0] is False

    def test_validate_citizenship(self, record):
        """Test cat3 validator for citizenship."""
        val = validators.if_then_validator(
                        condition_field_name='FAMILY_AFFILIATION', condition_function=validators.matches(1),
                        result_field_name='CITIZENSHIP_STATUS', result_function=validators.oneOf((1, 2)),
                    )
        record.FAMILY_AFFILIATION = 0
        result = val(record, RowSchema())
        assert result == (True, None, ['FAMILY_AFFILIATION', 'CITIZENSHIP_STATUS'])

        record.FAMILY_AFFILIATION = 1
        record.CITIZENSHIP_STATUS = 0
        result = val(record, RowSchema())
        assert result[0] is False

    def test_validate_cooperation_with_child_support(self, record):
        """Test cat3 validator for cooperation with child support."""
        val = validators.if_then_validator(
                        condition_field_name='FAMILY_AFFILIATION', condition_function=validators.isInLimits(1, 3),
                        result_field_name='COOPERATION_CHILD_SUPPORT', result_function=validators.oneOf((1, 2, 9)),
                    )
        record.FAMILY_AFFILIATION = 0
        result = val(record, RowSchema())
        assert result == (True, None, ['FAMILY_AFFILIATION', 'COOPERATION_CHILD_SUPPORT'])

        record.FAMILY_AFFILIATION = 1
        record.COOPERATION_CHILD_SUPPORT = 0
        result = val(record, RowSchema())
        assert result[0] is False

    def test_validate_months_federal_time_limit(self, record):
        """Test cat3 validator for federal time limit."""
        val = validators.validate__FAM_AFF__HOH__Fed_Time()
        record.FAMILY_AFFILIATION = 0
        result = val(record, RowSchema())
        assert result == (True, None, ['FAMILY_AFFILIATION', 'RELATIONSHIP_HOH', 'MONTHS_FED_TIME_LIMIT'])

        record.FAMILY_AFFILIATION = 1
        record.MONTHS_FED_TIME_LIMIT = "000"
        record.RELATIONSHIP_HOH = "01"
        result = val(record, RowSchema())
        assert result[0] is False

    def test_validate_employment_status(self, record):
        """Test cat3 validator for employment status."""
        val = validators.if_then_validator(
                        condition_field_name='FAMILY_AFFILIATION', condition_function=validators.isInLimits(1, 3),
                        result_field_name='EMPLOYMENT_STATUS', result_function=validators.isInLimits(1, 3),
                    )
        record.FAMILY_AFFILIATION = 0
        result = val(record, RowSchema())
        assert result == (True, None, ['FAMILY_AFFILIATION', 'EMPLOYMENT_STATUS'])

        record.FAMILY_AFFILIATION = 3
        record.EMPLOYMENT_STATUS = 4
        result = val(record, RowSchema())
        assert result[0] is False

    def test_validate_work_eligible_indicator(self, record):
        """Test cat3 validator for work eligibility."""
        val = validators.if_then_validator(
                        condition_field_name='FAMILY_AFFILIATION', condition_function=validators.oneOf((1, 2)),
                        result_field_name='WORK_ELIGIBLE_INDICATOR', result_function=validators.or_validators(
                            validators.isInStringRange(1, 9),
                            validators.matches('12')
                        ),
                    )
        record.FAMILY_AFFILIATION = 0
        result = val(record, RowSchema())
        assert result == (True, None, ['FAMILY_AFFILIATION', 'WORK_ELIGIBLE_INDICATOR'])

        record.FAMILY_AFFILIATION = 1
        record.WORK_ELIGIBLE_INDICATOR = "00"
        result = val(record, RowSchema())
        assert result[0] is False

    def test_validate_work_participation(self, record):
        """Test cat3 validator for work participation."""
        val = validators.if_then_validator(
                        condition_field_name='FAMILY_AFFILIATION', condition_function=validators.oneOf((1, 2)),
                        result_field_name='WORK_PART_STATUS', result_function=validators.oneOf(['01', '02', '05', '07',
                                                                                                '09', '15', '17', '18',
                                                                                                '19', '99']),
                    )
        record.FAMILY_AFFILIATION = 0
        result = val(record, RowSchema())
        assert result == (True, None, ['FAMILY_AFFILIATION', 'WORK_PART_STATUS'])

        record.FAMILY_AFFILIATION = 2
        record.WORK_PART_STATUS = "04"
        result = val(record, RowSchema())
        assert result[0] is False

        val = validators.if_then_validator(
                        condition_field_name='WORK_ELIGIBLE_INDICATOR',
                        condition_function=validators.isInStringRange(1, 5),
                        result_field_name='WORK_PART_STATUS',
                        result_function=validators.notMatches('99'),
                    )
        record.WORK_PART_STATUS = "99"
        record.WORK_ELIGIBLE_INDICATOR = "01"
        result = val(record, RowSchema())
        assert result[0] is False


class TestT3Cat3Validators(TestCat3ValidatorsBase):
    """Test category three validators for TANF T3 records."""

    @pytest.fixture
    def record(self):
        """Override default record with TANF T3 record."""
        return TanfT3Factory.create()

    def test_validate_ssn(self, record):
        """Test cat3 validator for relationship to head of household."""
        record.FAMILY_AFFILIATION = 1
        record.SSN = "199199991"
        val = validators.if_then_validator(
                  condition_field_name='FAMILY_AFFILIATION', condition_function=validators.matches(1),
                  result_field_name='SSN', result_function=validators.notOneOf(("999999999", "000000000")),
            )
        result = val(record, RowSchema())
        assert result == (True, None, ['FAMILY_AFFILIATION', 'SSN'])

        record.FAMILY_AFFILIATION = 1
        record.SSN = "999999999"
        result = val(record, RowSchema())
        assert result[0] is False

    def test_validate_t3_race_ethnicity(self, record):
        """Test cat3 validator for race/ethnicity."""
        races = ["RACE_HISPANIC", "RACE_AMER_INDIAN", "RACE_ASIAN", "RACE_BLACK", "RACE_HAWAIIAN", "RACE_WHITE"]
        record.FAMILY_AFFILIATION = 1
        for race in races:
            val = validators.if_then_validator(
                  condition_field_name='FAMILY_AFFILIATION', condition_function=validators.oneOf((1, 2)),
                  result_field_name=race, result_function=validators.oneOf((1, 2)),
            )
            result = val(record, RowSchema())
            assert result == (True, None, ['FAMILY_AFFILIATION', race])

        record.FAMILY_AFFILIATION = 0
        for race in races:
            val = validators.if_then_validator(
                  condition_field_name='FAMILY_AFFILIATION', condition_function=validators.oneOf((1, 2)),
                  result_field_name=race, result_function=validators.oneOf((1, 2)),
            )
            result = val(record, RowSchema())
            assert result == (True, None, ['FAMILY_AFFILIATION', race])

    def test_validate_relationship_hoh(self, record):
        """Test cat3 validator for relationship to head of household."""
        val = validators.if_then_validator(
                  condition_field_name='FAMILY_AFFILIATION', condition_function=validators.oneOf((1, 2)),
                  result_field_name='RELATIONSHIP_HOH', result_function=validators.isInStringRange(4, 9),
            )
        record.FAMILY_AFFILIATION = 0
        record.RELATIONSHIP_HOH = "04"
        result = val(record, RowSchema())
        assert result == (True, None, ['FAMILY_AFFILIATION', 'RELATIONSHIP_HOH'])

        record.FAMILY_AFFILIATION = 1
        record.RELATIONSHIP_HOH = "01"
        result = val(record, RowSchema())
        assert result[0] is False

    def test_validate_t3_education_level(self, record):
        """Test cat3 validator for education level."""
        val = validators.if_then_validator(
                  condition_field_name='FAMILY_AFFILIATION', condition_function=validators.matches(1),
                  result_field_name='EDUCATION_LEVEL', result_function=validators.notMatches("99"),
            )
        record.FAMILY_AFFILIATION = 1
        result = val(record, RowSchema())
        assert result == (True, None, ['FAMILY_AFFILIATION', 'EDUCATION_LEVEL'])

        record.FAMILY_AFFILIATION = 1
        record.EDUCATION_LEVEL = "99"
        result = val(record, RowSchema())
        assert result[0] is False

    def test_validate_t3_citizenship(self, record):
        """Test cat3 validator for citizenship."""
        val = validators.if_then_validator(
                  condition_field_name='FAMILY_AFFILIATION', condition_function=validators.matches(1),
                  result_field_name='CITIZENSHIP_STATUS', result_function=validators.oneOf((1, 2)),
            )
        record.FAMILY_AFFILIATION = 1
        result = val(record, RowSchema())
        assert result == (True, None, ['FAMILY_AFFILIATION', 'CITIZENSHIP_STATUS'])

        record.FAMILY_AFFILIATION = 1
        record.CITIZENSHIP_STATUS = 3
        result = val(record, RowSchema())
        assert result[0] is False

        val = validators.if_then_validator(
                  condition_field_name='FAMILY_AFFILIATION', condition_function=validators.matches(2),
                  result_field_name='CITIZENSHIP_STATUS', result_function=validators.oneOf((1, 2, 9)),
            )
        record.FAMILY_AFFILIATION = 2
        record.CITIZENSHIP_STATUS = 3
        result = val(record, RowSchema())
        assert result[0] is False


class TestT5Cat3Validators(TestCat3ValidatorsBase):
    """Test category three validators for TANF T5 records."""

    @pytest.fixture
    def record(self):
        """Override default record with TANF T5 record."""
        return TanfT5Factory.create()

    def test_validate_ssn(self, record):
        """Test cat3 validator for SSN."""
        val = validators.if_then_validator(
                  condition_field_name='FAMILY_AFFILIATION', condition_function=validators.notMatches(1),
                  result_field_name='SSN', result_function=validators.isNumber()
                  )

        result = val(record, RowSchema())
        assert result == (True, None, ['FAMILY_AFFILIATION', 'SSN'])

        record.SSN = "abc"
        record.FAMILY_AFFILIATION = 2

        result = val(record, RowSchema())
        assert result[0] is False

    def test_validate_ssn_citizenship(self, record):
        """Test cat3 validator for SSN/citizenship."""
        val = validators.validate__FAM_AFF__SSN()

        result = val(record, RowSchema())
        assert result == (True, None, ['FAMILY_AFFILIATION', 'CITIZENSHIP_STATUS', 'SSN'])

        record.FAMILY_AFFILIATION = 2
        record.SSN = "000000000"

        result = val(record, RowSchema())
        assert result[0] is False

    def test_validate_race_ethnicity(self, record):
        """Test cat3 validator for race/ethnicity."""
        races = ["RACE_HISPANIC", "RACE_AMER_INDIAN", "RACE_ASIAN", "RACE_BLACK", "RACE_HAWAIIAN", "RACE_WHITE"]
        record.FAMILY_AFFILIATION = 1
        for race in races:
            val = validators.if_then_validator(
                    condition_field_name='FAMILY_AFFILIATION', condition_function=validators.isInLimits(1, 3),
                    result_field_name='RACE_HISPANIC', result_function=validators.isInLimits(1, 2)
                  )
            result = val(record, RowSchema())
            assert result == (True, None, ['FAMILY_AFFILIATION', 'RACE_HISPANIC'])

        record.FAMILY_AFFILIATION = 1
        record.RACE_HISPANIC = 0
        record.RACE_AMER_INDIAN = 0
        record.RACE_ASIAN = 0
        record.RACE_BLACK = 0
        record.RACE_HAWAIIAN = 0
        record.RACE_WHITE = 0
        for race in races:
            val = validators.if_then_validator(
                    condition_field_name='FAMILY_AFFILIATION', condition_function=validators.isInLimits(1, 3),
                    result_field_name=race, result_function=validators.isInLimits(1, 2)
                  )
            result = val(record, RowSchema())
            assert result[0] is False

    def test_validate_marital_status(self, record):
        """Test cat3 validator for marital status."""
        val = validators.if_then_validator(
                    condition_field_name='FAMILY_AFFILIATION', condition_function=validators.isInLimits(1, 3),
                    result_field_name='MARITAL_STATUS', result_function=validators.isInLimits(0, 5)
                  )

        record.FAMILY_AFFILIATION = 0
        result = val(record, RowSchema())
        assert result == (True, None, ['FAMILY_AFFILIATION', 'MARITAL_STATUS'])

        record.FAMILY_AFFILIATION = 2
        record.MARITAL_STATUS = 6

        result = val(record, RowSchema())
        assert result[0] is False

    def test_validate_parent_minor(self, record):
        """Test cat3 validator for parent with minor."""
        val = validators.if_then_validator(
                    condition_field_name='FAMILY_AFFILIATION', condition_function=validators.isInLimits(1, 2),
                    result_field_name='PARENT_MINOR_CHILD', result_function=validators.isInLimits(1, 3)
                  )

        record.FAMILY_AFFILIATION = 0
        result = val(record, RowSchema())
        assert result == (True, None, ['FAMILY_AFFILIATION', 'PARENT_MINOR_CHILD'])

        record.FAMILY_AFFILIATION = 2
        record.PARENT_MINOR_CHILD = 0

        result = val(record, RowSchema())
        assert result[0] is False

    def test_validate_education(self, record):
        """Test cat3 validator for education level."""
        val = validators.if_then_validator(
                  condition_field_name='FAMILY_AFFILIATION', condition_function=validators.isInLimits(1, 3),
                  result_field_name='EDUCATION_LEVEL', result_function=validators.or_validators(
                      validators.isInStringRange(1, 16),
                      validators.isInStringRange(98, 99)
                      )
                  )

        record.FAMILY_AFFILIATION = 0
        result = val(record, RowSchema())
        assert result == (True, None, ['FAMILY_AFFILIATION', 'EDUCATION_LEVEL'])

        record.FAMILY_AFFILIATION = 2
        record.EDUCATION_LEVEL = "0"

        result = val(record, RowSchema())
        assert result[0] is False

    def test_validate_citizenship_status(self, record):
        """Test cat3 validator for citizenship status."""
        val = validators.if_then_validator(
                    condition_field_name='FAMILY_AFFILIATION', condition_function=validators.matches(1),
                    result_field_name='CITIZENSHIP_STATUS', result_function=validators.isInLimits(1, 2)
                  )

        record.FAMILY_AFFILIATION = 0
        result = val(record, RowSchema())
        assert result == (True, None, ['FAMILY_AFFILIATION', 'CITIZENSHIP_STATUS'])

        record.FAMILY_AFFILIATION = 1
        record.CITIZENSHIP_STATUS = 0

        result = val(record, RowSchema())
        assert result[0] is False

    def test_validate_hoh_fed_time(self, record):
        """Test cat3 validator for federal disability."""
        val = validators.validate__FAM_AFF__HOH__Count_Fed_Time()

        record.FAMILY_AFFILIATION = 0
        result = val(record, RowSchema())
        assert result == (True, None, ['FAMILY_AFFILIATION', 'RELATIONSHIP_HOH', 'COUNTABLE_MONTH_FED_TIME'])

        record.FAMILY_AFFILIATION = 1
        record.RELATIONSHIP_HOH = 1
        record.COUNTABLE_MONTH_FED_TIME = 0

        result = val(record, RowSchema())
        assert result[0] is False

    def test_validate_oasdi_insurance(self, record):
        """Test cat3 validator for OASDI insurance."""
        val = validators.if_then_validator(
                    condition_field_name='DATE_OF_BIRTH', condition_function=validators.olderThan(18),
                    result_field_name='REC_OASDI_INSURANCE', result_function=validators.isInLimits(1, 2)
                  )

        record.DATE_OF_BIRTH = 0
        result = val(record, RowSchema())
        assert result == (True, None, ['DATE_OF_BIRTH', 'REC_OASDI_INSURANCE'])

        record.DATE_OF_BIRTH = 200001
        record.REC_OASDI_INSURANCE = 0

        result = val(record, RowSchema())
        assert result[0] is False

    def test_validate_federal_disability(self, record):
        """Test cat3 validator for federal disability."""
        val = validators.if_then_validator(
                    condition_field_name='FAMILY_AFFILIATION', condition_function=validators.matches(1),
                    result_field_name='REC_FEDERAL_DISABILITY', result_function=validators.isInLimits(1, 2)
                  )

        record.FAMILY_AFFILIATION = 0
        result = val(record, RowSchema())
        assert result == (True, None, ['FAMILY_AFFILIATION', 'REC_FEDERAL_DISABILITY'])

        record.FAMILY_AFFILIATION = 1
        record.REC_FEDERAL_DISABILITY = 0

        result = val(record, RowSchema())
        assert result[0] is False


class TestT6Cat3Validators(TestCat3ValidatorsBase):
    """Test category three validators for TANF T6 records."""

    @pytest.fixture
    def record(self):
        """Override default record with TANF T6 record."""
        return TanfT6Factory.create()

    def test_sum_of_applications(self, record):
        """Test cat3 validator for sum of applications."""
        val = validators.sumIsEqual("NUM_APPLICATIONS", ["NUM_APPROVED", "NUM_DENIED"])

        record.NUM_APPLICATIONS = 2
        result = val(record, RowSchema())

        assert result == (True, None, ['NUM_APPLICATIONS', 'NUM_APPROVED', 'NUM_DENIED'])

        record.NUM_APPLICATIONS = 1
        result = val(record, RowSchema())

        assert result[0] is False

    def test_sum_of_families(self, record):
        """Test cat3 validator for sum of families."""
        val = validators.sumIsEqual("NUM_FAMILIES", ["NUM_2_PARENTS", "NUM_1_PARENTS", "NUM_NO_PARENTS"])

        record.NUM_FAMILIES = 3
        result = val(record, RowSchema())

        assert result == (True, None, ['NUM_FAMILIES', 'NUM_2_PARENTS', 'NUM_1_PARENTS', 'NUM_NO_PARENTS'])

        record.NUM_FAMILIES = 1
        result = val(record, RowSchema())

        assert result[0] is False

    def test_sum_of_recipients(self, record):
        """Test cat3 validator for sum of recipients."""
        val = validators.sumIsEqual("NUM_RECIPIENTS", ["NUM_ADULT_RECIPIENTS", "NUM_CHILD_RECIPIENTS"])

        record.NUM_RECIPIENTS = 2
        result = val(record, RowSchema())

        assert result == (True, None, ['NUM_RECIPIENTS', 'NUM_ADULT_RECIPIENTS', 'NUM_CHILD_RECIPIENTS'])

        record.NUM_RECIPIENTS = 1
        result = val(record, RowSchema())

        assert result[0] is False

class TestM5Cat3Validators(TestCat3ValidatorsBase):
    """Test category three validators for TANF T6 records."""

    @pytest.fixture
    def record(self):
        """Override default record with TANF T6 record."""
        return SSPM5Factory.create()

    def test_fam_affil_ssn(self, record):
        """Test cat3 validator for family affiliation and ssn."""
        val = validators.if_then_validator(
                        condition_field_name='FAMILY_AFFILIATION', condition_function=validators.matches(1),
                        result_field_name='SSN', result_function=validators.validateSSN(),
                  )

        result = val(record, RowSchema())
        assert result == (True, None, ["FAMILY_AFFILIATION", "SSN"])

        record.SSN = '111111111'
        result = val(record, RowSchema())

        assert result[0] is False

    def test_validate_race_ethnicity(self, record):
        """Test cat3 validator for race/ethnicity."""
        races = ["RACE_HISPANIC", "RACE_AMER_INDIAN", "RACE_ASIAN", "RACE_BLACK", "RACE_HAWAIIAN", "RACE_WHITE"]
        for race in races:
            val = validators.if_then_validator(
                        condition_field_name='FAMILY_AFFILIATION', condition_function=validators.isInLimits(1, 3),
                        result_field_name=race, result_function=validators.isInLimits(1, 2),
                  )
            result = val(record, RowSchema())
            assert result == (True, None, ['FAMILY_AFFILIATION', race])

    def test_fam_affil_marital_stat(self, record):
        """Test cat3 validator for family affiliation, and marital status."""
        val = validators.if_then_validator(
                        condition_field_name='FAMILY_AFFILIATION', condition_function=validators.isInLimits(1, 3),
                        result_field_name='MARITAL_STATUS', result_function=validators.isInLimits(1, 5),
                  )

        result = val(record, RowSchema())
        assert result == (True, None, ['FAMILY_AFFILIATION', 'MARITAL_STATUS'])

        record.MARITAL_STATUS = 0

        result = val(record, RowSchema())
        assert result[0] is False

    def test_fam_affil_parent_with_minor(self, record):
        """Test cat3 validator for family affiliation, and parent with minor child."""
        val = validators.if_then_validator(
                        condition_field_name='FAMILY_AFFILIATION', condition_function=validators.isInLimits(1, 2),
                        result_field_name='PARENT_MINOR_CHILD', result_function=validators.isInLimits(1, 3),
                  )

        result = val(record, RowSchema())
        assert result == (True, None, ['FAMILY_AFFILIATION', 'PARENT_MINOR_CHILD'])

        record.PARENT_MINOR_CHILD = 0

        result = val(record, RowSchema())
        assert result[0] is False

    def test_fam_affil_ed_level(self, record):
        """Test cat3 validator for family affiliation, and education level."""
        val = validators.if_then_validator(
                        condition_field_name='FAMILY_AFFILIATION', condition_function=validators.isInLimits(1, 3),
                        result_field_name='EDUCATION_LEVEL', result_function=validators.or_validators(
                            validators.isInStringRange(1, 16), validators.isInStringRange(98, 99)),
                  )

        result = val(record, RowSchema())
        assert result == (True, None, ['FAMILY_AFFILIATION', 'EDUCATION_LEVEL'])

        record.EDUCATION_LEVEL = 0

        result = val(record, RowSchema())
        assert result[0] is False

    def test_fam_affil_citz_stat(self, record):
        """Test cat3 validator for family affiliation, and citizenship status."""
        val = validators.if_then_validator(
                        condition_field_name='FAMILY_AFFILIATION', condition_function=validators.matches(1),
                        result_field_name='CITIZENSHIP_STATUS', result_function=validators.isInLimits(1, 3),
                  )

        result = val(record, RowSchema())
        assert result == (True, None, ['FAMILY_AFFILIATION', 'CITIZENSHIP_STATUS'])

        record.CITIZENSHIP_STATUS = 0

        result = val(record, RowSchema())
        assert result[0] is False

    def test_dob_oasdi_insur(self, record):
        """Test cat3 validator for dob, and REC_OASDI_INSURANCE."""
        val = validators.if_then_validator(
                        condition_field_name='DATE_OF_BIRTH', condition_function=validators.olderThan(18),
                        result_field_name='REC_OASDI_INSURANCE', result_function=validators.isInLimits(1, 2),
                  )

        result = val(record, RowSchema())
        assert result == (True, None, ['DATE_OF_BIRTH', 'REC_OASDI_INSURANCE'])

        record.REC_OASDI_INSURANCE = 0

        result = val(record, RowSchema())
        assert result[0] is False

    def test_fam_affil_fed_disability(self, record):
        """Test cat3 validator for family affiliation, and REC_FEDERAL_DISABILITY."""
        val = validators.if_then_validator(
                        condition_field_name='FAMILY_AFFILIATION', condition_function=validators.matches(1),
                        result_field_name='REC_FEDERAL_DISABILITY', result_function=validators.isInLimits(1, 2),
                  )

        result = val(record, RowSchema())
        assert result == (True, None, ['FAMILY_AFFILIATION', 'REC_FEDERAL_DISABILITY'])

        record.REC_FEDERAL_DISABILITY = 0

        result = val(record, RowSchema())
        assert result[0] is False


class TestCaseConsistencyValidator:
    """Test case consistency (cat4) validators."""

    def parse_header(self, datafile):
        """Parse datafile header into header object."""
        rawfile = datafile.file

        # parse header, trailer
        rawfile.seek(0)
        header_line = rawfile.readline().decode().strip()
        return schema_defs.header.parse_and_validate(
            header_line,
            util.make_generate_file_precheck_parser_error(datafile, 1)
        )

    @pytest.fixture
    def tanf_s1_records(self):
        """Return group of TANF Section 1 records."""
        t1 = TanfT1Factory.create()
        t2 = TanfT2Factory.create()
        t3 = TanfT3Factory.create()
        t3_1 = TanfT3Factory.create()
        return [t1, t2, t3, t3_1]

    @pytest.fixture
    def tanf_s1_schemas(self):
        """Return group of TANF Section 1 schemas."""
        s1 = schema_defs.tanf.t1.schemas[0]
        s2 = schema_defs.tanf.t2.schemas[0]
        s3 = schema_defs.tanf.t3.schemas[0]
        return [s1, s2, s3, s3]

    @pytest.fixture
    def small_correct_file(self, stt_user, stt):
        """Fixture for small_correct_file."""
        return util.create_test_datafile('small_correct_file.txt', stt_user, stt)

    @pytest.fixture
    def small_correct_file_header(self, small_correct_file):
        """Return a valid header record."""
        header, header_is_valid, header_errors = self.parse_header(small_correct_file)

        if not header_is_valid:
            logger.error('Header is not valid: %s', header_errors)
            return None
        return header
