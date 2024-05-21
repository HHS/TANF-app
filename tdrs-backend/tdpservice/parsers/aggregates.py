"""Aggregate methods for the parsers."""
from .row_schema import SchemaManager
from .models import ParserError, ParserErrorCategoryChoices
from .util import month_to_int, \
    transform_to_months, fiscal_to_calendar, get_prog_from_section
from .schema_defs.utils import get_program_models, get_text_from_df
from django.db.models import Q


def case_aggregates_by_month(df, dfs_status):
    """Return case aggregates by month."""
    section = str(df.section)  # section -> text
    program_type = get_prog_from_section(section)  # section -> program_type -> text

    # from datafile year/quarter, generate short month names for each month in quarter ala 'Jan', 'Feb', 'Mar'
    calendar_year, calendar_qtr = fiscal_to_calendar(df.year, df.quarter)
    month_list = transform_to_months(calendar_qtr)

    short_section = get_text_from_df(df)['section']
    schema_models_dict = get_program_models(program_type, short_section)
    schema_models = [model for model in schema_models_dict.values()]

    aggregate_data = {"months": [], "rejected": 0}
    for month in month_list:
        total = 0
        cases_with_errors = 0
        accepted = 0
        month_int = month_to_int(month)
        rpt_month_year = int(f"{calendar_year}{month_int}")
        if dfs_status == "Rejected":
            # we need to be careful here on examples of bad headers or empty files, since no month will be found
            # but we can rely on the frontend submitted year-quarter to still generate the list of months
            aggregate_data["months"].append({"accepted_with_errors": "N/A",
                                             "accepted_without_errors": "N/A",
                                             "month": month})
            continue

        case_numbers = set()
        for schema_model in schema_models:
            if isinstance(schema_model, SchemaManager):
                schema_model = schema_model.schemas[0]

            curr_case_numbers = set(schema_model.document.Django.model.objects.filter(datafile=df,
                                                                                      RPT_MONTH_YEAR=rpt_month_year)
                                    .distinct("CASE_NUMBER").values_list("CASE_NUMBER", flat=True))
            case_numbers = case_numbers.union(curr_case_numbers)

        total += len(case_numbers)
        cases_with_errors += ParserError.objects.filter(file=df, case_number__in=case_numbers)\
            .distinct('case_number').count()
        accepted = total - cases_with_errors

        aggregate_data['months'].append({"month": month,
                                         "accepted_without_errors": accepted,
                                         "accepted_with_errors": cases_with_errors})

    error_type_query = Q(error_type=ParserErrorCategoryChoices.PRE_CHECK) | \
        Q(error_type=ParserErrorCategoryChoices.CASE_CONSISTENCY)

    aggregate_data['rejected'] = ParserError.objects.filter(error_type_query, file=df)\
        .distinct("row_number").exclude(row_number=0).count()

    return aggregate_data


def total_errors_by_month(df, dfs_status):
    """Return total errors for each month in the reporting period."""
    calendar_year, calendar_qtr = fiscal_to_calendar(df.year, df.quarter)
    month_list = transform_to_months(calendar_qtr)

    total_errors_data = {"months": []}

    errors = ParserError.objects.all().filter(file=df)

    for month in month_list:
        if dfs_status == "Rejected":
            total_errors_data["months"].append(
                {"month": month, "total_errors": "N/A"})
            continue

        month_int = month_to_int(month)
        rpt_month_year = int(f"{calendar_year}{month_int}")

        error_count = errors.filter(rpt_month_year=rpt_month_year).count()
        total_errors_data["months"].append(
            {"month": month, "total_errors": error_count})

    return total_errors_data
