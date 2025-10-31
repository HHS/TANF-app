"""Program audit parser class."""

import logging

from django.conf import settings
from django.core.paginator import Paginator
from django.db.models import Count

from tdpservice.parsers import schema_defs
from tdpservice.parsers.parser_classes.tdr_parser import TanfDataReportParser

logger = logging.getLogger(__name__)


class ProgramAuditParser(TanfDataReportParser):
    """Parser class for TANF/SSP/Tribal program audit."""

    def __init__(self, datafile, dfs, section):
        super().__init__(datafile, dfs, section)
        self.header_schema = schema_defs.program_audit.header
        self.trailer_schema = schema_defs.program_audit.trailer

    def _delete_duplicates(self, record, duplicate_records):
        pass

    def _delete_exact_dups(self):
        """Overwrite _delete_exact_dups to handle pagination while skipping the delete step."""
        logger.info("Generating errors for exact duplicates.")
        for schemas in self.schema_manager.schema_map.values():
            schema = schemas[0]

            fields = [f.name for f in schema.fields if f.name != "BLANK"]
            records = schema.model.objects.filter(datafile=self.datafile)

            duplicates_vals = (
                records.values(*fields)
                .annotate(row_count=Count("line_number", distinct=True))
                .filter(row_count__gt=1)
            )
            paginator = Paginator(duplicates_vals, settings.BULK_CREATE_BATCH_SIZE)

            for page in paginator:
                self._generate_errors_and_delete_dups(
                    records, page, schema, self._generate_exact_dup_error_msg
                )

    def _delete_partial_dups(self):
        """Overwrite _delete_partial_dups to handle pagination while skipping the delete step."""
        # Partial duplicates are only relevant for active and closed case files
        if not self.is_active_or_closed:
            return

        logger.info("Generating errors for partial duplicates.")
        for schemas in self.schema_manager.schema_map.values():
            schema = schemas[0]
            fields = schema.get_partial_dup_fields()
            records = schema.model.objects.filter(datafile=self.datafile)

            if schema.partial_dup_exclusion_query is not None:
                records = records.exclude(schema.partial_dup_exclusion_query)

            partial_dups_values = (
                records.values(*fields)
                .annotate(row_count=Count("line_number", distinct=True))
                .filter(row_count__gt=1)
            )

            paginator = Paginator(partial_dups_values, settings.BULK_CREATE_BATCH_SIZE)

            for page in paginator:
                self._generate_errors_and_delete_dups(
                    records,
                    page,
                    schema,
                    self._generate_partial_dup_error_msg,
                )
