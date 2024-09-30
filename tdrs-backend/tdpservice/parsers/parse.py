"""Convert raw uploaded Datafile into a parsed model, and accumulate/return any errors."""


from django.conf import settings
from django.db.utils import DatabaseError
from elasticsearch.exceptions import ElasticsearchException
import itertools
import logging
from tdpservice.parsers.models import ParserErrorCategoryChoices, ParserError
from tdpservice.parsers import row_schema, schema_defs, util
from tdpservice.parsers.validators import category1
from tdpservice.parsers.validators.util import value_is_empty
from tdpservice.parsers.schema_defs.utils import get_section_reference, get_program_model
from tdpservice.parsers.case_consistency_validator import CaseConsistencyValidator
from tdpservice.parsers.util import log_parser_exception
from tdpservice.search_indexes.models.reparse_meta import ReparseMeta

logger = logging.getLogger(__name__)


def parse_datafile(datafile, dfs):
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
        update_meta_model(datafile, dfs)
        return errors
    elif header_is_valid and len(header_errors) > 0:
        logger.info(f"Preparser Warning: {len(header_errors)} header warnings encountered.")
        errors['header'] = header_errors
        bulk_create_errors({1: header_errors}, 1, flush=True)

    field_values = schema_defs.header.get_field_values_by_names(header_line,
                                                                {"encryption", "tribe_code", "state_fips"})
    is_encrypted = field_values["encryption"] == "E"
    is_tribal = not value_is_empty(field_values["tribe_code"], 3, extra_vals={'0'*3})

    logger.debug(f"Datafile has encrypted fields: {is_encrypted}.")
    logger.debug(f"Datafile: {datafile.__repr__()}, is Tribal: {is_tribal}.")

    program_type = f"Tribal {header['program_type']}" if is_tribal else header['program_type']
    section = header['type']
    logger.debug(f"Program type: {program_type}, Section: {section}.")

    cat4_error_generator = util.make_generate_case_consistency_parser_error(datafile)
    case_consistency_validator = CaseConsistencyValidator(
        header,
        program_type,
        datafile.stt.type,
        cat4_error_generator
    )

    # Validate tribe code in submission across program type and fips code
    generate_error = util.make_generate_parser_error(datafile, 1)
    tribe_is_valid, tribe_error = category1.validate_tribe_fips_program_agree(
        header['program_type'],
        field_values["tribe_code"],
        field_values["state_fips"],
        generate_error
    )

    if not tribe_is_valid:
        logger.info(f"Tribe Code ({field_values['tribe_code']}) inconsistency with Program Type " +
                    f"({header['program_type']}) and FIPS Code ({field_values['state_fips']}).",)
        errors['header'] = [tribe_error]
        bulk_create_errors({1: [tribe_error]}, 1, flush=True)
        update_meta_model(datafile, dfs)
        return errors

    # Ensure file section matches upload section
    section_is_valid, section_error = category1.validate_header_section_matches_submission(
        datafile,
        get_section_reference(program_type, section),
        util.make_generate_parser_error(datafile, 1)
    )

    if not section_is_valid:
        logger.info(f"Preparser Error -> Section is not valid: {section_error.error_message}")
        errors['document'] = [section_error]
        unsaved_parser_errors = {1: [section_error]}
        bulk_create_errors(unsaved_parser_errors, 1, flush=True)
        update_meta_model(datafile, dfs)
        return errors

    rpt_month_year_is_valid, rpt_month_year_error = category1.validate_header_rpt_month_year(
        datafile,
        header,
        util.make_generate_parser_error(datafile, 1)
    )
    if not rpt_month_year_is_valid:
        logger.info(f"Preparser Error -> Rpt Month Year is not valid: {rpt_month_year_error.error_message}")
        errors['document'] = [rpt_month_year_error]
        unsaved_parser_errors = {1: [rpt_month_year_error]}
        bulk_create_errors(unsaved_parser_errors, 1, flush=True)
        update_meta_model(datafile, dfs)
        return errors

    line_errors = parse_datafile_lines(datafile, dfs, program_type, section, is_encrypted, case_consistency_validator)

    errors = errors | line_errors

    return errors

def update_meta_model(datafile, dfs):
    """Update appropriate meta models."""
    ReparseMeta.increment_records_created(datafile.reparse_meta_models, dfs.total_number_of_records_created)
    ReparseMeta.increment_files_completed(datafile.reparse_meta_models)

def bulk_create_records(unsaved_records, line_number, header_count, datafile, dfs, flush=False):
    """Bulk create passed in records."""
    batch_size = settings.BULK_CREATE_BATCH_SIZE
    if (line_number % batch_size == 0 and header_count > 0) or flush:
        logger.debug("Bulk creating records.")
        num_db_records_created = 0
        num_expected_db_records = 0
        num_elastic_records_created = 0
        for document, records in unsaved_records.items():
            try:
                num_expected_db_records += len(records)
                created_objs = document.Django.model.objects.bulk_create(records)
                num_db_records_created += len(created_objs)
                num_elastic_records_created += document.update(created_objs)[0]
            except ElasticsearchException as e:
                log_parser_exception(datafile,
                                     f"Encountered error while indexing datafile documents: \n{e}",
                                     "error"
                                     )
                continue
            except DatabaseError as e:
                log_parser_exception(datafile,
                                     f"Encountered error while creating database records: \n{e}",
                                     "error"
                                     )
                return False
            except Exception as e:
                log_parser_exception(datafile,
                                     f"Encountered generic exception while creating database records: \n{e}",
                                     "error"
                                     )
                return False

        dfs.total_number_of_records_created += num_db_records_created
        if num_db_records_created != num_expected_db_records:
            logger.error(f"Bulk Django record creation only created {num_db_records_created}/" +
                         f"{num_expected_db_records}!")
        elif num_elastic_records_created != num_expected_db_records:
            logger.error(f"Bulk Elastic document creation only created {num_elastic_records_created}/" +
                         f"{num_expected_db_records}!")
        else:
            logger.info(f"Created {num_db_records_created}/{num_expected_db_records} records.")
        return num_db_records_created == num_expected_db_records
    return False

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
        try:
            model = document.Django.model
            qset = model.objects.filter(datafile=datafile)
            # We must tell elastic to delete the documents first because after we call `_raw_delete` the queryset will
            # be empty which will tell elastic that nothing needs updated.
            document.update(qset, refresh=True, action="delete")
            # WARNING: we can use `_raw_delete` in this case because our record models don't have cascading
            # dependencies. If that ever changes, we should NOT use `_raw_delete`.
            num_deleted = qset._raw_delete(qset.db)
            logger.debug(f"Deleted {num_deleted} records of type: {model}.")
        except ElasticsearchException as e:
            # Caught an Elastic exception, to ensure the quality of the DB, we will force the DB deletion and let
            # Elastic clean up later.
            log_parser_exception(datafile,
                                 f"Encountered error while indexing datafile documents: \n{e}",
                                 "error"
                                 )
            logger.warning("Encountered an Elastic exception, enforcing DB cleanup.")
            num_deleted, models = qset.delete()
            log_parser_exception(datafile,
                                 "Succesfully performed DB cleanup after elastic failure in rollback_records.",
                                 "info"
                                 )
        except DatabaseError as e:
            log_parser_exception(datafile,
                                 (f"Encountered error while deleting database records for model: {model}. "
                                  f"Exception: \n{e}"),
                                 "error"
                                 )
        except Exception as e:
            log_parser_exception(datafile,
                                 f"Encountered generic exception while trying to rollback records. Exception: \n{e}",
                                 "error"
                                 )

def rollback_parser_errors(datafile):
    """Delete created errors in the event of a failure."""
    try:
        logger.info("Rolling back created parser errors.")
        qset = ParserError.objects.filter(file=datafile)
        # WARNING: we can use `_raw_delete` in this case because our error models don't have cascading dependencies. If
        # that ever changes, we should NOT use `_raw_delete`.
        num_deleted = qset._raw_delete(qset.db)
        logger.debug(f"Deleted {num_deleted} ParserErrors.")
    except DatabaseError as e:
        log_parser_exception(datafile,
                             ("Encountered error while deleting database records for ParserErrors. "
                              f"Exception: \n{e}"),
                             "error"
                             )
    except Exception as e:
        log_parser_exception(datafile,
                             f"Encountered generic exception while rolling back ParserErrors. Exception: \n{e}.",
                             "error"
                             )

def validate_case_consistency(case_consistency_validator):
    """Force category four validation if we have reached the last case in the file."""
    if not case_consistency_validator.has_validated:
        return case_consistency_validator.validate() > 0
    return False

def generate_trailer_errors(trailer_errors, errors, unsaved_parser_errors, num_errors):
    """Generate trailer errors if we care to see them."""
    if settings.GENERATE_TRAILER_ERRORS:
        errors['trailer'] = trailer_errors
        unsaved_parser_errors.update({"trailer": trailer_errors})
        num_errors += len(trailer_errors)
    return errors, unsaved_parser_errors, num_errors

def create_no_records_created_pre_check_error(datafile, dfs):
    """Generate a precheck error if no records were created."""
    errors = {}
    created = 0
    if dfs.total_number_of_records_created == 0:
        generate_error = util.make_generate_parser_error(datafile, 0)
        err_obj = generate_error(
                schema=None,
                error_category=ParserErrorCategoryChoices.PRE_CHECK,
                error_message="No records created.",
                record=None,
                field=None
            )
        errors["no_records_created"] = [err_obj]
        created = 1
    return errors, created

def delete_serialized_records(duplicate_manager, dfs):
    """Delete all records that have already been serialized to the DB that have cat4 errors."""
    total_deleted = 0
    for document, ids in duplicate_manager.get_records_to_remove().items():
        try:
            model = document.Django.model
            qset = model.objects.filter(id__in=ids)
            # We must tell elastic to delete the documents first because after we call `_raw_delete` the queryset will
            # be empty which will tell elastic that nothing needs updated.
            document.update(qset, refresh=True, action="delete")
            # WARNING: we can use `_raw_delete` in this case because our record models don't have cascading
            # dependencies. If that ever changes, we should NOT use `_raw_delete`.
            num_deleted = qset._raw_delete(qset.db)
            total_deleted += num_deleted
            dfs.total_number_of_records_created -= num_deleted
            logger.debug(f"Deleted {num_deleted} records of type: {model}.")
        except ElasticsearchException as e:
            # Caught an Elastic exception, to ensure the quality of the DB, we will force the DB deletion and let
            # Elastic clean up later.
            log_parser_exception(dfs.datafile,
                                 ("Encountered error while indexing datafile documents. Enforcing DB cleanup. "
                                  f"Exception: \n{e}"),
                                 "error"
                                 )
            num_deleted, models = qset.delete()
            total_deleted += num_deleted
            dfs.total_number_of_records_created -= num_deleted
            log_parser_exception(dfs.datafile,
                                 "Succesfully performed DB cleanup after elastic failure in delete_serialized_records.",
                                 "info"
                                 )
        except DatabaseError as e:
            log_parser_exception(dfs.datafile,
                                 (f"Encountered error while deleting database records for model {model}. "
                                  f"Exception: \n{e}"),
                                 "error"
                                 )
        except Exception as e:
            log_parser_exception(dfs.datafile,
                                 (f"Encountered generic exception while deleting records of type {model}. "
                                  f"Exception: \n{e}"),
                                 "error"
                                 )
    if total_deleted:
        logger.info(f"Deleted a total of {total_deleted} records from the DB because of case consistenecy errors.")

def parse_datafile_lines(datafile, dfs, program_type, section, is_encrypted, case_consistency_validator):
    """Parse lines with appropriate schema and return errors."""
    rawfile = datafile.file
    errors = {}

    line_number = 0

    unsaved_records = util.SortedRecords(section)
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
    case_hash = None
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
            errors, unsaved_parser_errors, num_errors = generate_trailer_errors(trailer_errors,
                                                                                errors,
                                                                                unsaved_parser_errors,
                                                                                num_errors)

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
            rollback_records(unsaved_records.get_bulk_create_struct(), datafile)
            rollback_parser_errors(datafile)
            bulk_create_errors(preparse_error, num_errors, flush=True)
            update_meta_model(datafile, dfs)
            return errors

        if prev_sum != header_count + trailer_count:
            prev_sum = header_count + trailer_count
            continue

        schema_manager = get_schema_manager(line, section, program_type)

        records = manager_parse_line(line, schema_manager, generate_error, datafile, is_encrypted)
        num_records = len(records)

        record_number = 0
        for i in range(num_records):
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
                record_has_errors = len(record_errors) > 0
                should_remove, case_hash_to_remove, case_hash = case_consistency_validator.add_record(record,
                                                                                                      s,
                                                                                                      line,
                                                                                                      line_number,
                                                                                                      record_has_errors)
                unsaved_records.add_record(case_hash, (record, s.document), line_number)
                was_removed = unsaved_records.remove_case_due_to_errors(should_remove, case_hash_to_remove)
                case_consistency_validator.update_removed(case_hash_to_remove, should_remove, was_removed)
                dfs.total_number_of_records_in_file += 1

        # Add any generated cat4 errors to our error data structure & clear our caches errors list
        cat4_errors = case_consistency_validator.get_generated_errors()
        num_errors += len(cat4_errors)
        unsaved_parser_errors[None] = unsaved_parser_errors.get(None, []) + cat4_errors
        case_consistency_validator.clear_errors()

        all_created = bulk_create_records(unsaved_records.get_bulk_create_struct(), line_number, header_count,
                                          datafile, dfs)
        unsaved_records.clear(all_created)
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
        rollback_records(unsaved_records.get_bulk_create_struct(), datafile)
        rollback_parser_errors(datafile)
        preparse_error = {line_number: [err_obj]}
        bulk_create_errors(preparse_error, num_errors, flush=True)
        update_meta_model(datafile, dfs)
        return errors

    should_remove = validate_case_consistency(case_consistency_validator)
    was_removed = unsaved_records.remove_case_due_to_errors(should_remove, case_hash)
    case_consistency_validator.update_removed(case_hash, should_remove, was_removed)

    # Only checking "all_created" here because records remained cached if bulk create fails. This is the last chance to
    # successfully create the records.
    all_created = bulk_create_records(unsaved_records.get_bulk_create_struct(), line_number, header_count, datafile,
                                      dfs, flush=True)
    unsaved_records.clear(all_created)

    no_records_created_error, created = create_no_records_created_pre_check_error(datafile, dfs)
    num_errors += created
    unsaved_parser_errors.update(no_records_created_error)

    if not all_created:
        logger.error(f"Not all parsed records created for file: {datafile.id}!")
        rollback_records(unsaved_records.get_bulk_create_struct(), datafile)
        bulk_create_errors(unsaved_parser_errors, num_errors, flush=True)
        update_meta_model(datafile, dfs)
        return errors

    # Add any generated cat4 errors to our error data structure & clear our caches errors list
    cat4_errors = case_consistency_validator.get_generated_errors()
    num_errors += len(cat4_errors)
    unsaved_parser_errors[None] = unsaved_parser_errors.get(None, []) + cat4_errors
    case_consistency_validator.clear_errors()

    bulk_create_errors(unsaved_parser_errors, num_errors, flush=True)

    delete_serialized_records(case_consistency_validator.duplicate_manager, dfs)

    logger.debug(f"Cat4 validator cached {case_consistency_validator.total_cases_cached} cases and "
                 f"validated {case_consistency_validator.total_cases_validated} of them.")
    dfs.save()

    update_meta_model(datafile, dfs)

    return errors


def manager_parse_line(line, schema_manager, generate_error, datafile, is_encrypted=False):
    """Parse and validate a datafile line using SchemaManager."""
    if type(schema_manager) is row_schema.SchemaManager:
        schema_manager.datafile = datafile
    try:
        schema_manager.update_encrypted_fields(is_encrypted)
        records = schema_manager.parse_and_validate(line, generate_error)
        return records
    except AttributeError:
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
