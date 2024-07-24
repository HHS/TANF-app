from tdpservice.parsers.util import get_record_value_by_field_name
from .base import ValidatorFunctions
from .util import ValidationErrorArgs, make_validator

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
    def isAlphanumeric(**kwargs):
        return make_validator(
            ValidatorFunctions.isAlphanumeric(**kwargs),
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
                error_context_format='inline'
            )
            condition_success, msg1 = condition_function(condition_value, condition_field_eargs)

            result_value = get_record_value_by_field_name(record, result_field_name)
            result_field = row_schema.get_field_by_name(result_field_name)
            result_field_eargs = ValidationErrorArgs(
                value=result_value,
                row_schema=row_schema,
                friendly_name=result_field.friendly_name,
                item_num=result_field.item,
                error_context_format='inline'
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

        if_then_validator_func

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
