from tdpservice.parsers.util import fiscal_to_calendar, year_month_to_year_quarter, clean_options_string, get_record_value_by_field_name
from .base import ValidatorFunctions
from .util import ValidationErrorArgs, make_validator, evaluate_all, _is_all_zeros, _is_empty


def format_error_context(eargs: ValidationErrorArgs):
    """Format the error message for consistency across cat1 validators."""
    return f'{eargs.row_schema.record_type} Item {eargs.item_num} ({eargs.friendly_name}):'


class PreparsingValidators():
    @staticmethod
    def recordIsNotEmpty(start=0, end=None, **kwargs):
        return make_validator(
            ValidatorFunctions.isNotEmpty(**kwargs),
            lambda eargs: f'{format_error_context(eargs)} {str(eargs.value)} contains blanks '
            f'between positions {start} and {end if end else len(str(eargs.value))}.'
        )

    @staticmethod
    def recordHasLength(length, **kwargs):
        return make_validator(
            ValidatorFunctions.hasLength(length, **kwargs),
            lambda eargs:
                f"{eargs.row_schema.record_type}: record length is {len(eargs.value)} characters but must be {length}.",
        )

    @staticmethod
    def recordHasLengthBetween(min, max, **kwargs):
        _validator = ValidatorFunctions.isBetween(min, max, inclusive=True, **kwargs)
        return make_validator(
            lambda record: _validator(len(record)),
            lambda eargs:
                f"{eargs.row_schema.record_type}: record length of {len(eargs.value)} "
                f"characters is not in the range [{min}, {max}].",
        )

    # todo: this is only used for header/trailer, want custom error messages here anyway
    # make new custom validator functions
    @staticmethod
    def recordStartsWith(substr, func=None, **kwargs):
        return make_validator(
            ValidatorFunctions.startsWith(substr, **kwargs),
            lambda eargs: f'{eargs.value} must start with {substr}.'
        )

    @staticmethod
    def caseNumberNotEmpty(start=0, end=None, **kwargs):
        return make_validator(
            ValidatorFunctions.isNotEmpty(start, end, **kwargs),
            lambda eargs: f'{eargs.row_schema.record_type}: Case number {str(eargs.value)} cannot contain blanks.'
        )

    # todo: rewrite/test
    @staticmethod
    def or_priority_validators(validators=[]):
        """Return a validator that is true based on a priority of validators.

        validators: ordered list of validators to be checked
        """
        def or_priority_validators_func(value, eargs):
            for validator in validators:
                result, msg = validator(value, eargs)
                if not result:
                    return (result, msg)
            return (True, None)

        return or_priority_validators_func

    @staticmethod
    def validate_fieldYearMonth_with_headerYearQuarter():
        """Validate that the field year and month match the header year and quarter."""
        def validate_reporting_month_year_fields_header(line, eargs):
            row_schema = eargs.row_schema
            field_month_year = row_schema.get_field_values_by_names(
                line, ['RPT_MONTH_YEAR']).get('RPT_MONTH_YEAR')
            df_quarter = row_schema.datafile.quarter
            df_year = row_schema.datafile.year

            # get reporting month year from header
            field_year, field_quarter = year_month_to_year_quarter(f"{field_month_year}")
            file_calendar_year, file_calendar_qtr = fiscal_to_calendar(df_year, f"{df_quarter}")
            return (True, None) if str(file_calendar_year) == str(field_year) and file_calendar_qtr == field_quarter else (
                False, f"{row_schema.record_type}: Reporting month year {field_month_year} " +
                f"does not match file reporting year:{df_year}, quarter:{df_quarter}.",
                )

        return validate_reporting_month_year_fields_header

    @staticmethod
    def validateRptMonthYear():
        """Validate RPT_MONTH_YEAR."""
        return make_validator(
            lambda value: value[2:8].isdigit() and int(value[2:6]) > 1900 and value[6:8] in {
                "01", "02", "03", "04", "05", "06", "07", "08", "09", "10", "11", "12"
            },
            lambda eargs:
                f"{format_error_context(eargs)} The value: {eargs.value[2:8]}, "
                "does not follow the YYYYMM format for Reporting Year and Month.",
        )

    @staticmethod
    def t3_m3_child_validator(which_child):
        """T3 child validator."""
        def t3_first_child_validator_func(line, eargs):
            if not _is_empty(line, 1, 60) and len(line) >= 60:
                return (True, None)
            elif not len(line) >= 60:
                return (False, f"The first child record is too short at {len(line)} "
                        "characters and must be at least 60 characters.")
            else:
                return (False, "The first child record is empty.")

        def t3_second_child_validator_func(line, eargs):
            if not _is_empty(line, 60, 101) and len(line) >= 101 and \
                    not _is_empty(line, 8, 19) and \
                    not _is_all_zeros(line, 60, 101):
                return (True, None)
            elif not len(line) >= 101:
                return (False, f"The second child record is too short at {len(line)} "
                        "characters and must be at least 101 characters.")
            else:
                return (False, "The second child record is empty.")

        return t3_first_child_validator_func if which_child == 1 else t3_second_child_validator_func

    @staticmethod
    def calendarQuarterIsValid(start=0, end=None):
        """Validate that the calendar quarter value is valid."""
        return make_validator(
            lambda value: value[start:end].isnumeric() and int(value[start:end - 1]) >= 2020
            and int(value[end - 1:end]) > 0 and int(value[end - 1:end]) < 5,
            lambda eargs: f"{eargs.row_schema.record_type}: {eargs.value[start:end]} is invalid. "
            "Calendar Quarter must be a numeric representing the Calendar Year and Quarter formatted as YYYYQ",
        )
