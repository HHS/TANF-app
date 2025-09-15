"""Row schema for datafile."""

import logging
from abc import ABC, abstractmethod

from tdpservice.parsers.dataclasses import (
    ErrorGeneratorArgs,
    RawRow,
    SchemaResult,
    ValidationErrorArgs,
)
from tdpservice.parsers.error_generator import ErrorGeneratorFactory, ErrorGeneratorType
from tdpservice.parsers.fields import Field
from tdpservice.parsers.util import get_record_value_by_field_name
from tdpservice.parsers.validators.category2 import format_error_context
from tdpservice.parsers.validators.util import value_is_empty

logger = logging.getLogger(__name__)


class RowSchema(ABC):
    """Base schema class for tabular data."""

    def __init__(
        self,
        record_type,
        model,
        fields,
        generate_hashes_func,
        should_skip_partial_dup_func,
        preparsing_validators,
        quiet_preparser_errors,
    ):
        super().__init__()
        self.record_type = record_type
        self.model = model
        self.fields = list() if not fields else fields
        self.datafile = None
        self.error_generator_factory = None
        self.generate_hashes_func = generate_hashes_func
        self.should_skip_partial_dup_func = should_skip_partial_dup_func
        self.preparsing_validators = []
        if preparsing_validators is not None:
            self.preparsing_validators = preparsing_validators
        self.quiet_preparser_errors = quiet_preparser_errors

        self.field_error_generator_type = ErrorGeneratorType.FIELD_VALUE
        self.precheck_error_generator_type = ErrorGeneratorType.RECORD_PRE_CHECK
        self.postparsing_error_generator_type = ErrorGeneratorType.VALUE_CONSISTENCY

    @abstractmethod
    def parse_and_validate(self, row: RawRow) -> SchemaResult:
        """To be overriden in child class."""
        pass

    def parse_row(self, row: RawRow):
        """Create a model for the row based on the schema."""
        record = self.model()

        for field in self.fields:
            value = field.parse_value(row)

            if value is not None:
                if isinstance(record, dict):
                    record[field.name] = value
                else:
                    setattr(record, field.name, value)

        return record

    def prepare(self, datafile):
        """Prepare schema to validate."""
        self.datafile = datafile
        self.error_generator_factory = ErrorGeneratorFactory(self.datafile)

    def _add_field(self, item, name, length, position, type):
        """Add a field to the schema."""
        self.fields.append(Field(item, name, type, position))

    def add_fields(self, fields: list):
        """Add multiple fields to the schema."""
        for field, length, start, end, type in fields:
            self._add_field(field, length, start, end, type)

    def get_all_fields(self):
        """Get all fields from the schema."""
        return self.fields

    def run_field_validators(self, record, row_number):
        """Run all validators for each field in the parsed model."""
        is_valid = True
        errors = []

        generate_error = self.error_generator_factory.get_generator(
            generator_type=self.field_error_generator_type,
            row_number=row_number,
        )

        for field in self.fields:
            value = get_record_value_by_field_name(record, field.name)
            eargs = ValidationErrorArgs(
                value=value,
                row_schema=self,
                friendly_name=field.friendly_name,
                item_num=field.item,
            )

            is_empty = value_is_empty(value, len(field.position))
            if field.required and not is_empty:
                for validator in field.validators:
                    result = validator(value, eargs)
                    is_valid = (
                        False
                        if (not result.valid and not field.ignore_errors)
                        else is_valid
                    )
                    if result.error_message:
                        generator_args = ErrorGeneratorArgs(
                            record=record,
                            schema=self,
                            error_message=result.error_message,
                            offending_field=field,
                            fields=self.fields,
                            deprecated=result.deprecated,
                        )
                        errors.append(
                            generate_error(
                                generator_args=generator_args,
                            )
                        )
            elif field.required:
                is_valid = False
                generator_args = ErrorGeneratorArgs(
                    record=record,
                    schema=self,
                    error_message=(
                        f"{format_error_context(eargs)} "
                        "field is required but a value was not provided."
                    ),
                    offending_field=field,
                    fields=self.fields,
                )
                errors.append(
                    generate_error(
                        generator_args=generator_args,
                    )
                )

        return is_valid, errors

    def run_preparsing_validators(self, row: RawRow, record):
        """Run each of the `preparsing_validator` functions in the schema against the un-parsed row."""
        is_valid = True
        errors = []

        field = self.get_field_by_name("RecordType")
        generate_error = self.error_generator_factory.get_generator(
            generator_type=self.precheck_error_generator_type,
            row_number=row.row_num,
        )

        for validator in self.preparsing_validators:
            eargs = ValidationErrorArgs(
                value=row,
                row_schema=self,
                friendly_name=field.friendly_name if field else "record type",
                item_num=field.item if field else "0",
            )

            result = validator(row, eargs)
            is_valid = False if not result.valid else is_valid

            is_quiet_preparser_errors = (
                self.quiet_preparser_errors
                if type(self.quiet_preparser_errors) is bool
                else self.quiet_preparser_errors(row)
            )

            generator_args = ErrorGeneratorArgs(
                record=record,
                schema=self,
                error_message=result.error_message,
                offending_field=field,
                fields=self.fields,
                deprecated=result.deprecated,
            )

            if result.error_message and not is_quiet_preparser_errors:
                errors.append(generate_error(generator_args=generator_args))
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
        model=None,
        fields=None,
        # The default hash function covers all program types with record types ending in a 6 or 7.
        generate_hashes_func=lambda row, record: (hash(row), hash(record.RecordType)),
        should_skip_partial_dup_func=lambda record: False,
        get_partial_hash_members_func=lambda: ["RecordType"],
        preparsing_validators=None,
        postparsing_validators=None,
        quiet_preparser_errors=False,
    ):
        super().__init__(
            record_type,
            model,
            fields,
            generate_hashes_func,
            should_skip_partial_dup_func,
            preparsing_validators,
            quiet_preparser_errors,
        )

        self.get_partial_hash_members_func = get_partial_hash_members_func
        self.preparsing_validators = preparsing_validators
        self.postparsing_validators = []
        if postparsing_validators is not None:
            self.postparsing_validators = postparsing_validators

    def parse_and_validate(self, row: RawRow):
        """Run all validation steps in order, and parse the given row into a record."""
        errors = []

        # parse row to model
        record = self.parse_row(row)

        # run preparsing validators
        preparsing_is_valid, preparsing_errors = self.run_preparsing_validators(
            row, record
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
        fields_are_valid, field_errors = self.run_field_validators(record, row.row_num)

        # run postparsing validators
        postparsing_is_valid, postparsing_errors = self.run_postparsing_validators(
            record, row.row_num
        )

        is_valid = fields_are_valid and postparsing_is_valid
        errors = field_errors + postparsing_errors

        return SchemaResult(record, is_valid, errors)

    def run_postparsing_validators(self, record, row_number):
        """Run each of the `postparsing_validator` functions against the parsed model."""
        is_valid = True
        errors = []
        generate_error = self.error_generator_factory.get_generator(
            self.postparsing_error_generator_type, row_number
        )

        for validator in self.postparsing_validators:
            result = validator(record, self)
            is_valid = False if not result.valid else is_valid
            if result.error_message:
                # get field from field name
                fields = [self.get_field_by_name(name) for name in result.field_names]
                generator_args = ErrorGeneratorArgs(
                    record=record,
                    schema=self,
                    error_message=result.error_message,
                    offending_field=fields[-1],
                    fields=fields,
                    deprecated=result.deprecated,
                )
                errors.append(generate_error(generator_args=generator_args))
        return is_valid, errors


class HeaderSchema(TanfDataReportSchema):
    """Maps the schema for Header data rows."""

    def __init__(
        self,
        record_type="HEADER",
        model=None,
        fields=None,
        # The default hash function covers all program types with record types ending in a 6 or 7.
        generate_hashes_func=lambda row, record: (hash(row), hash(record.RecordType)),
        should_skip_partial_dup_func=lambda record: False,
        get_partial_hash_members_func=lambda: ["RecordType"],
        preparsing_validators=None,
        postparsing_validators=None,
        quiet_preparser_errors=False,
    ):
        super().__init__(
            record_type,
            model,
            fields,
            generate_hashes_func,
            should_skip_partial_dup_func,
            preparsing_validators,
            quiet_preparser_errors,
        )

        self.get_partial_hash_members_func = get_partial_hash_members_func
        self.preparsing_validators = preparsing_validators
        self.postparsing_validators = []
        if postparsing_validators is not None:
            self.postparsing_validators = postparsing_validators

        self.precheck_error_generator_type = ErrorGeneratorType.PRE_CHECK
        self.field_error_generator_type = ErrorGeneratorType.HEADER_FIELD_VALUE


class FRASchema(RowSchema):
    """Maps the schema for FRA data rows."""

    def __init__(
        self,
        record_type="FRA_RECORD",
        model=None,
        fields=None,
        generate_hashes_func=lambda row, record: (hash(row), hash(record.RecordType)),
        should_skip_partial_dup_func=lambda record: True,
        preparsing_validators=None,
        quiet_preparser_errors=False,
    ):
        super().__init__(
            record_type,
            model,
            fields,
            generate_hashes_func,
            should_skip_partial_dup_func,
            preparsing_validators,
            quiet_preparser_errors,
        )

        self.precheck_error_generator_type = ErrorGeneratorType.FRA
        self.field_error_generator_type = ErrorGeneratorType.FRA

    def parse_and_validate(self, row: RawRow):
        """Run all validation steps in order, and parse the given row into a record."""
        # Parse FRA row and run field validators, waiting for guidance on other categories of validators
        # The implementor should reference `UpdatedErrorReport.xlsx` to gain insight into appropriate
        # validators for fields.

        # parse row to model
        record = self.parse_row(row)

        # run preparsing validators
        preparsing_is_valid, preparsing_errors = self.run_preparsing_validators(
            row, record
        )
        is_quiet_preparser_errors = (
            self.quiet_preparser_errors
            if type(self.quiet_preparser_errors) is bool
            else self.quiet_preparser_errors(row)
        )
        if not preparsing_is_valid:
            if is_quiet_preparser_errors:
                preparsing_errors = []
            logger.info(
                f"{len(preparsing_errors)} category4 preparser error(s) encountered."
            )

        fields_are_valid, field_errors = self.run_field_validators(record, row.row_num)

        is_valid = fields_are_valid and preparsing_is_valid

        return SchemaResult(record, is_valid, field_errors + preparsing_errors)

    # def run_field_validators(self, record, row_number):
    #     """
    #     Run all validators for each field in the parsed model.

    #     NOTE: FRA (for the moment) needs all field based validators to produce category4 errors. This is the same exact
    #     logic as RowSchema.run_field_validators, but we need to override it here to ensure that the error category is
    #     correct.
    #     """
    #     is_valid = True
    #     errors = []

    #     for field in self.fields:
    #         value = get_record_value_by_field_name(record, field.name)
    #         eargs = ValidationErrorArgs(
    #             value=value,
    #             row_schema=self,
    #             friendly_name=field.friendly_name,
    #             item_num=field.item,
    #         )
    #         is_empty = value_is_empty(value, len(field.position))
    #         if field.required and not is_empty:
    #             for validator in field.validators:
    #                 result = validator(value, eargs)
    #                 is_valid = (
    #                     False
    #                     if (not result.valid and not field.ignore_errors)
    #                     else is_valid
    #                 )
    #                 if result.error_message:
    #                     errors.append(
    #                         generate_error(
    #                             schema=self,
    #                             error_category=self.field_error_type,
    #                             error_message=result.error_message,
    #                             record=record,
    #                             offending_field=field,
    #                             fields=self.fields,
    #                             deprecated=result.deprecated,
    #                         )
    #                     )
    #         elif field.required:
    #             is_valid = False
    #             errors.append(
    #                 generate_error(
    #                     schema=self,
    #                     error_category=ParserErrorCategoryChoices.PRE_CHECK,
    #                     error_message=(
    #                         f"{format_error_context(eargs)} "
    #                         "field is required but a value was not provided."
    #                     ),
    #                     record=record,
    #                     offending_field=field,
    #                     fields=self.fields,
    #                 )
    #             )

    #     return is_valid, errors
