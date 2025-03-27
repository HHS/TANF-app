"""Row schema for datafile."""

from abc import ABC, abstractmethod
from tdpservice.parsers.models import ParserErrorCategoryChoices
from tdpservice.parsers.fields import Field
from tdpservice.parsers.dataclasses import SchemaResult, RawRow, ValidationErrorArgs
from tdpservice.parsers.validators.util import value_is_empty
from tdpservice.parsers.validators.category2 import format_error_context
from tdpservice.parsers.util import get_record_value_by_field_name

import logging

logger = logging.getLogger(__name__)


class RowSchema(ABC):
    """Base schema class for tabular data."""

    def __init__(self, record_type,
                 document,
                 fields,
                 generate_hashes_func,
                 should_skip_partial_dup_func,
                 preparsing_validators,
                 quiet_preparser_errors):
        super().__init__()
        self.record_type = record_type
        self.document = document
        self.fields = list() if not fields else fields
        self.datafile = None
        self.generate_hashes_func = generate_hashes_func
        self.should_skip_partial_dup_func = should_skip_partial_dup_func
        self.preparsing_validators = []
        if preparsing_validators is not None:
            self.preparsing_validators = preparsing_validators
        self.quiet_preparser_errors = quiet_preparser_errors

    @abstractmethod
    def parse_and_validate(self, row: RawRow, generate_error) -> SchemaResult:
        """To be overriden in child class."""
        pass

    def parse_row(self, row: RawRow):
        """Create a model for the row based on the schema."""
        record = self.document.Django.model() if self.document is not None else dict()

        for field in self.fields:
            value = field.parse_value(row)

            if value is not None:
                if isinstance(record, dict):
                    record[field.name] = value
                else:
                    setattr(record, field.name, value)

        return record

    def set_datafile(self, datafile):
        """Datafile setter."""
        self.datafile = datafile

    def _add_field(self, item, name, length, position, type):
        """Add a field to the schema."""
        self.fields.append(
            Field(item, name, type, position)
        )

    def add_fields(self, fields: list):
        """Add multiple fields to the schema."""
        for field, length, start, end, type in fields:
            self._add_field(field, length, start, end, type)

    def get_all_fields(self):
        """Get all fields from the schema."""
        return self.fields

    def run_field_validators(self, record, generate_error):
        """Run all validators for each field in the parsed model."""
        is_valid = True
        errors = []

        for field in self.fields:
            value = get_record_value_by_field_name(record, field.name)
            eargs = ValidationErrorArgs(
                value=value,
                row_schema=self,
                friendly_name=field.friendly_name,
                item_num=field.item,
            )
            is_empty = value_is_empty(value, len(field.position))
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
                                record=record,
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
                        record=record,
                        field=field
                    )
                )

        return is_valid, errors

    def run_preparsing_validators(self, row: RawRow, record, generate_error):
        """Run each of the `preparsing_validator` functions in the schema against the un-parsed row."""
        is_valid = True
        errors = []

        field = self.get_field_by_name('RecordType')

        for validator in self.preparsing_validators:
            eargs = ValidationErrorArgs(
                value=row,
                row_schema=self,
                friendly_name=field.friendly_name if field else 'record type',
                item_num=field.item if field else '0',
            )

            result = validator(row, eargs)
            is_valid = False if not result.valid else is_valid

            is_quiet_preparser_errors = (
                self.quiet_preparser_errors
                if type(self.quiet_preparser_errors) is bool
                else self.quiet_preparser_errors(row)
            )
            if result.error and not is_quiet_preparser_errors:
                errors.append(
                    generate_error(
                        schema=self,
                        error_category=ParserErrorCategoryChoices.PRE_CHECK,
                        error_message=result.error,
                        record=record,
                        field=self.fields,
                        deprecated=result.deprecated,
                    )
                )
        return is_valid, errors

    def get_field_values_by_names(self, row: RawRow, names={}):
        """Return dictionary of field values keyed on their name."""
        field_values = {}
        for field in self.fields:
            if field.name in names:
                field_values[field.name] = field.parse_value(row)
        return field_values

    def get_field_by_name(self, name):
        """Get field by it's name."""
        for field in self.fields:
            if field.name == name:
                return field
        return None


class TanfDataReportSchema(RowSchema):
    """Maps the schema for TANF/SSP/Tribal data rows."""

    def __init__(
            self,
            record_type="T1",
            document=None,
            fields=None,
            # The default hash function covers all program types with record types ending in a 6 or 7.
            generate_hashes_func=lambda row, record: (hash(row),
                                                      hash(record.RecordType)),
            should_skip_partial_dup_func=lambda record: False,
            get_partial_hash_members_func=lambda: ["RecordType"],
            preparsing_validators=None,
            postparsing_validators=None,
            quiet_preparser_errors=False
            ):
        super().__init__(record_type, document, fields, generate_hashes_func,
                         should_skip_partial_dup_func, preparsing_validators, quiet_preparser_errors)

        self.get_partial_hash_members_func = get_partial_hash_members_func
        self.preparsing_validators = preparsing_validators
        self.postparsing_validators = []
        if postparsing_validators is not None:
            self.postparsing_validators = postparsing_validators

    def parse_and_validate(self, row: RawRow, generate_error):
        """Run all validation steps in order, and parse the given row into a record."""
        errors = []

        # parse row to model
        record = self.parse_row(row)

        # run preparsing validators
        preparsing_is_valid, preparsing_errors = self.run_preparsing_validators(
            row, record, generate_error
        )
        is_quiet_preparser_errors = (
                self.quiet_preparser_errors
                if type(self.quiet_preparser_errors) is bool
                else self.quiet_preparser_errors(row)
            )
        if not preparsing_is_valid:
            if is_quiet_preparser_errors:
                return SchemaResult(None, True, [])
            logger.info(f"{len(preparsing_errors)} preparser error(s) encountered.")
            return SchemaResult(None, False, preparsing_errors)

        # run field validators
        fields_are_valid, field_errors = self.run_field_validators(record, generate_error)

        # run postparsing validators
        postparsing_is_valid, postparsing_errors = self.run_postparsing_validators(record, generate_error)

        is_valid = fields_are_valid and postparsing_is_valid
        errors = field_errors + postparsing_errors

        return SchemaResult(record, is_valid, errors)

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


class FRASchema(RowSchema):
    """Maps the schema for FRA data rows."""

    def __init__(
            self,
            record_type="FRA_RECORD",
            document=None,
            fields=None,
            generate_hashes_func=lambda row, record: (hash(row),
                                                      hash(record.RecordType)),
            should_skip_partial_dup_func=lambda record: True,
            preparsing_validators=None,
            quiet_preparser_errors=False
            ):
        super().__init__(record_type, document, fields, generate_hashes_func,
                         should_skip_partial_dup_func, preparsing_validators, quiet_preparser_errors)

    def parse_and_validate(self, row: RawRow, generate_error):
        """Run all validation steps in order, and parse the given row into a record."""
        # Parse FRA row and run field validators, waiting for guidance on other categories of validators
        # The implementor should reference `UpdatedErrorReport.xlsx` to gain insight into appropriate
        # validators for fields.

        # parse row to model
        record = self.parse_row(row)

        # run preparsing validators
        preparsing_is_valid, preparsing_errors = self.run_preparsing_validators(
            row, record, generate_error
        )
        is_quiet_preparser_errors = (
                self.quiet_preparser_errors
                if type(self.quiet_preparser_errors) is bool
                else self.quiet_preparser_errors(row)
            )
        if not preparsing_is_valid:
            if is_quiet_preparser_errors:
                preparsing_errors = []
            logger.info(f"{len(preparsing_errors)} category4 preparser error(s) encountered.")
            return SchemaResult(None, False, preparsing_errors)

        fields_are_valid, field_errors = self.run_field_validators(record, generate_error)

        record = record if fields_are_valid else None

        return SchemaResult(record, fields_are_valid, field_errors)

    def run_preparsing_validators(self, row: RawRow, record, generate_error):
        """Run each of the `preparsing_validator` functions in the schema against the un-parsed row."""
        is_valid = True
        errors = []

        field = self.get_field_by_name('RecordType')

        for validator in self.preparsing_validators:
            eargs = ValidationErrorArgs(
                value=row,
                row_schema=self,
                friendly_name=field.friendly_name if field else 'record type',
                item_num=field.item if field else '0',
            )

            result = validator(row, eargs)
            is_valid = False if not result.valid else is_valid

            is_quiet_preparser_errors = (
                self.quiet_preparser_errors
                if type(self.quiet_preparser_errors) is bool
                else self.quiet_preparser_errors(row)
            )
            if result.error and not is_quiet_preparser_errors:
                errors.append(
                    generate_error(
                        schema=self,
                        error_category=ParserErrorCategoryChoices.CASE_CONSISTENCY,
                        error_message=result.error,
                        record=record,
                        offending_field=field,
                        fields=self.fields,
                        deprecated=result.deprecated,
                    )
                )
        return is_valid, errors

    def run_field_validators(self, record, generate_error):
        """
        Run all validators for each field in the parsed model.

        NOTE: FRA (for the moment) needs all field based validators to produce category1 errors. This is the same exact
        logic as RowSchema.run_field_validators, but we need to override it here to ensure that the error category is
        correct.
        """
        is_valid = True
        errors = []

        for field in self.fields:
            value = get_record_value_by_field_name(record, field.name)
            eargs = ValidationErrorArgs(
                value=value,
                row_schema=self,
                friendly_name=field.friendly_name,
                item_num=field.item,
            )
            is_empty = value_is_empty(value, len(field.position))
            should_validate = not field.required and not is_empty
            if (field.required and not is_empty) or should_validate:
                for validator in field.validators:
                    result = validator(value, eargs)
                    is_valid = False if (not result.valid and not field.ignore_errors) else is_valid
                    if result.error:
                        errors.append(
                            generate_error(
                                schema=self,
                                error_category=ParserErrorCategoryChoices.CASE_CONSISTENCY,
                                error_message=result.error,
                                record=record,
                                offending_field=field,
                                fields=self.fields,
                                deprecated=result.deprecated
                            )
                        )
            elif field.required:
                is_valid = False
                errors.append(
                    generate_error(
                        schema=self,
                        error_category=ParserErrorCategoryChoices.PRE_CHECK,
                        error_message=(
                            f"{format_error_context(eargs)} "
                            "field is required but a value was not provided."
                        ),
                        record=record,
                        offending_field=field,
                        fields=self.fields,
                    )
                )

        return is_valid, errors
