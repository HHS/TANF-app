"""Convert raw uploaded Datafile into a parsed model, and accumulate/return any errors."""

import os
from . import schema_defs
from . import validators
from . import schema_defs, validators, util
from tdpservice.data_files.models import DataFile
from .models import DataFileSummary, ParserError


def parse_datafile(datafile):
    """Parse and validate Datafile header/trailer, then select appropriate schema and parse/validate all lines."""
    rawfile = datafile.file
    errors = {}

    document_is_valid, document_error = validators.validate_single_header_trailer(
        rawfile,
        util.make_generate_parser_error(datafile, 1)
    )
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

    if datafile.section != section_names.get(program_type, {}).get(section):
        # error_func call 
        errors['document'] = \
            util.generate_parser_error(
                datafile=datafile,
                row_number=1,
                column_number=schema_defs.header.get_field('type').startIndex,
                item_number=0,
                field_name='type',
                category=1,
                error_type=util.error_types.get(1, None),
                error_message=f"Section '{section}' does not match upload section '{datafile.section}'",
                content_type=None,
                object_id=None,
                fields_json=None
            )

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
        record_is_valid, record_errors = parse_datafile_line(line, schema)

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

    return summary, errors

def parse_multi_record_line(line, schema, error_func):
    if schema:
        records = schema.parse_and_validate(line, error_func)

        for r in records:
            record, record_is_valid, record_errors = r

            if record:
                record.save()

                # for error_msg in record_errors:
                #     error_obj = ParserError.objects.create(
                #         file=None,
                #         row_number=None,
                #         column_number=None,
                #         field_name=None,
                #         category=None,
                #         case_number=getattr(record, 'CASE_NUMBER', None),
                #         error_message=error_msg,
                #         error_type=None,
                #         content_type=schema.model,
                #         object_id=record.pk,
                #         fields_json=None
                #     )

        return records

    return [(None, False, ['No schema selected.'])]


def parse_datafile_line(line, schema, error_func):
    """Parse and validate a datafile line and save any errors to the model."""
    if schema:
        record, record_is_valid, record_errors = schema.parse_and_validate(line, error_func)

        if record:
            record.errors = record_errors
            record.save()

            # for error_msg in record_errors:
            #         error_obj = ParserError.objects.create(
            #             file=None,
            #             row_number=None,
            #             column_number=None,
            #             field_name=None,
            #             category=None,
            #             case_number=None,
            #             error_message=error_msg,
            #             error_type=None,
            #             content_type=schema.model,
            #             object_id=record.pk,
            #             fields_json=None
            #         )

        return record_is_valid, record_errors

    return (False, ['No schema selected.'])


def get_schema_options(program_type):
    """Return the allowed schema options."""
    match program_type:
        case 'TAN':
            return schema_defs.tanf
        case 'SSP':
            # return schema_defs.ssp
            return None
        # case tribal?
    return None


def get_schema(line, section, schema_options):
    """Return the appropriate schema for the line."""
    if section == 'A' and line.startswith('T1'):
        return schema_options.t1
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
