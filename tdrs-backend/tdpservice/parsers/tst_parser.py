"""TANF/SSP/Tribal parser class."""

from django.conf import settings
from django.db.utils import DatabaseError
from elasticsearch.exceptions import ElasticsearchException
import logging
from tdpservice.parsers import schema_defs
from tdpservice.parsers.base_parser import BaseParser
from tdpservice.parsers.models import ParserErrorCategoryChoices
from tdpservice.parsers.util import log_parser_exception, make_generate_parser_error


logger = logging.getLogger(__name__)


class TSTParser(BaseParser):
    """Parser for TANF, SSP, and Tribal datafiles."""

    def __init__(self, datafile, dfs, section, program_type):
        super().__init__(datafile, dfs, section, program_type)
        self.case_consistency_validator = None
        self.trailer_count = 0
        self.multiple_trailer_errors = False
        self._init_schema_manager()

    def parse_and_validate(self):
        """Parse and validate the datafile."""
        header, field_vals, is_valid = self._validate_header()
        # Initialize CaseConsistencyValidator here

        # Move a lot of code from parse.py::parse_datafile_lines here to complete parsing.
        return self.errors

    def _validate_header(self):
        """Validate header and header fields."""
        # Basically all the code from parse.py::parse_datafile can go here.

        # This should return (header, field_vals, is_valid). We need the header and field_vals dicts
        # to instantiate the CaseConsistencyValidator.
        pass

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
                # We must tell elastic to delete the documents first because after we call `_raw_delete` the queryset will
                # be empty which will tell elastic that nothing needs updated.
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
                                    "Succesfully performed DB cleanup after elastic failure in delete_serialized_records.",
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