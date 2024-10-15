"""Utility functions for DataFile views."""
import base64
from io import BytesIO
import xlsxwriter
import calendar
from tdpservice.parsers.models import ParserErrorCategoryChoices
from django.conf import settings
from django.core.paginator import Paginator


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


def get_xls_serialized_file(parser_errors):
    """Return xls file created from the error."""
    row, col = 0, 0
    output = BytesIO()
    workbook = xlsxwriter.Workbook(output)
    worksheet = workbook.add_worksheet()

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

    row, col = 5, 0

    # write csv header
    bold = workbook.add_format({'bold': True})

    def format_header(header_list: list):
        """Format header."""
        return ' '.join([i.capitalize() for i in header_list.split('_')])

    # We will write the headers in the first row
    columns = ['case_number', 'year', 'month',
               'error_message', 'item_number', 'item_name',
               'internal_variable_name', 'row_number', 'error_type',
               ]
    for idx, col in enumerate(columns):
        worksheet.write(row, idx, format_header(col), bold)

    paginator = Paginator(parser_errors, settings.BULK_CREATE_BATCH_SIZE)
    row_idx = 6
    for page in paginator:
        for record in page.object_list:
            rpt_month_year = str(getattr(record, 'rpt_month_year', None))
            fields_json = getattr(record, 'fields_json', {})

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

    # autofit all columns except for the first one
    worksheet.autofit()
    worksheet.set_column(0, 0, 20)

    workbook.close()
    return {"xls_report": base64.b64encode(output.getvalue()).decode("utf-8")}
