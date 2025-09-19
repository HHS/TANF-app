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
from tdpservice.parsers.util import FrozenDict

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

    def _delete_exact_dups(self):
        """Delete exact duplicate records from the DB."""
        duplicate_error_generator = self.error_generator_factory.get_generator(
            ErrorGeneratorType.DYNAMIC_ROW_CASE_CONSISTENCY, None
        )
        for schemas in self.schema_manager.schema_map.values():
            schema = schemas[0]

            fields = [f.name for f in schema.fields]
            duplicate_vals = (
                schema.model.objects.filter(datafile=self.datafile)
                .exclude(SSN="999999999")
                .values(*fields)
                .annotate(row_count=Count("line_number", distinct=True))
                .filter(row_count__gt=1)
            )
            dup_errors = []
            for dup_vals_dict in duplicate_vals:
                dup_vals_dict.pop("row_count", None)
                dup_records = schema.model.objects.filter(**dup_vals_dict).order_by(
                    "line_number"
                )
                record = dup_records.first()
                for dup in dup_records[1:]:
                    generator_args = ErrorGeneratorArgs(
                        record=dup,
                        schema=schema,
                        error_message=(
                            "Duplicate Social Security Number within a month. Check that individual SSNs "
                            "within a single exit month are not included more than once. Record at line number "
                            f"{dup.line_number} is a duplicate of the record at line number {record.line_number}."
                        ),
                        fields=schema.fields,
                        row_number=dup.line_number,
                    )
                    # Perform Error Generation
                    dup_errors.append(
                        duplicate_error_generator(generator_args=generator_args)
                    )

                case_id_to_delete = (
                    FrozenDict(RecordType=record.RecordType)
                    if not self.is_active_or_closed
                    else FrozenDict(
                        RPT_MONTH_YEAR=record.RPT_MONTH_YEAR,
                        CASE_NUMBER=record.CASE_NUMBER,
                    )
                )
                # We add the case ID here because a case with a duplicate record must be purged in it's entirety.
                self.serialized_cases.add(case_id_to_delete)
                num_deleted = dup_records._raw_delete(dup_records.db)
                self.dfs.total_number_of_records_created -= num_deleted

            self.unsaved_parser_errors[None] = (
                self.unsaved_parser_errors.get(None, []) + dup_errors
            )
