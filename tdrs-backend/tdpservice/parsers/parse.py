"""Convert raw uploaded Datafile into a parsed model, and accumulate/return any errors."""

import os
from . import schema_defs, validators, util
from tdpservice.data_files.models import DataFile
from .models import DataFileSummary


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
    section_names = {
        'TAN': {
            'A': DataFile.Section.ACTIVE_CASE_DATA,
            'C': DataFile.Section.CLOSED_CASE_DATA,
            'G': DataFile.Section.AGGREGATE_DATA,
            'S': DataFile.Section.STRATUM_DATA,
        },
        'SSP': {
            'A': DataFile.Section.SSP_ACTIVE_CASE_DATA,
            'C': DataFile.Section.SSP_CLOSED_CASE_DATA,
            'G': DataFile.Section.SSP_AGGREGATE_DATA,
            'S': DataFile.Section.SSP_STRATUM_DATA,
        },
    }

    program_type = header['program_type']
    section = header['type']

    section_is_valid, section_error = validators.validate_header_section_matches_submission(
        datafile,
        section_names.get(program_type, {}).get(section)
    )

    if not section_is_valid:
        # error_func call
        errors['document'] = [section_error]
        return errors

    # parse line with appropriate schema
    rawfile.seek(0)
    line_number = 0
    schema_options = get_schema_options(program_type)

    for rawline in rawfile:
        line_number += 1
        line = rawline.decode().strip('\r\n')

        if line.startswith('HEADER') or line.startswith('TRAILER'):
            continue

        schema = get_schema(line, section, schema_options)

        if isinstance(schema, util.MultiRecordRowSchema):
            records = parse_multi_record_line(
                line,
                schema,
                util.make_generate_parser_error(datafile, line_number)
            )

            n = 0
            for r in records:
                n += 1
                record, record_is_valid, record_errors = r
                if not record_is_valid:
                    line_errors = errors.get(line_number, {})
                    line_errors[n] = record_errors
                    errors[line_number] = line_errors
        else:
            record_is_valid, record_errors = parse_datafile_line(
                line,
                schema,
                util.make_generate_parser_error(datafile, line_number)
            )

            if not record_is_valid:
                    errors[line_number] = record_errors

    summary = DataFileSummary(datafile=datafile)
    summary.set_status(errors)
    summary.save()

    return errors

def parse_multi_record_line(line, schema, error_func):
    """Parse a line with a multi-record schema."""
    if schema:
        records = schema.parse_and_validate(line, error_func)

        for r in records:
            record, record_is_valid, record_errors = r

            if record:
                record.save()

        return records

    return [(None, False, [
        error_func(
            schema=None,
            error_category="2",  # 1?
            error_message="No schema selected.",
            record=None,
            field=None
        )
    ])]


def parse_datafile_line(line, schema, error_func):
    """Parse and validate a datafile line and save any errors to the model."""
    if schema:
        record, record_is_valid, record_errors = schema.parse_and_validate(line, error_func)

        if record:
            record.save()

        return record_is_valid, record_errors

    return (False, [
        error_func(
            schema=None,
            error_category="1",  # 1?
            error_message="No schema selected.",
            record=None,
            field=None
        )
    ])


def get_schema_options(program_type):
    """Return the allowed schema options."""
    match program_type:
        case 'TAN':
            return schema_defs.tanf
        case 'SSP':
            return schema_defs.ssp
        # case tribal?
    return None


def get_schema(line, section, schema_options):
    """Return the appropriate schema for the line."""
    if section == 'A' and line.startswith('T1'):
        return schema_options.t1
    # elif section == 'A' and line.startswith('T2'):
    #     return None
    #     # return schema_options.t2
    # elif section == 'A' and line.startswith('T3'):
    #     return None
    #     # return schema_options.t3
    # elif section == 'C' and line.startswith('T4'):
    #     return None
    #     # return schema_options.t4
    # elif section == 'C' and line.startswith('T5'):
    #     return None
    #     # return schema_options.t5
    # elif section == 'G' and line.startswith('T6'):
    #     return None
    #     # return schema_options.t6
    # elif section == 'S' and line.startswith('T7'):
    #     return None
    #     # return schema_options.t7
    # elif section == 'A' and line.startswith('M1'):
    #     return schema_options.m1
    # elif section == 'A' and line.startswith('M2'):
    #     return schema_options.m2
    # elif section == 'A' and line.startswith('M3'):
    #     return schema_options.m3
    # elif section == 'C' and line.startswith('M4'):
    #     return None
    #     # return schema_options.t4
    # elif section == 'C' and line.startswith('M5'):
    #     return None
    #     # return schema_options.t5
    # elif section == 'G' and line.startswith('M6'):
    #     return None
    #     # return schema_options.t6
    # elif section == 'S' and line.startswith('M7'):
    #     return None
    #     # return schema_options.t7 
    else:  # Just a place-holder for linting until we full implement this.
        return None
