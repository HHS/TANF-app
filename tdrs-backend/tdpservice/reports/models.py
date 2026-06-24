"""Define report models."""

import os
import uuid

from django.db import models
from django.db.models import Max

from tdpservice.backends import DataFilesS3Storage
from tdpservice.common.models import FileRecord
from tdpservice.stts.models import STT
from tdpservice.users.models import User


class ReportType(models.TextChoices):
    """Report program type for feedback reports."""

    TANF_SSP = "TANF_SSP", "TANF/SSP"
    TRIBAL_TANF = "TRIBAL_TANF", "Tribal TANF"
    FRA = "FRA", "FRA"


def get_report_source_upload_path(instance, filename):
    """Produce a unique upload path for ReportSource files to S3."""
    return os.path.join(
        "reports",
        "source",
        f"{uuid.uuid4().hex}-{filename}",
    )


class ReportSource(FileRecord):
    """ReportSource is an intermediary model for submitting a zip file containing multiple zips to be parsed into ReportFile records."""

    class Status(models.TextChoices):
        """Whether or not a ReportSource record has been parsed into ReportFile records."""

        PENDING = "PENDING"
        PROCESSING = "PROCESSING"
        SUCCEEDED = "SUCCEEDED"
        FAILED = "FAILED"

    # Override FileRecord fields
    extension = models.CharField(max_length=8, default="zip")

    # Model Fields
    uploaded_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        related_name="report_sources",
        blank=False,
        null=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    processed_at = models.DateTimeField(null=True, blank=True)
    status = models.CharField(
        max_length=16, choices=Status.choices, default=Status.PENDING
    )
    date_extracted_on = models.DateField(null=True, blank=True)
    year = models.IntegerField(blank=True, null=True)
    report_type = models.CharField(
        max_length=16,
        choices=ReportType.choices,
        default=ReportType.TANF_SSP,
    )
    num_reports_created = models.PositiveIntegerField(default=0)
    error_message = models.TextField(null=True, blank=True)

    file = models.FileField(
        storage=DataFilesS3Storage,
        upload_to=get_report_source_upload_path,
        null=False,
        blank=False,
    )


def get_s3_upload_path(instance, filename):
    """Produce a unique upload path for ReportFile files to S3."""
    date_str = instance.date_extracted_on.strftime("%Y-%m-%d") if instance.date_extracted_on else "no-date"
    return os.path.join(
        f"reports/{instance.year}/{date_str}/{instance.stt.id}/{instance.report_type}/",
        filename,
    )


class ReportFile(FileRecord):
    """Represents a version of a report file."""

    class Meta:
        """Metadata."""

        constraints = [
            models.UniqueConstraint(
                fields=("version", "date_extracted_on", "year", "stt", "report_type"),
                name="unique_reports_reportfile_fields_v2",
            )
        ]

    # Override FileRecord fields
    extension = models.CharField(max_length=8, default="zip")

    # Model Fields
    created_at = models.DateTimeField(auto_now_add=True)
    date_extracted_on = models.DateField(null=True, blank=True)
    year = models.IntegerField()
    report_type = models.CharField(
        max_length=16,
        choices=ReportType.choices,
        default=ReportType.TANF_SSP,
    )

    version = models.IntegerField()

    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        related_name="report_files",
        blank=False,
        null=True,
    )
    stt = models.ForeignKey(
        STT,
        on_delete=models.SET_NULL,
        related_name="report_files",
        blank=False,
        null=True,
    )
    source = models.ForeignKey(
        ReportSource,
        on_delete=models.SET_NULL,
        related_name="report_files",
        blank=True,
        null=True,
    )

    file = models.FileField(
        storage=DataFilesS3Storage, upload_to=get_s3_upload_path, null=True, blank=True
    )

    @classmethod
    def create_new_version(self, data):
        """Create a new version of a report with an incremented version."""
        # EDGE CASE
        # We may need to try to get this all in one sql query
        # if we ever encounter race conditions.
        version = (
            self.find_latest_version_number(
                year=data["year"],
                date_extracted_on=data["date_extracted_on"],
                stt=data["stt"],
                report_type=data.get("report_type", ReportType.TANF_SSP),
            )
            or 0
        ) + 1

        return ReportFile.objects.create(
            version=version,
            **data,
        )

    @classmethod
    def find_latest_version_number(self, year, date_extracted_on, stt, report_type=ReportType.TANF_SSP):
        """Locate the latest version number in a series of report files."""
        return self.objects.filter(
            stt=stt, year=year, date_extracted_on=date_extracted_on, report_type=report_type
        ).aggregate(Max("version"))["version__max"]

    @classmethod
    def find_latest_version(self, year, date_extracted_on, stt, report_type=ReportType.TANF_SSP):
        """Locate the latest version of a report."""
        version = self.find_latest_version_number(year, date_extracted_on, stt, report_type)

        return self.objects.filter(
            version=version,
            year=year,
            date_extracted_on=date_extracted_on,
            stt=stt,
            report_type=report_type,
        ).first()
