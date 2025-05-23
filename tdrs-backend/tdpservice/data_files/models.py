"""Define data file models."""
import logging
import os
from hashlib import sha256
from io import StringIO
from typing import Union

from django.conf import settings
from django.contrib.admin.models import ADDITION, ContentType, LogEntry
from django.core.files.base import File
from django.db import models
from django.db.models import Max
from django.utils.html import format_html

from tdpservice.backends import DataFilesS3Storage
from tdpservice.stts.models import STT
from tdpservice.users.models import User

logger = logging.getLogger(__name__)


def get_file_shasum(file: Union[File, StringIO]) -> str:
    """Derive the SHA256 checksum of a file."""
    _hash = sha256()

    # If the file has the `open` method it needs to be called, otherwise this
    # input is a file-like object (ie. StringIO) and doesn't need to be opened.
    if hasattr(file, 'open'):
        f = file.open('rb')
    else:
        f = file

    # For large files we need to read it in by chunks to prevent invalid hashes
    if hasattr(f, 'multiple_chunks') and f.multiple_chunks():
        for chunk in f.chunks():
            _hash.update(chunk)
    else:
        content = f.read()

        # If the content is returned as a string we must encode it to bytes
        # or an error will be raised.
        if isinstance(content, str):
            content = content.encode('utf-8')

        _hash.update(content)

    # Ensure to reset the file so it can be read in further operations.
    f.seek(0)

    return _hash.hexdigest()

def get_s3_upload_path(instance, filename):
    """Produce a unique upload path for S3 files for a given STT and Quarter."""
    return os.path.join(
        f'data_files/{instance.year}/{instance.quarter}/{instance.stt.id}/{instance.section}/',
        filename
    )


# The Data File model was starting to explode, and I think that keeping this logic
# in its own abstract class is better for documentation purposes.
class FileRecord(models.Model):
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

class ReparseFileMeta(models.Model):
    """Meta data model representing a single file parse within a reparse execution."""

    data_file = models.ForeignKey('data_files.DataFile', on_delete=models.CASCADE, related_name='reparse_file_metas')
    reparse_meta = models.ForeignKey(
        'search_indexes.ReparseMeta',
        on_delete=models.CASCADE,
        related_name='reparse_file_metas'
    )

    finished = models.BooleanField(default=False)
    success = models.BooleanField(default=False)
    started_at = models.DateTimeField(auto_now_add=False, null=True)
    finished_at = models.DateTimeField(auto_now_add=False, null=True)

    num_records_created = models.PositiveIntegerField(default=0)
    cat_4_errors_generated = models.PositiveIntegerField(default=0)


class DataFile(FileRecord):
    """Represents a version of a data file."""

    class Section(models.TextChoices):
        """Enum for data file section."""

        TRIBAL_CLOSED_CASE_DATA = 'Tribal Closed Case Data'
        TRIBAL_ACTIVE_CASE_DATA = 'Tribal Active Case Data'
        TRIBAL_AGGREGATE_DATA = 'Tribal Aggregate Data'
        TRIBAL_STRATUM_DATA = 'Tribal Stratum Data'

        SSP_AGGREGATE_DATA = 'SSP Aggregate Data'
        SSP_CLOSED_CASE_DATA = 'SSP Closed Case Data'
        SSP_ACTIVE_CASE_DATA = 'SSP Active Case Data'
        SSP_STRATUM_DATA = 'SSP Stratum Data'

        ACTIVE_CASE_DATA = "Active Case Data"
        CLOSED_CASE_DATA = "Closed Case Data"
        AGGREGATE_DATA = "Aggregate Data"
        STRATUM_DATA = "Stratum Data"

        FRA_WORK_OUTCOME_TANF_EXITERS = "Work Outcomes of TANF Exiters"
        FRA_SECONDRY_SCHOOL_ATTAINMENT = "Secondary School Attainment"
        FRA_SUPPLEMENT_WORK_OUTCOMES = "Supplemental Work Outcomes"

        @classmethod
        def is_fra(cls, section: str) -> bool:
            """Determine if the section is a FRA section."""
            return section in [
                cls.FRA_WORK_OUTCOME_TANF_EXITERS,
                cls.FRA_SECONDRY_SCHOOL_ATTAINMENT,
                cls.FRA_SUPPLEMENT_WORK_OUTCOMES
            ]

        @classmethod
        def is_ssp(cls, section: str) -> bool:
            """Determine if the section is an SSP section."""
            return section in [
                cls.SSP_AGGREGATE_DATA,
                cls.SSP_ACTIVE_CASE_DATA,
                cls.SSP_CLOSED_CASE_DATA,
                cls.SSP_STRATUM_DATA
            ]

        @classmethod
        def is_tribal(cls, section: str) -> bool:
            """Determine if the section is a Tribal section."""
            return section in [
                cls.TRIBAL_AGGREGATE_DATA,
                cls.TRIBAL_ACTIVE_CASE_DATA,
                cls.TRIBAL_CLOSED_CASE_DATA,
                cls.TRIBAL_STRATUM_DATA
            ]

        @classmethod
        def is_tanf(cls, section: str) -> bool:
            """Determine if the section is a TANF section."""
            return section in [
                cls.ACTIVE_CASE_DATA,
                cls.CLOSED_CASE_DATA,
                cls.AGGREGATE_DATA,
                cls.STRATUM_DATA
            ]

    @staticmethod
    def get_fra_section_list():
        """Return FRA section list."""
        return [
                DataFile.Section.FRA_WORK_OUTCOME_TANF_EXITERS,
                DataFile.Section.FRA_SECONDRY_SCHOOL_ATTAINMENT,
                DataFile.Section.FRA_SUPPLEMENT_WORK_OUTCOMES
            ]

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

    s3_versioning_id = models.CharField(max_length=1024,
                                        blank=False,
                                        null=True
                                        )

    reparses = models.ManyToManyField(
        "search_indexes.ReparseMeta",
        through="data_files.ReparseFileMeta",
        help_text="Reparse events this file has been associated with.",
        related_name="files"
    )

    @property
    def prog_type(self):
        """Return the program type for a given section."""
        # e.g., 'SSP Closed Case Data'
        if self.Section.is_ssp(self.section):
            return 'SSP'
        elif self.Section.is_fra(self.section):
            return 'FRA'
        else:
            return 'TAN'

    @property
    def filename(self):
        """Return the correct filename for this data file."""
        return self.stt.filenames.get(self.section, None)

    @property
    def s3_location(self):
        """Return the S3 file location."""
        location = None
        if self.file:
            location = self.file.name
        return location

    @property
    def fiscal_year(self):
        """Return a string representation of the data file's fiscal year."""
        quarter_month_str = ""

        match self.quarter:
            case DataFile.Quarter.Q1:
                quarter_month_str = "(Oct - Dec)"
            case DataFile.Quarter.Q2:
                quarter_month_str = "(Jan - Mar)"
            case DataFile.Quarter.Q3:
                quarter_month_str = "(Apr - Jun)"
            case DataFile.Quarter.Q4:
                quarter_month_str = "(Jul - Sep)"

        return f"{self.year} - {self.quarter} {quarter_month_str}"

    @property
    def submitted_by(self):
        """Return the author as a string for this data file."""
        return self.user.get_full_name()

    @property
    def log_file(self):
        """Generate S3 path for the log file."""
        datafile = self
        if not datafile:
            return None
        LOG_PRE_FIX = "v1/data_files/logs"
        DOMAIN = settings.FRONTEND_BASE_URL
        if datafile:
            link = f"{LOG_PRE_FIX}/{datafile.year}/{datafile.quarter}/" \
                  f"{datafile.stt}/{datafile.section}"
            url = f"{DOMAIN}/{link}"  # Replace with your actual S3 URL
            return format_html("<a href='{url}'>{field}</a>",
                               field="Parser logs",
                               url=url)
        else:
            return None

    def admin_link(self):
        """Return a link to the admin console for this file."""
        return f"{settings.FRONTEND_BASE_URL}/admin/data_files/datafile/?id={self.pk}"

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

    def __repr__(self):
        """Return a string representation of the model."""
        return f"{{id: {self.id}, filename: {self.original_filename}, STT: {self.stt}, S3 location: " + \
               f"{self.s3_location}}}"

    def __str__(self):
        """Return a string representation of the model."""
        return f"filename: {self.original_filename}"

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
            # Was their an expectation here? THis wasn't ever defined.
            # Probbly pseudo code.
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
