"""TANF/SSP/Tribal parser class."""

import logging

from django.conf import settings

from tdpservice.data_files.models import DataFile
from tdpservice.parsers import schema_defs
from tdpservice.parsers.base_parser import BaseParser
from tdpservice.parsers.case_consistency_validator import CaseConsistencyValidator
from tdpservice.parsers.dataclasses import HeaderResult, Position, ValidationErrorArgs
from tdpservice.parsers.error_generator import ErrorGeneratorArgs, ErrorGeneratorType
from tdpservice.parsers.schema_defs.utils import ProgramManager
from tdpservice.parsers.validators import category1, category2
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

        cat4_error_generator = self.error_generator_factory.get_generator(
            ErrorGeneratorType.DYNAMIC_ROW_CASE_CONSISTENCY, None
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
        current_case_id = None
        for row in self.decoder.decode():
            offset += row.raw_length()
            self.current_row = row
            self.current_row_num = self.decoder.current_row_num

            self.header_count += int(row.value_at_is(HEADER_POSITION, "HEADER"))
            self.trailer_count += int(row.value_at_is(TRAILER_POSITION, "TRAILER"))

            is_last_line = offset == file_length
            self.evaluate_trailer(is_last_line)

            generate_error = self.error_generator_factory.get_generator(
                ErrorGeneratorType.MSG_ONLY_PRECHECK,
                self.current_row_num,
            )

            if self.header_count > 1:
                logger.info(
                    "Preparser Error -> Multiple headers found for file: "
                    f"{self.datafile.id} on line: {self.current_row_num}."
                )
                generator_args = ErrorGeneratorArgs(
                    record=None,
                    schema=None,
                    error_message="Multiple headers found.",
                    fields=[],
                )
                err_obj = generate_error(generator_args=generator_args)
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

            manager_result = self.schema_manager.parse_and_validate(row)
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
                        case_id_to_remove,
                        current_case_id,
                    ) = self.case_consistency_validator.add_record(
                        record, schema, self.current_row_num, record_has_errors
                    )
                    self.unsaved_records.add_record(
                        current_case_id, (record, schema.model), self.current_row_num
                    )
                    self.add_case_to_remove(should_remove, case_id_to_remove)

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
            generator_args = ErrorGeneratorArgs(
                record=None,
                schema=None,
                error_message="No headers found.",
                fields=[],
            )
            err_obj = generate_error(generator_args=generator_args)
            self.rollback_records()
            self.rollback_parser_errors()
            preparse_error = {self.current_row_num: [err_obj]}
            self.bulk_create_errors(flush=True)
            return

        should_remove = self.validate_case_consistency()
        self.add_case_to_remove(should_remove, current_case_id)

        # Only checking "all_created" here because records remained cached if bulk create fails.
        # This is the last chance to successfully create the records.
        all_created = self.bulk_create_records(self.header_count, flush=True)

        # Order matters. To ensure we also catch duplicate records, we check for them before deleting cases with cat4
        # Errors.
        self._delete_exact_dups()
        self._delete_partial_dups()
        self._delete_serialized_cases()

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

        self.generate_funded_ssn_errors()

        self.bulk_create_errors(flush=True)

        logger.debug(
            f"Cat4 validator cached {self.case_consistency_validator.total_cases_cached} cases and "
            f"validated {self.case_consistency_validator.total_cases_validated} of them."
        )

        self.bulk_create_errors(flush=True)
        self.dfs.save()

        return

    def _validate_header(self):
        """Validate header and header fields."""
        # parse & validate header
        header_row = self.decoder.get_header()
        header_row.row_num = 1
        header_schema = schema_defs.header
        header_schema.prepare(self.datafile)
        header, header_is_valid, header_errors = header_schema.parse_and_validate(
            header_row
        )
        if not header_is_valid:
            logger.info(
                f"Preparser Error: {len(header_errors)} header errors encountered."
            )
            self.num_errors += len(header_errors)
            self.unsaved_parser_errors.update({1: header_errors})
            self.bulk_create_errors(flush=True)
            return HeaderResult(is_valid=False)
        elif header_is_valid and len(header_errors) > 0:
            logger.info(
                f"Preparser Warning: {len(header_errors)} header warnings encountered."
            )
            self.num_errors += len(header_errors)
            self.unsaved_parser_errors.update({1: header_errors})

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

        generate_error = self.error_generator_factory.get_generator(
            ErrorGeneratorType.MSG_ONLY_PRECHECK, 1
        )

        # Validate tribe code in submission across program type and fips code
        tribe_result = category1.validate_tribe_fips_program_agree(
            header["program_type"],
            field_values["tribe_code"],
            field_values["state_fips"],
        )

        if not tribe_result.valid:
            logger.info(
                f"Tribe Code ({field_values['tribe_code']}) inconsistency with Program Type "
                + f"({header['program_type']}) and FIPS Code ({field_values['state_fips']}).",
            )
            self.num_errors += 1
            generator_args = ErrorGeneratorArgs(
                record=None,
                schema=None,
                error_message=tribe_result.error_message,
                fields=[],
            )
            err_obj = generate_error(generator_args=generator_args)
            self.unsaved_parser_errors.update({1: [err_obj]})
            self.bulk_create_errors(flush=True)
            return HeaderResult(is_valid=False)

        # Ensure file section matches upload section
        section_result = category1.validate_header_section_matches_submission(
            self.datafile,
            ProgramManager.get_section(program_type, section),
        )

        if not section_result.valid:
            logger.info(
                f"Preparser Error -> Section is not valid: {section_result.error_message}"
            )
            self.num_errors += 1
            generator_args = ErrorGeneratorArgs(
                record=None,
                schema=None,
                error_message=section_result.error_message,
                fields=[],
            )
            err_obj = generate_error(generator_args=generator_args)
            self.unsaved_parser_errors.update({1: [err_obj]})
            self.bulk_create_errors(flush=True)
            return HeaderResult(is_valid=False)

        rpt_month_year_result = category1.validate_header_rpt_month_year(
            self.datafile, header
        )
        if not rpt_month_year_result.valid:
            logger.info(
                f"Preparser Error -> Rpt Month Year is not valid: {rpt_month_year_result.error_message}"
            )
            self.num_errors += 1
            generator_args = ErrorGeneratorArgs(
                record=None,
                schema=None,
                error_message=rpt_month_year_result.error_message,
                fields=[],
            )
            err_obj = generate_error(generator_args=generator_args)
            self.unsaved_parser_errors.update({1: [err_obj]})
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
            generator_args = ErrorGeneratorArgs(
                record=None,
                schema=None,
                error_message="Multiple trailers found.",
                fields=[],
            )
            generate_error = self.error_generator_factory.get_generator(
                ErrorGeneratorType.MSG_ONLY_PRECHECK,
                self.current_row_num,
            )
            err_obj = generate_error(generator_args=generator_args)
            errors = (
                True,
                [err_obj],
            )
            self._generate_trailer_errors(errors)
        if self.trailer_count == 1 or is_last_line:
            trailer_schema = schema_defs.trailer
            trailer_schema.prepare(self.datafile)
            (
                record,
                trailer_is_valid,
                trailer_errors,
            ) = trailer_schema.parse_and_validate(self.current_row)
            self._generate_trailer_errors(trailer_errors)

    def _generate_trailer_errors(self, trailer_errors):
        """Generate trailer errors if we care to see them."""
        if settings.GENERATE_TRAILER_ERRORS:
            self.unsaved_parser_errors.update({"trailer": trailer_errors})
            self.num_errors += len(trailer_errors)

    def _generate_funded_ssn_errors(self, t2_schema, t2_records, t1_schema):
        """Inner function to validate and generate errors."""
        validator = category2.ssnAllOf(
            category2.isNumber(),
            category2.intHasLength(9),
            category2.valueNotAt(slice(0, 3), "000"),
            category2.valueNotAt(slice(0, 3), "666"),
            category2.valueNotAt(slice(3, 5), "00"),
            category2.valueNotAt(slice(5, 9), "0000"),
            error_message=(
                "Social Security Number is not valid. Check that the SSN is 9 digits, "
                "does not contain only zeroes in any one section, and does not contain "
                "dashes or other punctuation."
            ),
        )

        t1_fields = [t1_schema.get_field_by_name(name) for name in ("FUNDING_STREAM",)]
        t2_fields = [
            t2_schema.get_field_by_name(name) for name in ("FAMILY_AFFILIATION", "SSN")
        ]
        fields = t1_fields + t2_fields
        # Validate SSN for each T2 record
        for t2_record in t2_records.iterator(
            chunk_size=settings.BULK_CREATE_BATCH_SIZE
        ):
            ssn = getattr(t2_record, "SSN", None)
            if ssn:
                eargs = ValidationErrorArgs(
                    value=ssn,
                    row_schema=t2_schema,
                    friendly_name=fields[-1].friendly_name,
                    item_num=fields[-1].item,
                )
                result = validator(ssn, eargs)
                if not result.valid:
                    error_generator = self.error_generator_factory.get_generator(
                        ErrorGeneratorType.VALUE_CONSISTENCY, t2_record.line_number
                    )
                    generator_args = ErrorGeneratorArgs(
                        record=t2_record,
                        schema=t2_schema,
                        error_message=result.error_message,
                        offending_field=fields[-1],
                        fields=fields,
                        deprecated=result.deprecated,
                        row_number=t2_record.line_number,
                    )
                    if "funded_recipient_ssn" not in self.unsaved_parser_errors:
                        self.unsaved_parser_errors["funded_recipient_ssn"] = []
                    self.unsaved_parser_errors["funded_recipient_ssn"].append(
                        error_generator(generator_args=generator_args)
                    )
                    self.num_errors += 1
                    self.bulk_create_errors()

    def generate_funded_ssn_errors(self):
        """Generate SSN validation errors for T1/T2 records with specific funding stream and family affiliation."""
        if self.section == DataFile.Section.ACTIVE_CASE_DATA:
            t1_schema = None
            t2_schema = None
            for schemas in self.schema_manager.schema_map.values():
                schema = schemas[0]
                if schema.record_type == "T1":
                    t1_schema = schema
                elif schema.record_type == "T2":
                    t2_schema = schema

            if not t1_schema or not t2_schema:
                return

            # Get T1 records with FUNDING_STREAM = 1
            t1_records = t1_schema.model.objects.filter(
                datafile=self.datafile, FUNDING_STREAM=1
            )

            # Get T2 records with FAMILY_AFFILIATION = 1 that belong to the same cases as T1 records
            t1_case_numbers = t1_records.values_list("CASE_NUMBER", flat=True)
            t2_records = t2_schema.model.objects.filter(
                datafile=self.datafile,
                FAMILY_AFFILIATION=1,
                CASE_NUMBER__in=t1_case_numbers,
            )

            self._generate_funded_ssn_errors(t2_schema, t2_records, t1_schema)
