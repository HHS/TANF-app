"""Row schema for datafile."""

from dataclasses import dataclass
from django.db.models import Model
from tdpservice.parsers.models import ParserErrorCategoryChoices
from tdpservice.parsers.fields import Field, TransformField
from tdpservice.parsers.validators.util import value_is_empty, ValidationErrorArgs
from tdpservice.parsers.validators.category2 import format_error_context
from tdpservice.parsers.util import get_record_value_by_field_name
from typing import List, Tuple
import logging

logger = logging.getLogger(__name__)

class RowSchema:
    """Maps the schema for data lines."""

    def __init__(
            self,
            record_type="T1",
            document=None,
            # The default hash function covers all program types with record types ending in a 6 or 7.
            generate_hashes_func=lambda line, record: (hash(line),
                                                       hash(record.RecordType)),
            should_skip_partial_dup_func=lambda record: False,
            get_partial_hash_members_func=lambda: ["RecordType"],
            preparsing_validators=[],
            postparsing_validators=[],
            fields=[],
            quiet_preparser_errors=False,
            ):
        self.document = document
        self.generate_hashes_func = generate_hashes_func
        self.should_skip_partial_dup_func = should_skip_partial_dup_func
        self.get_partial_hash_members_func = get_partial_hash_members_func
        self.preparsing_validators = preparsing_validators
        self.postparsing_validators = postparsing_validators
        self.fields = fields
        self.quiet_preparser_errors = quiet_preparser_errors
        self.record_type = record_type
        self.datafile = None

    def _add_field(self, item, name, length, start, end, type):
        """Add a field to the schema."""
        self.fields.append(
            Field(item, name, type, start, end)
        )

    def add_fields(self, fields: list):
        """Add multiple fields to the schema."""
        for field, length, start, end, type in fields:
            self._add_field(field, length, start, end, type)

    def get_all_fields(self):
        """Get all fields from the schema."""
        return self.fields

    def parse_and_validate(self, line, generate_error):
        """Run all validation steps in order, and parse the given line into a record."""
        errors = []

        # run preparsing validators
        preparsing_is_valid, preparsing_errors = self.run_preparsing_validators(
            line, generate_error
        )
        is_quiet_preparser_errors = (
                self.quiet_preparser_errors
                if type(self.quiet_preparser_errors) is bool
                else self.quiet_preparser_errors(line)
            )
        if not preparsing_is_valid:
            if is_quiet_preparser_errors:
                return None, True, []
            logger.info(f"{len(preparsing_errors)} preparser error(s) encountered.")
            return None, False, preparsing_errors

        # parse line to model
        record = self.parse_line(line)

        # run field validators
        fields_are_valid, field_errors = self.run_field_validators(record, generate_error)

        # run postparsing validators
        postparsing_is_valid, postparsing_errors = self.run_postparsing_validators(record, generate_error)

        is_valid = fields_are_valid and postparsing_is_valid
        errors = field_errors + postparsing_errors

        return record, is_valid, errors

    def run_preparsing_validators(self, line, generate_error):
        """Run each of the `preparsing_validator` functions in the schema against the un-parsed line."""
        is_valid = True
        errors = []

        field = self.get_field_by_name('RecordType')

        for validator in self.preparsing_validators:
            eargs = ValidationErrorArgs(
                value=line,
                row_schema=self,
                friendly_name=field.friendly_name if field else 'record type',
                item_num=field.item if field else '0',
            )
            result = validator(line, eargs)
            is_valid = False if not result.valid else is_valid

            is_quiet_preparser_errors = (
                self.quiet_preparser_errors
                if type(self.quiet_preparser_errors) is bool
                else self.quiet_preparser_errors(line)
            )
            if result.error and not is_quiet_preparser_errors:
                errors.append(
                    generate_error(
                        schema=self,
                        error_category=ParserErrorCategoryChoices.PRE_CHECK,
                        error_message=result.error,
                        record=None,
                        field="Record_Type",
                        deprecated=result.deprecated,
                    )
                )

        return is_valid, errors

    def parse_line(self, line):
        """Create a model for the line based on the schema."""
        record = self.document.Django.model() if self.document is not None else dict()

        for field in self.fields:
            value = field.parse_value(line)

            if value is not None:
                if isinstance(record, dict):
                    record[field.name] = value
                else:
                    setattr(record, field.name, value)

        return record

    def run_field_validators(self, instance, generate_error):
        """Run all validators for each field in the parsed model."""
        is_valid = True
        errors = []

        for field in self.fields:
            value = get_record_value_by_field_name(instance, field.name)
            eargs = ValidationErrorArgs(
                value=value,
                row_schema=self,
                friendly_name=field.friendly_name,
                item_num=field.item,
            )

            is_empty = value_is_empty(value, field.endIndex-field.startIndex)
            should_validate = not field.required and not is_empty
            if (field.required and not is_empty) or should_validate:
                for validator in field.validators:
                    result = validator(value, eargs)
                    is_valid = False if (not result.valid and not field.ignore_errors) else is_valid
                    if result.error:
                        errors.append(
                            generate_error(
                                schema=self,
                                error_category=ParserErrorCategoryChoices.FIELD_VALUE,
                                error_message=result.error,
                                record=instance,
                                field=field,
                                deprecated=result.deprecated
                            )
                        )
            elif field.required:
                is_valid = False
                errors.append(
                    generate_error(
                        schema=self,
                        error_category=ParserErrorCategoryChoices.FIELD_VALUE,
                        error_message=(
                            f"{format_error_context(eargs)} "
                            "field is required but a value was not provided."
                        ),
                        record=instance,
                        field=field
                    )
                )

        return is_valid, errors

    def run_postparsing_validators(self, instance, generate_error):
        """Run each of the `postparsing_validator` functions against the parsed model."""
        is_valid = True
        errors = []

        for validator in self.postparsing_validators:
            result = validator(instance, self)
            is_valid = False if not result.valid else is_valid
            if result.error:
                # get field from field name
                fields = [self.get_field_by_name(name) for name in result.field_names]
                errors.append(
                    generate_error(
                        schema=self,
                        error_category=ParserErrorCategoryChoices.VALUE_CONSISTENCY,
                        error_message=result.error,
                        record=instance,
                        field=fields,
                        deprecated=result.deprecated
                    )
                )

        return is_valid, errors

    def get_field_values_by_names(self, line, names={}):
        """Return dictionary of field values keyed on their name."""
        field_values = {}
        for field in self.fields:
            if field.name in names:
                field_values[field.name] = field.parse_value(line)
        return field_values

    def get_field_by_name(self, name):
        """Get field by it's name."""
        for field in self.fields:
            if field.name == name:
                return field
        return None


@dataclass
class ManagerPVResult:
    """SchemaManager parse and validate result class."""

    # TODO: Update the `records` type to align the implementation of `SchemaResult`
    records: List[Tuple[Model, bool, List[Model]]]
    schemas: List[RowSchema]


class SchemaManager:
    """Manages all RowSchema's based on a file's program type and section."""

    def __init__(self, datafile, program_type, section):
        self.datafile = datafile
        self.program_type = program_type
        self.section = section
        self.schema_map = None
        self._init_schema_map()

    def _init_schema_map(self):
        """Initialize all schemas for the program type and section."""
        from tdpservice.parsers.schema_defs.utils import get_program_models, get_text_from_df
        short_section = get_text_from_df(self.datafile)['section']
        self.schema_map = get_program_models(self.program_type, short_section)
        for schemas in self.schema_map.values():
            for schema in schemas:
                schema.datafile = self.datafile

    def parse_and_validate(self, row, generate_error):
        """Run `parse_and_validate` for each schema provided and bubble up errors."""
        # row should know it's record type
        try:
            records = []
            schemas = self.schema_map[row.record_type]
            # TODO: We pass `raw_data` for now until the `RowSchema` and `Field` classes are
            # updated to support `RawRow`.
            for schema in schemas:
                record, is_valid, errors = schema.parse_and_validate(row.raw_data, generate_error)
                records.append((record, is_valid, errors))
            return ManagerPVResult(records=records, schemas=schemas)
        except Exception:
            records = [(None, False, [
                generate_error(
                    schema=None,
                    error_category=ParserErrorCategoryChoices.PRE_CHECK,
                    error_message="Unknown Record_Type was found.",
                    record=None,
                    field="Record_Type",
                )
            ])]
            return ManagerPVResult(records=records, schemas=[])

    def update_encrypted_fields(self, is_encrypted):
        """Update whether schema fields are encrypted or not."""
        # This should be called at the begining of parsing after the header has been parsed and we have access
        # to is_encrypted for TANF/SSP/Tribal
        for schemas in self.schema_map.values():
            for schema in schemas:
                for field in schema.fields:
                    if type(field) == TransformField and "is_encrypted" in field.kwargs:
                        field.kwargs['is_encrypted'] = is_encrypted
