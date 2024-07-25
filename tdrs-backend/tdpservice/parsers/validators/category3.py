import datetime
import logging
from tdpservice.parsers.util import get_record_value_by_field_name
from .base import ValidatorFunctions
from .util import ValidationErrorArgs, make_validator, evaluate_all

logger = logging.getLogger(__name__)

# @staticmethod
def format_error_context(eargs: ValidationErrorArgs):
    """Format the error message for consistency across cat3 validators."""
    return f'Item {eargs.item_num} ({eargs.friendly_name})'


# decorator takes ValidatorFunction as arg
# function handles error msg
# commit and msg eric

class PostparsingValidators():
    @staticmethod
    def isEqual(option, **kwargs):
        return make_validator(
            ValidatorFunctions.isEqual(option, **kwargs),
            lambda eargs: f'{format_error_context(eargs)} {eargs.value} must match {option}.'
        )

    @staticmethod
    def isNotEqual(option, **kwargs):
        return make_validator(
            ValidatorFunctions.isNotEqual(option, **kwargs),
            lambda eargs: f'{eargs.value} must not be equal to {option}.'
        )

    @staticmethod
    def isOneOf(options, **kwargs):
        return make_validator(
            ValidatorFunctions.isOneOf(options, **kwargs),
            lambda eargs: f'{eargs.value} must be one of {options}.'
        )

    @staticmethod
    def isNotOneOf(options, **kwargs):
        return make_validator(
            ValidatorFunctions.isNotOneOf(options, **kwargs),
            lambda eargs: f'{eargs.value} must not be one of {options}.'
        )

    @staticmethod
    def isGreaterThan(option, inclusive=False, **kwargs):
        return make_validator(
            ValidatorFunctions.isGreaterThan(option, inclusive, **kwargs),
            lambda eargs: f'{eargs.value} must be greater than {option}.'
        )

    @staticmethod
    def isLessThan(option, inclusive=False, **kwargs):
        return make_validator(
            ValidatorFunctions.isLessThan(option, inclusive, **kwargs),
            lambda eargs: f'{eargs.value} must be less than {option}.'
        )

    @staticmethod
    def isBetween(min, max, inclusive=False, **kwargs):
        return make_validator(
            ValidatorFunctions.isBetween(min, max, inclusive, **kwargs),
            lambda eargs: f'{eargs.value} must be between {min} and {max}.'
        )

    @staticmethod
    def startsWith(substr, **kwargs):
        return make_validator(
            ValidatorFunctions.startsWith(substr, **kwargs),
            lambda eargs: f'{eargs.value} must start with {substr}.'
        )

    @staticmethod
    def contains(substr, **kwargs):
        return make_validator(
            ValidatorFunctions.contains(substr, **kwargs),
            lambda eargs: f'{eargs.value} must contain {substr}.'
        )

    @staticmethod
    def isNumber(**kwargs):
        return make_validator(
            ValidatorFunctions.isNumber(**kwargs),
            lambda eargs: f'{eargs.value} must be a number.'
        )

    @staticmethod
    def isAlphaNumeric(**kwargs):
        return make_validator(
            ValidatorFunctions.isAlphaNumeric(**kwargs),
            lambda eargs: f'{eargs.value} must be alphanumeric.'
        )

    @staticmethod
    def isEmpty(start=0, end=None, **kwargs):
        return make_validator(
            ValidatorFunctions.isEmpty(start, end, **kwargs),
            lambda eargs: f'{eargs.value} must be empty.'
        )

    @staticmethod
    def isNotEmpty(start=0, end=None, **kwargs):
        return make_validator(
            ValidatorFunctions.isNotEmpty(start, end, **kwargs),
            lambda eargs: f'{eargs.value} must not be empty.'
        )

    @staticmethod
    def isBlank(**kwargs):
        return make_validator(
            ValidatorFunctions.isBlank(**kwargs),
            lambda eargs: f'{eargs.value} must be blank.'
        )

    @staticmethod
    def hasLength(length, **kwargs):
        return make_validator(
            ValidatorFunctions.hasLength(length, **kwargs),
            lambda eargs: f'{eargs.value} must have length {length}.'
        )

    @staticmethod
    def hasLengthGreaterThan(length, inclusive=False, **kwargs):
        return make_validator(
            ValidatorFunctions.hasLengthGreaterThan(length, inclusive, **kwargs),
            lambda eargs: f'{eargs.value} must have length greater than {length}.'
        )

    @staticmethod
    def intHasLength(length, **kwargs):
        return make_validator(
            ValidatorFunctions.intHasLength(length, **kwargs),
            lambda eargs: f'{eargs.value} must have length {length}.'
        )

    @staticmethod
    def isNotZero(number_of_zeros=1, **kwargs):
        return make_validator(
            ValidatorFunctions.isNotZero(number_of_zeros, **kwargs),
            lambda eargs: f'{eargs.value} must not be zero.'
        )

    @staticmethod
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
                # error_context_format='inline'
            )
            condition_success, msg1 = condition_function(condition_value, condition_field_eargs)

            result_value = get_record_value_by_field_name(record, result_field_name)
            result_field = row_schema.get_field_by_name(result_field_name)
            result_field_eargs = ValidationErrorArgs(
                value=result_value,
                row_schema=row_schema,
                friendly_name=result_field.friendly_name,
                item_num=result_field.item,
                # error_context_format='inline'
            )
            result_success, msg2 = result_function(result_value, result_field_eargs)

            fields = [condition_field_name, result_field_name]

            if not condition_success:
                return (True, None, fields)
            elif not result_success:
                center_error = None
                if condition_success:
                    center_error = f'{format_error_context(condition_field_eargs)} is {condition_value}' if condition_success else msg1
                else:
                    center_error = msg1
                error_message = f"If {center_error}, then {msg2}"
                return (result_success, error_message, fields)
            else:
                return (result_success, None, fields)

        return if_then_validator_func

    @staticmethod
    def orValidators(validators, **kwargs):
        """Return a validator that is true only if one of the validators is true."""
        def _validate(value, eargs):
            validator_results = evaluate_all(validators, value, eargs)

            if not any(result[0] for result in validator_results):
                return (False, " or ".join([result[1] for result in validator_results]))
            return (True, None)

        return _validate

    @staticmethod
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
                return (True, None, fields)
            return (
                False,
                f"{row_schema.record_type}: The sum of {sum_fields} does not equal {condition_field_name} "
                f"{condition_field.friendly_name} Item {condition_field.item}.",
                fields
            )

        return sumIsEqualFunc

    @staticmethod
    def sumIsLarger(fields, val):
        """Validate that the sum of the fields is larger than val."""
        def sumIsLargerFunc(record, row_schema):
            sum = 0
            for field in fields:
                temp_val = get_record_value_by_field_name(record, field)
                sum += 0 if temp_val is None else temp_val

            if sum > val:
                return (True, None, fields)

            return (
                False,
                f"{row_schema.record_type}: The sum of {fields} is not larger than {val}.",
                fields,
            )

        return sumIsLargerFunc

    @staticmethod
    def validate__FAM_AFF__SSN():
        """
        Validate social security number provided.

        If item FAMILY_AFFILIATION ==2 and item CITIZENSHIP_STATUS ==1 or 2,
        then item SSN != 000000000 -- 999999999.
        """
        # value is instance
        def validate(instance, row_schema):
            FAMILY_AFFILIATION = (
                instance["FAMILY_AFFILIATION"]
                if type(instance) is dict
                else getattr(instance, "FAMILY_AFFILIATION")
            )
            CITIZENSHIP_STATUS = (
                instance["CITIZENSHIP_STATUS"]
                if type(instance) is dict
                else getattr(instance, "CITIZENSHIP_STATUS")
            )
            SSN = instance["SSN"] if type(instance) is dict else getattr(instance, "SSN")
            if FAMILY_AFFILIATION == 2 and (
                CITIZENSHIP_STATUS == 1 or CITIZENSHIP_STATUS == 2
            ):
                if SSN in [str(i) * 9 for i in range(10)]:
                    return (
                        False,
                        f"{row_schema.record_type}: If FAMILY_AFFILIATION ==2 and CITIZENSHIP_STATUS==1 or 2, "
                        "then SSN != 000000000 -- 999999999.",
                        ["FAMILY_AFFILIATION", "CITIZENSHIP_STATUS", "SSN"],
                    )
                else:
                    return (True, None, ["FAMILY_AFFILIATION", "CITIZENSHIP_STATUS", "SSN"])
            else:
                return (True, None, ["FAMILY_AFFILIATION", "CITIZENSHIP_STATUS", "SSN"])

        return validate

    @staticmethod
    def validateSSN():
        """Validate that SSN value is not a repeating digit."""
        options = [str(i) * 9 for i in range(0, 10)]
        return make_validator(
            lambda value: value not in options,
            lambda eargs: f"{format_error_context(eargs)} {eargs.value} is in {options}."
        )

    @staticmethod
    def validate__WORK_ELIGIBLE_INDICATOR__HOH__AGE():
        """If WORK_ELIGIBLE_INDICATOR == 11 and AGE < 19, then RELATIONSHIP_HOH != 1."""
        # value is instance
        def validate(instance, row_schema):
            false_case = (False,
                        f"{row_schema.record_type}: If WORK_ELIGIBLE_INDICATOR == 11 and AGE < 19, "
                        "then RELATIONSHIP_HOH != 1",
                        ['WORK_ELIGIBLE_INDICATOR', 'RELATIONSHIP_HOH', 'DATE_OF_BIRTH']
                        )
            true_case = (True,
                        None,
                        ['WORK_ELIGIBLE_INDICATOR', 'RELATIONSHIP_HOH', 'DATE_OF_BIRTH'],
                        )
            try:
                WORK_ELIGIBLE_INDICATOR = (
                    instance["WORK_ELIGIBLE_INDICATOR"]
                    if type(instance) is dict
                    else getattr(instance, "WORK_ELIGIBLE_INDICATOR")
                )
                RELATIONSHIP_HOH = (
                    instance["RELATIONSHIP_HOH"]
                    if type(instance) is dict
                    else getattr(instance, "RELATIONSHIP_HOH")
                )
                RELATIONSHIP_HOH = int(RELATIONSHIP_HOH)

                DOB = str(
                    instance["DATE_OF_BIRTH"]
                    if type(instance) is dict
                    else getattr(instance, "DATE_OF_BIRTH")
                )

                RPT_MONTH_YEAR = str(
                    instance["RPT_MONTH_YEAR"]
                    if type(instance) is dict
                    else getattr(instance, "RPT_MONTH_YEAR")
                )

                RPT_MONTH_YEAR += "01"

                DOB_datetime = datetime.datetime.strptime(DOB, '%Y%m%d')
                RPT_MONTH_YEAR_datetime = datetime.datetime.strptime(RPT_MONTH_YEAR, '%Y%m%d')
                AGE = (RPT_MONTH_YEAR_datetime - DOB_datetime).days / 365.25

                if WORK_ELIGIBLE_INDICATOR == "11" and AGE < 19:
                    if RELATIONSHIP_HOH == 1:
                        return false_case
                    else:
                        return true_case
                else:
                    return true_case
            except Exception:
                vals = {"WORK_ELIGIBLE_INDICATOR": WORK_ELIGIBLE_INDICATOR,
                        "RELATIONSHIP_HOH": RELATIONSHIP_HOH,
                        "DOB": DOB
                        }
                logger.debug("Caught exception in validator: validate__WORK_ELIGIBLE_INDICATOR__HOH__AGE. " +
                            f"With field values: {vals}.")
                # Per conversation with Alex on 03/26/2024, returning the true case during exception handling to avoid
                # confusing the STTs.
                return true_case

        return validate

    @staticmethod
    def olderThan(min_age):
        """Validate that value is larger than min_age."""
        return make_validator(
            lambda value: datetime.date.today().year - int(str(value)[:4]) > min_age,
            lambda eargs:
                f"{format_error_context(eargs)} {str(eargs.value)[:4]} must be less "
                f"than or equal to {datetime.date.today().year - min_age} to meet the minimum age requirement."
        )
