"""Utility file for functions shared between all parsers even preparser."""
from .models import ParserError, ParserErrorCategoryChoices
from django.contrib.contenttypes.models import ContentType
from . import schema_defs
from tdpservice.data_files.models import DataFile
from datetime import datetime
from pathlib import Path


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

def value_is_empty(value, length):
    """Handle 'empty' values as field inputs."""
    empty_values = [
        ' '*length,  # '     '
        '#'*length,  # '#####'
    ]

    return value is None or value in empty_values


def generate_parser_error(datafile, line_number, schema, error_category, error_message, record=None, field=None):
    """Create and return a ParserError using args."""
    return ParserError.objects.create(
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

class Field:
    """Provides a mapping between a field name and its position."""

    def __init__(self, item, name, type, startIndex, endIndex, required=True, validators=[]):
        self.item = item
        self.name = name
        self.type = type
        self.startIndex = startIndex
        self.endIndex = endIndex
        self.required = required
        self.validators = validators

    def create(self, item, name, length, start, end, type):
        """Create a new field."""
        return Field(item, name, type, length, start, end)

    def __repr__(self):
        """Return a string representation of the field."""
        return f"{self.name}({self.startIndex}-{self.endIndex})"

    def parse_value(self, line):
        """Parse the value for a field given a line, startIndex, endIndex, and field type."""
        value = line[self.startIndex:self.endIndex]

        if value_is_empty(value, self.endIndex-self.startIndex):
            return None

        match self.type:
            case 'number':
                try:
                    value = int(value)
                    return value
                except ValueError:
                    return None
            case 'string':
                return value


class RowSchema:
    """Maps the schema for data lines."""

    def __init__(
            self,
            model=dict,
            preparsing_validators=[],
            postparsing_validators=[],
            fields=[],
            quiet_preparser_errors=False
            ):
        self.model = model
        self.preparsing_validators = preparsing_validators
        self.postparsing_validators = postparsing_validators
        self.fields = fields
        self.quiet_preparser_errors = quiet_preparser_errors

    def _add_field(self, item, name, length, start, end, type):
        """Add a field to the schema."""
        self.fields.append(
            Field(item, name, type, start, end)
        )

    def add_fields(self, fields: list):
        """Add multiple fields to the schema."""
        for field, length, start, end, type in fields:
            self._add_field(field, length, start, end, type)

    def get_all_fields(self):
        """Get all fields from the schema."""
        return self.fields

    def get_field(self, name):
        """Get a field from the schema by name."""
        for field in self.fields:
            if field.name == name:
                return field

    def parse_and_validate(self, line, generate_error):
        """Run all validation steps in order, and parse the given line into a record."""
        errors = []

        # run preparsing validators
        preparsing_is_valid, preparsing_errors = self.run_preparsing_validators(line, generate_error)

        if not preparsing_is_valid:
            if self.quiet_preparser_errors:
                return None, True, []
            return None, False, preparsing_errors

        # parse line to model
        record = self.parse_line(line)

        # run field validators
        fields_are_valid, field_errors = self.run_field_validators(record, generate_error)

        # run postparsing validators
        postparsing_is_valid, postparsing_errors = self.run_postparsing_validators(record, generate_error)

        is_valid = fields_are_valid and postparsing_is_valid
        errors = field_errors + postparsing_errors

        return record, is_valid, errors

    def run_preparsing_validators(self, line, generate_error):
        """Run each of the `preparsing_validator` functions in the schema against the un-parsed line."""
        is_valid = True
        errors = []

        for validator in self.preparsing_validators:
            validator_is_valid, validator_error = validator(line)
            is_valid = False if not validator_is_valid else is_valid

            if validator_error and not self.quiet_preparser_errors:
                errors.append(
                    generate_error(
                        schema=self,
                        error_category=ParserErrorCategoryChoices.PRE_CHECK,
                        error_message=validator_error,
                        record=None,
                        field=None
                    )
                )

        return is_valid, errors

    def parse_line(self, line):
        """Create a model for the line based on the schema."""
        record = self.model()

        for field in self.fields:
            value = field.parse_value(line)

            if value is not None:
                if isinstance(record, dict):
                    record[field.name] = value
                else:
                    setattr(record, field.name, value)

        return record

    def run_field_validators(self, instance, generate_error):
        """Run all validators for each field in the parsed model."""
        is_valid = True
        errors = []

        for field in self.fields:
            value = None
            if isinstance(instance, dict):
                value = instance.get(field.name, None)
            else:
                value = getattr(instance, field.name, None)

            if field.required and not value_is_empty(value, field.endIndex-field.startIndex):
                for validator in field.validators:
                    validator_is_valid, validator_error = validator(value)
                    is_valid = False if not validator_is_valid else is_valid
                    if validator_error:
                        errors.append(
                            generate_error(
                                schema=self,
                                error_category=ParserErrorCategoryChoices.FIELD_VALUE,
                                error_message=validator_error,
                                record=instance,
                                field=field
                            )
                        )
            elif field.required:
                is_valid = False
                errors.append(
                    generate_error(
                        schema=self,
                        error_category=ParserErrorCategoryChoices.FIELD_VALUE,
                        error_message=f"{field.name} is required but a value was not provided.",
                        record=instance,
                        field=field
                    )
                )

        return is_valid, errors

    def run_postparsing_validators(self, instance, generate_error):
        """Run each of the `postparsing_validator` functions against the parsed model."""
        is_valid = True
        errors = []

        for validator in self.postparsing_validators:
            validator_is_valid, validator_error = validator(instance)
            is_valid = False if not validator_is_valid else is_valid
            if validator_error:
                errors.append(
                    generate_error(
                        schema=self,
                        error_category=ParserErrorCategoryChoices.VALUE_CONSISTENCY,
                        error_message=validator_error,
                        record=instance,
                        field=None
                    )
                )

        return is_valid, errors

class MultiRecordRowSchema:
    """Maps a line to multiple `RowSchema`s and runs all parsers and validators."""

    def __init__(self, schemas):
        self.schemas = schemas

    def parse_and_validate(self, line, generate_error):
        """Run `parse_and_validate` for each schema provided and bubble up errors."""
        records = []

        for schema in self.schemas:
            r = schema.parse_and_validate(line, generate_error)
            records.append(r)

        return records

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
                    # 'T4': schema_defs.tanf.t4,
                    # 'T5': schema_defs.tanf.t5,
                }
            },
            'G': {
                'section': DataFile.Section.AGGREGATE_DATA,
                'models': {
                    # 'T6': schema_defs.tanf.t6,
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
            return None  # intentionally trigger the error_msg for unknown record type
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
    array = [1,2,3,4]  # wrapping around an array
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
    return datetime.strptime(month, '%b').month


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

    aggregate_data = {}
    for month in month_list:
        total = 0
        rejected = 0
        accepted = 0
        month_int = month_to_int(month)
        rpt_month_year = int(f"{calendar_year}{month_int}")

        if dfs_status == "Rejected":
            # we need to be careful here on examples of bad headers or empty files, since no month will be found
            # but we can rely on the frontend submitted year-quarter to still generate the list of months
            aggregate_data[month] = {"accepted": "N/A", "rejected": "N/A", "total": "N/A"}
            continue

        case_numbers = set()
        for schema_model in schema_models:
            if isinstance(schema_model, MultiRecordRowSchema):
                schema_model = schema_model.schemas[0]
            
            curr_case_numbers = set(schema_model.model.objects.filter(datafile=df).filter(RPT_MONTH_YEAR=rpt_month_year)
                       .distinct("CASE_NUMBER").values_list("CASE_NUMBER", flat=True))
            case_numbers = case_numbers.union(curr_case_numbers)

        total += len(case_numbers)
        rejected += ParserError.objects.filter(case_number__in=case_numbers).distinct('case_number').count()

        accepted = total - rejected

        aggregate_data[month] = {"accepted": accepted, "rejected": rejected, "total": total}

    return aggregate_data
