from tdpservice.parsers.util import fiscal_to_calendar, year_month_to_year_quarter, clean_options_string, get_record_value_by_field_name
from .base import ValidatorFunctions
from .util import ValidationErrorArgs, make_validator, evaluate_all



def format_error_context(eargs: ValidationErrorArgs):
    """Format the error message for consistency across cat2 validators."""
    return f'{eargs.row_schema.record_type} Item {eargs.item_num} ({eargs.friendly_name}):'


class PreparsingValidators():
    @staticmethod
    def recordHasLength(length, **kwargs):
        return make_validator(
            ValidatorFunctions.hasLength(length, **kwargs),
            lambda eargs:
                f"{eargs.row_schema.record_type}: record length is {len(eargs.value)} characters but must be {length}.",
        )

    # todo: this is only used for header/trailer, want custom error messages here anyway
    # make new custom validator functions
    @staticmethod
    def recordStartsWith(substr, func, **kwargs):
        return make_validator(
            ValidatorFunctions.startsWith(substr, **kwargs),
            lambda eargs: f'{eargs.value} must start with {substr}.'
        )

    @staticmethod
    def recordHasLengthBetween(min, max, **kwargs):
        _validator = ValidatorFunctions.isBetween(min, max, inclusive=True, **kwargs)
        return make_validator(
            lambda record, eargs: _validator(len(record), eargs),
            lambda eargs:
                f"{eargs.row_schema.record_type}: record length of {len(eargs.value)} "
                f"characters is not in the range [{min}, {max}].",
        )

    @staticmethod
    def caseNumberNotEmpty(start=0, end=None, **kwargs):
        return make_validator(
            ValidatorFunctions.isNotEmpty(start, end, **kwargs),
            lambda eargs: f'{eargs.row_schema.record_type}: Case number {str(eargs.value)} cannot contain blanks.'
        )

    @staticmethod
    def or_priority_validators(validators=[]):
        """Return a validator that is true based on a priority of validators.

        validators: ordered list of validators to be checked
        """
        def or_priority_validators_func(value, eargs):
            for validator in validators:
                result, msg = validator(value, eargs)[0]
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