"""Define data file models."""
import os

from django.db import models
from django.db.models import Max
from io import StringIO
from typing import Union
import logging
from django.contrib.admin.models import ContentType, LogEntry, ADDITION
from django.core.files.base import File
from django.db import models

from tdpservice.backends import DataFilesS3Storage
from tdpservice.stts.models import STT
from tdpservice.users.models import User


logger = logging.getLogger(__name__)

def get_s3_upload_path(instance, filename):
    """Produce a unique upload path for S3 files for a given STT and Quarter."""
    return os.path.join(
        f'data_files/{instance.stt.id}/{instance.quarter}',
        filename
    )


# The Data File model was starting to explode, and I think that keeping this logic
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


class DataFile(File):
    """Represents a version of a data file."""

    class Section(models.TextChoices):
        """Enum for data file section."""

        ACTIVE_CASE_DATA = "Active Case Data"
        CLOSED_CASE_DATA = "Closed Case Data"
        AGGREGATE_DATA = "Aggregate Data"
        STRATUM_DATA = "Stratum Data"

    class Quarter(models.TextChoices):
        """Enum for data file Quarter."""

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

    def create_filename(self, prefix='ADS.E2J'):
        STT_TYPES = ["state", "territory", "tribe"]
        SECTION = [i.value for i in list(self.Section)]
        #str(STT_TYPES.index(self.stt.type)+1)
        return ''.join(prefix+'.FTP'+str(SECTION.index(self.section))+'.TS' + self.stt.code)

    @classmethod
    def create_new_version(self, data):
        """Create a new version of a data file with an incremented version."""
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

        return DataFile.objects.create(version=version, **data,)

    @classmethod
    def find_latest_version_number(self, year, quarter, section, stt):
        """Locate the latest version number in a series of data files."""
        return self.objects.filter(
            stt=stt, year=year, quarter=quarter, section=section
        ).aggregate(Max("version"))["version__max"]

    @classmethod
    def find_latest_version(self, year, quarter, section, stt):
        """Locate the latest version of a data file."""
        version = self.find_latest_version_number(year, quarter, section, stt)

        return self.objects.filter(
            version=version, year=year, quarter=quarter, section=section, stt=stt,
        ).first()

class LegacyFileTransferManager(models.Manager):
    """Extends object manager functionality for LegacyFileTransfer model."""

    def record_scan(
        self,
        file: Union[File, StringIO],
        file_name: str,
        msg: str,
        result: 'LegacyFileTransfer.Result',
        uploaded_by: User
    ) -> 'LegacyFileTransfer':
        """Create a new LegacyFileTransfer instance with associated LogEntry."""
        try:
            file_shasum = get_file_shasum(file)
        except (AttributeError, TypeError, ValueError) as err:
            logger.error(f'Encountered error deriving file hash: {err}')
            file_shasum = 'INVALID'

        # Create the LegacyFileTransfer instance.
        fileTransfer = self.model.objects.create(
            file_name=file_name,
            file_size=(
                file.size
                if isinstance(file, File)
                else len(file.getvalue())
            ),
            file_shasum=file_shasum,
            result=result,
            uploaded_by=uploaded_by
        )

        # Create a new LogEntry that is tied to this model instance.
        content_type = ContentType.objects.get_for_model(LegacyFileTransfer)
        LogEntry.objects.log_action(
            user_id=uploaded_by.pk,
            content_type_id=content_type.pk,
            object_id=fileTransfer.pk,
            object_repr=str(fileTransfer),
            action_flag=ADDITION,
            change_message=msg
        )

        return fileTransfer


class LegacyFileTransfer(models.Model):
    """Represents a file transferred to ACF Titan for an uploaded file."""

    class Meta:
        """Model Meta options."""

        verbose_name = 'Legacy File Transfer'

    class Result(models.TextChoices):
        """Represents the possible results from a completed transfer."""

        COMPLETED = 'COMPLETED'
        ERROR = 'ERROR'

    sent_at = models.DateTimeField(auto_now_add=True)
    file_name = models.TextField()
    file_size = models.PositiveBigIntegerField(
        help_text='The file size in bytes'
    )
    file_shasum = models.TextField(
        help_text='The SHA256 checksum of the uploaded file'
    )
    result = models.CharField(
        choices=Result.choices,
        help_text='Transfer result for uploaded file',
        max_length=12
    )
    uploaded_by = models.ForeignKey(
        User,
        help_text='The user that uploaded the data file',
        null=True,
        on_delete=models.SET_NULL,
        related_name='fileTransfer'
    )

    data_file = models.ForeignKey(
        DataFile,
        blank=True,
        help_text='The resulting DataFile object, if this transfer was completed',
        null=True,
        on_delete=models.SET_NULL,
        related_name='fileTransfer'
    )

    objects = LegacyFileTransferManager()

    def __str__(self) -> str:
        """Return string representation of model instance."""
        return f'{self.file_name} ({self.file_size_humanized}) - {self.result}'

    @property
    def file_size_humanized(self) -> str:
        """Convert the file size into the largest human-readable unit."""
        size = self.file_size
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size < 1024.0:
                break
            size /= 1024.0

        return f'{size:.{2}f}{unit}'
