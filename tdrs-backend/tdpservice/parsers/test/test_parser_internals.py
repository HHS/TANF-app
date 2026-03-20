"""Unit tests for parser factory and schema manager internals."""

import pytest

from tdpservice.data_files.models import DataFile
from tdpservice.parsers.dataclasses import RawRow
from tdpservice.parsers.factory import ParserFactory
from tdpservice.parsers.fields import TransformField
from tdpservice.parsers.models import ParserErrorCategoryChoices
from tdpservice.parsers.parser_classes.base_parser import BaseParser
from tdpservice.parsers.parser_classes.fra_parser import FRAParser
from tdpservice.parsers.parser_classes.program_audit_parser import ProgramAuditParser
from tdpservice.parsers.parser_classes.tdr_parser import TanfDataReportParser
from tdpservice.parsers.schema_manager import SchemaManager


class TestParserFactory:
    """Tests for ParserFactory class selection and instantiation."""

    @pytest.mark.parametrize(
        "program_type, expected",
        [
            (DataFile.ProgramType.TANF, TanfDataReportParser),
            (DataFile.ProgramType.SSP, TanfDataReportParser),
            (DataFile.ProgramType.TRIBAL, TanfDataReportParser),
        ],
    )
    def test_get_class_tanf_like_programs(self, program_type, expected):
        """Return TANF parser for TANF/SSP/Tribal."""
        assert ParserFactory.get_class(program_type) is expected

    def test_get_class_program_audit(self):
        """Return ProgramAuditParser when program audit is requested."""
        assert (
            ParserFactory.get_class(
                DataFile.ProgramType.TANF, is_program_audit=True
            )
            is ProgramAuditParser
        )

    def test_get_class_fra(self):
        """Return FRAParser for FRA program type."""
        assert ParserFactory.get_class(DataFile.ProgramType.FRA) is FRAParser

    def test_get_class_unknown_raises(self):
        """Raise when no parser is available for program type."""
        with pytest.raises(ValueError, match="No parser available for program type"):
            ParserFactory.get_class("UNKNOWN")

    def test_get_instance_passes_kwargs(self, monkeypatch):
        """Ensure get_instance forwards kwargs and program metadata."""
        captured = {}

        class DummyParser:
            def __init__(self, **kwargs):
                self.kwargs = kwargs

        def fake_get_class(cls, program_type, is_program_audit=False):
            captured["program_type"] = program_type
            captured["is_program_audit"] = is_program_audit
            return DummyParser

        monkeypatch.setattr(ParserFactory, "get_class", classmethod(fake_get_class))

        instance = ParserFactory.get_instance(
            program_type=DataFile.ProgramType.TANF,
            is_program_audit=True,
            datafile="datafile",
            dfs="dfs",
            section="Active Case Data",
        )

        assert captured == {
            "program_type": DataFile.ProgramType.TANF,
            "is_program_audit": True,
        }
        assert instance.kwargs == {
            "datafile": "datafile",
            "dfs": "dfs",
            "section": "Active Case Data",
        }


class TestSchemaManager:
    """Tests for SchemaManager behavior."""

    @pytest.mark.django_db
    def test_parse_and_validate_unknown_record_type(self, small_correct_file):
        """Return record precheck error for unknown record type."""
        manager = SchemaManager(
            small_correct_file,
            small_correct_file.program_type,
            small_correct_file.section,
        )
        row = RawRow(
            data="Z9",
            raw_len=2,
            decoded_len=2,
            row_num=5,
            record_type="Z9",
        )

        result = manager.parse_and_validate(row)

        assert result.schemas == []
        assert len(result.records) == 1
        record, is_valid, errors = result.records[0]
        assert record is None
        assert is_valid is False
        assert len(errors) == 1
        assert errors[0].error_message == "Unknown Record_Type was found."
        assert errors[0].error_type == ParserErrorCategoryChoices.RECORD_PRE_CHECK

    @pytest.mark.django_db
    def test_update_encrypted_fields_updates_transform_fields(self, small_correct_file):
        """Update TransformField encryption flags across schemas."""
        manager = SchemaManager(
            small_correct_file,
            small_correct_file.program_type,
            small_correct_file.section,
        )

        transform_fields = []
        for schemas in manager.schema_map.values():
            for schema in schemas:
                for field in schema.fields:
                    if (
                        isinstance(field, TransformField)
                        and "is_encrypted" in field.kwargs
                    ):
                        transform_fields.append(field)

        assert transform_fields

        manager.update_encrypted_fields(True)

        assert all(field.kwargs["is_encrypted"] is True for field in transform_fields)


class DummyField:
    """Minimal field stand-in for duplicate message tests."""

    def __init__(self, name, item, friendly_name):
        """Store basic field metadata."""
        self.name = name
        self.item = item
        self.friendly_name = friendly_name


class DummySchema:
    """Minimal schema stand-in for duplicate message tests."""

    def __init__(self, fields):
        """Map fields by name for test helpers."""
        self._fields = {field.name: field for field in fields}

    def get_partial_dup_fields(self):
        """Return partial duplicate field names."""
        return list(self._fields.keys())

    def get_field_by_name(self, name):
        """Return field object by name."""
        return self._fields[name]


class DummyParser(BaseParser):
    """Parser stub to access BaseParser helpers."""

    def __init__(self):
        """No-op init for isolated BaseParser helper tests."""
        pass

    def parse_and_validate(self):
        """Implement required abstract method stub."""
        pass


class TestBaseParserMessages:
    """Tests for BaseParser duplicate message helpers."""

    def test_generate_exact_dup_error_msg(self):
        """Generate exact duplicate error message."""
        parser = DummyParser()
        msg = parser._generate_exact_dup_error_msg(None, "T1", 3, 2)
        assert (
            msg
            == "Duplicate record detected with record type T1 at line 3. "
            "Record is a duplicate of the record at line number 2."
        )

    def test_generate_partial_dup_error_msg_single_field(self):
        """Generate partial duplicate message for one field."""
        parser = DummyParser()
        schema = DummySchema([DummyField("case_number", 4, "Case Number")])

        msg = parser._generate_partial_dup_error_msg(schema, "T1", 3, 2)

        assert "Partial duplicate record detected with record type T1 at line 3." in msg
        assert msg.endswith("Item 4 (Case Number).")

    def test_generate_partial_dup_error_msg_multiple_fields(self):
        """Generate partial duplicate message for multiple fields."""
        parser = DummyParser()
        schema = DummySchema(
            [
                DummyField("case_number", 4, "Case Number"),
                DummyField("rpt_month_year", 5, "Reporting Month Year"),
            ]
        )

        msg = parser._generate_partial_dup_error_msg(schema, "T1", 3, 2)

        assert "Duplicated fields causing error:" in msg
        assert "Item 4 (Case Number), and Item 5 (Reporting Month Year)." in msg
