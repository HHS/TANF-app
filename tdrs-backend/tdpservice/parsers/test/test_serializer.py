"""Tests for the ParsingErrorSerializer."""
import pytest
from rest_framework.request import HttpRequest

from tdpservice.parsers.serializers import ParsingErrorSerializer
from tdpservice.parsers.test.factories import ParserErrorFactory


class TestParsingErrorSerializer:
    """Tests for parsing error serializer."""

    @pytest.fixture
    def parser_error_instance(self):
        """Create a parser error instance."""
        return ParserErrorFactory.create()

    @pytest.mark.django_db
    @pytest.mark.parametrize(
        "fields,data,expected",
        [
            (
                "file, row_number, column_number, item_number, field_name, "
                "category, error_message, error_type, created_at, fields_json, "
                "object_id, case_number, rpt_month_year, content_type_id",
                {},
                True,
            ),
            (
                "file, row_number, column_number, item_number, field_name, "
                "category, error_message, error_type, created_at, fields_json, "
                "object_id, content_type_id",
                {"row_number": "row number"},
                False,
            ),
        ],
    )
    def test_serializer_is_valid(self, parser_error_instance, fields, data, expected):
        """Test serializer validity for positive and negative cases."""
        request_instance = HttpRequest()
        request_instance.query_params = {"fields": fields}
        serializer = ParsingErrorSerializer(
            parser_error_instance,
            data=data,
            context={"request": request_instance},
            partial=True,
        )
        assert serializer.is_valid() is expected

    @pytest.mark.django_db
    def test_serializer_with_no_context(self, parser_error_instance):
        """If a serializer has no context it will return an invalid object."""
        with pytest.raises(Exception) as e:
            ParsingErrorSerializer(parser_error_instance, data={}, partial=True)
        assert str(e.value) == "'context'"
