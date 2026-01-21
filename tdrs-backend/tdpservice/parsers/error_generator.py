"""Class for generating all types of ParserErrors."""

from enum import Enum

from django.contrib.contenttypes.models import ContentType

from tdpservice.data_files.parser_error_choices import ParserErrorCategoryChoices

from .dataclasses import ErrorGeneratorArgs
from .models import ParserError


class ErrorGeneratorType(Enum):
    """Enum for error generator types."""

    PRE_CHECK = "pre_check"
    RECORD_PRE_CHECK = "record_pre_check"
    FIELD_VALUE = "field_value"
    HEADER_FIELD_VALUE = "header_field_value"
    VALUE_CONSISTENCY = "value_consistency"
    CASE_CONSISTENCY = "case_consistency"
    FRA = "fra_parser_error"

    MSG_ONLY_PRECHECK = "message_only_precheck"
    MSG_ONLY_RECORD_PRECHECK = "message_only_record_precheck"
    DYNAMIC_ROW_CASE_CONSISTENCY = "dynamic_row_case_consistency"


class ErrorGeneratorFactory:
    """Factory for generating all types of ParserErrors."""

    def __init__(self, datafile):
        self.datafile = datafile

    def get_generator(self, generator_type: ErrorGeneratorType, row_number: int):
        """Return a generator given a category type."""
        match generator_type:
            case ErrorGeneratorType.PRE_CHECK:
                return self.create_generate_precheck_error(row_number)
            case ErrorGeneratorType.RECORD_PRE_CHECK:
                return self.create_generate_record_precheck_error(row_number)
            case ErrorGeneratorType.FIELD_VALUE:
                return self.create_generate_field_value_error(row_number)
            case ErrorGeneratorType.HEADER_FIELD_VALUE:
                return self.create_generate_header_field_value_error(row_number)
            case ErrorGeneratorType.VALUE_CONSISTENCY:
                return self.create_generate_value_consistency_error(row_number)
            case ErrorGeneratorType.CASE_CONSISTENCY:
                return self.create_generate_case_consistency_error(row_number)
            case ErrorGeneratorType.FRA:
                return self.create_generate_fra_parser_error(row_number)
            case ErrorGeneratorType.MSG_ONLY_PRECHECK:
                return self.create_generate_message_only_precheck_error(row_number)
            case ErrorGeneratorType.MSG_ONLY_RECORD_PRECHECK:
                return self.create_generate_message_only_record_precheck_error(
                    row_number
                )
            case ErrorGeneratorType.DYNAMIC_ROW_CASE_CONSISTENCY:
                return self.create_generate_dynamic_row_case_consistency_error()
            case _:
                raise ValueError(f"Invalid error category: {generator_type}")

    def _generate_fields_json(self, fields):
        """Generate fields JSON."""
        fields_json = {
            "friendly_name": {
                getattr(f, "name", ""): getattr(f, "friendly_name", "") for f in fields
            },
            "item_numbers": {
                getattr(f, "name", ""): getattr(f, "item", "") for f in fields
            },
        }
        return fields_json

    def _generate_values_json(self, fields, record):
        """Generate values JSON."""
        values_json = {}
        for field in fields:
            name = getattr(field, "name", "")
            value = (
                getattr(record, name, None)
                if type(record) is not dict
                else record.get(name, None)
            )
            values_json[name] = value
        return values_json

    def create_generate_case_consistency_error(self, row_number):
        """Create a case consistency error generator."""

        def generate_case_consistency_error(generator_args: ErrorGeneratorArgs):
            field = generator_args.schema.record_type
            record = generator_args.record
            fields_json = self._generate_fields_json(generator_args.fields)
            values_json = self._generate_values_json(generator_args.fields, record)
            return ParserError(
                file=self.datafile,
                row_number=row_number,
                column_number=getattr(field, "item", ""),
                item_number=getattr(field, "item", ""),
                field_name=getattr(field, "name", ""),
                rpt_month_year=getattr(record, "RPT_MONTH_YEAR", None),
                case_number=getattr(record, "CASE_NUMBER", None),
                error_message=generator_args.error_message,
                error_type=ParserErrorCategoryChoices.CASE_CONSISTENCY,
                content_type=None,
                object_id=None,
                fields_json=fields_json,
                values_json=values_json,
                deprecated=generator_args.deprecated,
            )

        return generate_case_consistency_error

    def create_generate_precheck_error(self, row_number):
        """Create a precheck error generator."""

        def generate_precheck_error(generator_args: ErrorGeneratorArgs):
            """Generate a precheck error."""
            field = generator_args.schema.record_type
            record = generator_args.record
            fields_json = self._generate_fields_json(generator_args.fields)
            values_json = self._generate_values_json(generator_args.fields, record)
            return ParserError(
                file=self.datafile,
                row_number=row_number,
                column_number=getattr(field, "item", ""),
                item_number=getattr(field, "item", ""),
                field_name=getattr(field, "name", ""),
                rpt_month_year=getattr(record, "RPT_MONTH_YEAR", None),
                case_number=getattr(record, "CASE_NUMBER", None),
                error_message=generator_args.error_message,
                error_type=ParserErrorCategoryChoices.PRE_CHECK,
                content_type=None,
                object_id=None,
                fields_json=fields_json,
                values_json=values_json,
                deprecated=generator_args.deprecated,
            )

        return generate_precheck_error

    def create_generate_record_precheck_error(self, row_number):
        """Create a record precheck error generator."""

        def generate_record_precheck_error(generator_args: ErrorGeneratorArgs):
            """Generate a record precheck error."""
            field = generator_args.schema.record_type
            record = generator_args.record
            fields_json = self._generate_fields_json(generator_args.fields)
            values_json = self._generate_values_json(generator_args.fields, record)
            return ParserError(
                file=self.datafile,
                row_number=row_number,
                column_number=getattr(field, "item", ""),
                item_number=getattr(field, "item", ""),
                field_name=getattr(field, "name", ""),
                rpt_month_year=getattr(record, "RPT_MONTH_YEAR", None),
                case_number=getattr(record, "CASE_NUMBER", None),
                error_message=generator_args.error_message,
                error_type=ParserErrorCategoryChoices.RECORD_PRE_CHECK,
                content_type=None,
                object_id=None,
                fields_json=fields_json,
                values_json=values_json,
                deprecated=generator_args.deprecated,
            )

        return generate_record_precheck_error

    def create_generate_field_value_error(self, row_number):
        """Create a field value error generator."""

        def generate_field_value_error(generator_args: ErrorGeneratorArgs):
            """Generate a field value error."""
            field = generator_args.offending_field
            record = generator_args.record
            fields_json = self._generate_fields_json([field])
            values_json = self._generate_values_json([field], record)
            return ParserError(
                file=self.datafile,
                row_number=row_number,
                column_number=getattr(field, "item", ""),
                item_number=getattr(field, "item", ""),
                field_name=getattr(field, "name", ""),
                rpt_month_year=getattr(record, "RPT_MONTH_YEAR", None),
                case_number=getattr(record, "CASE_NUMBER", None),
                error_message=generator_args.error_message,
                error_type=ParserErrorCategoryChoices.FIELD_VALUE,
                content_type=ContentType.objects.get_for_model(
                    model=generator_args.schema.model
                ),
                object_id=record.id,
                fields_json=fields_json,
                values_json=values_json,
                deprecated=generator_args.deprecated,
            )

        return generate_field_value_error

    def create_generate_header_field_value_error(self, row_number):
        """Create a field value error generator."""

        def generate_header_field_value_error(generator_args: ErrorGeneratorArgs):
            """Generate a field value error."""
            field = generator_args.offending_field
            record = generator_args.record
            fields_json = self._generate_fields_json([field])
            values_json = self._generate_values_json([field], record)
            return ParserError(
                file=self.datafile,
                row_number=row_number,
                column_number=getattr(field, "item", ""),
                item_number=getattr(field, "item", ""),
                field_name=getattr(field, "name", ""),
                rpt_month_year=getattr(record, "RPT_MONTH_YEAR", None),
                case_number=getattr(record, "CASE_NUMBER", None),
                error_message=generator_args.error_message,
                error_type=ParserErrorCategoryChoices.FIELD_VALUE,
                fields_json=fields_json,
                values_json=values_json,
                deprecated=generator_args.deprecated,
            )

        return generate_header_field_value_error

    def create_generate_value_consistency_error(self, row_number):
        """Create a value consistency error generator."""

        def generate_value_consistency_error(generator_args: ErrorGeneratorArgs):
            """Generate a value consistency error."""
            field = generator_args.fields[-1]
            record = generator_args.record
            fields_json = self._generate_fields_json(generator_args.fields)
            values_json = self._generate_values_json(generator_args.fields, record)
            return ParserError(
                file=self.datafile,
                row_number=row_number,
                column_number=getattr(field, "item", ""),
                item_number=getattr(field, "item", ""),
                field_name=getattr(field, "name", ""),
                rpt_month_year=getattr(record, "RPT_MONTH_YEAR", None),
                case_number=getattr(record, "CASE_NUMBER", None),
                error_message=generator_args.error_message,
                error_type=ParserErrorCategoryChoices.VALUE_CONSISTENCY,
                content_type=ContentType.objects.get_for_model(
                    model=generator_args.schema.model
                ),
                object_id=record.id,
                fields_json=fields_json,
                values_json=values_json,
                deprecated=generator_args.deprecated,
            )

        return generate_value_consistency_error

    def create_generate_fra_parser_error(self, row_number):
        """Create a FRA parser error generator."""

        def generate_fra_parser_error(generator_args: ErrorGeneratorArgs):
            """Generate a FRA parser error."""
            field = generator_args.offending_field
            record = generator_args.record
            fields_json = self._generate_fields_json([field])
            values_json = self._generate_values_json(generator_args.fields, record)
            return ParserError(
                file=self.datafile,
                row_number=row_number,
                column_number=getattr(field, "item", ""),
                item_number=getattr(field, "item", ""),
                field_name=getattr(field, "name", ""),
                rpt_month_year=getattr(record, "RPT_MONTH_YEAR", None),
                case_number=getattr(record, "CASE_NUMBER", None),
                error_message=generator_args.error_message,
                error_type=ParserErrorCategoryChoices.CASE_CONSISTENCY,
                content_type=None,
                object_id=None,
                fields_json=fields_json,
                values_json=values_json,
                deprecated=generator_args.deprecated,
            )

        return generate_fra_parser_error

    def create_generate_message_only_precheck_error(self, row_number):
        """Create a message only precheck error generator."""

        def generate_message_only_precheck_error(generator_args: ErrorGeneratorArgs):
            """Generate a no records precheck error."""
            return ParserError(
                file=self.datafile,
                row_number=row_number,
                column_number="",
                item_number="",
                field_name="",
                rpt_month_year=None,
                case_number=None,
                error_message=generator_args.error_message,
                error_type=ParserErrorCategoryChoices.PRE_CHECK,
                content_type=None,
                object_id=None,
                fields_json={},
                values_json={},
                deprecated=generator_args.deprecated,
            )

        return generate_message_only_precheck_error

    def create_generate_message_only_record_precheck_error(self, row_number):
        """Create a message only record precheck error generator."""

        def generate_message_only_record_precheck_error(
            generator_args: ErrorGeneratorArgs,
        ):
            """Generate a no records precheck error."""
            return ParserError(
                file=self.datafile,
                row_number=row_number,
                column_number="",
                item_number="",
                field_name="",
                rpt_month_year=None,
                case_number=None,
                error_message=generator_args.error_message,
                error_type=ParserErrorCategoryChoices.RECORD_PRE_CHECK,
                content_type=None,
                object_id=None,
                fields_json={},
                values_json={},
                deprecated=generator_args.deprecated,
            )

        return generate_message_only_record_precheck_error

    def create_generate_dynamic_row_case_consistency_error(self):
        """Create a case consistency error generator."""

        def generate_dynamic_row_case_consistency_error(
            generator_args: ErrorGeneratorArgs,
        ):
            field = generator_args.schema.record_type
            record = generator_args.record
            fields_json = self._generate_fields_json(generator_args.fields)
            values_json = self._generate_values_json(generator_args.fields, record)
            return ParserError(
                file=self.datafile,
                row_number=generator_args.row_number,
                column_number=getattr(field, "item", ""),
                item_number=getattr(field, "item", ""),
                field_name=getattr(field, "name", ""),
                rpt_month_year=getattr(record, "RPT_MONTH_YEAR", None),
                case_number=getattr(record, "CASE_NUMBER", None),
                error_message=generator_args.error_message,
                error_type=ParserErrorCategoryChoices.CASE_CONSISTENCY,
                content_type=None,
                object_id=None,
                fields_json=fields_json,
                values_json=values_json,
                deprecated=generator_args.deprecated,
            )

        return generate_dynamic_row_case_consistency_error
