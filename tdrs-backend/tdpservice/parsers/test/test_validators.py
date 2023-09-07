"""Tests for generic validator functions."""

import pytest
from .. import validators
from tdpservice.parsers.test.factories import TanfT1Factory, TanfT2Factory, TanfT3Factory, TanfT5Factory, TanfT6Factory


def test_or_validators():
    """Test `or_validators` gives a valid result."""
    value = "2"
    validator = validators.or_validators(validators.matches(("2")), validators.matches(("3")))
    assert validator(value) == (True, None)
    assert validator("2") == (True, None)
    assert validator("3") == (True, None)
    assert validator("5") == (False, "5 does not match 2. or 5 does not match 3.")

    validator = validators.or_validators(validators.matches(("2")), validators.matches(("3")),
                                         validators.matches(("4")))
    assert validator(value) == (True, None)

    value = "3"
    assert validator(value) == (True, None)

    value = "4"
    assert validator(value) == (True, None)

    value = "5"
    assert validator(value) == (False, "5 does not match 2. or 5 does not match 3. or 5 does not match 4.")

    validator = validators.or_validators(validators.matches((2)), validators.matches((3)), validators.isLargerThan(4))
    assert validator(5) == (True, None)
    assert validator(1) == (False, "1 does not match 2. or 1 does not match 3. or 1 is not larger than 4.")

def test_if_validators():
    """Test `if_then_validator` gives a valid result."""
    value = {"Field1": "1", "Field2": "2"}
    validator = validators.if_then_validator(
          condition_field="Field1", condition_function=validators.matches('1'),
          result_field="Field2", result_function=validators.matches('2'),
      )
    assert validator(value) == (True, None)

    validator = validator = validators.if_then_validator(
          condition_field="Field1", condition_function=validators.matches('1'),
          result_field="Field2", result_function=validators.matches('1'),
      )
    result = validator(value)
    assert result == (False, 'if Field1 :1 validator1 passed then Field2 2 does not match 1.')


def test_and_validators():
    """Test `and_validators` gives a valid result."""
    validator = validators.and_validators(validators.isLargerThan(2), validators.isLargerThan(0))
    assert validator(1) == (False, '1 is not larger than 2.')
    assert validator(3) == (True, None)


def test_validate__FAM_AFF__SSN():
    """Test `validate__FAM_AFF__SSN` gives a valid result."""
    instance = {
        'FAMILY_AFFILIATION': 2,
        'CITIZENSHIP_STATUS': 1,
        'SSN': '0'*9,
    }
    result = validators.validate__FAM_AFF__SSN()(instance)
    assert result == (False,
                      'If FAMILY_AFFILIATION ==2 and CITIZENSHIP_STATUS==1 or 2, then SSN != 000000000 -- 999999999.')
    instance['SSN'] = '1'*8 + '0'
    result = validators.validate__FAM_AFF__SSN()(instance)
    assert result == (True, None)

def test_dateYearIsLargerThan():
    """Test `dateYearIsLargerThan` gives a valid result."""
    value = "199806"
    validator = validators.dateYearIsLargerThan(1999)
    result = validator(value)
    assert result == (False, '1998 year must be larger than 1999.')


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
    is_valid, error = validator(value)

    assert is_valid is False
    assert error == 'TEST does not match test.'


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
    is_valid, error = validator(value)

    assert is_valid is False
    assert error == '64 is not in [17, 24, 36].'


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
    is_valid, error = validator(value)

    assert is_valid is False
    assert error == '47 is not between 48 and 400.'


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
    is_valid, error = validator(value)
    assert is_valid is False
    assert error == '13 is not a valid month.'


def test_between_returns_invalid_for_string_value():
    """Test `between` gives an invalid result for strings."""
    value = '047'

    validator = validators.between(100, 400)
    is_valid, error = validator(value)

    assert is_valid is False
    assert error == '047 is not between 100 and 400.'


def test_hasLength_returns_valid():
    """Test `hasLength` gives a valid result."""
    value = 'abcd123'

    validator = validators.hasLength(7)
    is_valid, error = validator(value)

    assert is_valid is True
    assert error is None


def test_hasLength_returns_invalid():
    """Test `hasLength` gives an invalid result."""
    value = 'abcd123'

    validator = validators.hasLength(22)
    is_valid, error = validator(value)

    assert is_valid is False
    assert error == 'Value length 7 does not match 22.'


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
    is_valid, error = validator(value)

    assert is_valid is False
    assert error == '12345abcde does not contain 6789.'


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
    is_valid, error = validator(value)

    assert is_valid is False
    assert error == '12345abcde does not start with abc.'


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
    is_valid, error = validator(value)

    assert is_valid is False
    assert error == '          contains blanks between positions 0 and 9.'


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
    is_valid, error = validator(value)

    assert is_valid is False
    assert error == "111  333 contains blanks between positions 3 and 5."

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
          condition_field='RECEIVES_FOOD_STAMPS', condition_function=validators.matches(1),
          result_field='AMT_FOOD_STAMP_ASSISTANCE', result_function=validators.isLargerThan(0),
        )
        record.RECEIVES_FOOD_STAMPS = 1
        record.AMT_FOOD_STAMP_ASSISTANCE = 1
        result = val(record)
        assert result == (True, None)

        record.AMT_FOOD_STAMP_ASSISTANCE = 0
        result = val(record)
        assert result == (False, 'if RECEIVES_FOOD_STAMPS :1 validator1 passed then '
                          + 'AMT_FOOD_STAMP_ASSISTANCE 0 is not larger than 0.')

    def test_validate_subsidized_child_care(self, record):
        """Test cat3 validator for subsidized child care."""
        val = validators.if_then_validator(
          condition_field='RECEIVES_SUB_CC', condition_function=validators.notMatches(3),
          result_field='AMT_SUB_CC', result_function=validators.isLargerThan(0),
        )
        record.RECEIVES_SUB_CC = 4
        record.AMT_SUB_CC = 1
        result = val(record)
        assert result == (True, None)

        record.RECEIVES_SUB_CC = 4
        record.AMT_SUB_CC = 0
        result = val(record)
        assert result == (False, 'if RECEIVES_SUB_CC :4 validator1 passed then AMT_SUB_CC 0 is not larger than 0.')

    def test_validate_cash_amount_and_nbr_months(self, record):
        """Test cat3 validator for cash amount and number of months."""
        val = validators.if_then_validator(
          condition_field='CASH_AMOUNT', condition_function=validators.isLargerThan(0),
          result_field='NBR_MONTHS', result_function=validators.isLargerThan(0),
        )
        result = val(record)
        assert result == (True, None)

        record.CASH_AMOUNT = 1
        record.NBR_MONTHS = -1
        result = val(record)
        assert result == (False, 'if CASH_AMOUNT :1 validator1 passed then NBR_MONTHS -1 is not larger than 0.')

    def test_validate_child_care(self, record):
        """Test cat3 validator for child care."""
        val = validators.if_then_validator(
          condition_field='CC_AMOUNT', condition_function=validators.isLargerThan(0),
          result_field='CHILDREN_COVERED', result_function=validators.isLargerThan(0),
        )
        result = val(record)
        assert result == (True, None)

        record.CC_AMOUNT = 1
        record.CHILDREN_COVERED = -1
        result = val(record)
        assert result == (False, 'if CC_AMOUNT :1 validator1 passed then CHILDREN_COVERED -1 is not larger than 0.')

        val = validators.if_then_validator(
          condition_field='CC_AMOUNT', condition_function=validators.isLargerThan(0),
          result_field='CC_NBR_MONTHS', result_function=validators.isLargerThan(0),
        )
        record.CC_AMOUNT = 10
        record.CC_NBR_MONTHS = -1
        result = val(record)
        assert result == (False, 'if CC_AMOUNT :10 validator1 passed then CC_NBR_MONTHS -1 is not larger than 0.')

    def test_validate_transportation(self, record):
        """Test cat3 validator for transportation."""
        val = validators.if_then_validator(
          condition_field='TRANSP_AMOUNT', condition_function=validators.isLargerThan(0),
          result_field='TRANSP_NBR_MONTHS', result_function=validators.isLargerThan(0),
        )
        result = val(record)
        assert result == (True, None)

        record.TRANSP_AMOUNT = 1
        record.TRANSP_NBR_MONTHS = -1
        result = val(record)
        assert result == (False, 'if TRANSP_AMOUNT :1 validator1 passed then '
                          + 'TRANSP_NBR_MONTHS -1 is not larger than 0.')

    def test_validate_transitional_services(self, record):
        """Test cat3 validator for transitional services."""
        val = validators.if_then_validator(
          condition_field='TRANSITION_SERVICES_AMOUNT', condition_function=validators.isLargerThan(0),
          result_field='TRANSITION_NBR_MONTHS', result_function=validators.isLargerThan(0),
        )
        result = val(record)
        assert result == (True, None)

        record.TRANSITION_SERVICES_AMOUNT = 1
        record.TRANSITION_NBR_MONTHS = -1
        result = val(record)
        assert result == (False, 'if TRANSITION_SERVICES_AMOUNT :1 validator1 passed then '
                          + 'TRANSITION_NBR_MONTHS -1 is not larger than 0.')

    def test_validate_other(self, record):
        """Test cat3 validator for other."""
        val = validators.if_then_validator(
          condition_field='OTHER_AMOUNT', condition_function=validators.isLargerThan(0),
          result_field='OTHER_NBR_MONTHS', result_function=validators.isLargerThan(0),
        )
        result = val(record)
        assert result == (True, None)

        record.OTHER_AMOUNT = 1
        record.OTHER_NBR_MONTHS = -1
        result = val(record)
        assert result == (False, 'if OTHER_AMOUNT :1 validator1 passed then OTHER_NBR_MONTHS -1 is not larger than 0.')

    def test_validate_reasons_for_amount_of_assistance_reductions(self, record):
        """Test cat3 validator for assistance reductions."""
        val = validators.if_then_validator(
          condition_field='SANC_REDUCTION_AMT', condition_function=validators.isLargerThan(0),
          result_field='WORK_REQ_SANCTION', result_function=validators.oneOf((1, 2)),
        )
        record.SANC_REDUCTION_AMT = 1
        result = val(record)
        assert result == (True, None)

        record.SANC_REDUCTION_AMT = 10
        record.WORK_REQ_SANCTION = -1
        result = val(record)
        assert result == (False, 'if SANC_REDUCTION_AMT :10 validator1 passed then '
                          + 'WORK_REQ_SANCTION -1 is not in (1, 2).')

    def test_validate_sum(self, record):
        """Test cat3 validator for sum of cash fields."""
        val = validators.sumIsLarger(("AMT_FOOD_STAMP_ASSISTANCE", "AMT_SUB_CC", "CC_AMOUNT", "TRANSP_AMOUNT",
                                      "TRANSITION_SERVICES_AMOUNT", "OTHER_AMOUNT"), 0)
        result = val(record)
        assert result == (True, None)

        record.AMT_FOOD_STAMP_ASSISTANCE = 0
        record.AMT_SUB_CC = 0
        record.CC_AMOUNT = 0
        record.TRANSP_AMOUNT = 0
        record.TRANSITION_SERVICES_AMOUNT = 0
        record.OTHER_AMOUNT = 0
        result = val(record)
        assert result == (False, "The sum of ('AMT_FOOD_STAMP_ASSISTANCE', 'AMT_SUB_CC', 'CC_AMOUNT', " +
                          "'TRANSP_AMOUNT', 'TRANSITION_SERVICES_AMOUNT', 'OTHER_AMOUNT') is not larger than 0.")


class TestT2Cat3Validators(TestCat3ValidatorsBase):
    """Test category three validators for TANF T2 records."""

    @pytest.fixture
    def record(self):
        """Override default record with TANF T2 record."""
        return TanfT2Factory.create()

    def test_validate_ssn(self, record):
        """Test cat3 validator for social security number."""
        val = validators.if_then_validator(
                  condition_field='FAMILY_AFFILIATION', condition_function=validators.oneOf((1, 2)),
                  result_field='SSN', result_function=validators.notOneOf(("000000000", "111111111", "222222222",
                                                                           "333333333", "444444444", "555555555",
                                                                           "666666666", "777777777", "888888888",
                                                                           "999999999")),
            )
        record.SSN = "999989999"
        record.FAMILY_AFFILIATION = 1
        result = val(record)
        assert result == (True, None)

        record.FAMILY_AFFILIATION = 1
        record.SSN = "999999999"
        result = val(record)
        assert result == (False, "if FAMILY_AFFILIATION :1 validator1 passed then "
                          + "SSN 999999999 is in ('000000000', '111111111', " +
                          "'222222222', '333333333', '444444444', '555555555', '666666666', '777777777', '888888888'," +
                          " '999999999').")

    def test_validate_race_ethnicity(self, record):
        """Test cat3 validator for race/ethnicity."""
        races = ["RACE_HISPANIC", "RACE_AMER_INDIAN", "RACE_ASIAN", "RACE_BLACK", "RACE_HAWAIIAN", "RACE_WHITE"]
        record.FAMILY_AFFILIATION = 1
        for race in races:
            val = validators.if_then_validator(
                  condition_field='FAMILY_AFFILIATION', condition_function=validators.oneOf((1, 2, 3)),
                  result_field=race, result_function=validators.isInLimits(1, 2),
            )
            result = val(record)
            assert result == (True, None)

        record.FAMILY_AFFILIATION = 0
        for race in races:
            val = validators.if_then_validator(
                  condition_field='FAMILY_AFFILIATION', condition_function=validators.oneOf((1, 2, 3)),
                  result_field=race, result_function=validators.isInLimits(1, 2)
            )
            result = val(record)
            assert result == (True, None)

    def test_validate_marital_status(self, record):
        """Test cat3 validator for marital status."""
        val = validators.if_then_validator(
                        condition_field='FAMILY_AFFILIATION', condition_function=validators.isInLimits(1, 3),
                        result_field='MARITAL_STATUS', result_function=validators.isInLimits(1, 5),
                    )
        record.FAMILY_AFFILIATION = 1
        result = val(record)
        assert result == (True, None)

        record.FAMILY_AFFILIATION = 3
        record.MARITAL_STATUS = 0
        result = val(record)
        assert result == (False, 'if FAMILY_AFFILIATION :3 validator1 passed then MARITAL_STATUS 0 is not larger or ' +
                          'equal to 1 and smaller or equal to 5.')

    def test_validate_parent_with_minor(self, record):
        """Test cat3 validator for parent with a minor child."""
        val = validators.if_then_validator(
                        condition_field='FAMILY_AFFILIATION', condition_function=validators.isInLimits(1, 3),
                        result_field='PARENT_WITH_MINOR_CHILD', result_function=validators.isInLimits(1, 3),
                    )
        result = val(record)
        assert result == (True, None)

        record.PARENT_WITH_MINOR_CHILD = 0
        result = val(record)
        assert result == (False, 'if FAMILY_AFFILIATION :1 validator1 passed then PARENT_WITH_MINOR_CHILD 0 is not ' +
                          'larger or equal to 1 and smaller or equal to 3.')

    def test_validate_education_level(self, record):
        """Test cat3 validator for education level."""
        val = validators.if_then_validator(
                      condition_field='FAMILY_AFFILIATION', condition_function=validators.oneOf((1, 2, 3)),
                      result_field='EDUCATION_LEVEL', result_function=validators.oneOf(("01", "02", "03", "04", "05",
                                                                                        "06", "07", "08", "09", "10",
                                                                                        "11", "12", "13", "14", "15",
                                                                                        "16", "98", "99")),
                )
        record.FAMILY_AFFILIATION = 3
        result = val(record)
        assert result == (True, None)

        record.FAMILY_AFFILIATION = 1
        record.EDUCATION_LEVEL = "00"
        result = val(record)
        assert result == (False, "if FAMILY_AFFILIATION :1 validator1 passed then "
                          + "EDUCATION_LEVEL 00 is not in ('01', '02', '03', '04', '05', '06',"
                          + " '07', '08', '09', '10', '11', '12', '13', '14', '15', '16', '98', '99').")

    def test_validate_citizenship(self, record):
        """Test cat3 validator for citizenship."""
        val = validators.if_then_validator(
                        condition_field='FAMILY_AFFILIATION', condition_function=validators.matches(1),
                        result_field='CITIZENSHIP_STATUS', result_function=validators.oneOf((1, 2)),
                    )
        record.FAMILY_AFFILIATION = 0
        result = val(record)
        assert result == (True, None)

        record.FAMILY_AFFILIATION = 1
        record.CITIZENSHIP_STATUS = 0
        result = val(record)
        assert result == (False, 'if FAMILY_AFFILIATION :1 validator1 passed then CITIZENSHIP_STATUS 0 ' +
                          'is not in (1, 2).')

    def test_validate_cooperation_with_child_support(self, record):
        """Test cat3 validator for cooperation with child support."""
        val = validators.if_then_validator(
                        condition_field='FAMILY_AFFILIATION', condition_function=validators.isInLimits(1, 3),
                        result_field='COOPERATION_CHILD_SUPPORT', result_function=validators.oneOf((1, 2, 9)),
                    )
        record.FAMILY_AFFILIATION = 0
        result = val(record)
        assert result == (True, None)

        record.FAMILY_AFFILIATION = 1
        record.COOPERATION_CHILD_SUPPORT = 0
        result = val(record)
        assert result == (False, 'if FAMILY_AFFILIATION :1 validator1 passed then COOPERATION_CHILD_SUPPORT 0 ' +
                          'is not in (1, 2, 9).')

    def test_validate_months_federal_time_limit(self, record):
        """Test cat3 validator for federal time limit."""
        # TODO THIS ISNT EXACTLY RIGHT SINCE FED TIME LIMIT IS A STRING.
        val = validators.validate__FAM_AFF__HOH__Fed_Time()
        record.FAMILY_AFFILIATION = 0
        result = val(record)
        assert result == (True, None)

        record.FAMILY_AFFILIATION = 1
        record.MONTHS_FED_TIME_LIMIT = "000"
        record.RELATIONSHIP_HOH = "01"
        result = val(record)
        assert result == (False, 'If FAMILY_AFFILIATION == 2 and MONTHS_FED_TIME_LIMIT== 1 or 2, ' +
                          'then MONTHS_FED_TIME_LIMIT > 1.')

    def test_validate_employment_status(self, record):
        """Test cat3 validator for employment status."""
        val = validators.if_then_validator(
                        condition_field='FAMILY_AFFILIATION', condition_function=validators.isInLimits(1, 3),
                        result_field='EMPLOYMENT_STATUS', result_function=validators.isInLimits(1, 3),
                    )
        record.FAMILY_AFFILIATION = 0
        result = val(record)
        assert result == (True, None)

        record.FAMILY_AFFILIATION = 3
        record.EMPLOYMENT_STATUS = 4
        result = val(record)
        assert result == (False, 'if FAMILY_AFFILIATION :3 validator1 passed then EMPLOYMENT_STATUS 4 is not larger ' +
                          'or equal to 1 and smaller or equal to 3.')

    def test_validate_work_eligible_indicator(self, record):
        """Test cat3 validator for work eligibility."""
        val = validators.if_then_validator(
                        condition_field='FAMILY_AFFILIATION', condition_function=validators.oneOf((1, 2)),
                        result_field='WORK_ELIGIBLE_INDICATOR', result_function=validators.or_validators(
                            validators.isInStringRange(1, 9),
                            validators.matches('12')
                        ),
                    )
        record.FAMILY_AFFILIATION = 0
        result = val(record)
        assert result == (True, None)

        record.FAMILY_AFFILIATION = 1
        record.WORK_ELIGIBLE_INDICATOR = "00"
        result = val(record)
        assert result == (False, 'if FAMILY_AFFILIATION :1 validator1 passed then WORK_ELIGIBLE_INDICATOR 00 is not ' +
                          'in range [1, 9]. or 00 does not match 12.')

    def test_validate_work_participation(self, record):
        """Test cat3 validator for work participation."""
        val = validators.if_then_validator(
                        condition_field='FAMILY_AFFILIATION', condition_function=validators.oneOf((1, 2)),
                        result_field='WORK_PART_STATUS', result_function=validators.oneOf(['01', '02', '05', '07', '09',
                                                                                           '15', '17', '18', '19', '99']
                                                                                          ),
                    )
        record.FAMILY_AFFILIATION = 0
        result = val(record)
        assert result == (True, None)

        record.FAMILY_AFFILIATION = 2
        record.WORK_PART_STATUS = "04"
        result = val(record)
        assert result == (False, "if FAMILY_AFFILIATION :2 validator1 passed then WORK_PART_STATUS 04 is not " +
                          "in ['01', '02', '05', '07', '09', '15', '17', '18', '19', '99'].")

        val = validators.if_then_validator(
                        condition_field='WORK_ELIGIBLE_INDICATOR', condition_function=validators.isInStringRange(1, 5),
                        result_field='WORK_PART_STATUS', result_function=validators.notMatches('99'),
                    )
        record.WORK_PART_STATUS = "99"
        record.WORK_ELIGIBLE_INDICATOR = "01"
        result = val(record)
        assert result == (False, 'if WORK_ELIGIBLE_INDICATOR :01 validator1 passed then '
                          + 'WORK_PART_STATUS 99 matches 99.')


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
                  condition_field='FAMILY_AFFILIATION', condition_function=validators.matches(1),
                  result_field='SSN', result_function=validators.notOneOf(("999999999", "000000000")),
            )
        result = val(record)
        assert result == (True, None)

        record.FAMILY_AFFILIATION = 1
        record.SSN = "999999999"
        result = val(record)
        assert result == (False, "if FAMILY_AFFILIATION :1 validator1 passed then "
                          + "SSN 999999999 is in ('999999999', '000000000').")

    def test_validate_t3_race_ethnicity(self, record):
        """Test cat3 validator for race/ethnicity."""
        races = ["RACE_HISPANIC", "RACE_AMER_INDIAN", "RACE_ASIAN", "RACE_BLACK", "RACE_HAWAIIAN", "RACE_WHITE"]
        record.FAMILY_AFFILIATION = 1
        for race in races:
            val = validators.if_then_validator(
                  condition_field='FAMILY_AFFILIATION', condition_function=validators.oneOf((1, 2)),
                  result_field=race, result_function=validators.oneOf((1, 2)),
            )
            result = val(record)
            assert result == (True, None)

        record.FAMILY_AFFILIATION = 0
        for race in races:
            val = validators.if_then_validator(
                  condition_field='FAMILY_AFFILIATION', condition_function=validators.oneOf((1, 2)),
                  result_field=race, result_function=validators.oneOf((1, 2)),
            )
            result = val(record)
            assert result == (True, None)

    def test_validate_relationship_hoh(self, record):
        """Test cat3 validator for relationship to head of household."""
        val = validators.if_then_validator(
                  condition_field='FAMILY_AFFILIATION', condition_function=validators.oneOf((1, 2)),
                  result_field='RELATIONSHIP_HOH', result_function=validators.isInStringRange(4, 9),
            )
        record.FAMILY_AFFILIATION = 0
        record.RELATIONSHIP_HOH = "04"
        result = val(record)
        assert result == (True, None)

        record.FAMILY_AFFILIATION = 1
        record.RELATIONSHIP_HOH = "01"
        result = val(record)
        assert result == (False, 'if FAMILY_AFFILIATION :1 validator1 passed then RELATIONSHIP_HOH 01 is ' +
                          'not in range [4, 9].')

    def test_validate_t3_education_level(self, record):
        """Test cat3 validator for education level."""
        val = validators.if_then_validator(
                  condition_field='FAMILY_AFFILIATION', condition_function=validators.matches(1),
                  result_field='EDUCATION_LEVEL', result_function=validators.notMatches("99"),
            )
        record.FAMILY_AFFILIATION = 1
        result = val(record)
        assert result == (True, None)

        record.FAMILY_AFFILIATION = 1
        record.EDUCATION_LEVEL = "99"
        result = val(record)
        assert result == (False, 'if FAMILY_AFFILIATION :1 validator1 passed then EDUCATION_LEVEL 99 matches 99.')

    def test_validate_t3_citizenship(self, record):
        """Test cat3 validator for citizenship."""
        val = validators.if_then_validator(
                  condition_field='FAMILY_AFFILIATION', condition_function=validators.matches(1),
                  result_field='CITIZENSHIP_STATUS', result_function=validators.oneOf((1, 2)),
            )
        record.FAMILY_AFFILIATION = 1
        result = val(record)
        assert result == (True, None)

        record.FAMILY_AFFILIATION = 1
        record.CITIZENSHIP_STATUS = 3
        result = val(record)
        assert result == (False, 'if FAMILY_AFFILIATION :1 validator1 passed then CITIZENSHIP_STATUS 3 ' +
                          'is not in (1, 2).')

        val = validators.if_then_validator(
                  condition_field='FAMILY_AFFILIATION', condition_function=validators.matches(2),
                  result_field='CITIZENSHIP_STATUS', result_function=validators.oneOf((1, 2, 9)),
            )
        record.FAMILY_AFFILIATION = 2
        record.CITIZENSHIP_STATUS = 3
        result = val(record)
        assert result == (False, 'if FAMILY_AFFILIATION :2 validator1 passed then CITIZENSHIP_STATUS 3 ' +
                          'is not in (1, 2, 9).')


class TestT5Cat3Validators(TestCat3ValidatorsBase):
    """Test category three validators for TANF T5 records."""

    @pytest.fixture
    def record(self):
        """Override default record with TANF T5 record."""
        return TanfT5Factory.create()

    def test_validate_ssn(self, record):
        """Test cat3 validator for SSN."""
        val = validators.if_then_validator(
                  condition_field='FAMILY_AFFILIATION', condition_function=validators.notMatches(1),
                  result_field='SSN', result_function=validators.isNumber()
                  )

        result = val(record)
        assert result == (True, None)

        record.SSN = "abc"
        record.FAMILY_AFFILIATION = 2

        result = val(record)
        assert result == (False, 'if FAMILY_AFFILIATION :2 validator1 passed then SSN abc is not a number.')

    def test_validate_ssn_citizenship(self, record):
        """Test cat3 validator for SSN/citizenship."""
        val = validators.validate__FAM_AFF__SSN()

        result = val(record)
        assert result == (True, None)

        record.FAMILY_AFFILIATION = 2
        record.SSN = "000000000"

        result = val(record)
        assert result == (False, "If FAMILY_AFFILIATION ==2 and CITIZENSHIP_STATUS==1 or 2, then SSN " +
                          "!= 000000000 -- 999999999.")

    def test_validate_race_ethnicity(self, record):
        """Test cat3 validator for race/ethnicity."""
        races = ["RACE_HISPANIC", "RACE_AMER_INDIAN", "RACE_ASIAN", "RACE_BLACK", "RACE_HAWAIIAN", "RACE_WHITE"]
        record.FAMILY_AFFILIATION = 1
        for race in races:
            val = validators.if_then_validator(
                    condition_field='FAMILY_AFFILIATION', condition_function=validators.isInLimits(1, 3),
                    result_field='RACE_HISPANIC', result_function=validators.isInLimits(1, 2)
                  )
            result = val(record)
            assert result == (True, None)

        record.FAMILY_AFFILIATION = 1
        record.RACE_HISPANIC = 0
        record.RACE_AMER_INDIAN = 0
        record.RACE_ASIAN = 0
        record.RACE_BLACK = 0
        record.RACE_HAWAIIAN = 0
        record.RACE_WHITE = 0
        for race in races:
            val = validators.if_then_validator(
                    condition_field='FAMILY_AFFILIATION', condition_function=validators.isInLimits(1, 3),
                    result_field=race, result_function=validators.isInLimits(1, 2)
                  )
            result = val(record)
            assert result == (False, f'if FAMILY_AFFILIATION :1 validator1 passed then {race} 0 is not larger or ' +
                              'equal to 1 and smaller or equal to 2.')

    def test_validate_marital_status(self, record):
        """Test cat3 validator for marital status."""
        val = validators.if_then_validator(
                    condition_field='FAMILY_AFFILIATION', condition_function=validators.isInLimits(1, 3),
                    result_field='MARITAL_STATUS', result_function=validators.isInLimits(0, 5)
                  )

        record.FAMILY_AFFILIATION = 0
        result = val(record)
        assert result == (True, None)

        record.FAMILY_AFFILIATION = 2
        record.MARITAL_STATUS = 6

        result = val(record)
        assert result == (False, 'if FAMILY_AFFILIATION :2 validator1 passed then MARITAL_STATUS 6 is not larger or ' +
                          'equal to 0 and smaller or equal to 5.')

    def test_validate_parent_minor(self, record):
        """Test cat3 validator for parent with minor."""
        val = validators.if_then_validator(
                    condition_field='FAMILY_AFFILIATION', condition_function=validators.isInLimits(1, 2),
                    result_field='PARENT_MINOR_CHILD', result_function=validators.isInLimits(1, 3)
                  )

        record.FAMILY_AFFILIATION = 0
        result = val(record)
        assert result == (True, None)

        record.FAMILY_AFFILIATION = 2
        record.PARENT_MINOR_CHILD = 0

        result = val(record)
        assert result == (False, 'if FAMILY_AFFILIATION :2 validator1 passed then PARENT_MINOR_CHILD 0 is not larger ' +
                          'or equal to 1 and smaller or equal to 3.')

    def test_validate_education(self, record):
        """Test cat3 validator for education level."""
        val = validators.if_then_validator(
                  condition_field='FAMILY_AFFILIATION', condition_function=validators.isInLimits(1, 3),
                  result_field='EDUCATION_LEVEL', result_function=validators.or_validators(
                      validators.isInStringRange(1, 16),
                      validators.isInStringRange(98, 99)
                      )
                  )

        record.FAMILY_AFFILIATION = 0
        result = val(record)
        assert result == (True, None)

        record.FAMILY_AFFILIATION = 2
        record.EDUCATION_LEVEL = "0"

        result = val(record)
        assert result == (False, "if FAMILY_AFFILIATION :2 validator1 passed then EDUCATION_LEVEL 0 is not in range " +
                          "[1, 16]. or 0 is not in range [98, 99].")

    def test_validate_citizenship_status(self, record):
        """Test cat3 validator for citizenship status."""
        val = validators.if_then_validator(
                    condition_field='FAMILY_AFFILIATION', condition_function=validators.matches(1),
                    result_field='CITIZENSHIP_STATUS', result_function=validators.isInLimits(1, 2)
                  )

        record.FAMILY_AFFILIATION = 0
        result = val(record)
        assert result == (True, None)

        record.FAMILY_AFFILIATION = 1
        record.CITIZENSHIP_STATUS = 0

        result = val(record)
        assert result == (False, 'if FAMILY_AFFILIATION :1 validator1 passed then CITIZENSHIP_STATUS 0 is not larger ' +
                          'or equal to 1 and smaller or equal to 2.')

    def test_validate_hoh_fed_time(self, record):
        """Test cat3 validator for federal disability."""
        val = validators.validate__FAM_AFF__HOH__Count_Fed_Time()

        record.FAMILY_AFFILIATION = 0
        result = val(record)
        assert result == (True, None)

        record.FAMILY_AFFILIATION = 1
        record.RELATIONSHIP_HOH = 1
        record.COUNTABLE_MONTH_FED_TIME = 0

        result = val(record)
        assert result == (False, 'If FAMILY_AFFILIATION == 2 and COUNTABLE_MONTH_FED_TIME== 1 or 2, then ' +
                          'COUNTABLE_MONTH_FED_TIME > 1.')

    def test_validate_oasdi_insurance(self, record):
        """Test cat3 validator for OASDI insurance."""
        val = validators.if_then_validator(
                    condition_field='DATE_OF_BIRTH', condition_function=validators.olderThan(18),
                    result_field='REC_OASDI_INSURANCE', result_function=validators.isInLimits(1, 2)
                  )

        record.DATE_OF_BIRTH = 0
        result = val(record)
        assert result == (True, None)

        record.DATE_OF_BIRTH = 200001
        record.REC_OASDI_INSURANCE = 0

        result = val(record)
        assert result == (False, 'if DATE_OF_BIRTH :200001 validator1 passed then REC_OASDI_INSURANCE 0 is not ' +
                          'larger or equal to 1 and smaller or equal to 2.')

    def test_validate_federal_disability(self, record):
        """Test cat3 validator for federal disability."""
        val = validators.if_then_validator(
                    condition_field='FAMILY_AFFILIATION', condition_function=validators.matches(1),
                    result_field='REC_FEDERAL_DISABILITY', result_function=validators.isInLimits(1, 2)
                  )

        record.FAMILY_AFFILIATION = 0
        result = val(record)
        assert result == (True, None)

        record.FAMILY_AFFILIATION = 1
        record.REC_FEDERAL_DISABILITY = 0

        result = val(record)
        assert result == (False, 'if FAMILY_AFFILIATION :1 validator1 passed then REC_FEDERAL_DISABILITY 0 is not ' +
                          'larger or equal to 1 and smaller or equal to 2.')


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
        result = val(record)

        assert result == (True, None)

        record.NUM_APPLICATIONS = 1
        result = val(record)

        assert result == (False, "The sum of ['NUM_APPROVED', 'NUM_DENIED'] does not equal NUM_APPLICATIONS.")

    def test_sum_of_families(self, record):
        """Test cat3 validator for sum of families."""
        val = validators.sumIsEqual("NUM_FAMILIES", ["NUM_2_PARENTS", "NUM_1_PARENTS", "NUM_NO_PARENTS"])

        record.NUM_FAMILIES = 3
        result = val(record)

        assert result == (True, None)

        record.NUM_FAMILIES = 1
        result = val(record)

        assert result == (False, "The sum of ['NUM_2_PARENTS', 'NUM_1_PARENTS', 'NUM_NO_PARENTS'] does not equal " +
                          "NUM_FAMILIES.")

    def test_sum_of_recipients(self, record):
        """Test cat3 validator for sum of recipients."""
        val = validators.sumIsEqual("NUM_RECIPIENTS", ["NUM_ADULT_RECIPIENTS", "NUM_CHILD_RECIPIENTS"])

        record.NUM_RECIPIENTS = 2
        result = val(record)

        assert result == (True, None)

        record.NUM_RECIPIENTS = 1
        result = val(record)

        assert result == (False, "The sum of ['NUM_ADULT_RECIPIENTS', 'NUM_CHILD_RECIPIENTS'] does not equal " +
                          "NUM_RECIPIENTS.")
