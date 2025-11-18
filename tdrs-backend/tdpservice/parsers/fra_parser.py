"""FRA parser class."""

import logging

from django.db.models import Count

from tdpservice.parsers.base_parser import BaseParser
from tdpservice.parsers.dataclasses import HeaderResult, Position
from tdpservice.parsers.error_generator import (
    ErrorGeneratorArgs,
    ErrorGeneratorFactory,
    ErrorGeneratorType,
)

logger = logging.getLogger(__name__)


class FRAParser(BaseParser):
    """Parser for FRA datafiles."""

    # Subject to change if other FRA sections have different row column layouts than FRA_WORK_OUTCOME_TANF_EXITERS.
    EXIT_DATE_POSITION = Position(0)
    SSN_POSITION = Position(1)

    def __init__(self, datafile, dfs, section):
        super().__init__(datafile, dfs, section)

    def _create_header_error(self):
        """Create FRA header error and return invalid HeaderResult."""
        generate_error = ErrorGeneratorFactory(self.datafile).get_generator(
            ErrorGeneratorType.MSG_ONLY_PRECHECK, 1
        )
        generator_args = ErrorGeneratorArgs(
            record=None,
            schema=None,
            error_message="File does not begin with FRA data.",
            fields=[],
        )
        self.num_errors += 1
        error = generate_error(generator_args)
        self.unsaved_parser_errors.update({1: [error]})
        self.bulk_create_errors(flush=True)
        return HeaderResult(is_valid=False)

    def _validate_header(self):
        """Validate that the file does NOT have a header and that it begins with FRA data."""
        header_row = self.decoder.get_header()

        if len(header_row) != 2 or not all(header_row):
            return self._create_header_error()

        return HeaderResult(is_valid=True, program_type="FRA")

    def parse_and_validate(self):
        """Parse and validate the datafile."""
        header_result = self._validate_header()
        if not header_result.is_valid:
            return

        self._init_schema_manager(header_result.program_type)

        for row in self.decoder.decode():
            self.current_row_num = self.decoder.current_row_num

            manager_result = self.schema_manager.parse_and_validate(row)
            records = manager_result.records
            schemas = manager_result.schemas
            num_records = len(records)

            record_number = 0
            self.dfs.total_number_of_records_in_file += num_records
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

                schema = schemas[i]
                record.datafile = self.datafile

                row_hash = hash(row)
                if record_is_valid:
                    self.unsaved_records.add_record(
                        row_hash, (record, schema.model), self.current_row_num
                    )

            self.bulk_create_records(1)
            self.bulk_create_errors()

        # Only checking "all_created" here because records remained cached if bulk create fails.
        # This is the last chance to successfully create the records.
        all_created = self.bulk_create_records(1, flush=True)

        # Must happen after last bulk create
        self._delete_exact_dups()
        self.create_no_records_created_pre_check_error()

        if not all_created:
            logger.error(
                f"Not all parsed records created for file: {self.datafile.id}!"
            )
            self.rollback_records()
            self.bulk_create_errors(flush=True)
            return

        self.bulk_create_errors(flush=True)

        self.dfs.save()

        return

    def _generate_exact_dup_error_msg(
        self, schema, record_type, curr_line_number, existing_line_number
    ):
        """Generate exact duplicate error message for FRA records."""
        return (
            "Duplicate Social Security Number within a month. Check that individual SSNs "
            "within a single exit month are not included more than once. Record at line number "
            f"{curr_line_number} is a duplicate of the record at line number {existing_line_number}."
        )

    def _delete_exact_dups(self):
        """Delete exact duplicate records from the DB."""
        for schemas in self.schema_manager.schema_map.values():
            schema = schemas[0]
            fields = [f.name for f in schema.fields]
            records = schema.model.objects.filter(datafile=self.datafile)

            while True:
                # We have to re-evaluate this query each time after we call _raw_delete because it changes the OFFSET
                # that Postgres manages to help us slice the query set to avoid bringing the whole thing it into memory.
                # This functions exactly the same as the Paginator but allows us to avoid the OFFSET problem it
                # by caching the underlying query/DB state.
                duplicate_vals = (
                    records.exclude(SSN="999999999")
                    .values(*fields)
                    .annotate(row_count=Count("line_number", distinct=True))
                    .filter(row_count__gt=1)
                )
                if not duplicate_vals:
                    break
                self._generate_errors_and_delete_dups(
                    records, duplicate_vals, schema, self._generate_exact_dup_error_msg
                )
