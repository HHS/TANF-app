"""FRA parser class."""

import logging
from tdpservice.parsers.base_parser import BaseParser
from tdpservice.parsers.dataclasses import HeaderResult, Position
from tdpservice.parsers.models import ParserErrorCategoryChoices
from tdpservice.parsers.util import make_generate_fra_parser_error


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
        generate_error = make_generate_fra_parser_error(self.datafile, 1)
        self.num_errors += 1
        error = generate_error(schema=None,
                               error_category=ParserErrorCategoryChoices.PRE_CHECK,
                               error_message="File does not begin with FRA data.",
                               fields=[],
                               )
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
            generate_error = make_generate_fra_parser_error(self.datafile, self.current_row_num)

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
                    logger.debug(f"Record #{i} from line {self.current_row_num} is invalid.")
                    self.unsaved_parser_errors.update({f"{self.current_row_num}_{i}": record_errors})
                    self.num_errors += len(record_errors)
                if record:
                    schema = schemas[i]
                    record.datafile = self.datafile

                    # TODO: update schema.document when document is removed.
                    self.unsaved_records.add_record(hash(row), (record, schema.model), self.current_row_num)
                    self.dfs.total_number_of_records_in_file += 1

            self.bulk_create_records(1)
            self.bulk_create_errors()

        # Only checking "all_created" here because records remained cached if bulk create fails.
        # This is the last chance to successfully create the records.
        all_created = self.bulk_create_records(1, flush=True)

        # Must happen after last bulk create
        self.create_no_records_created_pre_check_error()

        if not all_created:
            logger.error(f"Not all parsed records created for file: {self.datafile.id}!")
            self.rollback_records()
            self.bulk_create_errors(flush=True)
            return

        self.bulk_create_errors(flush=True)

        self.dfs.save()

        return
