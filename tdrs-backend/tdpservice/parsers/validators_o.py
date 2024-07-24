"""Generic parser validator functions for use in schema definitions."""

import datetime
import logging
import functools
from dataclasses import dataclass
from abc import ABC, abstractmethod
from typing import Any
from tdpservice.parsers.models import ParserErrorCategoryChoices
from tdpservice.parsers.util import fiscal_to_calendar, year_month_to_year_quarter, clean_options_string, get_record_value_by_field_name

logger = logging.getLogger(__name__)


# helpers

def decorator(func):
    @functools.wraps(func)
    def wrapper_decorator(*args, **kwargs):
        # Do something before
        value = func(*args, **kwargs)
        # Do something after
        return value
    return wrapper_decorator


# def make_validator(validator_func, error_func):
#     """Return a function accepting a value input and returning (bool, string) to represent validation state."""
#     def validator(
#             value,
#             validator_option=None,
#             row_schema=None,
#             friendly_name=None,
#             item_num=None,
#             error_context_format='prefix'
#         ):
#         eargs = ValidationErrorArgs(
#             value=value,
#             row_schema=row_schema,
#             friendly_name=friendly_name,
#             item_num=item_num,
#             error_context_format=error_context_format
#         )

#         try:
#             if validator_func(value):
#                 return (True, None)
#             return (False, error_func(eargs))
#         except Exception:
#             logger.exception("Caught exception in validator.")
#             return (False, error_func(eargs))
#     return validator


def make_validator(validator_func, error_func):
    def validator(value, eargs):
        try:
            if validator_func(value):
                return (True, None)
        except Exception:
            logger.exception("Caught exception in validator.")
        return (False, error_func(eargs))

    return validator


# def value_is_empty(value, length, extra_vals={}):
#     """Handle 'empty' values as field inputs."""
#     # TODO: have to build mixed type handling for value
#     empty_values = {
#         '',
#         ' '*length,  # '     '
#         '#'*length,  # '#####'
#         '_'*length,  # '_____'
#     }

#     empty_values = empty_values.union(extra_vals)

#     return value is None or value in empty_values


# def _is_empty(value, start, end):
#     end = end if end else len(str(value))
#     vlen = end - start
#     subv = str(value)[start:end]
#     return value_is_empty(subv, vlen) or len(subv) < vlen


# def evaluate_all(validators, value, eargs):
#     return [
#         validator(value, eargs)
#         for validator in validators
#     ]


# class ValidatorFunctions:
#     @staticmethod
#     def _handle_cast(val, cast):
#         return cast(val)

#     @staticmethod
#     def _handle_kwargs(val, **kwargs):
#         if 'cast' in kwargs:
#             val = ValidatorFunctions._handle_cast(val, kwargs['cast'])

#         return val

#     @staticmethod
#     def _make_validator(func, **kwargs):
#         def _validate(val):
#             val = ValidatorFunctions._handle_kwargs(val, kwargs)
#             return func(val)
#         return _validate

#     @staticmethod
#     def isEqual(option, **kwargs):
#         return ValidatorFunctions._make_validator(
#             lambda val: val == option,
#             kwargs
#         )

#     @staticmethod
#     def isNotEqual(option, **kwargs):
#         return ValidatorFunctions._make_validator(
#             lambda val: val != option,
#             kwargs
#         )

#     @staticmethod
#     def isOneOf(options, **kwargs):
#         def check_option(value):
#             # split the option if it is a range and append the range to the options
#             for option in options:
#                 if "-" in str(option):
#                     start, end = option.split("-")
#                     options.extend([i for i in range(int(start), int(end) + 1)])
#                     options.remove(option)
#             return value in options

#         return ValidatorFunctions._make_validator(
#             lambda val: check_option(val),
#             kwargs
#         )

#     def isNotOneOf(options, **kwargs):
#         return ValidatorFunctions._make_validator(
#             lambda val: val not in options,
#             kwargs
#         )

#     @staticmethod
#     def isGreaterThan(option, inclusive=False, **kwargs):
#         return ValidatorFunctions._make_validator(
#             lambda val: val > option if not inclusive else val >= option,
#             kwargs
#         )

#     @staticmethod
#     def isLessThan(option, inclusive=False, **kwargs):
#         return ValidatorFunctions._make_validator(
#             lambda val: val < option if not inclusive else val <= option,
#             kwargs
#         )

#     @staticmethod
#     def isBetween(min, max, inclusive=False, **kwargs):
#         return ValidatorFunctions._make_validator(
#             lambda val: min < val < max if not inclusive else min <= val <= max,
#             kwargs
#         )

#     @staticmethod
#     def startsWith(substr, **kwargs):
#         return ValidatorFunctions._make_validator(
#             lambda val: str(val).startswith(substr),
#             kwargs
#         )

#     @staticmethod
#     def contains(substr, **kwargs):
#         return ValidatorFunctions._make_validator(
#             lambda val: str(val).find(substr) != -1,
#             kwargs
#         )

#     @staticmethod
#     def isNumber(**kwargs):
#         return ValidatorFunctions._make_validator(
#             lambda val: str(val).strip().isnumeric(),
#             kwargs
#         )

#     @staticmethod
#     def isAlphanumeric(**kwargs):
#         return ValidatorFunctions._make_validator(
#             lambda val: val.isalnum(),
#             kwargs
#         )

#     @staticmethod
#     def isEmpty(start=0, end=None, **kwargs):
#         return ValidatorFunctions._make_validator(
#             lambda val: not _is_empty(val, start, end),
#             kwargs
#         )

#     @staticmethod
#     def isNotEmpty(start=0, end=None, **kwargs):
#         return ValidatorFunctions._make_validator(
#             lambda val: _is_empty(val, start, end),
#             kwargs
#         )

#     @staticmethod
#     def isBlank(**kwargs):
#         return ValidatorFunctions._make_validator(
#             lambda val: val.isspace(),
#             kwargs
#         )

#     @staticmethod
#     def hasLength(length, **kwargs):
#         return ValidatorFunctions._make_validator(
#             lambda val: len(val) == length,
#             kwargs
#         )

#     @staticmethod
#     def hasLengthGreaterThan(length, inclusive=False, **kwargs):
#         return ValidatorFunctions._make_validator(
#             lambda val: len(val) > length if not inclusive else len(val) >= length,
#             kwargs
#         )

#     @staticmethod
#     def intHasLength(length, **kwargs):
#         return ValidatorFunctions._make_validator(
#             lambda val: sum(c.isdigit() for c in str(val)) == length,
#             kwargs
#         )

#     @staticmethod
#     def isNotZero(number_of_zeros=1, **kwargs):
#         return ValidatorFunctions._make_validator(
#             lambda val: val != "0" * number_of_zeros,
#             kwargs
#         )


# class PreparsingValidators(ValidatorFunctions):
#     @staticmethod
#     def recordHasLength():
#         pass

#     @staticmethod
#     def or_priority_validators():
#         pass


# class FieldValidators():
#     @staticmethod
#     def isEqual(option, **kwargs):
#         return make_validator(
#             ValidatorFunctions.isEqual(option, kwargs),
#             lambda eargs: f"{format_error_context(eargs)} {eargs.value} does not match {option}."
#         )

#     @staticmethod
#     def isNotEqual(option, **kwargs):
#         return make_validator(
#             ValidatorFunctions.isNotEqual(option, kwargs),
#             lambda eargs: f"{format_error_context(eargs)} {eargs.value} matches {option}."
#         )

#     @staticmethod
#     def isOneOf(options, **kwargs):
#         return make_validator(
#             ValidatorFunctions.isOneOf(options, kwargs),
#             lambda eargs: f"{format_error_context(eargs)} {eargs.value} is not in {clean_options_string(options)}."
#         )

#     @staticmethod
#     def isNotOneOf(options, **kwargs):
#         return make_validator(
#             ValidatorFunctions.isOneOf(options, kwargs),
#             lambda eargs: f"{format_error_context(eargs)} {eargs.value} is in {clean_options_string(options)}."
#         )

#     @staticmethod
#     def isGreaterThan(option, inclusive=False, **kwargs):
#         return make_validator(
#             ValidatorFunctions.isGreaterThan(option, inclusive, kwargs),
#             lambda eargs: f"{format_error_context(eargs)} {eargs.value} is not larger than {option}."
#         )

#     @staticmethod
#     def isLessThan(option, inclusive=False, **kwargs):
#         return make_validator(
#             ValidatorFunctions.isLessThan(option, inclusive, kwargs),
#             lambda eargs: f"{format_error_context(eargs)} {eargs.value} is not smaller than {option}."
#         )

#     @staticmethod
#     def isBetween(min, max, inclusive=False, **kwargs):
#         def inclusive_err(eargs):
#             return f"{format_error_context(eargs)} {eargs.value} is not in range [{min}, {max}]."

#         def exclusive_err(eargs):
#             return f"{format_error_context(eargs)} {eargs.value} is not between {min} and {max}.",

#         return make_validator(
#             ValidatorFunctions.isBetween(min, max, inclusive, kwargs),
#             inclusive_err if inclusive else exclusive_err
#         )

#     @staticmethod
#     def startsWith(substr, **kwargs):
#         return make_validator(
#             ValidatorFunctions.startsWith(substr, kwargs),
#             lambda eargs: f"{format_error_context(eargs)} {eargs.value} does not start with {substr}."
#         )

#     @staticmethod
#     def contains(substr, **kwargs):
#         return make_validator(
#             ValidatorFunctions.startsWith(substr, kwargs),
#             lambda eargs: f"{format_error_context(eargs)} {eargs.value} does not contain {substr}."
#         )

#     @staticmethod
#     def isNumber(**kwargs):
#         return make_validator(
#             ValidatorFunctions.isNumber(kwargs),
#             lambda eargs: f"{format_error_context(eargs)} {eargs.value} is not a number."
#         )

#     @staticmethod
#     def isAlphanumeric(**kwargs):
#         return make_validator(
#             ValidatorFunctions.isAlphanumeric(kwargs),
#             lambda eargs: f"{format_error_context(eargs)} {eargs.value} is not alphanumeric."
#         )

#     @staticmethod
#     def isEmpty(start=0, end=None, **kwargs):
#         return make_validator(
#             ValidatorFunctions.isEmpty(kwargs),
#             lambda eargs: f'{format_error_context(eargs)} {eargs.value} is not blank '
#             f'between positions {start} and {end if end else len(eargs.value)}.'
#         )

#     @staticmethod
#     def isNotEmpty(start=0, end=None, **kwargs):
#         return make_validator(
#             ValidatorFunctions.isNotEmpty(kwargs),
#             lambda eargs: f'{format_error_context(eargs)} {str(eargs.value)} contains blanks '
#             f'between positions {start} and {end if end else len(str(eargs.value))}.'
#         )

#     @staticmethod
#     def isBlank(**kwargs):
#         return make_validator(
#             ValidatorFunctions.isBlank(kwargs),
#             lambda eargs: f"{format_error_context(eargs)} {eargs.value} is not blank."
#         )

#     @staticmethod
#     def hasLength(length, **kwargs):
#         return make_validator(
#             ValidatorFunctions.hasLength(length, kwargs),
#             lambda eargs: f"{format_error_context(eargs)} field length "
#             f"is {len(eargs.value)} characters but must be {length}.",
#         )

#     @staticmethod
#     def hasLengthGreaterThan(length, inclusive=False, **kwargs):
#         return make_validator(
#             ValidatorFunctions.hasLengthGreaterThan(length, inclusive, kwargs),
#             lambda eargs: f"{format_error_context(eargs)} Value length {len(eargs.value)} is not greater than {length}."
#         )

#     @staticmethod
#     def intHasLength(length, **kwargs):
#         return make_validator(
#             ValidatorFunctions.hasLengthGreaterThan(length, kwargs),
#             lambda eargs: f"{format_error_context(eargs)} {eargs.value} does not have exactly {length} digits.",
#         )

#     @staticmethod
#     def isNotZero(number_of_zeros=1, **kwargs):
#         return make_validator(
#             ValidatorFunctions.isNotZero(number_of_zeros, kwargs),
#             lambda eargs: f"{format_error_context(eargs)} {eargs.value} is zero."
#         )

#     @staticmethod
#     def orValidators(validators, **kwargs):
#         """Return a validator that is true only if one of the validators is true."""
#         def _validate(value, eargs):
#             validator_results = evaluate_all(validators, value, eargs)

#             if not any(result[0] for result in validator_results):
#                 return (False, " or ".join([result[1] for result in validator_results]))
#             return (True, None)

#         return _validate


# class PostparsingValidators(ValidatorFunctions):
#     @staticmethod
#     def isEqual(option, **kwargs):
#         return make_validator(
#             ValidatorFunctions.isEqual(option, kwargs),
#             lambda eargs: f'{eargs.value} must be equal to {option}.'
#         )

#     @staticmethod
#     def isNotEqual(option, **kwargs):
#         return make_validator(
#             ValidatorFunctions.isNotEqual(option, kwargs),
#             lambda eargs: f'{eargs.value} must not be equal to {option}.'
#         )

#     @staticmethod
#     def isOneOf(options, **kwargs):
#         return make_validator(
#             ValidatorFunctions.isOneOf(options, kwargs),
#             lambda eargs: f'{eargs.value} must be one of {options}.'
#         )

#     @staticmethod
#     def isNotOneOf(options, **kwargs):
#         return make_validator(
#             ValidatorFunctions.isNotOneOf(options, kwargs),
#             lambda eargs: f'{eargs.value} must not be one of {options}.'
#         )

#     @staticmethod
#     def isGreaterThan(option, inclusive=False, **kwargs):
#         return make_validator(
#             ValidatorFunctions.isGreaterThan(option, inclusive, kwargs),
#             lambda eargs: f'{eargs.value} must be greater than {option}.'
#         )

#     @staticmethod
#     def isLessThan(option, inclusive=False, **kwargs):
#         return make_validator(
#             ValidatorFunctions.isLessThan(option, inclusive, kwargs),
#             lambda eargs: f'{eargs.value} must be less than {option}.'
#         )

#     @staticmethod
#     def isBetween(min, max, inclusive=False, **kwargs):
#         return make_validator(
#             ValidatorFunctions.isBetween(min, max, inclusive, kwargs),
#             lambda eargs: f'{eargs.value} must be between {min} and {max}.'
#         )

#     @staticmethod
#     def startsWith(substr, **kwargs):
#         return make_validator(
#             ValidatorFunctions.startsWith(substr, kwargs),
#             lambda eargs: f'{eargs.value} must start with {substr}.'
#         )

#     @staticmethod
#     def contains(substr, **kwargs):
#         return make_validator(
#             ValidatorFunctions.contains(substr, kwargs),
#             lambda eargs: f'{eargs.value} must contain {substr}.'
#         )

#     @staticmethod
#     def isNumber(**kwargs):
#         return make_validator(
#             ValidatorFunctions.isNumber(kwargs),
#             lambda eargs: f'{eargs.value} must be a number.'
#         )

#     @staticmethod
#     def isAlphanumeric(**kwargs):
#         return make_validator(
#             ValidatorFunctions.isAlphanumeric(kwargs),
#             lambda eargs: f'{eargs.value} must be alphanumeric.'
#         )

#     @staticmethod
#     def isEmpty(start=0, end=None, **kwargs):
#         return make_validator(
#             ValidatorFunctions.isEmpty(start, end, kwargs),
#             lambda eargs: f'{eargs.value} must be empty.'
#         )

#     @staticmethod
#     def isNotEmpty(start=0, end=None, **kwargs):
#         return make_validator(
#             ValidatorFunctions.isNotEmpty(start, end, kwargs),
#             lambda eargs: f'{eargs.value} must not be empty.'
#         )

#     @staticmethod
#     def isBlank(**kwargs):
#         return make_validator(
#             ValidatorFunctions.isBlank(kwargs),
#             lambda eargs: f'{eargs.value} must be blank.'
#         )

#     @staticmethod
#     def hasLength(length, **kwargs):
#         return make_validator(
#             ValidatorFunctions.hasLength(length, kwargs),
#             lambda eargs: f'{eargs.value} must have length {length}.'
#         )

#     @staticmethod
#     def hasLengthGreaterThan(length, inclusive=False, **kwargs):
#         return make_validator(
#             ValidatorFunctions.hasLengthGreaterThan(length, inclusive, kwargs),
#             lambda eargs: f'{eargs.value} must have length greater than {length}.'
#         )

#     @staticmethod
#     def intHasLength(length, **kwargs):
#         return make_validator(
#             ValidatorFunctions.intHasLength(length, kwargs),
#             lambda eargs: f'{eargs.value} must have length {length}.'
#         )

#     @staticmethod
#     def isNotZero(number_of_zeros=1, **kwargs):
#         return make_validator(
#             ValidatorFunctions.isNotZero(number_of_zeros, kwargs),
#             lambda eargs: f'{eargs.value} must not be zero.'
#         )

#     @staticmethod
#     def if_then_validator(condition_field_name, condition_function, result_field_name, result_function, **kwargs):
#         """Return second validation if the first validator is true.
#         :param condition_field: function that returns (bool, string) to represent validation state
#         :param condition_function: function that returns (bool, string) to represent validation state
#         :param result_field: function that returns (bool, string) to represent validation state
#         :param result_function: function that returns (bool, string) to represent validation state
#         """
#         def if_then_validator_func(record, row_schema):
#             condition_value = get_record_value_by_field_name(record, condition_field_name)
#             condition_field = row_schema.get_field_by_name(condition_field_name)
#             condition_field_eargs = ValidationErrorArgs(
#                 value=condition_value,
#                 row_schema=row_schema,
#                 friendly_name=condition_field.friendly_name,
#                 item_num=condition_field.item,
#                 error_context_format='inline'
#             )
#             condition_success, msg1 = condition_function(condition_value, condition_field_eargs)

#             result_value = get_record_value_by_field_name(record, result_field_name)
#             result_field = row_schema.get_field_by_name(result_field_name)
#             result_field_eargs = ValidationErrorArgs(
#                 value=result_value,
#                 row_schema=row_schema,
#                 friendly_name=result_field.friendly_name,
#                 item_num=result_field.item,
#                 error_context_format='inline'
#             )
#             result_success, msg2 = result_function(result_value, result_field_eargs)

#             fields = [condition_field_name, result_field_name]

#             if not condition_success:
#                 return (True, None, fields)
#             elif not result_success:
#                 center_error = None
#                 if condition_success:
#                     center_error = f'{format_error_context(condition_field_eargs)} is {condition_value}' if condition_success else msg1
#                 else:
#                     center_error = msg1
#                 error_message = f"If {center_error}, then {msg2}"
#                 return (result_success, error_message, fields)
#             else:
#                 return (result_success, None, fields)

#         if_then_validator_func

#     @staticmethod
#     def sumIsEqual(condition_field_name, sum_fields=[]):
#         """Validate that the sum of the sum_fields equals the condition_field."""
#         def sumIsEqualFunc(record, row_schema):
#             sum = 0
#             for field in sum_fields:
#                 val = get_record_value_by_field_name(record, field)
#                 sum += 0 if val is None else val

#             condition_val = get_record_value_by_field_name(record, condition_field_name)
#             condition_field = row_schema.get_field_by_name(condition_field_name)
#             fields = [condition_field_name]
#             fields.extend(sum_fields)

#             if sum == condition_val:
#                 return (True, None, fields)
#             return (
#                 False,
#                 f"{row_schema.record_type}: The sum of {sum_fields} does not equal {condition_field_name} "
#                 "{condition_field.friendly_name} Item {condition_field.item}.",
#                 fields
#             )

#         return sumIsEqualFunc

#     @staticmethod
#     def sumIsLarger(fields, val):
#         """Validate that the sum of the fields is larger than val."""
#         def sumIsLargerFunc(record, row_schema):
#             sum = 0
#             for field in fields:
#                 temp_val = get_record_value_by_field_name(record, field)
#                 sum += 0 if temp_val is None else temp_val

#             if sum > val:
#                 return (True, None, fields)

#             return (
#                 False,
#                 f"{row_schema.record_type}: The sum of {fields} is not larger than {val}.",
#                 fields,
#             )

#         return sumIsLargerFunc


class CustomValidators():
    @staticmethod
    def validate__FAM_AFF__SSN():
        pass


# @dataclass
# class ValidationErrorArgs:
#     """Dataclass for args to `make_validator` `error_func`s."""

#     value: Any
#     validation_option: Any
#     row_schema: object  # RowSchema causes circular import
#     friendly_name: str
#     item_num: str
#     error_context_format: str = 'prefix'


# def format_error_context(eargs: ValidationErrorArgs):
#     """Format the error message for consistency across cat2 validators."""
#     match eargs.error_context_format:
#         case 'inline':
#             return f'Item {eargs.item_num} ({eargs.friendly_name})'

#         case 'prefix' | _:
#             return f'{eargs.row_schema.record_type} Item {eargs.item_num} ({eargs.friendly_name}):'


# postparsing validators


# def or_validators(*args, **kwargs):
#     """Return a validator that is true only if one of the validators is true."""
#     def _validate(validators, value, row_schema, friendly_name, item_num, error_context_format):
#         validator_results = evaluate_all(validators, value, row_schema, friendly_name, item_num, error_context_format)

#         if not any(result[0] for result in validator_results):
#             return (False, " or ".join([result[1] for result in validator_results]))
#         return (True, None)

#     return (
#         lambda value, row_schema, friendly_name,
#         item_num, error_context_format='inline':
#             _validate(args, value, row_schema, friendly_name, item_num, error_context_format)
#     )


# def and_validators(validator1, validator2):
#     """Return a validator that is true only if both validators are true."""
#     def _validate(validators, value, row_schema, friendly_name, item_num, error_context_format):
#         validator_results = evaluate_all(validators, value, row_schema, friendly_name, item_num, error_context_format)
#         result1, msg1 = validator_results[0]
#         result2, msg2 = validator_results[1]

#         if result1 and result2:
#             return (True, None)
#         elif result1 and not result2:
#             return (False, "1 but not 2")
#         elif result2 and not result1:
#             return (False, "2 but not 1")
#         else:
#             return (False, "Neither")

#     return (
#         lambda value, row_schema, friendly_name, item_num:
#             _validate([validator1, validator2], value, row_schema, friendly_name, item_num, 'inline')
#     )


# def or_priority_validators(validators=[]):
#     """Return a validator that is true based on a priority of validators.

#     validators: ordered list of validators to be checked
#     """
#     def or_priority_validators_func(value, rows_schema, friendly_name=None, item_num=None):
#         for validator in validators:
#             result, msg = validator(value, rows_schema, friendly_name, item_num, 'inline')[0]
#             if not result:
#                 return (result, msg)
#         return (True, None)

#     return or_priority_validators_func


# def extended_and_validators(*args, **kwargs):
#     """Return a validator that is true only if all validators are true."""
#     def _validate(validators, value, row_schema, friendly_name, item_num, error_context_format):
#         validator_results = evaluate_all(validators, value, row_schema, friendly_name, item_num, error_context_format)

#         if not all(result[0] for result in validator_results):
#             return (False, " and ".join([result[1] for result in validator_results]))
#         return (True, None)

#     def returned_func(value, row_schema, friendly_name, item_num):
#         return _validate(args, value, row_schema, friendly_name, item_num, 'inline')
#     return returned_func


# def if_then_validator(
#     condition_field_name, condition_function, result_field_name, result_function
# ):
#     """Return second validation if the first validator is true.

#     :param condition_field: function that returns (bool, string) to represent validation state
#     :param condition_function: function that returns (bool, string) to represent validation state
#     :param result_field: function that returns (bool, string) to represent validation state
#     :param result_function: function that returns (bool, string) to represent validation state
#     """

#     def if_then_validator_func(record, row_schema):
#         condition_value = get_record_value_by_field_name(record, condition_field_name)
#         condition_field = row_schema.get_field_by_name(condition_field_name)
#         condition_success, msg1 = condition_function(
#             condition_value,
#             row_schema,
#             condition_field.friendly_name,
#             condition_field.item,
#             'inline'
#         )

#         result_value = get_record_value_by_field_name(record, result_field_name)
#         result_field = row_schema.get_field_by_name(result_field_name)
#         result_success, msg2 = result_function(
#             result_value,
#             row_schema,
#             result_field.friendly_name,
#             result_field.item,
#             'inline'
#         )

#         fields = [condition_field_name, result_field_name]

#         if not condition_success:
#             return (True, None, fields)
#         elif not result_success:
#             center_error = None
#             if condition_success:
#                 eargs = ValidationErrorArgs(
#                     value=condition_value,
#                     row_schema=row_schema,
#                     friendly_name=condition_field.friendly_name,
#                     item_num=condition_field.item,
#                     error_context_format='inline'
#                 )
#                 center_error = f'{format_error_context(eargs)} is {condition_value}' if condition_success else msg1
#             else:
#                 center_error = msg1
#             error_message = f"If {center_error}, then {msg2}"
#             return (result_success, error_message, fields)
#         else:
#             return (result_success, None, fields)

#     return lambda value, row_schema: if_then_validator_func(value, row_schema)


# def sumIsEqual(condition_field_name, sum_fields=[]):
#     """Validate that the sum of the sum_fields equals the condition_field."""

#     def sumIsEqualFunc(record, row_schema):
#         sum = 0
#         for field in sum_fields:
#             val = get_record_value_by_field_name(record, field)
#             sum += 0 if val is None else val

#         condition_val = get_record_value_by_field_name(record, condition_field_name)
#         condition_field = row_schema.get_field_by_name(condition_field_name)
#         fields = [condition_field_name]
#         fields.extend(sum_fields)

#         if sum == condition_val:
#             return (True, None, fields)
#         return (
#             False,
#             f"{row_schema.record_type}: The sum of {sum_fields} does not equal {condition_field_name} {condition_field.friendly_name} Item {condition_field.item}.",
#             fields
#         )

#     return sumIsEqualFunc


# def sumIsLarger(fields, val):
#     """Validate that the sum of the fields is larger than val."""

#     def sumIsLargerFunc(record, row_schema):
#         sum = 0
#         for field in fields:
#             temp_val = get_record_value_by_field_name(record, field)
#             sum += 0 if temp_val is None else temp_val

#         if sum > val:
#             return (True, None, fields)

#         return (
#             False,
#             f"{row_schema.record_type}: The sum of {fields} is not larger than {val}.",
#             fields,
#         )

#     return sumIsLargerFunc


# # preparsing validators


# def field_year_month_with_header_year_quarter():
#     """Validate that the field year and month match the header year and quarter."""
#     def validate_reporting_month_year_fields_header(
#             line, row_schema, friendly_name, item_num, error_context_format=None):

#         field_month_year = row_schema.get_field_values_by_names(line, ['RPT_MONTH_YEAR']).get('RPT_MONTH_YEAR')
#         df_quarter = row_schema.datafile.quarter
#         df_year = row_schema.datafile.year

#         # get reporting month year from header
#         field_year, field_quarter = year_month_to_year_quarter(f"{field_month_year}")
#         file_calendar_year, file_calendar_qtr = fiscal_to_calendar(df_year, f"{df_quarter}")
#         return (True, None) if str(file_calendar_year) == str(field_year) and file_calendar_qtr == field_quarter else (
#             False, f"{row_schema.record_type}: Reporting month year {field_month_year} " +
#             f"does not match file reporting year:{df_year}, quarter:{df_quarter}.",
#             )

#     return validate_reporting_month_year_fields_header


# def recordHasLength(length):
#     """Validate that value (string or array) has a length matching length param."""
#     return make_validator(
#         lambda value: len(value) == length,
#         lambda eargs: f"{eargs.row_schema.record_type}: record length is "
#         f"{len(eargs.value)} characters but must be {length}.",
#     )


# def recordHasLengthBetween(lower, upper, error_func=None):
#     """Validate that value (string or array) has a length matching length param."""
#     return make_validator(
#         lambda value: len(value) >= lower and len(value) <= upper,
#         lambda eargs: error_func(eargs.value, lower, upper)
#         if error_func
#         else
#         f"{eargs.row_schema.record_type}: record length of {len(eargs.value)} "
#         f"characters is not in the range [{lower}, {upper}].",
#     )


# def caseNumberNotEmpty(start=0, end=None):
#     """Validate that string value isn't only blanks."""
#     return make_validator(
#         lambda value: not _is_empty(value, start, end),
#         lambda eargs: f'{eargs.row_schema.record_type}: Case number {str(eargs.value)} cannot contain blanks.'
#     )


# def calendarQuarterIsValid(start=0, end=None):
#     """Validate that the calendar quarter value is valid."""
#     return make_validator(
#         lambda value: value[start:end].isnumeric() and int(value[start:end - 1]) >= 2020
#         and int(value[end - 1:end]) > 0 and int(value[end - 1:end]) < 5,
#         lambda eargs: f"{eargs.row_schema.record_type}: {eargs.value[start:end]} is invalid. "
#         "Calendar Quarter must be a numeric representing the Calendar Year and Quarter formatted as YYYYQ",
#     )


# # field validators


def matches(option, error_func=None):
    """Validate that value is equal to option."""
    return make_validator(
        lambda eargs: error_func(option)
        if error_func
        else f"{format_error_context(eargs)} {eargs.value} does not match {option}.",
    )


# def notMatches(option):
#     """Validate that value is not equal to option."""
#     return make_validator(
#         lambda value: value != option,
#         lambda eargs: f"{format_error_context(eargs)} {eargs.value} matches {option}."
#     )


# def oneOf(options=[]):
#     """Validate that value does not exist in the provided options array."""
#     """
#     accepts options as list of: string, int or string range ("3-20")
#     """

#     def check_option(value, options):
#         # split the option if it is a range and append the range to the options
#         for option in options:
#             if "-" in str(option):
#                 start, end = option.split("-")
#                 options.extend([i for i in range(int(start), int(end) + 1)])
#                 options.remove(option)
#         return value in options

#     return make_validator(
#         lambda value: check_option(value, options),
#         lambda eargs:
#             f"{format_error_context(eargs)} {eargs.value} is not in {clean_options_string(options)}."
#     )


# def notOneOf(options=[]):
#     """Validate that value exists in the provided options array."""
#     return make_validator(
#         lambda value: value not in options,
#         lambda eargs:
#             f"{format_error_context(eargs)} {eargs.value} is in {clean_options_string(options)}."
#     )


# def between(min, max):
#     """Validate value, when casted to int, is greater than min and less than max."""
#     return make_validator(
#         lambda value: int(value) > min and int(value) < max,
#         lambda eargs:
#             f"{format_error_context(eargs)} {eargs.value} is not between {min} and {max}.",
#     )


# def fieldHasLength(length):
#     """Validate that the field value (string or array) has a length matching length param."""
#     return make_validator(
#         lambda value: len(value) == length,
#         lambda eargs:
#             f"{eargs.row_schema.record_type} field length is {len(eargs.value)} characters but must be {length}.",
#     )


# def hasLengthGreaterThan(val, error_func=None):
#     """Validate that value (string or array) has a length greater than val."""
#     return make_validator(
#         lambda value: len(value) >= val,
#         lambda eargs:
#             f"Value length {len(eargs.value)} is not greater than {val}.",
#     )


# def intHasLength(num_digits):
#     """Validate the number of digits in an integer."""
#     return make_validator(
#         lambda value: sum(c.isdigit() for c in str(value)) == num_digits,
#         lambda eargs:
#             f"{format_error_context(eargs)} {eargs.value} does not have exactly {num_digits} digits.",
#     )


# def contains(substring):
#     """Validate that string value contains the given substring param."""
#     return make_validator(
#         lambda value: value.find(substring) != -1,
#         lambda eargs: f"{format_error_context(eargs)} {eargs.value} does not contain {substring}.",
#     )


# def startsWith(substring, error_func=None):
#     """Validate that string value starts with the given substring param."""
#     return make_validator(
#         lambda value: value.startswith(substring),
#         lambda eargs: error_func(substring)
#         if error_func
#         else f"{format_error_context(eargs)} {eargs.value} does not start with {substring}.",

#         '''
#         if Item 1 (Condition Field) is 1, then Item 2 (Result Field) xyz does not start with abc.
#         '''

#         # decoupling of cat2/3 error messages
#         # separate into different files

#         # refactor parser into class-based structure
#         # turn make_validator into a decorator
#     )


# def isNumber():
#     """Validate that value can be casted to a number."""
#     return make_validator(
#         lambda value: str(value).strip().isnumeric(),
#         lambda eargs: f"{format_error_context(eargs)} {eargs.value} is not a number."
#     )


# def isAlphaNumeric():
#     """Validate that value is alphanumeric."""
#     return make_validator(
#         lambda value: value.isalnum(),
#         lambda eargs: f"{format_error_context(eargs)} {eargs.value} is not alphanumeric."
#     )


# def isBlank():
#     """Validate that string value is blank."""
#     return make_validator(
#         lambda value: value.isspace(),
#         lambda eargs: f"{format_error_context(eargs)} {eargs.value} is not blank."
#     )


# def isInStringRange(lower, upper):
#     """Validate that string value is in a specific range."""
#     return make_validator(
#         lambda value: int(value) >= lower and int(value) <= upper,
#         lambda eargs: f"{format_error_context(eargs)} {eargs.value} is not in range [{lower}, {upper}].",
#     )


# def isStringLargerThan(val):
#     """Validate that string value is larger than val."""
#     return make_validator(
#         lambda value: int(value) > val,
#         lambda eargs: f"{format_error_context(eargs)} {eargs.value} is not larger than {val}.",
#     )


# def notEmpty(start=0, end=None):
#     """Validate that string value isn't only blanks."""
#     return make_validator(
#         lambda value: not _is_empty(value, start, end),
#         lambda eargs:
#             f'{format_error_context(eargs)} {str(eargs.value)} contains blanks '
#             f'between positions {start} and {end if end else len(str(eargs.value))}.'
#     )


# def isEmpty(start=0, end=None):
#     """Validate that string value is only blanks."""
#     return make_validator(
#         lambda value: _is_empty(value, start, end),
#         lambda eargs:
#             f'{format_error_context(eargs)} {eargs.value} is not blank '
#             f'between positions {start} and {end if end else len(eargs.value)}.'
#     )


# def notZero(number_of_zeros=1):
#     """Validate that value is not zero."""
#     return make_validator(
#         lambda value: value != "0" * number_of_zeros,
#         lambda eargs: f"{format_error_context(eargs)} {eargs.value} is zero."
#     )


# def isLargerThan(LowerBound):
#     """Validate that value is larger than the given value."""
#     return make_validator(
#         lambda value: float(value) > LowerBound if value is not None else False,
#         lambda eargs: f"{format_error_context(eargs)} {eargs.value} is not larger than {LowerBound}.",
#     )


# def isSmallerThan(UpperBound):
#     """Validate that value is smaller than the given value."""
#     return make_validator(
#         lambda value: value < UpperBound,
#         lambda eargs: f"{format_error_context(eargs)} {eargs.value} is not smaller than {UpperBound}.",
#     )


# def isLargerThanOrEqualTo(LowerBound):
#     """Validate that value is larger than the given value."""
#     return make_validator(
#         lambda value: value >= LowerBound,
#         lambda eargs: f"{format_error_context(eargs)} {eargs.value} is not larger than {LowerBound}.",
#     )


# def isSmallerThanOrEqualTo(UpperBound):
#     """Validate that value is smaller than the given value."""
#     return make_validator(
#         lambda value: value <= UpperBound,
#         lambda eargs: f"{format_error_context(eargs)} {eargs.value} is not smaller than {UpperBound}.",
#     )


# def isInLimits(LowerBound, UpperBound):
#     """Validate that value is in a range including the limits."""
#     return make_validator(
#         lambda value: int(value) >= LowerBound and int(value) <= UpperBound,
#         lambda eargs:
#             f"{format_error_context(eargs)} {eargs.value} is not larger or equal "
#             f"to {LowerBound} and smaller or equal to {UpperBound}."
#     )

# # custom validators

# def dateMonthIsValid():
#     """Validate that in a monthyear combination, the month is a valid month."""
#     return make_validator(
#         lambda value: int(str(value)[4:6]) in range(1, 13),
#         lambda eargs: f"{format_error_context(eargs)} {str(eargs.value)[4:6]} is not a valid month.",
#     )

# def dateDayIsValid():
#     """Validate that in a monthyearday combination, the day is a valid day."""
#     return make_validator(
#         lambda value: int(str(value)[6:]) in range(1, 32),
#         lambda eargs: f"{format_error_context(eargs)} {str(eargs.value)[6:]} is not a valid day.",
#     )


# def olderThan(min_age):
#     """Validate that value is larger than min_age."""
#     return make_validator(
#         lambda value: datetime.date.today().year - int(str(value)[:4]) > min_age,
#         lambda eargs:
#             f"{format_error_context(eargs)} {str(eargs.value)[:4]} must be less "
#             f"than or equal to {datetime.date.today().year - min_age} to meet the minimum age requirement."
#     )


# def dateYearIsLargerThan(year):
#     """Validate that in a monthyear combination, the year is larger than the given year."""
#     return make_validator(
#         lambda value: int(str(value)[:4]) > year,
#         lambda eargs: f"{format_error_context(eargs)} Year {str(eargs.value)[:4]} must be larger than {year}.",
#     )


# def quarterIsValid():
#     """Validate in a year quarter combination, the quarter is valid."""
#     return make_validator(
#         lambda value: int(str(value)[-1]) > 0 and int(str(value)[-1]) < 5,
#         lambda eargs: f"{format_error_context(eargs)} {str(eargs.value)[-1]} is not a valid quarter.",
#     )


# def validateSSN():
#     """Validate that SSN value is not a repeating digit."""
#     options = [str(i) * 9 for i in range(0, 10)]
#     return make_validator(
#         lambda value: value not in options,
#         lambda eargs: f"{format_error_context(eargs)} {eargs.value} is in {options}."
#     )


# def validateRace():
#     """Validate race."""
#     return make_validator(
#         lambda value: value >= 0 and value <= 2,
#         lambda eargs:
#             f"{format_error_context(eargs)} {eargs.value} is not greater than or equal to 0 "
#             "or smaller than or equal to 2."
#     )


# def validateRptMonthYear():
#     """Validate RPT_MONTH_YEAR."""
#     return make_validator(
#         lambda value: value[2:8].isdigit() and int(value[2:6]) > 1900 and value[6:8] in {"01", "02", "03", "04", "05",
#                                                                                          "06", "07", "08", "09", "10",
#                                                                                          "11", "12"},
#         lambda eargs:
#             f"{format_error_context(eargs)} The value: {eargs.value[2:8]}, "
#             "does not follow the YYYYMM format for Reporting Year and Month.",
#     )


# outlier validators

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

def validate_header_section_matches_submission(datafile, section, generate_error):
    """Validate header section matches submission section."""
    is_valid = datafile.section == section

    error = None
    if not is_valid:
        error = generate_error(
            schema=None,
            error_category=ParserErrorCategoryChoices.PRE_CHECK,
            error_message=f"Data does not match the expected layout for {datafile.section}.",
            record=None,
            field=None,
        )

    return is_valid, error


def validate_tribe_fips_program_agree(program_type, tribe_code, state_fips_code, generate_error):
    """Validate tribe code, fips code, and program type all agree with eachother."""
    is_valid = False

    if program_type == 'TAN' and value_is_empty(state_fips_code, 2, extra_vals={'0'*2}):
        is_valid = not value_is_empty(tribe_code, 3, extra_vals={'0'*3})
    else:
        is_valid = value_is_empty(tribe_code, 3, extra_vals={'0'*3})

    error = None
    if not is_valid:
        error = generate_error(
            schema=None,
            error_category=ParserErrorCategoryChoices.PRE_CHECK,

            error_message=f"Tribe Code ({tribe_code}) inconsistency with Program Type ({program_type}) and " +
            f"FIPS Code ({state_fips_code}).",
            record=None,
            field=None
        )

    return is_valid, error


def validate_header_rpt_month_year(datafile, header, generate_error):
    """Validate header rpt_month_year."""
    # the header year/quarter represent a calendar period, and frontend year/qtr represents a fiscal period
    header_calendar_qtr = f"Q{header['quarter']}"
    header_calendar_year = header['year']
    file_calendar_year, file_calendar_qtr = fiscal_to_calendar(datafile.year, f"{datafile.quarter}")

    is_valid = file_calendar_year is not None and file_calendar_qtr is not None
    is_valid = is_valid and file_calendar_year == header_calendar_year and file_calendar_qtr == header_calendar_qtr

    error = None
    if not is_valid:
        error = generate_error(
            schema=None,
            error_category=ParserErrorCategoryChoices.PRE_CHECK,
            error_message=f"Submitted reporting year:{header['year']}, quarter:Q{header['quarter']} doesn't match "
            + f"file reporting year:{datafile.year}, quarter:{datafile.quarter}.",
            record=None,
            field=None,
        )
    return is_valid, error


def _is_all_zeros(value, start, end):
    """Check if a value is all zeros."""
    return value[start:end] == "0" * (end - start)


def t3_m3_child_validator(which_child):
    """T3 child validator."""
    def t3_first_child_validator_func(value, temp, friendly_name, item_num):
        if not _is_empty(value, 1, 60) and len(value) >= 60:
            return (True, None)
        elif not len(value) >= 60:
            return (False, f"The first child record is too short at {len(value)} "
                    "characters and must be at least 60 characters.")
        else:
            return (False, "The first child record is empty.")

    def t3_second_child_validator_func(value, temp, friendly_name, item_num):
        if not _is_empty(value, 60, 101) and len(value) >= 101 and \
                not _is_empty(value, 8, 19) and \
                not _is_all_zeros(value, 60, 101):
            return (True, None)
        elif not len(value) >= 101:
            return (False, f"The second child record is too short at {len(value)} "
                    "characters and must be at least 101 characters.")
        else:
            return (False, "The second child record is empty.")

    return t3_first_child_validator_func if which_child == 1 else t3_second_child_validator_func


def is_quiet_preparser_errors(min_length, empty_from=61, empty_to=101):
    """Return a function that checks if the length is valid and if the value is empty."""
    def return_value(value):
        is_length_valid = len(value) >= min_length
        is_empty = value_is_empty(
            value[empty_from:empty_to],
            len(value[empty_from:empty_to])
            )
        return not (is_length_valid and not is_empty and not _is_all_zeros(value, empty_from, empty_to))
    return return_value


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
