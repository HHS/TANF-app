"""Utility file for functions shared between all parsers even preparser."""
from .models import ParserError, ParserErrorCategoryChoices
from django.contrib.contenttypes.models import ContentType
from . import schema_defs
from tdpservice.data_files.models import DataFile

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
    '''
    Centralized function to return the appropriate schema for a given program, section, and query.
    @param program: the abbreviated program type (.e.g, 'TAN')
    @param section: the section of the file (.e.g, 'A');; or ACTIVE_CASE_DATA
    @param query: the query for section_names (.e.g, 'section', 'models', etc.)
    @return: the appropriate references (e.g., ACTIVE_CASE_DATA or {t1,t2,t3}) ;; returning 'A'
    '''

    # ensure file section matches upload section
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
                    #'T4': schema_defs.tanf.t4,
                    #'T5': schema_defs.tanf.t5,
                }
            },
            'G': {
                'section':DataFile.Section.AGGREGATE_DATA,
                'models': {
                    #'T6': schema_defs.tanf.t6,
                }
            },
            'S': {
                'section':DataFile.Section.STRATUM_DATA,
                'models': {
                    #'T7': schema_defs.tanf.t7,
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
                'section':DataFile.Section.SSP_CLOSED_CASE_DATA,
                'models': {
                    #'S4': schema_defs.ssp.m4,
                    #'S5': schema_defs.ssp.m5,
                }
            },
            'G': {
                'section':DataFile.Section.SSP_AGGREGATE_DATA,
                'models': {
                    #'S6': schema_defs.ssp.m6,
                }
            },
            'S': {
                'section':DataFile.Section.SSP_STRATUM_DATA,
                'models': {
                    #'S7': schema_defs.ssp.m7,
                }
            }
        },
        # TODO: tribal tanf
    }
        
    #TODO: add error handling for bad inputs -- how does `get` handle bad inputs?
    if query == "text":
        for prog_name, prog_dict in schema_options.items():
            for sect,val in prog_dict.items():
                if val['section'] == section:
                    return {'program_type':prog_name, 'section': sect}
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

    
#TODO is it more flexible w/o option? we can do filtering in wrapper functions
# if option is empty, null, none, just return more

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
    return get_schema_options(program=str_prog, section=str_section, query='models')

def get_program_model(str_prog, str_section, str_model):
    return get_schema_options(program=str_prog, section=str_section, query='models', model_name=str_model)

def get_section_reference(str_prog, str_section):
    return get_schema_options(program=str_prog, section=str_section, query='section')

def get_text_from_model(model):
    get_schema_options()

def get_text_from_df(df):
    return get_schema_options("", section=df.section, query='text')

def get_prog_from_section(str_section):  # this is pure, we could use get_schema_options but it's hard
    # 'SSP Closed Case Data'
    if str_section.startswith('SSP'):
        return 'SSP'
    elif str_section.startswith('Tribal'):
        return 'TAN'  # problematic, do we need to infer tribal entirely from tribe/fips code? should we make a new type?
    else:
        return 'TAN'
    
    #TODO: if given a datafile (section), we can reverse back to the program b/c the 
    # section string has "tribal/ssp" in it, then process of elimination we have tanf

def get_schema(line, section, program_type):
    """Return the appropriate schema for the line."""
    line_type = line[0:2]
    return get_schema_options(program_type, section, query='models', model_name=line_type)

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

def case_aggregates_by_month(df):
    """Return case aggregates by month."""
    section = str(df.section)  # section -> text
    print("section: ", section)
    program_type = get_prog_from_section(section)  # section -> program_type -> text
    print("program_type: ", program_type)

    # from datafile quarter, generate short month names for each month in quarter ala 'Jan', 'Feb', 'Mar'
    month_list = transform_to_months(df.quarter)
    print("month_list: ", month_list)
    # or we do upgrade get_schema_options to always take named params vs string text?

    short_section = get_text_from_df(df)['section']
    models = get_program_models(program_type, short_section)
    print("models: ", models)

    #TODO: convert models from dict to list of only the references

    '''
    section:  Active Case Data
    program_type:  TAN
    month_list:  ['Jan', 'Feb', 'Mar']
    models:  {'T1': <tdpservice.parsers.util.RowSchema object at 0xffff8afca230>, 
    'T2': <tdpservice.parsers.util.RowSchema object at 0xffff8b3a3730>, 
    'T3': <tdpservice.parsers.util.MultiRecordRowSchema object at 0xffff8b3a2b30>}
    '''
    


    # using a django queryset, filter by datafile to find relevant search_index objects

    # count the number of objects in the queryset and assign to total
    # using a queryset of parserError objects, filter by datafile and error_type to get count of rejected cases
    # subtract rejected cases from total to get accepted cases
    # return a dict of month: {accepted: x, rejected: y, total: z}
    '''for month in month_list:
        total = 0
        rejected = 0
        accepted = 0

        for model in models:
            total += model.objects.filter(datafile=df, month=month).count() # todo change to RPT_MONTH_YEAR
            rejected += model.objects.filter(datafile=df, error.exists()).count() # todo filter doesn't actually work this way
            #ParserError.objects.filter(datafile=df, month=month).count() #TODO filter where field_name != header or trailer ??
            accepted +=  total - rejected # again look for all objects where generic relation to error is false/empty

        case_aggregates_by_month[month] = {}
            
        # filter by month
        # filter by model
        # filter by datafile
        # count objects
        # add to dict
    '''