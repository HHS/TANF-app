"""Convert raw uploaded Datafile into a parsed model, and accumulate/return any errors."""


from django.db import DatabaseError
import itertools
import logging
from .models import ParserErrorCategoryChoices, ParserError
from . import schema_defs, validators, util

logger = logging.getLogger(__name__)


def parse_datafile(datafile):
    """Parse and validate Datafile header/trailer, then select appropriate schema and parse/validate all lines."""
    rawfile = datafile.file
    errors = {}

    # parse header, trailer
    rawfile.seek(0)
    header_line = rawfile.readline().decode().strip()
    header, header_is_valid, header_errors = schema_defs.header.parse_and_validate(
        header_line,
        util.make_generate_parser_error(datafile, 1)
    )
    if not header_is_valid:
        errors['header'] = header_errors
        bulk_create_errors({1: header_errors}, 1, flush=True)
        return errors

    is_encrypted = util.contains_encrypted_indicator(header_line, schema_defs.header.get_field_by_name("encryption"))

    # ensure file section matches upload section
    program_type = header['program_type']
    section = header['type']

    section_is_valid, section_error = validators.validate_header_section_matches_submission(
        datafile,
        program_type,
        section,
    )

    if not section_is_valid:
        errors['document'] = [section_error]
        unsaved_parser_errors = {1: [section_error]}
        bulk_create_errors(unsaved_parser_errors, 1, flush=True)
        return errors

    line_errors = parse_datafile_lines(datafile, program_type, section, is_encrypted)

    errors = errors | line_errors

    return errors


def bulk_create_records(unsaved_records, line_number, header_count, batch_size=10000, flush=False):
    """Bulk create passed in records."""
    if (line_number % batch_size == 0 and header_count > 0) or flush:
        try:
            num_created = 0
            num_expected = 0
            for model, records in unsaved_records.items():
                num_expected += len(records)
                num_created += len(model.objects.bulk_create(records))
            return num_created == num_expected, {}
        except DatabaseError as e:
            logger.error(f"Encountered error while creating datafile records: {e}")
            return False, unsaved_records
    return True, unsaved_records

def bulk_create_errors(unsaved_parser_errors, num_errors, batch_size=5000, flush=False):
    """Bulk create all ParserErrors."""
    if flush or (unsaved_parser_errors and num_errors >= batch_size):
        ParserError.objects.bulk_create(list(itertools.chain.from_iterable(unsaved_parser_errors.values())))
        return {}, 0
    return unsaved_parser_errors, num_errors

def evaluate_trailer(datafile, trailer_count, multiple_trailer_errors, is_last_line, line, line_number):
    """Validate datafile trailer and return associated errors if any."""
    if trailer_count > 1 and not multiple_trailer_errors:
        return (True, [util.make_generate_parser_error(datafile, line_number)(
                schema=None,
                error_category=ParserErrorCategoryChoices.PRE_CHECK,
                error_message="Multiple trailers found.",
                record=None,
                field=None
                )])
    if trailer_count == 1 or is_last_line:
        record, trailer_is_valid, trailer_errors = schema_defs.trailer.parse_and_validate(
            line,
            util.make_generate_parser_error(datafile, line_number)
        )
        return (multiple_trailer_errors, None if not trailer_errors else trailer_errors)
    return (False, None)

def rollback_records(unsaved_records, datafile):
    """Delete created records in the event of a failure."""
    for model in unsaved_records:
        model.objects.filter(datafile=datafile).delete()

def rollback_parser_errors(datafile):
    """Delete created errors in the event of a failure."""
    ParserError.objects.filter(file=datafile).delete()

def parse_datafile_lines(datafile, program_type, section, is_encrypted):
    """Parse lines with appropriate schema and return errors."""
    rawfile = datafile.file
    errors = {}

    line_number = 0
    schema_manager_options = get_schema_manager_options(program_type)

    unsaved_records = {}
    unsaved_parser_errors = {}

    header_count = 0
    trailer_count = 0
    prev_sum = 0
    num_errors = 0
    multiple_trailer_errors = False

    # Note: it is unnecessary to call rawfile.seek(0) again because the generator
    # automatically starts back at the begining of the file.
    file_length = len(rawfile)
    offset = 0
    for rawline in rawfile:
        line_number += 1
        offset += len(rawline)
        line = rawline.decode().strip('\r\n')

        header_count += int(line.startswith('HEADER'))
        trailer_count += int(line.startswith('TRAILER'))

        is_last = offset == file_length
        multiple_trailer_errors, trailer_errors = evaluate_trailer(datafile, trailer_count, multiple_trailer_errors,
                                                                   is_last, line, line_number)

        if trailer_errors is not None:
            errors['trailer'] = trailer_errors
            unsaved_parser_errors.update({"trailer": trailer_errors})
            num_errors += len(trailer_errors)

        generate_error = util.make_generate_parser_error(datafile, line_number)

        if header_count > 1:
            errors.update({'document': ['Multiple headers found.']})
            err_obj = generate_error(
                schema=None,
                error_category=ParserErrorCategoryChoices.PRE_CHECK,
                error_message="Multiple headers found.",
                record=None,
                field=None
            )
            preparse_error = {line_number: [err_obj]}
            unsaved_parser_errors.update(preparse_error)
            rollback_records(unsaved_records, datafile)
            rollback_parser_errors(datafile)
            bulk_create_errors(preparse_error, num_errors, flush=True)
            return errors

        if prev_sum != header_count + trailer_count:
            prev_sum = header_count + trailer_count
            continue

        schema_manager = get_schema_manager(line, section, schema_manager_options)

        schema_manager.update_encrypted_fields(is_encrypted)

        records = manager_parse_line(line, schema_manager, generate_error)

        record_number = 0
        for i in range(len(records)):
            r = records[i]
            record_number += 1
            record, record_is_valid, record_errors = r
            if not record_is_valid:
                errors.update({f"{line_number}_{i}": record_errors})
                unsaved_parser_errors.update({f"{line_number}_{i}": record_errors})
                num_errors += len(record_errors)
            if record:
                s = schema_manager.schemas[i]
                record.datafile = datafile
                unsaved_records.setdefault(s.model, []).append(record)

        all_created, unsaved_records = bulk_create_records(unsaved_records, line_number, header_count,)
        unsaved_parser_errors, num_errors = bulk_create_errors(unsaved_parser_errors, num_errors)

    if header_count == 0:
        errors.update({'document': ['No headers found.']})
        err_obj = generate_error(
            schema=None,
            error_category=ParserErrorCategoryChoices.PRE_CHECK,
            error_message="No headers found.",
            record=None,
            field=None
        )
        rollback_records(unsaved_records, datafile)
        rollback_parser_errors(datafile)
        preparse_error = {line_number: [err_obj]}
        bulk_create_errors(preparse_error, num_errors, flush=True)
        return errors

    # Only checking "all_created" here because records remained cached if bulk create fails. This is the last chance to
    # successfully create the records.
    all_created, unsaved_records = bulk_create_records(unsaved_records, line_number, header_count, flush=True)
    if not all_created:
        rollback_records(unsaved_records, datafile)
        bulk_create_errors(unsaved_parser_errors, num_errors, flush=True)
        return errors

    bulk_create_errors(unsaved_parser_errors, num_errors, flush=True)

    return errors


def manager_parse_line(line, schema_manager, generate_error):
    """Parse and validate a datafile line using SchemaManager."""
    if schema_manager.schemas:
        records = schema_manager.parse_and_validate(line, generate_error)
        return records

    return [(None, False, [
        generate_error(
            schema=None,
            error_category=ParserErrorCategoryChoices.PRE_CHECK,
            error_message="Record Type is missing from record.",
            record=None,
            field=None
        )
    ])]


def get_schema_manager_options(program_type):
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
                    'T4': schema_defs.tanf.t4,
                    'T5': schema_defs.tanf.t5,
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


def get_schema_manager(line, section, schema_options):
    """Return the appropriate schema for the line."""
    line_type = line[0:2]
    return schema_options.get(section, {}).get(line_type, util.SchemaManager([]))
