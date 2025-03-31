"""Overloaded base validators and custom postparsing validators."""

import datetime
import logging
from tdpservice.parsers.util import get_record_value_by_field_name
from tdpservice.parsers.validators import base
from tdpservice.parsers.validators.util import Result, validator, make_validator, evaluate_all
from tdpservice.parsers.dataclasses import ValidationErrorArgs
from django.conf import settings

logger = logging.getLogger(__name__)


def format_error_context(eargs: ValidationErrorArgs):
    """Format the error message for consistency across cat3 validators."""
    return f'Item {eargs.item_num} ({eargs.friendly_name})'


@validator(base.isEqual)
def isEqual(option, **kwargs):
    """Return a custom message for the isEqual validator."""
    return lambda eargs: f'must match {option}'


@validator(base.isNotEqual)
def isNotEqual(option, **kwargs):
    """Return a custom message for the isNotEqual validator."""
    return lambda eargs: f'must not be equal to {option}'


@validator(base.isOneOf)
def isOneOf(options, **kwargs):
    """Return a custom message for the isOneOf validator."""
    return lambda eargs: f'must be one of {options}'


@validator(base.isNotOneOf)
def isNotOneOf(options, **kwargs):
    """Return a custom message for the isNotOneOf validator."""
    return lambda eargs: f'must not be one of {options}'


@validator(base.isGreaterThan)
def isGreaterThan(option, inclusive=False, **kwargs):
    """Return a custom message for the isGreaterThan validator."""
    return lambda eargs: f'must be greater than {option}'


@validator(base.isLessThan)
def isLessThan(option, inclusive=False, **kwargs):
    """Return a custom message for the isLessThan validator."""
    return lambda eargs: f'must be less than {option}'


@validator(base.isBetween)
def isBetween(min, max, inclusive=False, **kwargs):
    """Return a custom message for the isBetween validator."""
    return lambda eargs: f'must be between {min} and {max}'


@validator(base.startsWith)
def startsWith(substr, **kwargs):
    """Return a custom message for the startsWith validator."""
    return lambda eargs: f'must start with {substr}'


@validator(base.contains)
def contains(substr, **kwargs):
    """Return a custom message for the contains validator."""
    return lambda eargs: f'must contain {substr}'


@validator(base.isNumber)
def isNumber(**kwargs):
    """Return a custom message for the isNumber validator."""
    return lambda eargs: 'must be a number'


@validator(base.isAlphaNumeric)
def isAlphaNumeric(**kwargs):
    """Return a custom message for the isAlphaNumeric validator."""
    return lambda eargs: 'must be alphanumeric'


@validator(base.isEmpty)
def isEmpty(start=0, end=None, **kwargs):
    """Return a custom message for the isEmpty validator."""
    return lambda eargs: 'must be empty'


@validator(base.isNotEmpty)
def isNotEmpty(start=0, end=None, **kwargs):
    """Return a custom message for the isNotEmpty validator."""
    return lambda eargs: 'must not be empty'


@validator(base.isBlank)
def isBlank(**kwargs):
    """Return a custom message for the isBlank validator."""
    return lambda eargs: 'must be blank'


@validator(base.hasLength)
def hasLength(length, **kwargs):
    """Return a custom message for the hasLength validator."""
    return lambda eargs: f'must have length {length}'


@validator(base.hasLengthGreaterThan)
def hasLengthGreaterThan(length, inclusive=False, **kwargs):
    """Return a custom message for the hasLengthGreaterThan validator."""
    return lambda eargs: f'must have length greater than {length}'


@validator(base.intHasLength)
def intHasLength(length, **kwargs):
    """Return a custom message for the intHasLength validator."""
    return lambda eargs: f'must have length {length}'


@validator(base.isNotZero)
def isNotZero(number_of_zeros=1, **kwargs):
    """Return a custom message for the isNotZero validator."""
    return lambda eargs: 'must not be zero'


def isOlderThan(min_age):
    """Validate that value is larger than min_age."""
    def _validate(val):
        birth_year = int(str(val)[:4])
        age = datetime.date.today().year - birth_year
        _validator = base.isGreaterThan(min_age)
        result = _validator(age)
        return result

    return make_validator(
        _validate,
        lambda eargs:
            f"{str(eargs.value)[:4]} must be less "
            f"than or equal to {datetime.date.today().year - min_age} to meet the minimum age requirement."
    )


def validateSSN():
    """Validate that SSN value is not a repeating digit."""
    options = [str(i) * 9 for i in range(0, 10)]
    return make_validator(
        base.isNotOneOf(options),
        lambda eargs: f"is in {options}."
    )


# compositional validators, build an error message using multiple of the above functions
def ifThenAlso(condition_field_name, condition_function, result_field_name, result_function, **kwargs):
    """Return second validation if the first validator is true.

    :param condition_field: function that returns (bool, string) to represent validation state
    :param condition_function: function that returns (bool, string) to represent validation state
    :param result_field: function that returns (bool, string) to represent validation state
    :param result_function: function that returns (bool, string) to represent validation state
    """
    def if_then_validator_func(record, row_schema):
        condition_value = get_record_value_by_field_name(record, condition_field_name)
        condition_field = row_schema.get_field_by_name(condition_field_name)
        condition_field_eargs = ValidationErrorArgs(
            value=condition_value,
            row_schema=row_schema,
            friendly_name=condition_field.friendly_name,
            item_num=condition_field.item,
        )
        condition_result = condition_function(condition_value, condition_field_eargs)

        result_value = get_record_value_by_field_name(record, result_field_name)
        result_field = row_schema.get_field_by_name(result_field_name)
        result_field_eargs = ValidationErrorArgs(
            value=result_value,
            row_schema=row_schema,
            friendly_name=result_field.friendly_name,
            item_num=result_field.item,
        )
        result_result = result_function(result_value, result_field_eargs)

        if not condition_result.valid:
            return Result(field_names=[result_field_name, condition_field_name])
        elif not result_result.valid:
            center_error = None
            if condition_result.valid:
                center_error = f'{format_error_context(condition_field_eargs)} is {condition_value}'
            else:
                center_error = condition_result.error
            error_message = (
                f"Since {center_error}, then {format_error_context(result_field_eargs)} "
                f"{result_value} {result_result.error}"
            )

            return Result(valid=result_result.valid, error=error_message,
                          field_names=[condition_field_name, result_field_name])
        else:
            return Result(valid=result_result.valid, field_names=[condition_field_name, result_field_name])

    return if_then_validator_func


def orValidators(validators, **kwargs):
    """Return a validator that is true only if one of the validators is true."""
    is_if_result_func = kwargs.get('if_result', False)

    def _validate(value, eargs):
        validator_results = evaluate_all(validators, value, eargs)

        if not any(result.valid for result in validator_results):
            error_msg = f'{format_error_context(eargs)} {value} ' if not is_if_result_func else ''
            error_msg += " or ".join([result.error for result in validator_results]) + '.'
            return Result(valid=False, error=error_msg)

        return Result()

    return _validate


# custom validators
def sumIsEqual(condition_field_name, sum_fields=[]):
    """Validate that the sum of the sum_fields equals the condition_field."""
    def sumIsEqualFunc(record, row_schema):
        sum = 0
        for field in sum_fields:
            val = get_record_value_by_field_name(record, field)
            sum += 0 if val is None else val

        condition_val = get_record_value_by_field_name(record, condition_field_name)
        condition_field = row_schema.get_field_by_name(condition_field_name)
        fields = [condition_field_name]
        fields.extend(sum_fields)

        if sum == condition_val:
            return Result(field_names=fields)
        return Result(
            valid=False,
            error=(f"{row_schema.record_type}: The sum of {sum_fields} does not equal {condition_field_name} "
                   f"{condition_field.friendly_name} Item {condition_field.item}."),
            field_names=fields
        )

    return sumIsEqualFunc


def sumIsLarger(fields, val):
    """Validate that the sum of the fields is larger than val."""
    def sumIsLargerFunc(record, row_schema):
        sum = 0
        for field in fields:
            temp_val = get_record_value_by_field_name(record, field)
            sum += 0 if temp_val is None else temp_val

        if sum > val:
            return Result(field_names=fields)

        return Result(
            valid=False,
            error=f"{row_schema.record_type}: The sum of {fields} is not larger than {val}.",
            field_names=fields
        )

    return sumIsLargerFunc

def suppress_pilot_state(condition_field_name, result_field_name, validator):
    """Supresses the passed validation should the state be an FRA pilot state."""
    def validate(record, row_schema):
        pilotStates = settings.FRA_PILOT_STATES

        stt = row_schema.datafile.stt

        if stt.type is not None and stt.type.lower() == 'state' and stt.postal_code in pilotStates:
            return Result(field_names=[condition_field_name, result_field_name])

        return validator(record, row_schema)

    return validate


def validate__FAM_AFF__SSN():
    """
    Validate social security number provided.

    Since item FAMILY_AFFILIATION ==2 and item CITIZENSHIP_STATUS ==1 or 2,
    then item SSN != 000000000 -- 999999999.
    """
    # value is instance
    def validate(record, row_schema):
        fam_affil_field = row_schema.get_field_by_name('FAMILY_AFFILIATION')
        FAMILY_AFFILIATION = get_record_value_by_field_name(record, 'FAMILY_AFFILIATION')
        fam_affil_eargs = ValidationErrorArgs(
            value=FAMILY_AFFILIATION,
            row_schema=row_schema,
            friendly_name=fam_affil_field.friendly_name,
            item_num=fam_affil_field.item,
        )

        cit_stat_field = row_schema.get_field_by_name('CITIZENSHIP_STATUS')
        CITIZENSHIP_STATUS = get_record_value_by_field_name(record, 'CITIZENSHIP_STATUS')
        cit_stat_eargs = ValidationErrorArgs(
            value=CITIZENSHIP_STATUS,
            row_schema=row_schema,
            friendly_name=cit_stat_field.friendly_name,
            item_num=cit_stat_field.item,
        )

        ssn_field = row_schema.get_field_by_name('SSN')
        SSN = get_record_value_by_field_name(record, 'SSN')
        ssn_eargs = ValidationErrorArgs(
            value=SSN,
            row_schema=row_schema,
            friendly_name=ssn_field.friendly_name,
            item_num=ssn_field.item,
        )

        if FAMILY_AFFILIATION == 2 and (
            CITIZENSHIP_STATUS == 1 or CITIZENSHIP_STATUS == 2
        ):
            if SSN in [str(i) * 9 for i in range(10)]:
                return Result(
                    valid=False,
                    error=(f"{row_schema.record_type}: Since {format_error_context(fam_affil_eargs)} is 2 "
                           f"and {format_error_context(cit_stat_eargs)} is 1 or 2, "
                           f"then {format_error_context(ssn_eargs)} must not be in 000000000 -- 999999999."),
                    field_names=["FAMILY_AFFILIATION", "CITIZENSHIP_STATUS", "SSN"],
                )
            else:
                return Result(field_names=["FAMILY_AFFILIATION", "CITIZENSHIP_STATUS", "SSN"])
        else:
            return Result(field_names=["FAMILY_AFFILIATION", "CITIZENSHIP_STATUS", "SSN"])

    return validate


def validate__WORK_ELIGIBLE_INDICATOR__HOH__AGE():
    """If WORK_ELIGIBLE_INDICATOR == 11 and AGE < 19, then RELATIONSHIP_HOH != 1."""
    # value is instance
    def validate(record, row_schema):
        work_elig_field = row_schema.get_field_by_name('WORK_ELIGIBLE_INDICATOR')
        work_elig_eargs = ValidationErrorArgs(
            value=None,
            row_schema=row_schema,
            friendly_name=work_elig_field.friendly_name,
            item_num=work_elig_field.item,
        )

        relat_hoh_field = row_schema.get_field_by_name('RELATIONSHIP_HOH')
        relat_hoh_eargs = ValidationErrorArgs(
            value=None,
            row_schema=row_schema,
            friendly_name=relat_hoh_field.friendly_name,
            item_num=relat_hoh_field.item,
        )

        dob_field = row_schema.get_field_by_name('DATE_OF_BIRTH')
        age_eargs = ValidationErrorArgs(
            value=None,
            row_schema=row_schema,
            friendly_name='Age',
            item_num=dob_field.item,
        )

        false_case = Result(
            valid=False,
            error=(f"{row_schema.record_type}: Since {format_error_context(work_elig_eargs)} is 11 "
                   f"and {format_error_context(age_eargs)} is less than 19, "
                   f"then {format_error_context(relat_hoh_eargs)} must not be 1."),
            field_names=['WORK_ELIGIBLE_INDICATOR', 'RELATIONSHIP_HOH', 'DATE_OF_BIRTH'],
        )
        true_case = Result(field_names=['WORK_ELIGIBLE_INDICATOR', 'RELATIONSHIP_HOH', 'DATE_OF_BIRTH'])

        try:
            WORK_ELIGIBLE_INDICATOR = get_record_value_by_field_name(record, 'WORK_ELIGIBLE_INDICATOR')
            RELATIONSHIP_HOH = int(get_record_value_by_field_name(record, 'RELATIONSHIP_HOH'))
            DOB = get_record_value_by_field_name(record, 'DATE_OF_BIRTH')
            RPT_MONTH_YEAR = get_record_value_by_field_name(record, 'RPT_MONTH_YEAR')
            RPT_MONTH_YEAR += "01"

            DOB_datetime = datetime.datetime.strptime(DOB, '%Y%m%d')
            RPT_MONTH_YEAR_datetime = datetime.datetime.strptime(RPT_MONTH_YEAR, '%Y%m%d')

            # age computation should use generic
            AGE = (RPT_MONTH_YEAR_datetime - DOB_datetime).days / 365.25

            if WORK_ELIGIBLE_INDICATOR == "11" and AGE < 19:
                if RELATIONSHIP_HOH == 1:
                    return false_case
                else:
                    return true_case
            else:
                return true_case
        except Exception:
            vals = {
                "WORK_ELIGIBLE_INDICATOR": WORK_ELIGIBLE_INDICATOR,
                "RELATIONSHIP_HOH": RELATIONSHIP_HOH,
            }
            logger.debug(
                "Caught exception in validator: validate__WORK_ELIGIBLE_INDICATOR__HOH__AGE. " +
                f"With field values: {vals}."
            )
            # Per conversation with Alex on 03/26/2024, returning the true case during exception handling to avoid
            # confusing the STTs.
            return true_case

    return validate
