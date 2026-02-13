"""Aggregate methods for the parsers."""

from django.db.models import Q as Query

from tdpservice.parsers.models import ParserError, ParserErrorCategoryChoices
from tdpservice.parsers.schema_defs.utils import ProgramManager
from tdpservice.parsers.util import (
    fiscal_to_calendar,
    month_to_int,
    transform_to_months,
)


def case_aggregates_by_month(df, dfs_status):
    """Return case aggregates by month."""
    program_type = str(df.program_type)

    # from datafile year/quarter, generate short month names for each month in quarter ala 'Jan', 'Feb', 'Mar'
    calendar_year, calendar_qtr = fiscal_to_calendar(df.year, df.quarter)
    month_list = transform_to_months(calendar_qtr)

    schemas = ProgramManager.get_schemas(program_type, df.section, df.is_program_audit)

    aggregate_data = {"months": [], "rejected": 0}
    all_errors = ParserError.objects.filter(file=df, deprecated=False)

    rpt_month_years = []
    for month in month_list:
        month_int = month_to_int(month)
        rpt_month_years.append(int(f"{calendar_year}{month_int}"))

    if dfs_status == "Rejected":
        for month in month_list:
            aggregate_data["months"].append(
                {
                    "accepted_with_errors": "N/A",
                    "accepted_without_errors": "N/A",
                    "month": month,
                }
            )
    else:
        # One query per schema for all months instead of one per schema per month
        case_numbers_by_month = {rmy: set() for rmy in rpt_month_years}
        for schema in schemas.values():
            schema = schema[0]
            records = (
                schema.model.objects.filter(datafile=df, RPT_MONTH_YEAR__in=rpt_month_years)
                .values_list("CASE_NUMBER", "RPT_MONTH_YEAR")
                .distinct()
            )
            for case_number, rmy in records:
                case_numbers_by_month[rmy].add(case_number)

        # One error query for all months
        all_case_numbers = set().union(*case_numbers_by_month.values())
        error_cases_by_month = {rmy: set() for rmy in rpt_month_years}
        error_records = (
            all_errors.filter(case_number__in=all_case_numbers, rpt_month_year__in=rpt_month_years)
            .values_list("case_number", "rpt_month_year")
            .distinct()
        )
        for case_number, rmy in error_records:
            error_cases_by_month[rmy].add(case_number)

        for month, rmy in zip(month_list, rpt_month_years):
            total = len(case_numbers_by_month[rmy])
            # Intersect to exclude rejected records that generated cat1/cat4 errors since they aren't serialized
            cases_with_errors = len(error_cases_by_month[rmy] & case_numbers_by_month[rmy])
            accepted = total - cases_with_errors

            aggregate_data["months"].append(
                {
                    "month": month,
                    "accepted_without_errors": accepted,
                    "accepted_with_errors": cases_with_errors,
                }
            )

    error_type_query = (
        Query(error_type=ParserErrorCategoryChoices.PRE_CHECK)
        | Query(error_type=ParserErrorCategoryChoices.RECORD_PRE_CHECK)
        | Query(error_type=ParserErrorCategoryChoices.CASE_CONSISTENCY)
    )

    aggregate_data["rejected"] = (
        all_errors.filter(error_type_query)
        .distinct("row_number")
        .exclude(row_number=0)
        .count()
    )

    return aggregate_data


def total_errors_by_month(df, dfs_status):
    """Return total errors for each month in the reporting period."""
    calendar_year, calendar_qtr = fiscal_to_calendar(df.year, df.quarter)
    month_list = transform_to_months(calendar_qtr)

    total_errors_data = {"months": []}

    errors = ParserError.objects.all().filter(file=df, deprecated=False)

    for month in month_list:
        if dfs_status == "Rejected":
            total_errors_data["months"].append({"month": month, "total_errors": "N/A"})
            continue

        month_int = month_to_int(month)
        rpt_month_year = int(f"{calendar_year}{month_int}")

        error_count = errors.filter(rpt_month_year=rpt_month_year).count()
        total_errors_data["months"].append(
            {"month": month, "total_errors": error_count}
        )

    return total_errors_data


def fra_total_errors(df):
    """Return total errors for the file."""
    errors = ParserError.objects.all().filter(file=df, deprecated=False)
    return {"total_errors": errors.count()}
