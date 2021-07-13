"""Generate test data for Report files."""
import factory

from tdpservice.users.test.factories import UserFactory
from tdpservice.stts.test.factories import STTFactory


class ReportFileFactory(factory.django.DjangoModelFactory):
    """Generate test data for report files."""

    class Meta:
        """Hardcoded meta data for report files."""

        model = "reports.ReportFile"

    original_filename = "report.txt"
    slug = "report-txt-slug"
    extension = "txt"
    section = "Active Case Data"
    quarter = "Q1"
    year = "2020"
    version = 1
    user = factory.SubFactory(UserFactory)
    stt = factory.SubFactory(STTFactory)
    file = factory.django.FileField(data=b'test', filename='my_data_file.txt')
