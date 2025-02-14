"""TANF/SSP/Tribal parser class."""

from dataclasses import dataclass
from django.conf import settings
from django.db.utils import DatabaseError
from elasticsearch.exceptions import ElasticsearchException
import logging
from tdpservice.parsers import schema_defs
from tdpservice.parsers.base_parser import BaseParser
from tdpservice.parsers.case_consistency_validator import CaseConsistencyValidator
from tdpservice.parsers.decoders import Position
from tdpservice.parsers.models import ParserErrorCategoryChoices
from tdpservice.parsers.schema_defs.utils import get_section_reference
from tdpservice.parsers.util import log_parser_exception, make_generate_case_consistency_parser_error, \
    make_generate_file_precheck_parser_error, make_generate_parser_error
from tdpservice.parsers.validators import category1
from tdpservice.parsers.validators.util import value_is_empty


logger = logging.getLogger(__name__)


HEADER_POSITION = Position(0, 6)
TRAILER_POSITION = Position(0, 7)


@dataclass
class HeaderResult:
    """Header validation result class."""

    is_valid: bool
    header: dict | None = None
    program_type: str | None = None


class TSTParser(BaseParser):
    """Parser for TANF, SSP, and Tribal datafiles."""

    def __init__(self, datafile, dfs, section, program_type):
        super().__init__(datafile, dfs, section, program_type)
        self.case_consistency_validator = None
        self.multiple_trailer_errors = False
        self.header_count = 0
        self.trailer_count = 0

    def parse_and_validate(self):
        """Parse and validate the datafile."""
        header_result = self._validate_header()
        if not header_result.is_valid:
            return self.errors

        cat4_error_generator = make_generate_case_consistency_parser_error(self.datafile)
        self.case_consistency_validator = CaseConsistencyValidator(
            header_result.header,
            header_result.program_type,
            self.datafile.stt.type,
            cat4_error_generator
        )

        prev_sum = 0
        file_length = len(self.datafile.file)
        offset = 0
        case_hash = None
        for row in self.decoder.decode():
            offset += len(row)
            self.current_row = row
            row_number = self.decoder.current_row_num

            self.header_count += int(row.value_at_is(HEADER_POSITION, "HEADER"))
            self.trailer_count += int(row.value_at_is(TRAILER_POSITION, "TRAILER"))

            is_last_line = offset == file_length
            self.evaluate_trailer(is_last_line)

            generate_error = make_generate_parser_error(self.datafile, row_number)

            if self.header_count > 1:
                logger.info("Preparser Error -> Multiple headers found for file: "
                            f"{self.datafile.id} on line: {row_number}.")
                self.errors.update({'document': ['Multiple headers found.']})
                err_obj = generate_error(
                    schema=None,
                    error_category=ParserErrorCategoryChoices.PRE_CHECK,
                    error_message="Multiple headers found.",
                    record=None,
                    field=None
                )
                preparse_error = {row_number: [err_obj]}
                self.unsaved_parser_errors.update(preparse_error)
                self.rollback_records()
                self.rollback_parser_errors()
                self.bulk_create_errors(flush=True)
                return self.errors

            if prev_sum != self.header_count + self.trailer_count:
                prev_sum = self.header_count + self.trailer_count
                continue

            manager_result = self.schema_manager.parse_and_validate(row, generate_error)
            records = manager_result.records
            schemas = manager_result.schemas
            num_records = len(records)

            record_number = 0
            for i in range(num_records):
                r = records[i]
                record_number += 1
                record, record_is_valid, record_errors = r
                if not record_is_valid:
                    logger.debug(f"Record #{i} from line {row_number} is invalid.")
                    line_errors = self.errors.get(f"{row_number}_{i}", {})
                    line_errors.update({record_number: record_errors})
                    self.errors.update({f"{row_number}_{i}": record_errors})
                    self.unsaved_parser_errors.update({f"{row_number}_{i}": record_errors})
                    self.num_errors += len(record_errors)
                if record:
                    schema = schemas[i]
                    record.datafile = self.datafile
                    record_has_errors = len(record_errors) > 0
                    should_remove, case_hash_to_remove, case_hash = self.case_consistency_validator.add_record(
                        record,
                        schema,
                        row.raw_data,
                        row_number,
                        record_has_errors
                    )
                    # TODO: update schema.document when document is removed.
                    self.unsaved_records.add_record(case_hash, (record, schema.document), row_number)
                    was_removed = self.unsaved_records.remove_case_due_to_errors(should_remove, case_hash_to_remove)
                    self.case_consistency_validator.update_removed(case_hash_to_remove, should_remove, was_removed)
                    self.dfs.total_number_of_records_in_file += 1

            # Add any generated cat4 errors to our error data structure & clear our caches errors list
            cat4_errors = self.case_consistency_validator.get_generated_errors()
            self.num_errors += len(cat4_errors)
            self.unsaved_parser_errors[None] = self.unsaved_parser_errors.get(None, []) + cat4_errors
            self.case_consistency_validator.clear_errors()

            self.bulk_create_records(self.header_count)
            self.bulk_create_errors()

        if self.header_count == 0:
            logger.info(f"Preparser Error -> No headers found for file: {self.datafile.id}.")
            self.errors.update({'document': ['No headers found.']})
            err_obj = generate_error(
                schema=None,
                error_category=ParserErrorCategoryChoices.PRE_CHECK,
                error_message="No headers found.",
                record=None,
                field=None
            )
            self.rollback_records()
            self.rollback_parser_errors()
            preparse_error = {row_number: [err_obj]}
            self.bulk_create_errors(flush=True)
            return self.errors

        should_remove = self.validate_case_consistency()
        was_removed = self.unsaved_records.remove_case_due_to_errors(should_remove, case_hash)
        self.case_consistency_validator.update_removed(case_hash, should_remove, was_removed)

        # Only checking "all_created" here because records remained cached if bulk create fails.
        # This is the last chance to successfully create the records.
        all_created = self.bulk_create_records(self.header_count, flush=True)

        self.delete_serialized_records()
        self.create_no_records_created_pre_check_error()

        if not all_created:
            logger.error(f"Not all parsed records created for file: {self.datafile.id}!")
            self.rollback_records()
            self.bulk_create_errors(flush=True)
            return self.errors

        # Add any generated cat4 errors to our error data structure & clear our caches errors list
        cat4_errors = self.case_consistency_validator.get_generated_errors()
        self.num_errors += len(cat4_errors)
        self.unsaved_parser_errors[None] = self.unsaved_parser_errors.get(None, []) + cat4_errors
        self.case_consistency_validator.clear_errors()

        self.bulk_create_errors(flush=True)

        logger.debug(f"Cat4 validator cached {self.case_consistency_validator.total_cases_cached} cases and "
                     f"validated {self.case_consistency_validator.total_cases_validated} of them.")
        self.dfs.save()

        return self.errors

    def _validate_header(self):
        """Validate header and header fields."""
        # parse & validate header
        header_row = next(self.decoder.decode())
        header, header_is_valid, header_errors = schema_defs.header.parse_and_validate(
            # TODO: just pass header_row when schemas and fields are updated to accept it.
            header_row.raw_data,
            make_generate_file_precheck_parser_error(self.datafile, 1)
        )
        if not header_is_valid:
            logger.info(f"Preparser Error: {len(header_errors)} header errors encountered.")
            self.errors['header'] = header_errors
            self.bulk_create_errors({1: header_errors}, 1, flush=True)
            return HeaderResult(is_valid=False)
        elif header_is_valid and len(header_errors) > 0:
            logger.info(f"Preparser Warning: {len(header_errors)} header warnings encountered.")
            self.errors['header'] = header_errors
            self.bulk_create_errors({1: header_errors}, 1, flush=True)

        # Grab important fields from header
        # TODO: just pass header_row when schemas and fields are updated to accept it.
        field_values = schema_defs.header.get_field_values_by_names(header_row.raw_data,
                                                                    {"encryption", "tribe_code", "state_fips"})
        is_encrypted = field_values["encryption"] == "E"
        is_tribal = not value_is_empty(field_values["tribe_code"], 3, extra_vals={'0'*3})

        logger.debug(f"Datafile has encrypted fields: {is_encrypted}.")
        logger.debug(f"Datafile: {repr(self.datafile)}, is Tribal: {is_tribal}.")

        program_type = f"Tribal {header['program_type']}" if is_tribal else header['program_type']
        section = header['type']
        logger.debug(f"Program type: {program_type}, Section: {section}.")

        # Validate tribe code in submission across program type and fips code
        generate_error = make_generate_parser_error(self.datafile, 1)
        tribe_result = category1.validate_tribe_fips_program_agree(
            header['program_type'],
            field_values["tribe_code"],
            field_values["state_fips"],
            generate_error
        )

        if not tribe_result.valid:
            logger.info(f"Tribe Code ({field_values['tribe_code']}) inconsistency with Program Type " +
                        f"({header['program_type']}) and FIPS Code ({field_values['state_fips']}).",)
            self.errors['header'] = [tribe_result.error]
            self.bulk_create_errors({1: [tribe_result.error]}, 1, flush=True)
            return HeaderResult(is_valid=False)

        # Ensure file section matches upload section
        section_result = category1.validate_header_section_matches_submission(
            self.datafile,
            get_section_reference(program_type, section),
            make_generate_parser_error(self.datafile, 1)
        )

        if not section_result.valid:
            logger.info(f"Preparser Error -> Section is not valid: {section_result.error}")
            self.errors['document'] = [section_result.error]
            unsaved_parser_errors = {1: [section_result.error]}
            self.bulk_create_errors(unsaved_parser_errors, 1, flush=True)
            return HeaderResult(is_valid=False)

        rpt_month_year_result = category1.validate_header_rpt_month_year(
            self.datafile,
            header,
            make_generate_parser_error(self.datafile, 1)
        )
        if not rpt_month_year_result.valid:
            logger.info(f"Preparser Error -> Rpt Month Year is not valid: {rpt_month_year_result.error}")
            self.errors['document'] = [rpt_month_year_result.error]
            unsaved_parser_errors = {1: [rpt_month_year_result.error]}
            self.bulk_create_errors(unsaved_parser_errors, 1, flush=True)
            return HeaderResult(is_valid=False)

        return HeaderResult(is_valid=True, header=header, program_type=program_type)

    def validate_case_consistency(self):
        """Force category four validation if we have reached the last case in the file."""
        if not self.case_consistency_validator.has_validated:
            return self.case_consistency_validator.validate() > 0
        return False

    def evaluate_trailer(self, is_last_line):
        """Validate datafile trailer and generate associated errors if any."""
        if self.trailer_count > 1 and not self.multiple_trailer_errors:
            errors = (True, [make_generate_parser_error(self.datafile, self.current_row_num)(
                schema=None,
                error_category=ParserErrorCategoryChoices.PRE_CHECK,
                error_message="Multiple trailers found.",
                record=None,
                field=None
                )])
            self._generate_trailer_errors(errors)
        if self.trailer_count == 1 or is_last_line:
            record, trailer_is_valid, trailer_errors = schema_defs.trailer.parse_and_validate(
                # TODO: this should take just current_row when schema/field is updated in follow on work.
                self.current_row.raw_data,
                make_generate_parser_error(self.datafile, self.current_row_num)
            )
            self._generate_trailer_errors(trailer_errors)

    def _generate_trailer_errors(self, trailer_errors):
        """Generate trailer errors if we care to see them."""
        if settings.GENERATE_TRAILER_ERRORS:
            self.errors['trailer'] = trailer_errors
            self.unsaved_parser_errors.update({"trailer": trailer_errors})
            self.num_errors += len(trailer_errors)

    def delete_serialized_records(self):
        """Delete all records that have already been serialized to the DB that have cat4 errors."""
        total_deleted = 0
        duplicate_manager = self.case_consistency_validator.duplicate_manager
        for document, ids in duplicate_manager.get_records_to_remove().items():
            try:
                model = document.Django.model
                qset = model.objects.filter(id__in=ids)
                # We must tell elastic to delete the documents first because after we call `_raw_delete`
                # the queryset will be empty which will tell elastic that nothing needs updated.
                document.update(qset, refresh=True, action="delete")
                # WARNING: we can use `_raw_delete` in this case because our record models don't have cascading
                # dependencies. If that ever changes, we should NOT use `_raw_delete`.
                num_deleted = qset._raw_delete(qset.db)
                total_deleted += num_deleted
                self.dfs.total_number_of_records_created -= num_deleted
                logger.debug(f"Deleted {num_deleted} records of type: {model}.")
            except ElasticsearchException as e:
                # Caught an Elastic exception, to ensure the quality of the DB, we will force the DB deletion and let
                # Elastic clean up later.
                log_parser_exception(self.datafile,
                                     ("Encountered error while indexing datafile documents. Enforcing DB cleanup. "
                                      f"Exception: \n{e}"),
                                     "error"
                                     )
                num_deleted, models = qset.delete()
                total_deleted += num_deleted
                self.dfs.total_number_of_records_created -= num_deleted
                log_parser_exception(self.datafile,
                                     ("Succesfully performed DB cleanup after elastic failure "
                                      "in delete_serialized_records."),
                                     "info"
                                     )
            except DatabaseError as e:
                log_parser_exception(self.datafile,
                                     (f"Encountered error while deleting database records for model {model}. "
                                      f"Exception: \n{e}"),
                                     "error"
                                     )
            except Exception as e:
                log_parser_exception(self.datafile,
                                     (f"Encountered generic exception while deleting records of type {model}. "
                                      f"Exception: \n{e}"),
                                     "error"
                                     )
