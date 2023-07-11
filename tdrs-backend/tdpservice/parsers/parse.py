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
        util.get_section_reference(program_type, section) 
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

