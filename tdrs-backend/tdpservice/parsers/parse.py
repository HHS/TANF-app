"""Convert raw uploaded Datafile into a parsed model, and accumulate/return any errors."""


from django.db import DatabaseError
import itertools
import logging
from .models import ParserErrorCategoryChoices, ParserError
from . import schema_defs, validators, util
from .schema_defs.utils import get_section_reference, get_program_model
from .case_consistency_validator import CaseConsistencyValidator

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
        util.make_generate_file_precheck_parser_error(datafile, 1)
    )
    if not header_is_valid:
        logger.info(f"Preparser Error: {len(header_errors)} header errors encountered.")
        errors['header'] = header_errors
        bulk_create_errors({1: header_errors}, 1, flush=True)
        return errors

    # TODO: write a test for this line
    case_consistency_validator = CaseConsistencyValidator(header, util.make_generate_parser_error(datafile, None))

    field_values = schema_defs.header.get_field_values_by_names(header_line,
                                                                {"encryption", "tribe_code", "state_fips"})

    # Validate tribe code in submission across program type and fips code
    generate_error = util.make_generate_parser_error(datafile, 1)
    tribe_is_valid, tribe_error = validators.validate_tribe_fips_program_agree(header['program_type'],
                                                                               field_values["tribe_code"],
                                                                               field_values["state_fips"],
                                                                               generate_error)

    if not tribe_is_valid:
        logger.info(f"Tribe Code ({field_values['tribe_code']}) inconsistency with Program Type " +
                    f"({header['program_type']}) and FIPS Code ({field_values['state_fips']}).",)
        errors['header'] = [tribe_error]
        bulk_create_errors({1: [tribe_error]}, 1, flush=True)
        return errors

    is_encrypted = field_values["encryption"] == "E"
    is_tribal = not validators.value_is_empty(field_values["tribe_code"], 3, extra_vals={'0'*3})

    logger.debug(f"Datafile has encrypted fields: {is_encrypted}.")
    logger.debug(f"Datafile: {datafile.__repr__()}, is Tribal: {is_tribal}.")

    # ensure file section matches upload section
    program_type = f"Tribal {header['program_type']}" if is_tribal else header['program_type']
    section = header['type']
    logger.debug(f"Program type: {program_type}, Section: {section}.")

    section_is_valid, section_error = validators.validate_header_section_matches_submission(
        datafile,
        get_section_reference(program_type, section),
        util.make_generate_parser_error(datafile, 1)
    )

    if not section_is_valid:
        logger.info(f"Preparser Error -> Section is not valid: {section_error.error_message}")
        errors['document'] = [section_error]
        unsaved_parser_errors = {1: [section_error]}
        bulk_create_errors(unsaved_parser_errors, 1, flush=True)
        return errors

    rpt_month_year_is_valid, rpt_month_year_error = validators.validate_header_rpt_month_year(
        datafile,
        header,
        util.make_generate_parser_error(datafile, 1)
    )
    if not rpt_month_year_is_valid:
        logger.info(f"Preparser Error -> Rpt Month Year is not valid: {rpt_month_year_error.error_message}")
        errors['document'] = [rpt_month_year_error]
        unsaved_parser_errors = {1: [rpt_month_year_error]}
        bulk_create_errors(unsaved_parser_errors, 1, flush=True)
        return errors

    line_errors = parse_datafile_lines(datafile, program_type, section, is_encrypted, case_consistency_validator)

    errors = errors | line_errors

    return errors

def bulk_create_records(unsaved_records, line_number, header_count, batch_size=10000, flush=False):
    """Bulk create passed in records."""
    if (line_number % batch_size == 0 and header_count > 0) or flush:
        logger.debug("Bulk creating records.")
        try:
            num_db_records_created = 0
            num_expected_db_records = 0
            num_elastic_records_created = 0
            for document, records in unsaved_records.items():
                num_expected_db_records += len(records)
                created_objs = document.Django.model.objects.bulk_create(records)
                num_elastic_records_created += document.update(created_objs)[0]
                num_db_records_created += len(created_objs)
            if num_db_records_created != num_expected_db_records:
                logger.error(f"Bulk Django record creation only created {num_db_records_created}/" +
                             f"{num_expected_db_records}!")
            elif num_elastic_records_created != num_expected_db_records:
                logger.error(f"Bulk Elastic document creation only created {num_elastic_records_created}/" +
                             f"{num_expected_db_records}!")
            else:
                logger.info(f"Created {num_db_records_created}/{num_expected_db_records} records.")
            return num_db_records_created == num_expected_db_records and \
                num_elastic_records_created == num_expected_db_records, {}
        except DatabaseError as e:
            logger.error(f"Encountered error while creating datafile records: {e}")
            return False, unsaved_records
    return True, unsaved_records

def bulk_create_errors(unsaved_parser_errors, num_errors, batch_size=5000, flush=False):
    """Bulk create all ParserErrors."""
    if flush or (unsaved_parser_errors and num_errors >= batch_size):
        logger.debug("Bulk creating ParserErrors.")
        num_created = len(ParserError.objects.bulk_create(list(itertools.chain.from_iterable(
            unsaved_parser_errors.values()))))
        logger.info(f"Created {num_created}/{num_errors} ParserErrors.")
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
    logger.info("Rolling back created records.")
    for document in unsaved_records:
        model = document.Django.model
        num_deleted, models = model.objects.filter(datafile=datafile).delete()
        logger.debug(f"Deleted {num_deleted} records of type: {model}.")

def rollback_parser_errors(datafile):
    """Delete created errors in the event of a failure."""
    logger.info("Rolling back created parser errors.")
    num_deleted, models = ParserError.objects.filter(file=datafile).delete()
    logger.debug(f"Deleted {num_deleted} {ParserError}.")

def validate_case_consistency(case_consistency_validator):
    """Force category four validation if we have reached the last case in the file."""
    if not case_consistency_validator.has_validated:
        case_consistency_validator.validate()

def parse_datafile_lines(datafile, program_type, section, is_encrypted, case_consistency_validator):
    """Parse lines with appropriate schema and return errors."""
    rawfile = datafile.file
    errors = {}

    line_number = 0

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
            logger.debug(f"{len(trailer_errors)} trailer error(s) detected for file " +
                         f"'{datafile.original_filename}' on line {line_number}.")
            errors['trailer'] = trailer_errors
            unsaved_parser_errors.update({"trailer": trailer_errors})
            num_errors += len(trailer_errors)

        generate_error = util.make_generate_parser_error(datafile, line_number)

        if header_count > 1:
            logger.info(f"Preparser Error -> Multiple headers found for file: {datafile.id} on line: {line_number}.")
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

        schema_manager = get_schema_manager(line, section, program_type)

        records = manager_parse_line(line, schema_manager, generate_error, is_encrypted)

        record_number = 0
        for i in range(len(records)):
            r = records[i]
            record_number += 1
            record, record_is_valid, record_errors = r
            if not record_is_valid:
                logger.debug(f"Record #{i} from line {line_number} is invalid.")
                line_errors = errors.get(f"{line_number}_{i}", {})
                line_errors.update({record_number: record_errors})
                errors.update({f"{line_number}_{i}": record_errors})
                unsaved_parser_errors.update({f"{line_number}_{i}": record_errors})
                num_errors += len(record_errors)
            if record:
                s = schema_manager.schemas[i]
                record.datafile = datafile
                unsaved_records.setdefault(s.document, []).append(record)
                case_consistency_validator.add_record(record, s, len(record_errors) > 0)

        # Add any generated cat4 errors to our error data structure & clear our caches errors list
        unsaved_parser_errors[None] = unsaved_parser_errors.get(None, []) + case_consistency_validator.get_generated_errors()
        case_consistency_validator.clear_errors()

        all_created, unsaved_records = bulk_create_records(unsaved_records, line_number, header_count,)
        unsaved_parser_errors, num_errors = bulk_create_errors(unsaved_parser_errors, num_errors)

    if header_count == 0:
        logger.info(f"Preparser Error -> No headers found for file: {datafile.id}.")
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
        logger.error(f"Not all parsed records created for file: {datafile.id}!")
        rollback_records(unsaved_records, datafile)
        bulk_create_errors(unsaved_parser_errors, num_errors, flush=True)
        return errors

    bulk_create_errors(unsaved_parser_errors, num_errors, flush=True)

    validate_case_consistency(case_consistency_validator)

    logger.debug(f"Cat4 validator cached {case_consistency_validator.total_cases_cached} cases and "
                 f"validated {case_consistency_validator.total_cases_validated} of them.")

    return errors


def manager_parse_line(line, schema_manager, generate_error, is_encrypted=False):
    """Parse and validate a datafile line using SchemaManager."""
    try:
        schema_manager.update_encrypted_fields(is_encrypted)
        records = schema_manager.parse_and_validate(line, generate_error)
        return records
    except AttributeError as e:
        logger.error(e)
        return [(None, False, [
            generate_error(
                schema=None,
                error_category=ParserErrorCategoryChoices.PRE_CHECK,
                error_message="Unknown Record_Type was found.",
                record=None,
                field="Record_Type",
            )
        ])]

def get_schema_manager(line, section, program_type):
    """Return the appropriate schema for the line."""
    line_type = line[0:2]
    return get_program_model(program_type, section, line_type)
