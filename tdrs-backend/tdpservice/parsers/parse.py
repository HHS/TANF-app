"""Convert raw uploaded Datafile into a parsed model, and accumulate/return any errors."""


import os
from . import schema_defs
from . import validators


def parse_datafile(datafile):
    """Parse and validate Datafile header/trailer, then select appropriate schema and parse/validate all lines."""
    rawfile = datafile.file
    errors = {}

    document_is_valid, document_error = validators.validate_document(rawfile, datafile.section)
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

    # determine the file type
    schema_options = None
    match header['program_type']:
        case 'TAN':
            # schema_options = schema_defs.tanf
            schema_options = None
        case 'SSP':
            # schema_options = schema_defs.ssp
            schema_options = None
        # case tribal?

    # ensure section matches given
    section_names = {
        'A': 'Active Case Data',
        'C': 'Closed Case Data',
        'G': 'Aggregate Data',
        'S': 'Stratum Data',
    }

    if not section_names[header['type']] == datafile.section:
        errors['document'] = ['Section does not match']
        return errors

    # parse line with appropriate schema
    rawfile.seek(0)
    line_number = 0

    for rawline in rawfile:
        line_number += 1
        line = rawline.decode().strip('\r\n')
        schema = get_schema(line, schema_options)

        if schema:
            record, record_is_valid, record_errors = schema.parse_and_validate(line)
            if not record_is_valid:
                errors[line_number] = record_errors

            record.errors = errors
            record.save()

    return errors


def get_schema(line, schema_options):
    """Return the appropriate schema for the line."""
    if line.startswith('HEADER'):
        return None
    elif line.startswith('TRAILER'):
        return None
    elif line.startswith('T1'):
        return None
        # return schema_options.t1
    elif line.startswith('T2'):
        return None
        # return schema_options.t2
    elif line.startswith('T3'):
        return None
        # return schema_options.t3
    elif line.startswith('T4'):
        return None
        # return schema_options.t4
    elif line.startswith('T5'):
        return None
        # return schema_options.t5
    elif line.startswith('T6'):
        return None
        # return schema_options.t6
    elif line.startswith('T7'):
        return None
        # return schema_options.t7
    else:
        return None
