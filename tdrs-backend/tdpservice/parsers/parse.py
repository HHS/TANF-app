"""Convert raw uploaded Datafile into a parsed model, and accumulate/return any errors."""

import os
from . import schema_defs, validators, util
from .models import ParserErrorCategoryChoices
from tdpservice.data_files.models import DataFile


def parse_datafile(datafile):
    """Parse and validate Datafile header/trailer, then select appropriate schema and parse/validate all lines."""
    rawfile = datafile.file
    errors = {}

    document_is_valid, document_error = validators.validate_single_header_trailer(datafile)
    if not document_is_valid:
        errors['document'] = [document_error]
        return errors

    # get header line
    rawfile.seek(0)
    header_line = rawfile.readline().decode().strip()

    # get trailer line
    rawfile.seek(0)
    rawfile.seek(-2, os.SEEK_END)
    while rawfile.read(1) != b'\n':
        rawfile.seek(-2, os.SEEK_CUR)

    trailer_line = rawfile.readline().decode().strip('\n')

    # parse header, trailer
    header, header_is_valid, header_errors = schema_defs.header.parse_and_validate(
        header_line,
        util.make_generate_parser_error(datafile, 1)
    )
    if not header_is_valid:
        errors['header'] = header_errors
        return errors

    trailer, trailer_is_valid, trailer_errors = schema_defs.trailer.parse_and_validate(
        trailer_line,
        util.make_generate_parser_error(datafile, -1)
    )
    if not trailer_is_valid:
        errors['trailer'] = trailer_errors



    program_type = header['program_type']
    section = header['type']

    section_is_valid, section_error = validators.validate_header_section_matches_submission(
        datafile,
        get_section_field(program_type, section)
    )

    if not section_is_valid:
        errors['document'] = [section_error]
        return errors

    line_errors = parse_datafile_lines(datafile, program_type, section)

    errors = errors | line_errors

    # errors['summary'] = DataFileSummary.objects.create(
    #     datafile=datafile,
    #     status=DataFileSummary.get_status(errors)
    # )

    # or perhaps just invert this?
    # what does it look like having the errors dict as a field of the summary?
    # summary.errors = errors  --- but I don't want/need to store this in DB
    # divesting that storage and just using my FK to datafile so I can run querysets later
    # perserves the ability to use the summary object to generate the errors dict

    # perhaps just formalize the entire errors struct?
    # pros:
    #   - can be used to generate error report
    #   - can be used to generate summary
    #  - can be used to generate error count
    #  - can be used to generate error count by type
    #  - can be used to generate error count by record type
    #  - can be used to generate error count by field
    #  - can be used to generate error count by field type
    #  - has a consistent structure between differing file types
    #  - has testable functions for each of the above
    #  - has agreed-upon inputs/outputs
    # cons:
    #  - requires boilerplate to generate
    #  - different structures may be needed for different purposes
    #  - built-in dict may be easier to reference ala Cameron
    #  - built-in dict is freer-form and complete already

    return errors


def parse_datafile_lines(datafile, program_type, section):
    """Parse lines with appropriate schema and return errors."""
    #dfs = DataFileSummary.object.create(datafile=datafile)
    # and then what, pass in program_type to case_aggregates after loop?
    errors = {}
    rawfile = datafile.file

    rawfile.seek(0)
    line_number = 0

    for rawline in rawfile:
        line_number += 1
        line = rawline.decode().strip('\r\n')

        if line.startswith('HEADER') or line.startswith('TRAILER'):
            continue

        schema = get_schema(line, section, program_type)
        if schema is None:
            errors[line_number] = [util.generate_parser_error(
                datafile=datafile,
                line_number=line_number,
                schema=None,
                error_category=ParserErrorCategoryChoices.PRE_CHECK,
                error_message="Unknown Record_Type was found.",
                record=None,
                field="Record_Type",
            )]
            continue

        if isinstance(schema, util.MultiRecordRowSchema):
            records = parse_multi_record_line(
                line,
                schema,
                util.make_generate_parser_error(datafile, line_number)
            )

            record_number = 0
            for r in records:
                record_number += 1
                record, record_is_valid, record_errors = r
                if not record_is_valid:
                    line_errors = errors.get(line_number, {})
                    line_errors[record_number] = record_errors
                    errors[line_number] = line_errors
        else:
            record_is_valid, record_errors = parse_datafile_line(
                line,
                schema,
                util.make_generate_parser_error(datafile, line_number)
            )

            if not record_is_valid:
                errors[line_number] = record_errors

    return errors


def parse_multi_record_line(line, schema, generate_error):
    """Parse and validate a datafile line using MultiRecordRowSchema."""
    records = schema.parse_and_validate(line, generate_error)

    for r in records:
        record, record_is_valid, record_errors = r

        if record:
            record.save()

    return records


def parse_datafile_line(line, schema, generate_error):
    """Parse and validate a datafile line and save any errors to the model."""
    record, record_is_valid, record_errors = schema.parse_and_validate(line, generate_error)

    if record:
        record.save()

    return record_is_valid, record_errors

def get_schema_options(program, section, query=None, model=None, model_name=None):
    '''
    Centralized function to return the appropriate schema for a given program, section, and query.
    @param program: the abbreviated program type (.e.g, 'TAN')
    @param section: the section of the file (.e.g, 'A')
    @param query: the query for section_names (.e.g, 'section', 'models', etc.)
    @return: the appropriate references (e.g., ACTIVE_CASE_DATA or {t1,t2,t3}) 
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
                    'S1': schema_defs.ssp.m1,
                    'S2': schema_defs.ssp.m2,
                    'S3': schema_defs.ssp.m3,
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
                if val==model:
                    return {'program_type':prog_name, 'section': sect}
        raise ValueError("Model not found in schema_defs")
    elif query == "section":
        return schema_options.get(program, {}).get(section, None)[query]
    elif query == "models":
        links = schema_options.get(program, {}).get(section, None)

        # if query is not chosen or wrong input, return all options
        # query = 'models', model = 'T1'
        models = links.get(query, links)

        return models.get(model_name, models)

    
#TODO is it more flexible w/o option? we can do filtering in wrapper functions
# if option is empty, null, none, just return more

'''
text -> section
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



    #TODO: if given a datafile (section), we can reverse back to the program b/c the section string has "tribal/ssp" in it, then process of elimination we have tanf


def get_schema(line, section, program_type):
    """Return the appropriate schema for the line."""
    line_type = line[0:2]
    return get_schema_options(program_type, section, query='models', model_name=line_type)
