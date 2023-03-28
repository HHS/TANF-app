"""Convert raw uploaded Datafile into a parsed model, and accumulate/return any errors."""


import os
from . import schema_defs
from . import validators


def parse_datafile(datafile):
    """Parse and validate Datafile header/trailer, then select appropriate schema and parse/validate all lines."""
    rawfile = datafile.file
    errors = {}

    document_is_valid, document_error = validators.validate_single_header_trailer(rawfile)
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
    header, header_is_valid, header_errors = schema_defs.header.parse_and_validate(header_line)
    if not header_is_valid:
        errors['header'] = header_errors

    trailer, trailer_is_valid, trailer_errors = schema_defs.trailer.parse_and_validate(trailer_line)
    if not trailer_is_valid:
        errors['trailer'] = trailer_errors

    if not header_is_valid or not trailer_is_valid:
        return errors

    # ensure file section matches upload section
    section_names = {
        'A': 'Active Case Data',
        'C': 'Closed Case Data',
        'G': 'Aggregate Data',
        'S': 'Stratum Data',
    }

    section = header['type']

    if datafile.section.find(section_names[section]) == -1:
        errors['document'] = ['Section does not match.']
        return errors

    # parse line with appropriate schema
    rawfile.seek(0)
    line_number = 0
    schema_options = get_schema_options(header['program_type'])

    for rawline in rawfile:
        line_number += 1
        line = rawline.decode().strip('\r\n')

        if line.startswith('HEADER') or line.startswith('TRAILER'):
            continue

        schema = get_schema(line, section, schema_options)
        record_is_valid, record_errors = parse_datafile_line(line, schema)

        if not record_is_valid:
            errors[line_number] = record_errors

    return errors


def parse_datafile_line(line, schema):
    """Parse and validate a datafile line and save any errors to the model."""
    if schema:
        record, record_is_valid, record_errors = schema.parse_and_validate(line)

        if record:
            record.errors = record_errors
            record.save()

        return record_is_valid, record_errors

    return (False, ['No schema selected.'])


def get_schema_options(program_type):
    """Return the allowed schema options."""
    match program_type:
        case 'TAN':
            # schema_options = schema_defs.tanf
            return None
        case 'SSP':
            # schema_options = schema_defs.ssp
            return None
        # case tribal?
    return None


def get_schema(line, section, schema_options):
    """Return the appropriate schema for the line."""
    if section == 'A' and line.startswith('T1'):
        return None
        # return schema_options.t1
    elif section == 'A' and line.startswith('T2'):
        return None
        # return schema_options.t2
    elif section == 'A' and line.startswith('T3'):
        return None
        # return schema_options.t3
    elif section == 'C' and line.startswith('T4'):
        return None
        # return schema_options.t4
    elif section == 'C' and line.startswith('T5'):
        return None
        # return schema_options.t5
    elif section == 'G' and line.startswith('T6'):
        return None
        # return schema_options.t6
    elif section == 'S' and line.startswith('T7'):
        return None
        # return schema_options.t7
    else:
        return None
