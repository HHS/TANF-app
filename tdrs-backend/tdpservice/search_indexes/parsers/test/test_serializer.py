"""Tests for the ParsingErrorSerializer."""
import pytest
from tdpservice.search_indexes.parsers.serializers import ParsingErrorSerializer
from tdpservice.search_indexes.parsers.test.factories import ParserErrorFactory
from rest_framework.request import HttpRequest

@pytest.fixture
def parser_error_instance():
    """Create a parser error instance."""
    return ParserErrorFactory.create()


@pytest.mark.django_db
def test_serializer_with_valid_data(parser_error_instance):
    """If a serializer has valid data it will return a valid object."""
    request_instance = HttpRequest()
    request_instance.query_params = {
        'fields': 'file, row_number, column_number, item_number, field_name,\
        category, error_message, error_type, created_at, fields_json, object_id, content_type_id'

    }
    serializer = ParsingErrorSerializer(
        parser_error_instance,
        data={},
        context={
            'request': request_instance
        },
        partial=True)
    assert serializer.is_valid() is True


@pytest.mark.django_db
def test_serializer_with_invalid_data(parser_error_instance):
    """If a serializer has invalid data it will return an invalid object."""
    request_instance = HttpRequest()
    request_instance.query_params = {
        'fields': 'file, row_number, column_number, item_number, field_name,\
        category, error_message, error_type, created_at, fields_json, object_id, content_type_id'

    }
    serializer = ParsingErrorSerializer(
        parser_error_instance,
        data={'row_number': 'row number'},
        context={
            'request': request_instance
        },
        partial=True)
    assert serializer.is_valid() is False


@pytest.mark.django_db
def test_serializer_with_no_context(parser_error_instance):
    """If a serializer has no context it will return an invalid object."""
    with pytest.raises(Exception) as e:
        ParsingErrorSerializer(
            parser_error_instance,
            data={},
            partial=True)
    print(e.value)
    assert str(e.value) == "'context'"
