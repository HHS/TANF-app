"""Generate test data for Report files."""

import uuid
import factory

from tdpservice.reports.models import ReportIngest
from tdpservice.stts.test.factories import STTFactory
from tdpservice.users.test.factories import UserFactory


class ReportFileFactory(factory.django.DjangoModelFactory):
    """Factory to generate ReportFile instances."""

    class Meta:
        """Metadata."""

        model = "reports.ReportFile"

    original_filename = "report.zip"
    slug = "report.zip"
    extension = "zip"
    quarter = "Q1"
    year = 2024
    version = 1

    user = factory.SubFactory(UserFactory)
    stt = factory.SubFactory(STTFactory)

    file = factory.django.FileField(
        filename="my-report.zip", data=b"PK\x03\x04fakezipcontent"
    )


class ReportIngestFactory(factory.django.DjangoModelFactory):
    """Factory to generate ReportIngest instances."""

    class Meta:
        """Metadata."""

        model = "reports.ReportIngest"

    uploaded_by = factory.SubFactory(UserFactory)
    original_filename = "master_bundle.zip"
    s3_key = factory.LazyAttribute(lambda _: f"reports/master/{uuid.uuid4()}.zip")
    status = ReportIngest.Status.PENDING
    num_reports_created = 0
    error_message = ""
