"""Utility file for functions shared between all parsers even preparser."""
from .models import ParserError
from django.contrib.contenttypes.models import ContentType
from tdpservice.data_files.models import DataFile
from datetime import datetime
from pathlib import Path
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
    fields = [*field] if type(field) is list else [field]
    fields_json = {
        "friendly_name": {
            getattr(f, 'name', ''): getattr(f, 'friendly_name', '') for f in fields
        }
    }

    return ParserError(
        file=datafile,
        row_number=line_number,
        column_number=getattr(field, 'item', None),
        item_number=getattr(field, 'item', None),
        field_name=getattr(field, 'name', None) if hasattr(field, 'name') else field,
        rpt_month_year=getattr(record, 'RPT_MONTH_YEAR', None),
        case_number=getattr(record, 'CASE_NUMBER', None),
        error_message=error_message,
        error_type=error_category,
        content_type=ContentType.objects.get_for_model(
            model=schema.document.Django.model if schema else None
        ) if record and not isinstance(record, dict) else None,
        object_id=getattr(record, 'id', None) if record and not isinstance(record, dict) else None,
        fields_json=fields_json
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
            field=field,
        )

    return generate


def make_generate_file_precheck_parser_error(datafile, line_number):
    """Configure a generate_parser_error that acts as a file pre-check error."""
    def generate(schema, error_category, error_message, record=None, field=None):
        return generate_parser_error(
            datafile=datafile,
            line_number=line_number,
            schema=schema,
            error_category=error_category,
            error_message=error_message,
            record=record,
            field=None,  # purposely overridden to force a "Rejected" status for certain file precheck errors
        )

    return generate


def contains_encrypted_indicator(line, encryption_field):
    """Determine if line contains encryption indicator."""
    if encryption_field is not None:
        return encryption_field.parse_value(line) == "E"
    return False


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


def get_prog_from_section(str_section):
    """Return the program type for a given section."""
    # e.g., 'SSP Closed Case Data'
    if str_section.startswith('SSP'):
        return 'SSP'
    elif str_section.startswith('Tribal'):
        return 'Tribal TAN'
    else:
        return 'TAN'

    # TODO: if given a datafile (section), we can reverse back to the program b/c the
    # section string has "tribal/ssp" in it, then process of elimination we have tanf


def fiscal_to_calendar(year, fiscal_quarter):
    """Decrement the input quarter text by one."""
    array = [1, 2, 3, 4]  # wrapping around an array
    int_qtr = int(fiscal_quarter[1:])  # remove the 'Q', e.g., 'Q1' -> '1'
    if int_qtr == 1:
        year = year - 1

    ind_qtr = array.index(int_qtr)  # get the index so we can easily wrap-around end of array
    return year, "Q{}".format(array[ind_qtr - 1])  # return the previous quarter


def calendar_to_fiscal(calendar_year, fiscal_quarter):
    return calendar_year - 1 if fiscal_quarter == 'Q1' else calendar_year


def transform_to_months(quarter):
    """Return a list of months in a quarter depending the quarter's format."""
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

def year_month_to_year_quarter(year_month):
    """Return the year and quarter from a year_month string."""
    def get_quarter_from_month(month):
        """Return the quarter from a month."""
        if month in ["01", "02", "03"]:
            return "Q1"
        elif month in ["04", "05", "06"]:
            return "Q2"
        elif month in ["07", "08", "09"]:
            return "Q3"
        elif month in ["10", "11", "12"]:
            return "Q4"
        else:
            return "Invalid month value."

    year = year_month[:4]
    month = year_month[4:]
    quarter = get_quarter_from_month(month)
    return year, quarter


def get_years_apart(rpt_month_year_date, date):
    """Return the number of years (double) between rpt_month_year_date and the target date - both `datetime`s."""
    delta = rpt_month_year_date - date
    age = delta.days/365.25
    return age
