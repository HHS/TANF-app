"""Manager class for a datafile's schema's."""

import logging

from tdpservice.parsers.dataclasses import ManagerPVResult
from tdpservice.parsers.error_generator import (
    ErrorGeneratorArgs,
    ErrorGeneratorFactory,
    ErrorGeneratorType,
)
from tdpservice.parsers.fields import TransformField
from tdpservice.parsers.schema_defs.utils import ProgramManager

logger = logging.getLogger(__name__)


class SchemaManager:
    """Manages all RowSchema's based on a file's program type and section."""

    def __init__(self, datafile, program_type, section):
        self.datafile = datafile
        self.error_generator_factory = ErrorGeneratorFactory(self.datafile)
        self.program_type = program_type
        self.section = section
        self.is_program_audit = datafile.is_program_audit
        self.schema_map = None
        self._init_schema_map()

    def _init_schema_map(self):
        """Initialize all schemas for the program type and section."""
        self.schema_map = ProgramManager.get_schemas(
            self.program_type, self.section, self.is_program_audit
        )
        for schemas in self.schema_map.values():
            for schema in schemas:
                schema.prepare(self.datafile)

    def parse_and_validate(self, row):
        """Run `parse_and_validate` for each schema provided and bubble up errors."""
        try:
            records = []
            schemas = self.schema_map[row.record_type]
            for schema in schemas:
                record, is_valid, errors = schema.parse_and_validate(row)
                records.append((record, is_valid, errors))
            return ManagerPVResult(records=records, schemas=schemas)
        except Exception as e:
            logger.exception("Exception in SchemaManager.parse_and_validate")
            logger.exception(e)
            generator_args = ErrorGeneratorArgs(
                record=None,
                schema=None,
                error_message="Unknown Record_Type was found.",
                offending_field=None,
                fields=None,
            )
            records = [
                (
                    None,
                    False,
                    [
                        self.error_generator_factory.get_generator(
                            generator_type=ErrorGeneratorType.MSG_ONLY_RECORD_PRECHECK,
                            row_number=row.row_num,
                        )(generator_args)
                    ],
                )
            ]
            return ManagerPVResult(records=records, schemas=[])

    def update_encrypted_fields(self, is_encrypted):
        """Update whether schema fields are encrypted or not."""
        # This should be called at the begining of parsing after the header has been parsed and we have access
        # to is_encrypted for TANF/SSP/Tribal
        for schemas in self.schema_map.values():
            for schema in schemas:
                for field in schema.fields:
                    if type(field) == TransformField and "is_encrypted" in field.kwargs:
                        field.kwargs["is_encrypted"] = is_encrypted
