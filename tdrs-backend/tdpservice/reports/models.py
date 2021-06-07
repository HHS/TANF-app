"""Define report models."""
import os

from django.conf import settings
from django.db import models
from django.db.models import Max
from storages.backends.s3boto3 import S3Boto3Storage

from tdpservice.stts.models import STT
from tdpservice.users.models import User


def get_s3_upload_path(instance, filename):
    """Produce a unique upload path for S3 files for a given STT and Quarter."""
    return os.path.join(
        f'data_files/{instance.stt.id}/{instance.quarter}',
        filename
    )


class DataFilesS3Storage(S3Boto3Storage):
    """An S3 backed storage provider for user uploaded Data Files.

    This class is used instead of the built-in to allow specifying a distinct
    bucket from the one used to store Django Admin static files.
    """

    bucket_name = settings.DATA_FILES_AWS_STORAGE_BUCKET_NAME


# The Report File model was starting to explode, and I think that keeping this logic
# in its own abstract class is better for documentation purposes.
class File(models.Model):
    """Abstract type representing a file stored in S3."""

    class Meta:
        """Metadata."""

        abstract = True
    # Keep the file name because it will be different in s3,
    # but the interface will still want to present the file with its
    # original name.
    original_filename = models.CharField(max_length=256,
                                         blank=False,
                                         null=False)
    # Slug is the name of the file in S3
    # NOTE: Currently unused, may be removed with a later release
    slug = models.CharField(max_length=256, blank=False, null=False)
    # Not all files will have the correct extension,
    # or even have one at all. The UI will provide this information
    # separately
    extension = models.CharField(max_length=8, default="txt")


class ReportFile(File):
    """Represents a version of a report file."""

    class Section(models.TextChoices):
        """Enum for report section."""

        ACTIVE_CASE_DATA = "Active Case Data"
        CLOSED_CASE_DATA = "Closed Case Data"
        AGGREGATE_DATA = "Aggregate Data"
        STRATUM_DATA = "Stratum Data"

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
                fields=("section", "version", "quarter", "year", "stt"),
                name="constraint_name",
            )
        ]

    created_at = models.DateTimeField(auto_now_add=True)
    quarter = models.CharField(max_length=16,
                               blank=False,
                               null=False,
                               choices=Quarter.choices)
    year = models.IntegerField()
    section = models.CharField(max_length=32,
                               blank=False,
                               null=False,
                               choices=Section.choices)

    version = models.IntegerField()

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="user", blank=False, null=False
    )
    stt = models.ForeignKey(
        STT, on_delete=models.CASCADE, related_name="sttRef", blank=False, null=False
    )

    # NOTE: `file` is only temporarily nullable until we complete the issue:
    # https://github.com/raft-tech/TANF-app/issues/755
    file = models.FileField(
        storage=DataFilesS3Storage,
        upload_to=get_s3_upload_path,
        null=True,
        blank=True
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
                section=data["section"],
                stt=data["stt"],
            )
            or 0
        ) + 1

        return ReportFile.objects.create(version=version, **data,)

    @classmethod
    def find_latest_version_number(self, year, quarter, section, stt):
        """Locate the latest version number in a series of report files."""
        return self.objects.filter(
            stt=stt, year=year, quarter=quarter, section=section
        ).aggregate(Max("version"))["version__max"]

    @classmethod
    def find_latest_version(self, year, quarter, section, stt):
        """Locate the latest version of a report."""
        version = self.find_latest_version_number(year, quarter, section, stt)

        return self.objects.filter(
            version=version, year=year, quarter=quarter, section=section, stt=stt,
        ).first()
