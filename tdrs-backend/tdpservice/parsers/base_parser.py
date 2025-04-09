"""Base parser logic associated to all parser classes."""

from abc import ABC, abstractmethod
from django.conf import settings
from django.db.utils import DatabaseError
import itertools
import logging
from tdpservice.parsers import util
from tdpservice.parsers.decoders import DecoderFactory
from tdpservice.parsers.models import ParserErrorCategoryChoices, ParserError
from tdpservice.parsers.schema_manager import SchemaManager
from tdpservice.parsers.util import SortedRecords, log_parser_exception

logger = logging.getLogger(__name__)

class BaseParser(ABC):
    """Abstract base class for all parsers."""

    def __init__(self, datafile, dfs, section):
        super().__init__()
        self.datafile = datafile
        self.dfs = dfs
        self.section = section
        self.program_type = None

        # Initialized decoder.
        self.decoder = DecoderFactory.get_instance(datafile.file)

        self.current_row = None
        self.current_row_num = 0

        # Specifying unsaved_records here may or may not work for FRA files. If not, we can move it down the
        # inheritance hierarchy.
        self.unsaved_records = SortedRecords(section)
        self.unsaved_parser_errors = dict()
        self.num_errors = 0

    @abstractmethod
    def parse_and_validate(self):
        """To be overriden in child class."""
        pass

    def _init_schema_manager(self, program_type):
        """Initialize the schema manager with the given program type."""
        # program_type is manipulated by some parsers. E.g. the tdr_parser has to prefix a tribal TANF's program type
        # with "Tribal" since it's base program type would just be TANF.
        self.program_type = program_type
        self.schema_manager = SchemaManager(self.datafile, self.program_type, self.section)

    def bulk_create_records(self, header_count, flush=False):
        """Bulk create unsaved_records."""
        batch_size = settings.BULK_CREATE_BATCH_SIZE
        if (self.current_row_num % batch_size == 0 and header_count > 0) or flush:
            logger.debug("Bulk creating records.")
            num_db_records_created = 0
            num_expected_db_records = 0
            for model, records in self.unsaved_records.get_bulk_create_struct().items():
                try:
                    num_expected_db_records += len(records)
                    created_objs = model.objects.bulk_create(records)
                    num_db_records_created += len(created_objs)
                except DatabaseError as e:
                    log_parser_exception(self.datafile,
                                         f"Encountered error while creating database records: \n{e}",
                                         "error"
                                         )
                    return False
                except Exception as e:
                    log_parser_exception(self.datafile,
                                         f"Encountered generic exception while creating database records: \n{e}",
                                         "error"
                                         )
                    return False

            self.dfs.total_number_of_records_created += num_db_records_created
            if num_db_records_created != num_expected_db_records:
                logger.error(f"Bulk Django record creation only created {num_db_records_created}/" +
                             f"{num_expected_db_records}!")
            else:
                logger.info(f"Created {num_db_records_created}/{num_expected_db_records} records.")

            all_created = num_db_records_created == num_expected_db_records
            self.unsaved_records.clear(all_created)
            return all_created

    def bulk_create_errors(self, batch_size=5000, flush=False):
        """Bulk create unsaved_parser_errors."""
        if flush or (self.unsaved_parser_errors and self.num_errors >= batch_size):
            logger.debug("Bulk creating ParserErrors.")
            num_created = len(ParserError.objects.bulk_create(list(itertools.chain.from_iterable(
                self.unsaved_parser_errors.values()))))
            logger.info(f"Created {num_created}/{self.num_errors} ParserErrors.")
            self.unsaved_parser_errors = dict()
            self.num_errors = 0

    def rollback_records(self):
        """Delete created records in the event of a failure."""
        logger.info("Rolling back created records.")
        for model in self.unsaved_records.get_bulk_create_struct():
            try:
                qset = model.objects.filter(datafile=self.datafile)
                # WARNING: we can use `_raw_delete` in this case because our record models don't have cascading
                # dependencies. If that ever changes, we should NOT use `_raw_delete`.
                num_deleted = qset._raw_delete(qset.db)
                logger.debug(f"Deleted {num_deleted} records of type: {model}.")
            except DatabaseError as e:
                log_parser_exception(self.datafile,
                                     (f"Encountered error while deleting database records for model: {model}. "
                                      f"Exception: \n{e}"),
                                     "error"
                                     )
            except Exception as e:
                log_parser_exception(self.datafile,
                                     ("Encountered generic exception while trying to rollback "
                                      f"records. Exception: \n{e}"),
                                     "error"
                                     )

    def rollback_parser_errors(self):
        """Delete created errors in the event of a failure."""
        try:
            logger.info("Rolling back created parser errors.")
            qset = ParserError.objects.filter(file=self.datafile)
            # WARNING: we can use `_raw_delete` in this case because our error models don't have cascading dependencies.
            # If that ever changes, we should NOT use `_raw_delete`.
            num_deleted = qset._raw_delete(qset.db)
            logger.debug(f"Deleted {num_deleted} ParserErrors.")
        except DatabaseError as e:
            log_parser_exception(self.datafile,
                                 ("Encountered error while deleting database records for ParserErrors. "
                                  f"Exception: \n{e}"),
                                 "error"
                                 )
        except Exception as e:
            log_parser_exception(self.datafile,
                                 f"Encountered generic exception while rolling back ParserErrors. Exception: \n{e}.",
                                 "error"
                                 )

    def create_no_records_created_pre_check_error(self):
        """Generate a precheck error if no records were created."""
        if self.dfs.total_number_of_records_created == 0:
            errors = {}
            generate_error = util.make_generate_parser_error(self.datafile, 0)
            err_obj = generate_error(
                    schema=None,
                    error_category=ParserErrorCategoryChoices.PRE_CHECK,
                    error_message="No records created.",
                    record=None,
                    field=None
                )
            errors["no_records_created"] = [err_obj]
            self.unsaved_parser_errors.update(errors)
            self.num_errors += 1

    def _delete_serialized_records(self, duplicate_manager):
        """Delete all records that have already been serialized to the DB that have cat4 errors."""
        total_deleted = 0
        for model, ids in duplicate_manager.get_records_to_remove().items():
            try:
                qset = model.objects.filter(id__in=ids)
                # WARNING: we can use `_raw_delete` in this case because our record models don't have cascading
                # dependencies. If that ever changes, we should NOT use `_raw_delete`.
                num_deleted = qset._raw_delete(qset.db)
                total_deleted += num_deleted
                self.dfs.total_number_of_records_created -= num_deleted
                logger.debug(f"Deleted {num_deleted} records of type: {model}.")
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
