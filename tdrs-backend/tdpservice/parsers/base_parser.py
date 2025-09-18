"""Base parser logic associated to all parser classes."""

import itertools
import logging
from abc import ABC, abstractmethod

from django.conf import settings
from django.db.models import Count, Q
from django.db.utils import DatabaseError

from tdpservice.parsers.decoders import DecoderFactory
from tdpservice.parsers.error_generator import (
    ErrorGeneratorArgs,
    ErrorGeneratorFactory,
    ErrorGeneratorType,
)
from tdpservice.parsers.models import ParserError
from tdpservice.parsers.schema_manager import SchemaManager
from tdpservice.parsers.util import (
    DecoderUnknownException,
    FrozenDict,
    Records,
    log_parser_exception,
)

logger = logging.getLogger(__name__)


class BaseParser(ABC):
    """Abstract base class for all parsers."""

    def __init__(self, datafile, dfs, section):
        super().__init__()
        self.datafile = datafile
        self.error_generator_factory = ErrorGeneratorFactory(datafile)
        self.dfs = dfs
        self.section = section
        self.program_type = None
        self.is_active_or_closed = "Active" in self.section or "Closed" in self.section

        self.current_row = None
        self.current_row_num = 0

        # Specifying unsaved_records here may or may not work for FRA files. If not, we can move it down the
        # inheritance hierarchy.
        self.unsaved_records = Records()
        self.unsaved_parser_errors = dict()
        self.num_errors = 0

        # Track cases that have already been serialized that need to be removed because of a case consistency error.
        self.serialized_cases = set()

        # Initialized decoder.
        self._init_decoder()

    @abstractmethod
    def parse_and_validate(self):
        """To be overriden in child class."""
        pass

    def _init_decoder(self):
        """Initialize the decoder."""
        try:
            self.decoder = DecoderFactory.get_instance(self.datafile.file)
        except ValueError as e:
            log_parser_exception(
                self.datafile, f"Could not determine encoding of file: \n{e}", "error"
            )
            if self.datafile.Section.is_fra(self.section):
                msg = (
                    "Could not determine encoding of FRA file. If the file is an XLSX file, ensure it "
                    "can be opened in Excel. If the file is a CSV, ensure it can be opened in a text "
                    "editor and is UTF-8 encoded."
                )
            else:
                msg = "Could not determine encoding of TANF file. Ensure the file is UTF-8 encoded."
            generate_error = self.error_generator_factory.get_generator(
                ErrorGeneratorType.MSG_ONLY_PRECHECK, 0
            )
            generator_args = ErrorGeneratorArgs(
                record=None,
                schema=None,
                error_message=msg,
                fields=[],
            )
            err_obj = generate_error(generator_args=generator_args)
            self.unsaved_parser_errors.update({0: [err_obj]})
            self.num_errors += 1
            self.bulk_create_errors(flush=True)
            raise DecoderUnknownException(msg)

    def _init_schema_manager(self, program_type):
        """Initialize the schema manager with the given program type."""
        # program_type is manipulated by some parsers. E.g. the tdr_parser has to prefix a tribal TANF's program type
        # with "Tribal" since it's base program type would just be TANF.
        self.program_type = program_type
        self.schema_manager = SchemaManager(
            self.datafile, self.program_type, self.section
        )

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
                    log_parser_exception(
                        self.datafile,
                        f"Encountered error while creating database records: \n{e}",
                        "error",
                    )
                    return False
                except Exception as e:
                    log_parser_exception(
                        self.datafile,
                        f"Encountered generic exception while creating database records: \n{e}",
                        "error",
                    )
                    return False

            self.dfs.total_number_of_records_created += num_db_records_created
            if num_db_records_created != num_expected_db_records:
                logger.error(
                    f"Bulk Django record creation only created {num_db_records_created}/"
                    + f"{num_expected_db_records}!"
                )
            else:
                logger.info(
                    f"Created {num_db_records_created}/{num_expected_db_records} records."
                )

            all_created = num_db_records_created == num_expected_db_records
            self.unsaved_records.clear(all_created)
            return all_created

    def bulk_create_errors(self, batch_size=5000, flush=False):
        """Bulk create unsaved_parser_errors."""
        if flush or (self.unsaved_parser_errors and self.num_errors >= batch_size):
            logger.debug("Bulk creating ParserErrors.")
            num_created = len(
                ParserError.objects.bulk_create(
                    list(
                        itertools.chain.from_iterable(
                            self.unsaved_parser_errors.values()
                        )
                    )
                )
            )
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
                log_parser_exception(
                    self.datafile,
                    (
                        f"Encountered error while deleting database records for model: {model}. "
                        f"Exception: \n{e}"
                    ),
                    "error",
                )
            except Exception as e:
                log_parser_exception(
                    self.datafile,
                    (
                        "Encountered generic exception while trying to rollback "
                        f"records. Exception: \n{e}"
                    ),
                    "error",
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
            log_parser_exception(
                self.datafile,
                (
                    "Encountered error while deleting database records for ParserErrors. "
                    f"Exception: \n{e}"
                ),
                "error",
            )
        except Exception as e:
            log_parser_exception(
                self.datafile,
                f"Encountered generic exception while rolling back ParserErrors. Exception: \n{e}.",
                "error",
            )

    def create_no_records_created_pre_check_error(self):
        """Generate a precheck error if no records were created."""
        no_records_allowed = (
            "Closed Case Data" in self.section
            and self.dfs.total_number_of_records_created
            == self.dfs.total_number_of_records_in_file
        )
        if self.dfs.total_number_of_records_created == 0 and not no_records_allowed:
            errors = {}
            generate_error = self.error_generator_factory.get_generator(
                ErrorGeneratorType.MSG_ONLY_PRECHECK, 0
            )
            generator_args = ErrorGeneratorArgs(
                record=None,
                schema=None,
                error_message="No records created.",
                fields=[],
            )
            err_obj = generate_error(generator_args=generator_args)
            errors["no_records_created"] = [err_obj]
            self.unsaved_parser_errors.update(errors)
            self.num_errors += 1

    # TODO: Delete this method
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
                log_parser_exception(
                    self.datafile,
                    (
                        f"Encountered error while deleting database records for model {model}. "
                        f"Exception: \n{e}"
                    ),
                    "error",
                )
            except Exception as e:
                log_parser_exception(
                    self.datafile,
                    (
                        f"Encountered generic exception while deleting records of type {model}. "
                        f"Exception: \n{e}"
                    ),
                    "error",
                )

    def add_case_to_remove(self, should_remove, case_id: FrozenDict):
        """Add case ID to set of IDs to be removed later."""
        if should_remove:
            self.serialized_cases.add(case_id)

    def _delete_serialized_cases(self):
        """Delete all cases that have already been serialized to the DB with cat4 errors."""
        if len(self.serialized_cases):
            cases = Q()
            for case in self.serialized_cases:
                cases |= Q(**case)
                print(f"Deleting case with cat4: {case}")
            for schemas in self.schema_manager.schema_map.values():
                schema = schemas[0]
                num_deleted, _ = schema.model.objects.filter(
                    cases, datafile=self.datafile
                ).delete()
                self.dfs.total_number_of_records_created -= num_deleted

    # TODO: paginate this
    def _delete_exact_dups(self):
        """Delete exact duplicate records from the DB."""
        duplicate_error_generator = self.error_generator_factory.get_generator(
            ErrorGeneratorType.DYNAMIC_ROW_CASE_CONSISTENCY, None
        )
        for schemas in self.schema_manager.schema_map.values():
            schema = schemas[0]

            fields = [f.name for f in schema.fields if f.name != "BLANK"]
            duplicate_vals = (
                schema.model.objects.filter(datafile=self.datafile)
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
                    record_type = dup_vals_dict.get("RecordType", None)
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

    def _get_partial_dup_error_msg(
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

    # TODO: paginate this
    def _delete_partial_dups(self):
        """Delete partial duplicate records from the DB."""
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
                        error_message=self._get_partial_dup_error_msg(
                            schema, record_type, dup.line_number, record.line_number
                        ),
                        fields=schema.fields,
                        row_number=record.line_number,
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
                num_deleted, _ = dup_records.delete()
                self.dfs.total_number_of_records_created -= num_deleted

            self.unsaved_parser_errors[None] = (
                self.unsaved_parser_errors.get(None, []) + dup_errors
            )
