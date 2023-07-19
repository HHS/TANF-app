"""Convert raw uploaded Datafile into a parsed model, and accumulate/return any errors."""

import os
from . import schema_defs, validators, util
from .models import ParserErrorCategoryChoices


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

    # ensure file section matches upload section
    program_type = header['program_type']
    section = header['type']

    section_is_valid, section_error = validators.validate_header_section_matches_submission(
        datafile,
        util.get_section_reference(program_type, section)
    )

    if not section_is_valid:
        errors['document'] = [section_error]
        return errors

    line_errors = parse_datafile_lines(datafile, program_type, section)

    errors = errors | line_errors

    return errors


def parse_datafile_lines(datafile, program_type, section):
    """Parse and validate all lines in a datafile."""
    errors = {}
    rawfile = datafile.file

    rawfile.seek(0)
    line_number = 0

    for rawline in rawfile:
        line_number += 1
        line = rawline.decode().strip('\r\n')

        if line.startswith('HEADER') or line.startswith('TRAILER'):
            continue

        schema = util.get_schema(line, section, program_type)
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
                util.make_generate_parser_error(datafile, line_number),
                datafile
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
                util.make_generate_parser_error(datafile, line_number),
                datafile
            )

            if not record_is_valid:
                errors[line_number] = record_errors

    return errors


def parse_multi_record_line(line, schema, generate_error, datafile):
    """Parse and validate a datafile line using MultiRecordRowSchema."""
    if schema:
        records = schema.parse_and_validate(line, generate_error)

        for r in records:
            record, record_is_valid, record_errors = r

            if record:
                record.datafile = datafile
                record.save()

        return records



def parse_datafile_line(line, schema, generate_error, datafile):
    """Parse and validate a datafile line and save any errors to the model."""
    if schema:
        record, record_is_valid, record_errors = schema.parse_and_validate(line, generate_error)

        if record:
            record.datafile = datafile
            record.save()

        return record_is_valid, record_errors


def get_schema_options(program_type):
    """Return the allowed schema options."""
    match program_type:
        case 'TAN':
            return {
                'A': {
                    'T1': schema_defs.tanf.t1,
                    'T2': schema_defs.tanf.t2,
                    'T3': schema_defs.tanf.t3,
                },
                'C': {
                    # 'T4': schema_options.t4,
                    # 'T5': schema_options.t5,
                },
                'G': {
                    # 'T6': schema_options.t6,
                },
                'S': {
                    # 'T7': schema_options.t7,
                },
            }
        case 'SSP':
            return {
                'A': {
                    'M1': schema_defs.ssp.m1,
                    'M2': schema_defs.ssp.m2,
                    'M3': schema_defs.ssp.m3,
                },
                'C': {
                    # 'M4': schema_options.m4,
                    # 'M5': schema_options.m5,
                },
                'G': {
                    # 'M6': schema_options.m6,
                },
                'S': {
                    # 'M7': schema_options.m7,
                },
            }
        # case tribal?
    return None


def get_schema(line, section, schema_options):
    """Return the appropriate schema for the line."""
    line_type = line[0:2]
    return schema_options.get(section, {}).get(line_type, None)
