"""Utility functions for DataFile views."""
import base64
from io import BytesIO
import xlsxwriter
import calendar
from tdpservice.parsers.models import ParserErrorCategoryChoices
from django.conf import settings
from django.core.paginator import Paginator
from django.db.models import Count


def format_error_msg(error_msg, fields_json):
    """Format error message."""
    for key, value in fields_json['friendly_name'].items():
        error_msg = error_msg.replace(key, value) if value else error_msg
    return error_msg


def friendly_names(fields_json):
    """Return comma separated string of friendly names."""
    return ','.join([i for i in fields_json['friendly_name'].values()])


def internal_names(fields_json):
    """Return comma separated string of internal names."""
    return ','.join([i for i in fields_json['friendly_name'].keys()])


def check_fields_json(fields_json, field_name):
    """If fields_json is None, impute field name to avoid NoneType errors."""
    if not fields_json:
        child_dict = {field_name: field_name} if field_name else {}
        fields_json = {'friendly_name': child_dict}
    return fields_json


def write_worksheet_banner(worksheet):
    """Write worksheet banner."""
    row, col = 0, 0

    # write beta banner
    worksheet.write(
        row, col,
        "Please refer to the most recent versions of the coding " +
        "instructions (linked below) when looking up items " +
        "and allowable values during the data revision process"
    )

    row, col = 1, 0
    worksheet.write_url(
        row, col,
        'https://www.acf.hhs.gov/ofa/policy-guidance/tribal-tanf-data-coding-instructions',
        string='For Tribal TANF data reports: Tribal TANF Instructions',
    )

    row, col = 2, 0
    worksheet.write_url(
        row, col,
        'https://www.acf.hhs.gov/ofa/policy-guidance/acf-ofa-pi-23-04',
        string='For TANF and SSP-MOE data reports: TANF / SSP-MOE (ACF-199 / ACF-209) Instructions'
    )

    row, col = 3, 0
    worksheet.write_url(
        row, col,
        'https://tdp-project-updates.app.cloud.gov/knowledge-center/viewing-error-reports.html',
        string='Visit the Knowledge Center for further guidance on reviewing error reports'
    )


def format_header(header_list: list):
    """Format header."""
    return ' '.join([i.capitalize() for i in header_list.split('_')])


def write_prioritized_errors(worksheet, prioritized_errors, bold):
    """Write prioritized errors to spreadsheet."""
    row, col = 5, 0

    # We will write the headers in the first row
    columns = ['case_number', 'year', 'month',
               'error_message', 'item_number', 'item_name',
               'internal_variable_name', 'row_number', 'error_type',
               ]
    for idx, col in enumerate(columns):
        worksheet.write(row, idx, format_header(col), bold)

    paginator = Paginator(prioritized_errors.order_by('-pk'), settings.BULK_CREATE_BATCH_SIZE)
    row_idx = 6
    for page in paginator:
        for record in page.object_list:
            rpt_month_year = getattr(record, 'rpt_month_year', None)
            rpt_month_year = str(rpt_month_year) if rpt_month_year else ""

            fields_json = check_fields_json(getattr(record, 'fields_json', {}), record.field_name)

            worksheet.write(row_idx, 0, record.case_number)
            worksheet.write(row_idx, 1, rpt_month_year[:4])
            worksheet.write(row_idx, 2, calendar.month_name[int(rpt_month_year[4:])] if rpt_month_year[4:] else None)
            worksheet.write(row_idx, 3, format_error_msg(record.error_message, fields_json))
            worksheet.write(row_idx, 4, record.item_number)
            worksheet.write(row_idx, 5, friendly_names(fields_json))
            worksheet.write(row_idx, 6, internal_names(fields_json))
            worksheet.write(row_idx, 7, record.row_number)
            worksheet.write(row_idx, 8, str(ParserErrorCategoryChoices(record.error_type).label))
            row_idx += 1


def write_aggregate_errors(worksheet, all_errors, bold):
    """Aggregate by error message and write."""
    row, col = 5, 0

    # We will write the headers in the first row
    columns = ['year', 'month', 'error_message', 'item_number', 'item_name',
               'internal_variable_name', 'error_type', 'number_of_occurrences'
               ]
    for idx, col in enumerate(columns):
        worksheet.write(row, idx, format_header(col), bold)

    aggregates = all_errors.values('rpt_month_year', 'error_message',
                                   'item_number', 'field_name',
                                   'fields_json', 'error_type').annotate(num_occurrences=Count('error_message'))

    paginator = Paginator(aggregates.order_by('-num_occurrences'), settings.BULK_CREATE_BATCH_SIZE)
    row_idx = 6
    for page in paginator:
        for record in page.object_list:
            rpt_month_year = record['rpt_month_year']
            rpt_month_year = str(rpt_month_year) if rpt_month_year else ""

            fields_json = check_fields_json(record['fields_json'], record['field_name'])

            worksheet.write(row_idx, 0, rpt_month_year[:4])
            worksheet.write(row_idx, 1, calendar.month_name[int(rpt_month_year[4:])] if rpt_month_year[4:] else None)
            worksheet.write(row_idx, 2, format_error_msg(record['error_message'], fields_json))
            worksheet.write(row_idx, 3, record['item_number'])
            worksheet.write(row_idx, 4, friendly_names(fields_json))
            worksheet.write(row_idx, 5, internal_names(fields_json))
            worksheet.write(row_idx, 6, str(ParserErrorCategoryChoices(record['error_type']).label))
            worksheet.write(row_idx, 7, record['num_occurrences'])
            row_idx += 1


def get_xls_serialized_file(all_errors, prioritized_errors):
    """Return xls file created from the error."""
    output = BytesIO()
    workbook = xlsxwriter.Workbook(output)
    prioritized_sheet = workbook.add_worksheet(name="Priorities")
    aggregate_sheet = workbook.add_worksheet(name="Aggregates")

    write_worksheet_banner(prioritized_sheet)
    write_worksheet_banner(aggregate_sheet)

    bold = workbook.add_format({'bold': True})
    write_prioritized_errors(prioritized_sheet, prioritized_errors, bold)
    write_aggregate_errors(aggregate_sheet, all_errors, bold)

    # autofit all columns except for the first one
    prioritized_sheet.autofit()
    prioritized_sheet.set_column(0, 0, 20)
    aggregate_sheet.autofit()
    aggregate_sheet.set_column(0, 0, 20)

    workbook.close()
    return {"xls_report": base64.b64encode(output.getvalue()).decode("utf-8")}
