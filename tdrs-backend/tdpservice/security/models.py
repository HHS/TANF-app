"""Models for the tdpservice.security app."""
from hashlib import sha256
from io import StringIO
from os.path import join
from typing import Union
import logging

from django.contrib.admin.models import ContentType, LogEntry, ADDITION
from django.core.files.base import File
from django.db import models
from django.utils.timezone import now

from tdpservice.backends import DataFilesS3Storage
from tdpservice.data_files.models import DataFile
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


def get_zap_s3_upload_path(instance, _):
    """Produce a unique upload path for ZAP reports stored in S3."""
    return join(
        f'owasp_reports/{instance.scanned_at.date()}/{instance.app_target}',
        'owasp_report.html'
    )


class ClamAVFileScanManager(models.Manager):
    """Extends object manager functionality for ClamAVFileScan model."""

    def record_scan(
        self,
        file: Union[File, StringIO],
        file_name: str,
        msg: str,
        result: 'ClamAVFileScan.Result',
        uploaded_by: User
    ) -> 'ClamAVFileScan':
        """Create a new ClamAVFileScan instance with associated LogEntry."""
        try:
            file_shasum = get_file_shasum(file)
        except (AttributeError, TypeError, ValueError) as err:
            logger.error(f'Encountered error deriving file hash: {err}')
            file_shasum = 'INVALID'

        # Create the ClamAVFileScan instance.
        av_scan = self.model.objects.create(
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
        content_type = ContentType.objects.get_for_model(ClamAVFileScan)
        LogEntry.objects.log_action(
            user_id=uploaded_by.pk,
            content_type_id=content_type.pk,
            object_id=av_scan.pk,
            object_repr=str(av_scan),
            action_flag=ADDITION,
            change_message=msg
        )

        return av_scan


class ClamAVFileScan(models.Model):
    """Represents a ClamAV virus scan performed for an uploaded file."""

    class Meta:
        """Model Meta options."""

        verbose_name = 'Clam AV File Scan'

    class Result(models.TextChoices):
        """Represents the possible results from a completed ClamAV scan."""

        CLEAN = 'CLEAN'
        INFECTED = 'INFECTED'
        ERROR = 'ERROR'

    scanned_at = models.DateTimeField(auto_now_add=True)
    file_name = models.TextField()
    file_size = models.PositiveBigIntegerField(
        help_text='The file size in bytes'
    )
    file_shasum = models.TextField(
        help_text='The SHA256 checksum of the uploaded file'
    )
    result = models.CharField(
        choices=Result.choices,
        help_text='Scan result for uploaded file',
        max_length=12
    )
    uploaded_by = models.ForeignKey(
        User,
        help_text='The user that uploaded the scanned file',
        null=True,
        on_delete=models.SET_NULL,
        related_name='av_scans'
    )

    data_file = models.ForeignKey(
        DataFile,
        blank=True,
        help_text='The resulting DataFile object, if this scan was clean',
        null=True,
        on_delete=models.SET_NULL,
        related_name='av_scans'
    )

    objects = ClamAVFileScanManager()

    def __str__(self) -> str:
        """Return string representation of model instance."""
        return f'{self.file_name} ({self.file_size_humanized}) - {self.result}'

    @property
    def file_size_humanized(self) -> str:
        """Convert the file size into the largest human readable unit."""
        size = self.file_size
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size < 1024.0:
                break
            size /= 1024.0

        return f'{size:.{2}f}{unit}'


class OwaspZapScanManager(models.Manager):
    """Extends object manager functionality for OwaspZapScan model."""

    def record_scan(
        self,
        app_target: str,
        html_report: Union[File, StringIO],
        fail_count: int,
        pass_count: int,
        warn_count: int,
    ) -> 'ClamAVFileScan':
        """Create a new OwaspZapScan instance with associated LogEntry."""
        # A LogEntry must be tied to a user, but these records get created from
        # nightly system level processes. To allow us to still capture these
        # logs we will create a reserved system user that cannot log in and has
        # no permissions or groups.
        system_user, created = User.objects.get_or_create(username='system')
        if created:
            logger.debug('Created reserved system user')

        # Create the OwaspZapScan instance.
        zap_scan = self.model.objects.create(
            app_target=app_target,
            html_report=html_report,
            scanned_at=now(),
            fail_count=fail_count,
            pass_count=pass_count,
            warn_count=warn_count
        )

        # Format a message using the supplied metrics
        msg = (
            f'OWASP ZAP scan completed with result: {zap_scan.result}. '
            f'FAIL: {fail_count}, WARN: {warn_count}, PASS: {pass_count}'
        )

        # Create a new LogEntry that is tied to this model instance.
        content_type = ContentType.objects.get_for_model(OwaspZapScan)
        LogEntry.objects.log_action(
            user_id=system_user.pk,
            content_type_id=content_type.pk,
            object_id=zap_scan.pk,
            object_repr=str(zap_scan),
            action_flag=ADDITION,
            change_message=msg
        )

        return zap_scan


class OwaspZapScan(models.Model):
    """Tracks the results of a scheduled run of the OWASP ZAP scan.

    OWASP ZAP scan is an automated penetration testing tool which provides us
    a security analysis of our deployed applications. These scans are run
    nightly by Circle CI which triggers a Cloud Foundry Task to download
    and store the results in this model.

    Reference: https://www.zaproxy.org/
    """

    class AppTarget(models.TextChoices):
        BACKEND = 'tdrs-backend'
        FRONTEND = 'tdrs-frontend'

    class Meta:
        """Model Meta options."""

        verbose_name = 'OWASP ZAP Scan'

    app_target = models.CharField(
        choices=AppTarget.choices,
        help_text='The application that was scanned',
        max_length=32
    )
    html_report = models.FileField(
        help_text='The generated HTML ZAP Scanning Report',
        storage=DataFilesS3Storage,
        upload_to=get_zap_s3_upload_path
    )
    scanned_at = models.DateTimeField(
        auto_now_add=True,
        help_text='The date and time this scan was processed'
    )
    fail_count = models.PositiveSmallIntegerField(
        help_text='The number of alerts raised at FAIL level during the scan'
    )
    pass_count = models.PositiveIntegerField(
        help_text='The number of passed rules during the scan'
    )
    warn_count = models.PositiveIntegerField(
        help_text='The number of alerts raised at WARN level during the scan'
    )

    objects = OwaspZapScanManager()

    def __str__(self):
        """Return the string representation of a model instance."""
        return (
            f'{self.get_app_target_display()}: {self.scanned_at.date()} '
            f'({self.result})'
        )

    @property
    def result(self) -> str:
        """Returns a summarized result of the scan."""
        if self.fail_count > 0:
            return 'Failed'
        elif self.warn_count > 0:
            return 'Warning'
        elif self.pass_count > 0:
            return 'Passed'
        else:
            return 'Error'
