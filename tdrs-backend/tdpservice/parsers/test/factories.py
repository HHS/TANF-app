"""Factories for generating test data for parsers."""
import factory

from tdpservice.parsers.models import DataFileSummary, ParserErrorCategoryChoices
from tdpservice.data_files.test.factories import DataFileFactory
from tdpservice.users.test.factories import UserFactory
from tdpservice.stts.test.factories import STTFactory

class ParsingFileFactory(factory.django.DjangoModelFactory):
    """Generate test data for data files."""

    class Meta:
        """Hardcoded meta data for data files."""

        model = "data_files.DataFile"

    original_filename = "data_file.txt"
    slug = "data_file-txt-slug"
    extension = "txt"
    section = "Active Case Data"
    quarter = "Q1"
    year = "2020"
    version = 1
    user = factory.SubFactory(UserFactory)
    stt = factory.SubFactory(STTFactory)
    file = factory.django.FileField(data=b'test', filename='my_data_file.txt')
    s3_versioning_id = 0

class DataFileSummaryFactory(factory.django.DjangoModelFactory):
    """Generate test data for data files."""

    class Meta:
        """Hardcoded meta data for data files."""

        model = DataFileSummary

    status = DataFileSummary.Status.PENDING

    case_aggregates = {
        "rejected": 0,
        "months": [
            {
                "accepted_without_errors": 100,
                "accepted_with_errors": 10,
                "month": "Jan",
            },
            {
                "accepted_without_errors": 100,
                "accepted_with_errors": 10,
                "month": "Feb",
            },
            {
                "accepted_without_errors": 100,
                "accepted_with_errors": 10,
                "month": "Mar",
            },
        ]
    }

    datafile = factory.SubFactory(DataFileFactory)


class ParserErrorFactory(factory.django.DjangoModelFactory):
    """Generate test data for parser errors."""

    class Meta:
        """Hardcoded meta data for parser errors."""

        model = "parsers.ParserError"

    file = factory.SubFactory(DataFileFactory)
    row_number = 1
    column_number = "1"
    item_number = "1"
    field_name = "test field name"
    case_number = '1'
    rpt_month_year = 202001
    error_message = "test error message"
    error_type = ParserErrorCategoryChoices.PRE_CHECK

    created_at = factory.Faker("date_time")
    fields_json = {"test": "test"}

    object_id = 1
    content_type_id = 1
