"""Utility file for functions shared between all parsers even preparser."""
from .models import ParserError
from django.contrib.contenttypes.models import ContentType
from . import schema_defs
from tdpservice.data_files.models import DataFile
from datetime import datetime
from pathlib import Path
from .fields import TransformField
import logging

logger = logging.getLogger(__name__)


def create_test_datafile(filename, stt_user, stt, section='Active Case Data'):
    """Create a test DataFile instance with the given file attached."""
    path = str(Path(__file__).parent.joinpath('test/data')) + f'/{filename}'
    datafile = DataFile.create_new_version({
        'quarter': 'Q1',
        'year': 2021,
        'section': section,
        'user': stt_user,
        'stt': stt
    })

    with open(path, 'rb') as file:
        datafile.file.save(filename, file)

    return datafile


def generate_parser_error(datafile, line_number, schema, error_category, error_message, record=None, field=None):
    """Create and return a ParserError using args."""
    return ParserError(
        file=datafile,
        row_number=line_number,
        column_number=getattr(field, 'item', None),
        item_number=getattr(field, 'item', None),
        field_name=getattr(field, 'name', None),
        rpt_month_year=getattr(record, 'RPT_MONTH_YEAR', None),
        case_number=getattr(record, 'CASE_NUMBER', None),
        error_message=error_message,
        error_type=error_category,
        content_type=ContentType.objects.get_for_model(
            model=schema.model if schema else None
        ) if record and not isinstance(record, dict) else None,
        object_id=getattr(record, 'id', None) if record and not isinstance(record, dict) else None,
        fields_json=None
    )


def make_generate_parser_error(datafile, line_number):
    """Configure generate_parser_error with a datafile and line number."""
    def generate(schema, error_category, error_message, record=None, field=None):
        return generate_parser_error(
            datafile=datafile,
            line_number=line_number,
            schema=schema,
            error_category=error_category,
            error_message=error_message,
            record=record,
            field=field
        )

    return generate


class SchemaManager:
    """Manages one or more RowSchema's and runs all parsers and validators."""

    def __init__(self, schemas):
        self.schemas = schemas

    def parse_and_validate(self, line, generate_error):
        """Run `parse_and_validate` for each schema provided and bubble up errors."""
        records = []

        for schema in self.schemas:
            record, is_valid, errors = schema.parse_and_validate(line, generate_error)
            records.append((record, is_valid, errors))

        return records

    def update_encrypted_fields(self, is_encrypted):
        """Update whether schema fields are encrypted or not."""
        for schema in self.schemas:
            for field in schema.fields:
                if type(field) == TransformField and "is_encrypted" in field.kwargs:
                    field.kwargs['is_encrypted'] = is_encrypted

def contains_encrypted_indicator(line, encryption_field):
    """Determine if line contains encryption indicator."""
    if encryption_field is not None:
        return encryption_field.parse_value(line) == "E"
    return False

def get_schema_options(program, section, query=None, model=None, model_name=None):
    """Centralized function to return the appropriate schema for a given program, section, and query.

    TODO: need to rework this docstring as it is outdated hence the weird ';;' for some of them.

    @param program: the abbreviated program type (.e.g, 'TAN')
    @param section: the section of the file (.e.g, 'A');; or ACTIVE_CASE_DATA
    @param query: the query for section_names (.e.g, 'section', 'models', etc.)
    @return: the appropriate references (e.g., ACTIVE_CASE_DATA or {t1,t2,t3}) ;; returning 'A'
    """
    schema_options = {
        'TAN': {
            'A': {
                'section': DataFile.Section.ACTIVE_CASE_DATA,
                'models': {
                    'T1': schema_defs.tanf.t1,
                    'T2': schema_defs.tanf.t2,
                    'T3': schema_defs.tanf.t3,
                }
            },
            'C': {
                'section': DataFile.Section.CLOSED_CASE_DATA,
                'models': {
                    'T4': schema_defs.tanf.t4,
                    'T5': schema_defs.tanf.t5,
                }
            },
            'G': {
                'section': DataFile.Section.AGGREGATE_DATA,
                'models': {
                    'T6': schema_defs.tanf.t6,
                }
            },
            'S': {
                'section': DataFile.Section.STRATUM_DATA,
                'models': {
                    # 'T7': schema_defs.tanf.t7,
                }
            }
        },
        'SSP': {
            'A': {
                'section': DataFile.Section.SSP_ACTIVE_CASE_DATA,
                'models': {
                    'M1': schema_defs.ssp.m1,
                    'M2': schema_defs.ssp.m2,
                    'M3': schema_defs.ssp.m3,
                }
            },
            'C': {
                'section': DataFile.Section.SSP_CLOSED_CASE_DATA,
                'models': {
                    # 'S4': schema_defs.ssp.m4,
                    # 'S5': schema_defs.ssp.m5,
                }
            },
            'G': {
                'section': DataFile.Section.SSP_AGGREGATE_DATA,
                'models': {
                    # 'S6': schema_defs.ssp.m6,
                }
            },
            'S': {
                'section': DataFile.Section.SSP_STRATUM_DATA,
                'models': {
                    # 'S7': schema_defs.ssp.m7,
                }
            }
        },
        # TODO: tribal tanf
    }

    if query == "text":
        for prog_name, prog_dict in schema_options.items():
            for sect, val in prog_dict.items():
                if val['section'] == section:
                    return {'program_type': prog_name, 'section': sect}
        raise ValueError("Model not found in schema_defs")
    elif query == "section":
        return schema_options.get(program, {}).get(section, None)[query]
    elif query == "models":
        links = schema_options.get(program, {}).get(section, None)

        # if query is not chosen or wrong input, return all options
        # query = 'models', model = 'T1'
        models = links.get(query, links)

        if model_name is None:
            return models
        elif model_name not in models.keys():
            logger.debug(f"Model {model_name} not found in schema_defs")
            return []  # intentionally trigger the error_msg for unknown record type
        else:
            return models.get(model_name, models)


'''
text -> section YES
text -> models{} YES
text -> model YES
datafile -> model
    ^ section -> program -> model
datafile -> text
model -> text YES
section -> text

text**: input string from the header/file
'''

def get_program_models(str_prog, str_section):
    """Return the models dict for a given program and section."""
    return get_schema_options(program=str_prog, section=str_section, query='models')

def get_program_model(str_prog, str_section, str_model):
    """Return singular model for a given program, section, and name."""
    return get_schema_options(program=str_prog, section=str_section, query='models', model_name=str_model)

def get_section_reference(str_prog, str_section):
    """Return the named section reference for a given program and section."""
    return get_schema_options(program=str_prog, section=str_section, query='section')

def get_text_from_df(df):
    """Return the short-hand text for program, section for a given datafile."""
    return get_schema_options("", section=df.section, query='text')

def get_prog_from_section(str_section):
    """Return the program type for a given section."""
    # e.g., 'SSP Closed Case Data'
    if str_section.startswith('SSP'):
        return 'SSP'
    elif str_section.startswith('Tribal'):
        return 'TAN'  # problematic, do we need to infer tribal entirely from tribe/fips code?
    else:
        return 'TAN'

    # TODO: if given a datafile (section), we can reverse back to the program b/c the
    # section string has "tribal/ssp" in it, then process of elimination we have tanf

def get_schema(line, section, program_type):
    """Return the appropriate schema for the line."""
    line_type = line[0:2]
    return get_schema_options(program_type, section, query='models', model_name=line_type)

def fiscal_to_calendar(year, fiscal_quarter):
    """Decrement the input quarter text by one."""
    array = [1, 2, 3, 4]  # wrapping around an array
    int_qtr = int(fiscal_quarter[1:])  # remove the 'Q', e.g., 'Q1' -> '1'
    if int_qtr == 1:
        year = year - 1

    ind_qtr = array.index(int_qtr)  # get the index so we can easily wrap-around end of array
    return year, "Q{}".format(array[ind_qtr - 1])  # return the previous quarter

def transform_to_months(quarter):
    """Return a list of months in a quarter."""
    match quarter:
        case "Q1":
            return ["Jan", "Feb", "Mar"]
        case "Q2":
            return ["Apr", "May", "Jun"]
        case "Q3":
            return ["Jul", "Aug", "Sep"]
        case "Q4":
            return ["Oct", "Nov", "Dec"]
        case _:
            raise ValueError("Invalid quarter value.")


def month_to_int(month):
    """Return the integer value of a month."""
    return datetime.strptime(month, '%b').strftime('%m')


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

            curr_case_numbers = set(schema_model.model.objects.filter(datafile=df).filter(RPT_MONTH_YEAR=rpt_month_year)
                                    .distinct("CASE_NUMBER").values_list("CASE_NUMBER", flat=True))
            case_numbers = case_numbers.union(curr_case_numbers)

        total += len(case_numbers)
        cases_with_errors += ParserError.objects.filter(case_number__in=case_numbers).distinct('case_number').count()
        accepted = total - cases_with_errors

        aggregate_data['months'].append({"month": month,
                                         "accepted_without_errors": accepted,
                                         "accepted_with_errors": cases_with_errors})

    aggregate_data['rejected'] = ParserError.objects.filter(file=df).filter(case_number=None).count()

    return aggregate_data
