"""Factories for generating test data for parsers."""
import factory
from tdpservice.data_files.test.factories import DataFileFactory

class ParserErrorFactory(factory.django.DjangoModelFactory):
    """Generate test data for parser errors."""

    class Meta:
        """Hardcoded meta data for parser errors."""

        model = "parsers.ParserError"

    file = factory.SubFactory(DataFileFactory)
    row_number = 1
    column_number = 1
    item_number = "1"
    field_name = "test field name"
    case_number = '1'
    rpt_month_year = 202001
    error_message = "test error message"
    error_type = "out of range"

    created_at = factory.Faker("date_time")
    fields_json = {"test": "test"}

    object_id = 1
    content_type_id = 1
