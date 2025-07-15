"""TANF/SSP/Tribal parser class."""

import logging

from django.conf import settings

from tdpservice.parsers import schema_defs
from tdpservice.parsers.base_parser import BaseParser
from tdpservice.parsers.case_consistency_validator import CaseConsistencyValidator
from tdpservice.parsers.dataclasses import HeaderResult, Position
from tdpservice.parsers.models import ParserErrorCategoryChoices
from tdpservice.parsers.schema_defs.utils import ProgramManager
from tdpservice.parsers.util import (
    make_generate_case_consistency_parser_error,
    make_generate_file_precheck_parser_error,
    make_generate_parser_error,
)
from tdpservice.parsers.validators import category1
from tdpservice.parsers.validators.util import value_is_empty

logger = logging.getLogger(__name__)


HEADER_POSITION = Position(0, 6)
TRAILER_POSITION = Position(0, 7)


class TanfDataReportParser(BaseParser):
    """Parser for TANF, SSP, and Tribal datafiles."""

    def __init__(self, datafile, dfs, section):
        super().__init__(datafile, dfs, section)
        self.case_consistency_validator = None
        self.multiple_trailer_errors = False
        self.header_count = 0
        self.trailer_count = 0

    def parse_and_validate(self):
        """Parse and validate the datafile."""
        header_result = self._validate_header()
        if not header_result.is_valid:
            return

        self._init_schema_manager(header_result.program_type)
        self.schema_manager.update_encrypted_fields(header_result.is_encrypted)

        cat4_error_generator = make_generate_case_consistency_parser_error(
            self.datafile
        )
        self.case_consistency_validator = CaseConsistencyValidator(
            header_result.header,
            header_result.program_type,
            self.datafile.stt.type,
            cat4_error_generator,
        )

        prev_sum = 0
        file_length = len(self.datafile.file)
        offset = 0
        case_hash = None
        for row in self.decoder.decode():
            offset += row.raw_length()
            self.current_row = row
            self.current_row_num = self.decoder.current_row_num

            self.header_count += int(row.value_at_is(HEADER_POSITION, "HEADER"))
            self.trailer_count += int(row.value_at_is(TRAILER_POSITION, "TRAILER"))

            is_last_line = offset == file_length
            self.evaluate_trailer(is_last_line)

            generate_error = make_generate_parser_error(
                self.datafile, self.current_row_num
            )

            if self.header_count > 1:
                logger.info(
                    "Preparser Error -> Multiple headers found for file: "
                    f"{self.datafile.id} on line: {self.current_row_num}."
                )
                err_obj = generate_error(
                    schema=None,
                    error_category=ParserErrorCategoryChoices.PRE_CHECK,
                    error_message="Multiple headers found.",
                    record=None,
                    field=None,
                )
                preparse_error = {self.current_row_num: [err_obj]}
                self.unsaved_parser_errors = dict()
                self.unsaved_parser_errors.update(preparse_error)
                self.rollback_records()
                self.rollback_parser_errors()
                self.bulk_create_errors(flush=True)
                return

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
                    logger.debug(
                        f"Record #{i} from line {self.current_row_num} is invalid."
                    )
                    self.unsaved_parser_errors.update(
                        {f"{self.current_row_num}_{i}": record_errors}
                    )
                    self.num_errors += len(record_errors)
                if record:
                    schema = schemas[i]
                    record.datafile = self.datafile
                    record_has_errors = len(record_errors) > 0
                    (
                        should_remove,
                        case_hash_to_remove,
                        case_hash,
                    ) = self.case_consistency_validator.add_record(
                        record, schema, row, self.current_row_num, record_has_errors
                    )
                    self.unsaved_records.add_record(
                        case_hash, (record, schema.model), self.current_row_num
                    )
                    was_removed = self.unsaved_records.remove_case_due_to_errors(
                        should_remove, case_hash_to_remove
                    )
                    self.case_consistency_validator.update_removed(
                        case_hash_to_remove, should_remove, was_removed
                    )
                    self.dfs.total_number_of_records_in_file += 1

            # Add any generated cat4 errors to our error data structure & clear our caches errors list
            cat4_errors = self.case_consistency_validator.get_generated_errors()
            self.num_errors += len(cat4_errors)
            self.unsaved_parser_errors[None] = (
                self.unsaved_parser_errors.get(None, []) + cat4_errors
            )
            self.case_consistency_validator.clear_errors()

            self.bulk_create_records(self.header_count)
            self.bulk_create_errors()

        if self.header_count == 0:
            logger.info(
                f"Preparser Error -> No headers found for file: {self.datafile.id}."
            )
            self.errors.update({"model": ["No headers found."]})
            err_obj = generate_error(
                schema=None,
                error_category=ParserErrorCategoryChoices.PRE_CHECK,
                error_message="No headers found.",
                record=None,
                field=None,
            )
            self.rollback_records()
            self.rollback_parser_errors()
            preparse_error = {self.current_row_num: [err_obj]}
            self.bulk_create_errors(flush=True)
            return

        should_remove = self.validate_case_consistency()
        was_removed = self.unsaved_records.remove_case_due_to_errors(
            should_remove, case_hash
        )
        self.case_consistency_validator.update_removed(
            case_hash, should_remove, was_removed
        )

        # Only checking "all_created" here because records remained cached if bulk create fails.
        # This is the last chance to successfully create the records.
        all_created = self.bulk_create_records(self.header_count, flush=True)

        self.delete_serialized_records()
        self.create_no_records_created_pre_check_error()

        if not all_created:
            logger.error(
                f"Not all parsed records created for file: {self.datafile.id}!"
            )
            self.rollback_records()
            self.bulk_create_errors(flush=True)
            return

        # Add any generated cat4 errors to our error data structure & clear our caches errors list
        cat4_errors = self.case_consistency_validator.get_generated_errors()
        self.num_errors += len(cat4_errors)
        self.unsaved_parser_errors[None] = (
            self.unsaved_parser_errors.get(None, []) + cat4_errors
        )
        self.case_consistency_validator.clear_errors()

        self.bulk_create_errors(flush=True)

        logger.debug(
            f"Cat4 validator cached {self.case_consistency_validator.total_cases_cached} cases and "
            f"validated {self.case_consistency_validator.total_cases_validated} of them."
        )
        self.dfs.save()

        return

    def _validate_header(self):
        """Validate header and header fields."""
        # parse & validate header
        header_row = self.decoder.get_header()
        header, header_is_valid, header_errors = schema_defs.header.parse_and_validate(
            header_row, make_generate_file_precheck_parser_error(self.datafile, 1)
        )
        if not header_is_valid:
            logger.info(
                f"Preparser Error: {len(header_errors)} header errors encountered."
            )
            self.num_errors += 1
            self.unsaved_parser_errors.update({1: header_errors})
            self.bulk_create_errors(flush=True)
            return HeaderResult(is_valid=False)
        elif header_is_valid and len(header_errors) > 0:
            logger.info(
                f"Preparser Warning: {len(header_errors)} header warnings encountered."
            )
            self.num_errors += 1
            self.unsaved_parser_errors.update({1: header_errors})
            self.bulk_create_errors(flush=True)

        # Grab important fields from header
        field_values = schema_defs.header.get_field_values_by_names(
            header_row, {"encryption", "tribe_code", "state_fips"}
        )
        is_encrypted = field_values["encryption"] == "E"
        is_tribal = not value_is_empty(
            field_values["tribe_code"], 3, extra_vals={"0" * 3}
        )

        logger.debug(f"Datafile has encrypted fields: {is_encrypted}.")
        logger.debug(f"Datafile: {repr(self.datafile)}, is Tribal: {is_tribal}.")

        program_type = (
            f"Tribal {header['program_type']}" if is_tribal else header["program_type"]
        )
        section = header["type"]
        logger.debug(f"Program type: {program_type}, Section: {section}.")

        # Validate tribe code in submission across program type and fips code
        generate_error = make_generate_parser_error(self.datafile, 1)
        tribe_result = category1.validate_tribe_fips_program_agree(
            header["program_type"],
            field_values["tribe_code"],
            field_values["state_fips"],
            generate_error,
        )

        if not tribe_result.valid:
            logger.info(
                f"Tribe Code ({field_values['tribe_code']}) inconsistency with Program Type "
                + f"({header['program_type']}) and FIPS Code ({field_values['state_fips']}).",
            )
            self.num_errors += 1
            self.unsaved_parser_errors.update({1: [tribe_result.error]})
            self.bulk_create_errors(flush=True)
            return HeaderResult(is_valid=False)

        # Ensure file section matches upload section
        section_result = category1.validate_header_section_matches_submission(
            self.datafile,
            ProgramManager.get_section(program_type, section),
            make_generate_parser_error(self.datafile, 1),
        )

        if not section_result.valid:
            logger.info(
                f"Preparser Error -> Section is not valid: {section_result.error}"
            )
            self.num_errors += 1
            self.unsaved_parser_errors.update({1: [section_result.error]})
            self.bulk_create_errors(flush=True)
            return HeaderResult(is_valid=False)

        rpt_month_year_result = category1.validate_header_rpt_month_year(
            self.datafile, header, make_generate_parser_error(self.datafile, 1)
        )
        if not rpt_month_year_result.valid:
            logger.info(
                f"Preparser Error -> Rpt Month Year is not valid: {rpt_month_year_result.error}"
            )
            self.num_errors += 1
            self.unsaved_parser_errors.update({1: [rpt_month_year_result.error]})
            self.bulk_create_errors(flush=True)
            return HeaderResult(is_valid=False)

        return HeaderResult(
            is_valid=True,
            header=header,
            program_type=program_type,
            is_encrypted=is_encrypted,
        )

    def validate_case_consistency(self):
        """Force category four validation if we have reached the last case in the file."""
        if not self.case_consistency_validator.has_validated:
            return self.case_consistency_validator.validate() > 0
        return False

    def evaluate_trailer(self, is_last_line):
        """Validate datafile trailer and generate associated errors if any."""
        if self.trailer_count > 1 and not self.multiple_trailer_errors:
            errors = (
                True,
                [
                    make_generate_parser_error(self.datafile, self.current_row_num)(
                        schema=None,
                        error_category=ParserErrorCategoryChoices.PRE_CHECK,
                        error_message="Multiple trailers found.",
                        record=None,
                        field=None,
                    )
                ],
            )
            self._generate_trailer_errors(errors)
        if self.trailer_count == 1 or is_last_line:
            (
                record,
                trailer_is_valid,
                trailer_errors,
            ) = schema_defs.trailer.parse_and_validate(
                self.current_row,
                make_generate_parser_error(self.datafile, self.current_row_num),
            )
            self._generate_trailer_errors(trailer_errors)

    def _generate_trailer_errors(self, trailer_errors):
        """Generate trailer errors if we care to see them."""
        if settings.GENERATE_TRAILER_ERRORS:
            self.unsaved_parser_errors.update({"trailer": trailer_errors})
            self.num_errors += len(trailer_errors)

    def delete_serialized_records(self):
        """Delete all records that have already been serialized to the DB that have cat4 errors."""
        duplicate_manager = self.case_consistency_validator.duplicate_manager
        self._delete_serialized_records(duplicate_manager)
