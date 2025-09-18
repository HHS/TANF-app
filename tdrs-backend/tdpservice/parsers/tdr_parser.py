"""TANF/SSP/Tribal parser class."""

import logging

from django.conf import settings

from tdpservice.parsers import schema_defs
from tdpservice.parsers.base_parser import BaseParser
from tdpservice.parsers.case_consistency_validator import CaseConsistencyValidator
from tdpservice.parsers.dataclasses import HeaderResult, Position
from tdpservice.parsers.error_generator import ErrorGeneratorArgs, ErrorGeneratorType
from tdpservice.parsers.schema_defs.utils import ProgramManager
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
                        record, schema, row, self.current_row_num, record_has_errors
                    )
                    self.unsaved_records.add_record(
                        current_case_id, (record, schema.model), self.current_row_num
                    )
                    if should_remove:
                        self.serialized_cases.add(case_id_to_remove)

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
        if should_remove:
            self.serialized_cases.add(case_id_to_remove)

        # Only checking "all_created" here because records remained cached if bulk create fails.
        # This is the last chance to successfully create the records.
        all_created = self.bulk_create_records(self.header_count, flush=True)

        # Order matters. If a case had case consistency errors and duplicate errors, only the case consistency errors are reflected. We want to keep this order
        # because that is what happens for the in-memory case now also. I.e. if a case is removed from the in memory cache it won't generate duplicate errors
        # if they exist.
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

        logger.debug(
            f"Cat4 validator cached {self.case_consistency_validator.total_cases_cached} cases and "
            f"validated {self.case_consistency_validator.total_cases_validated} of them."
        )

        self.bulk_create_errors(flush=True)
        self.dfs.save()

        return

    def _delete_serialized_cases(self):
        from django.db.models import Q

        if len(self.serialized_cases):
            cases = Q()
            for case in self.serialized_cases:
                cases |= Q(**case)
            for schemas in self.schema_manager.schema_map.values():
                schema = schemas[0]
                num_deleted, _ = schema.model.objects.filter(
                    cases, datafile=self.datafile
                ).delete()
                self.dfs.total_number_of_records_created -= num_deleted

    def _delete_exact_dups(self):
        """"""
        from django.db.models import Count, Q

        duplicate_error_generator = self.error_generator_factory.get_generator(
            ErrorGeneratorType.DYNAMIC_ROW_CASE_CONSISTENCY, None
        )
        for schemas in self.schema_manager.schema_map.values():
            schema = schemas[0]

            fields = [f.name for f in schema.fields if f.name != "BLANK"]
            dups = (
                schema.model.objects.filter(datafile=self.datafile)
                .values(*fields)
                .annotate(row_count=Count("line_number", distinct=True))
                .filter(row_count__gt=1)
            )
            dup_errors = []
            print(f"Count: {schema.model.objects.count()}")
            for d in dups:
                d.pop("row_count", None)
                dup_records = schema.model.objects.filter(**d).order_by("line_number")
                record = dup_records.first()
                for dup in dup_records[1:]:
                    record_type = d.get("RecordType", None)
                    generator_args = ErrorGeneratorArgs(
                        record=record,
                        schema=schema,
                        error_message=f"Duplicate record detected with record type {record_type} at line {dup.line_number}. Record is a duplicate of the record at line number {record.line_number}.",
                        fields=schema.fields,
                        row_number=record.line_number,
                    )
                    # Perform Error Generation
                    dup_errors.append(
                        duplicate_error_generator(generator_args=generator_args)
                    )
                num_deleted, _ = dup_records.delete()
                self.dfs.total_number_of_records_created -= num_deleted

            self.unsaved_parser_errors[None] = (
                self.unsaved_parser_errors.get(None, []) + dup_errors
            )

    def __get_partial_dup_error_msg(
        self, schema, record_type, curr_line_number, existing_line_number
    ):
        """Generate partial duplicate error message with friendly names."""
        field_names = schema.get_partial_hash_members_func()
        err_msg = (
            f"Partial duplicate record detected with record type "
            f"{record_type} at line {curr_line_number}. Record is a partial duplicate of the "
            f"record at line number {existing_line_number}. Duplicated fields causing error: "
        )
        for i, name in enumerate(field_names):
            field = schema.get_field_by_name(name)
            item_and_name = f"Item {field.item} ({field.friendly_name})"
            if i == len(field_names) - 1 and len(field_names) != 1:
                err_msg += f"and {item_and_name}."
            elif len(field_names) == 1:
                err_msg += f"{item_and_name}."
            else:
                err_msg += f"{item_and_name}, "
        return err_msg

    def _delete_partial_dups(self):
        from django.db.models import Count, Q

        duplicate_error_generator = self.error_generator_factory.get_generator(
            ErrorGeneratorType.DYNAMIC_ROW_CASE_CONSISTENCY, None
        )
        for schemas in self.schema_manager.schema_map.values():
            schema = schemas[0]
            fields = schema.get_partial_hash_members_func()
            dups = (
                schema.model.objects.filter(datafile=self.datafile)
                .values(*fields)
                .annotate(row_count=Count("line_number", distinct=True))
                .filter(row_count__gt=1)
            )
            dup_errors = []
            for d in dups:
                d.pop("row_count", None)
                dup_records = schema.model.objects.filter(**d).order_by("line_number")
                record = dup_records.first()
                for dup in dup_records[1:]:
                    record_type = d.get("RecordType", None)
                    generator_args = ErrorGeneratorArgs(
                        record=record,
                        schema=schema,
                        error_message=self.__get_partial_dup_error_msg(
                            schema, record_type, dup.line_number, record.line_number
                        ),
                        fields=schema.fields,
                        row_number=record.line_number,
                    )
                    # Perform Error Generation
                    dup_errors.append(
                        duplicate_error_generator(generator_args=generator_args)
                    )
                num_deleted, _ = dup_records.delete()
                self.dfs.total_number_of_records_created -= num_deleted

            self.unsaved_parser_errors[None] = (
                self.unsaved_parser_errors.get(None, []) + dup_errors
            )

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
            generate_error = self.error_generator_factory.get_error_generator(
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

    def delete_serialized_records(self):
        """Delete all records that have already been serialized to the DB that have cat4 errors."""
        duplicate_manager = self.case_consistency_validator.duplicate_manager
        self._delete_serialized_records(duplicate_manager)
