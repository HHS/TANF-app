"""Define report models."""

import os

from django.db import models
from django.db.models import Max

from tdpservice.backends import DataFilesS3Storage
from tdpservice.common.models import FileRecord
from tdpservice.stts.models import STT
from tdpservice.users.models import User


def get_s3_upload_path(instance, filename):
    """Produce a unique upload path for S3 files for a given STT and Quarter."""
    return os.path.join(
        f"reports/{instance.year}/{instance.quarter}/{instance.stt.id}/",
        filename,
    )


class ReportFile(FileRecord):
    """Represents a version of a report file."""

    class Quarter(models.TextChoices):
        """Enum for report Quarter."""

        Q1 = "Q1"
        Q2 = "Q2"
        Q3 = "Q3"
        Q4 = "Q4"

    class Meta:
        """Metadata."""

        constraints = [
            models.UniqueConstraint(
                fields=("version", "quarter", "year", "stt"),
                name="unique_reports_reportfile_fields",
            )
        ]

    created_at = models.DateTimeField(auto_now_add=True)
    quarter = models.CharField(
        max_length=16, blank=False, null=False, choices=Quarter.choices
    )
    year = models.IntegerField()

    version = models.IntegerField()

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="report_files",
        blank=False,
        null=False,
    )
    stt = models.ForeignKey(
        STT,
        on_delete=models.CASCADE,
        related_name="report_files",
        blank=False,
        null=False,
    )

    # NOTE: `file` is only temporarily nullable until we complete the issue:
    # https://github.com/raft-tech/TANF-app/issues/755
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
                quarter=data["quarter"],
                stt=data["stt"],
            )
            or 0
        ) + 1

        return ReportFile.objects.create(
            version=version,
            **data,
        )

    @classmethod
    def find_latest_version_number(self, year, quarter, stt):
        """Locate the latest version number in a series of report files."""
        return self.objects.filter(
            stt=stt, year=year, quarter=quarter
        ).aggregate(Max("version"))["version__max"]

    @classmethod
    def find_latest_version(self, year, quarter, stt):
        """Locate the latest version of a report."""
        version = self.find_latest_version_number(year, quarter, stt)

        return self.objects.filter(
            version=version,
            year=year,
            quarter=quarter,
            stt=stt,
        ).first()


class ReportIngest(models.Model):
    """ReportIngest is an intermediary model for submitting a zip file containing multiple zips to be parsed into ReportFile records."""

    class Status(models.TextChoices):
        """Whether or not a ReportIngest record has been parsed into ReportFile records."""

        PENDING = "PENDING"
        PROCESSING = "PROCESSING"
        SUCCEEDED = "SUCCEEDED"
        FAILED = "FAILED"

    uploaded_by = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="report_ingests"
    )
    original_filename = models.CharField(max_length=256)
    s3_key = models.CharField(max_length=1024)  # where the master zip lives
    created_at = models.DateTimeField(auto_now_add=True)
    processed_at = models.DateTimeField(null=True, blank=True)
    status = models.CharField(
        max_length=16, choices=Status.choices, default=Status.PENDING
    )
    num_reports_created = models.PositiveIntegerField(default=0)
    error_message = models.TextField(null=True, blank=True)
