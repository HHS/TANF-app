"""Utility file for functions shared between all parsers even preparser."""
from .models import ParserError
from django.contrib.contenttypes.models import ContentType
from tdpservice.data_files.models import DataFile
from pathlib import Path
from .fields import TransformField
from datetime import datetime

def create_test_datafile(filename, stt_user, stt, section='Active Case Data'):
    """Create a test DataFile instance with the given file attached."""
    path = str(Path(__file__).parent.joinpath('test/data')) + f'/{filename}'
    datafile = DataFile.create_new_version({
        'quarter': '4',
        'year': 2022,
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

def month_to_int(month):
    """Return the integer value of a month."""
    return datetime.strptime(month, '%b').strftime('%m')

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
