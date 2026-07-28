"""Generate test data for Report files."""

import datetime
import uuid
import factory

from tdpservice.reports.models import ReportSource, ReportType
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
    date_extracted_on = datetime.date(2024, 2, 28)
    year = 2024
    report_type = ReportType.TANF_SSP
    version = 1

    user = factory.SubFactory(UserFactory)
    stt = factory.SubFactory(STTFactory)

    file = factory.django.FileField(
        filename="my-report.zip", data=b"PK\x03\x04fakezipcontent"
    )


class FRAReportFileFactory(ReportFileFactory):
    """Factory to generate FRA ReportFile instances."""

    report_type = ReportType.FRA


class TribalTANFReportFileFactory(ReportFileFactory):
    """Factory to generate Tribal TANF ReportFile instances."""

    report_type = ReportType.TRIBAL_TANF


class ReportSourceFactory(factory.django.DjangoModelFactory):
    """Factory to generate ReportSource instances."""

    class Meta:
        """Metadata."""

        model = "reports.ReportSource"

    uploaded_by = factory.SubFactory(UserFactory)
    original_filename = "report_source.zip"
    slug = factory.LazyAttribute(lambda _: f"reports/source/{uuid.uuid4()}.zip")
    status = ReportSource.Status.PENDING
    date_extracted_on = datetime.date(2024, 2, 28)
    year = 2024
    report_type = ReportType.TANF_SSP
    num_reports_created = 0
    error_message = ""


class FRAReportSourceFactory(ReportSourceFactory):
    """Factory to generate FRA ReportSource instances."""

    report_type = ReportType.FRA


class TribalTANFReportSourceFactory(ReportSourceFactory):
    """Factory to generate Tribal TANF ReportSource instances."""

    report_type = ReportType.TRIBAL_TANF
