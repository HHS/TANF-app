"""Utility functions for DataFile views."""
import base64
from io import BytesIO
import xlsxwriter
import calendar
from django.conf import settings
from django.core.paginator import Paginator
from django.db.models import Count, Q

from abc import ABC, abstractmethod
from tdpservice.data_files.models import DataFile
from tdpservice.data_files.util import ParserErrorCategoryChoices
from tdpservice.parsers.models import ParserError
from tdpservice.search_indexes.models.fra import TANF_Exiter1


class ErrorReportFactory:
    """Factory class for error report generators."""

    @staticmethod
    def get_error_report_generator(datafile):
        """Get error report generator."""
        active = DataFile.Section.ACTIVE_CASE_DATA
        closed = DataFile.Section.CLOSED_CASE_DATA
        if active in datafile.section or closed in datafile.section:
            return ActiveClosedErrorReport(datafile)
        elif (DataFile.Section.AGGREGATE_DATA in datafile.section or
              DataFile.Section.STRATUM_DATA in datafile.section):
            return AggregateStratumErrorReport(datafile)
        elif datafile.section == DataFile.Section.FRA_WORK_OUTCOME_TANF_EXITERS:
            return FRADataErrorReport(datafile)
        else:
            raise ValueError(f"Unsupported section: {datafile.section}")


class ErrorReportBase(ABC):
    """Base class for error report generators."""

    def __init__(self, datafile):
        super().__init__()
        self.datafile = datafile
        self.parser_errors = ParserError.objects.filter(file=datafile, deprecated=False)
        self.output = BytesIO()
        self.workbook = xlsxwriter.Workbook(self.output)
        self.row_generator = self.get_row_generator()

    @abstractmethod
    def generate(self):
        """To be overriden in child class."""
        pass

    @abstractmethod
    def get_row_generator(self):
        """Get row generator for error report."""
        pass

    @abstractmethod
    def get_columns(self):
        """Get the columns for header."""
        pass

    def format_header(self, header_list: list):
        """Format header."""
        return ' '.join([i.capitalize() for i in header_list.split('_')])

    def format_error_msg(self, error_msg, fields_json):
        """Format error message."""
        for key, value in fields_json['friendly_name'].items():
            error_msg = error_msg.replace(key, value) if value else error_msg
        return error_msg

    def friendly_names(self, fields_json):
        """Return comma separated string of friendly names."""
        return ','.join([i for i in fields_json['friendly_name'].values()])

    def internal_names(self, fields_json):
        """Return comma separated string of internal names."""
        return ','.join([i for i in fields_json['friendly_name'].keys()])

    def check_fields_json(self, fields_json, field_name):
        """If fields_json is None, impute field name to avoid NoneType errors."""
        if not fields_json:
            child_dict = {field_name: field_name} if field_name else {}
            fields_json = {'friendly_name': child_dict}
        return fields_json


class FRADataErrorReport(ErrorReportBase):
    """FRA Error Report generator."""

    def __init__(self, datafile):
        super().__init__(datafile)

    def generate(self):
        """Generate and return FRA error report."""
        worksheet = self.workbook.add_worksheet(name="Error Report")

        bold = self.workbook.add_format({'bold': True})
        columns = self.get_columns()
        for idx, col in enumerate(columns):
            worksheet.write(0, idx, self.format_header(col), bold)

        row_idx = 1
        for error in self.parser_errors.iterator():
            ssn = error.values_json.get('SSN', '')
            exit_date = error.values_json.get('EXIT_DATE', None)
            fields_json = self.check_fields_json(getattr(error, 'fields_json', {}), error.field_name)
            row = self.row_generator(error, exit_date, ssn, fields_json)
            worksheet.write_row(row_idx, 0, row)
            row_idx += 1

        self.workbook.close()
        return {"xls_report": base64.b64encode(self.output.getvalue())}

    def get_columns(self):
        """Get the columns for header."""
        return ["exit_date", "ssn", "error_location_in_file", "error_description"]

    def _obscure_ssn(self, ssn):
        """Obscure SSN."""
        return f"*****{ssn[-4:]}"

    def get_row_generator(self):
        """Get row generator for error report."""
        return lambda error, exit_date, ssn, fields_json: (exit_date,
                                                           self._obscure_ssn(ssn),
                                                           f"{error.column_number}{error.row_number}",
                                                           self.format_error_msg(error.error_message, fields_json),)


class TanfDataErrorReportBase(ErrorReportBase):
    """TANF Data Report Error Report generator."""

    def __init__(self, datafile):
        super().__init__(datafile)
        self.prioritized_errors = self.get_prioritized_queryset()

    @abstractmethod
    def get_prioritized_queryset(self):
        """Generate a prioritized queryset of ParserErrors."""
        pass

    def generate(self):
        """Generate and return TDR error report."""
        prioritized_sheet = self.workbook.add_worksheet(name="Critical")
        aggregate_sheet = self.workbook.add_worksheet(name="Summary")

        self.write_worksheet_banner(prioritized_sheet)
        self.write_worksheet_banner(aggregate_sheet)

        bold = self.workbook.add_format({'bold': True})
        self.write_prioritized_errors(prioritized_sheet, bold)
        self.write_aggregate_errors(aggregate_sheet, bold)

        # autofit all columns except for the first one
        prioritized_sheet.autofit()
        prioritized_sheet.set_column(0, 0, 20)
        aggregate_sheet.autofit()
        aggregate_sheet.set_column(0, 0, 20)

        self.workbook.close()
        return {"xls_report": base64.b64encode(self.output.getvalue())}

    def write_prioritized_errors(self, worksheet, bold):
        """Write prioritized errors to spreadsheet."""
        # We will write the headers in the first row, remove case_number if we are s3/s4
        columns = self.get_columns()
        for idx, col in enumerate(columns):
            worksheet.write(5, idx, self.format_header(col), bold)

        paginator = Paginator(self.prioritized_errors.order_by('pk'), settings.BULK_CREATE_BATCH_SIZE)
        row_idx = 6
        for page in paginator:
            for error in page.object_list:
                rpt_month_year = getattr(error, 'rpt_month_year', None)
                rpt_month_year = str(rpt_month_year) if rpt_month_year else ""
                fields_json = self.check_fields_json(getattr(error, 'fields_json', {}), error.field_name)

                worksheet.write_row(row_idx, 0, self.row_generator(error, rpt_month_year, fields_json))
                row_idx += 1

    def write_aggregate_errors(self, worksheet, bold):
        """Aggregate by error message and write."""
        row, col = 5, 0

        # We will write the headers in the first row
        columns = ['year', 'month', 'error_message', 'item_number', 'item_name',
                   'internal_variable_name', 'error_type', 'number_of_occurrences']
        for idx, col in enumerate(columns):
            worksheet.write(row, idx, self.format_header(col), bold)

        aggregates = self.parser_errors.values('rpt_month_year',
                                               'error_message',
                                               'item_number',
                                               'field_name',
                                               'fields_json',
                                               'error_type').annotate(num_occurrences=Count('error_message'))

        paginator = Paginator(aggregates.order_by('-num_occurrences'), settings.BULK_CREATE_BATCH_SIZE)
        row_idx = 6
        for page in paginator:
            for error in page.object_list:
                rpt_month_year = error['rpt_month_year']
                rpt_month_year = str(rpt_month_year) if rpt_month_year else ""

                fields_json = self.check_fields_json(error['fields_json'], error['field_name'])

                worksheet.write(row_idx, 0, rpt_month_year[:4])
                worksheet.write(row_idx, 1, calendar.month_name[int(rpt_month_year[4:])] if rpt_month_year[4:]
                                else None)
                worksheet.write(row_idx, 2, self.format_error_msg(error['error_message'], fields_json))
                worksheet.write(row_idx, 3, error['item_number'])
                worksheet.write(row_idx, 4, self.friendly_names(fields_json))
                worksheet.write(row_idx, 5, self.internal_names(fields_json))
                worksheet.write(row_idx, 6, str(ParserErrorCategoryChoices(error['error_type']).label))
                worksheet.write(row_idx, 7, error['num_occurrences'])
                row_idx += 1

    def write_worksheet_banner(self, worksheet):
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


class ActiveClosedErrorReport(TanfDataErrorReportBase):
    """TANF Data Report Error Report generator for Active and Closed files."""

    def __init__(self, datafile):
        super().__init__(datafile)
        self.prioritized_errors = self.get_prioritized_queryset()

    def get_prioritized_queryset(self):
        """Generate a prioritized queryset of ParserErrors."""
        PRIORITIZED_CAT2 = (
            ("FAMILY_AFFILIATION", "CITIZENSHIP_STATUS", "CLOSURE_REASON"),
        )
        PRIORITIZED_CAT3 = (
            ("FAMILY_AFFILIATION", "SSN"),
            ("FAMILY_AFFILIATION", "CITIZENSHIP_STATUS"),
            ("AMT_FOOD_STAMP_ASSISTANCE", "AMT_SUB_CC", "CASH_AMOUNT", "CC_AMOUNT", "TRANSP_AMOUNT"),
            ("FAMILY_AFFILIATION", "SSN", "CITIZENSHIP_STATUS"),
            ("FAMILY_AFFILIATION", "PARENT_MINOR_CHILD"),
            ("FAMILY_AFFILIATION", "EDUCATION_LEVEL"),
            ("FAMILY_AFFILIATION", "WORK_ELIGIBLE_INDICATOR"),
            ("CITIZENSHIP_STATUS", "WORK_ELIGIBLE_INDICATOR"),
        )

        # All cat1/4 errors
        error_type_query = Q(error_type=ParserErrorCategoryChoices.PRE_CHECK) | \
            Q(error_type=ParserErrorCategoryChoices.CASE_CONSISTENCY)
        filtered_errors = self.parser_errors.filter(error_type_query)

        for fields in PRIORITIZED_CAT2:
            filtered_errors = filtered_errors.union(self.parser_errors.filter(
                field_name__in=fields,
                error_type=ParserErrorCategoryChoices.FIELD_VALUE
            ))

        for fields in PRIORITIZED_CAT3:
            filtered_errors = filtered_errors.union(self.parser_errors.filter(
                fields_json__friendly_name__has_keys=fields,
                error_type=ParserErrorCategoryChoices.VALUE_CONSISTENCY
            ))

        return filtered_errors

    def get_row_generator(self):
        """Get row generator for error report."""
        return lambda error, rpt_month_year, fields_json: (error.case_number,
                                                           rpt_month_year[:4],
                                                           calendar.month_name[int(rpt_month_year[4:])] if
                                                           rpt_month_year[4:] else None,
                                                           self.format_error_msg(error.error_message, fields_json),
                                                           error.item_number,
                                                           self.friendly_names(fields_json),
                                                           self.internal_names(fields_json),
                                                           error.row_number,
                                                           str(ParserErrorCategoryChoices(error.error_type).label))

    def get_columns(self):
        """Get the columns for header."""
        columns = ['case_number', 'year', 'month', 'error_message', 'item_number', 'item_name',
                   'internal_variable_name', 'row_number', 'error_type',]
        return columns


class AggregateStratumErrorReport(TanfDataErrorReportBase):
    """TANF Data Report Error Report generator for Aggregate and Stratum files."""

    def __init__(self, datafile):
        super().__init__(datafile)
        self.prioritized_errors = self.get_prioritized_queryset()

    def get_prioritized_queryset(self):
        """Generate a prioritized queryset of ParserErrors."""
        return self.parser_errors

    def get_row_generator(self):
        """Get row generator for error report."""
        return lambda error, rpt_month_year, fields_json: (rpt_month_year[:4],
                                                           calendar.month_name[int(rpt_month_year[4:])] if
                                                           rpt_month_year[4:] else None,
                                                           self.format_error_msg(error.error_message, fields_json),
                                                           error.item_number,
                                                           self.friendly_names(fields_json),
                                                           self.internal_names(fields_json),
                                                           error.row_number,
                                                           str(ParserErrorCategoryChoices(error.error_type).label))

    def get_columns(self):
        """Get the columns for header."""
        columns = ['year', 'month', 'error_message', 'item_number', 'item_name',
                   'internal_variable_name', 'row_number', 'error_type',]
        return columns
