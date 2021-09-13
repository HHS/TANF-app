from hashlib import sha256

from django.contrib.admin.models import ContentType, LogEntry, ADDITION
from django.db import models

from tdpservice.data_files.models import DataFile
from tdpservice.users.models import User


class ClamAVFileScanManager(models.Manager):
    """Extends object manager functionality with common operations."""

    def log_result(self, file, file_name, msg, result, uploaded_by):
        """TODO."""
        scan_result = self.model.objects.create(
            file_name=file_name,
            file_shasum=sha256(file.read()).hexdigest(),
            result=result,
            uploaded_by=uploaded_by
        )
        content_type = ContentType.objects.get_for_model(ClamAVFileScan)
        LogEntry.objects.log_action(
            user_id=uploaded_by.pk,
            content_type_id=content_type.pk,
            object_id=scan_result.pk,
            object_repr=str(scan_result),
            action_flag=ADDITION,
            change_message=msg
        )

        return scan_result


class ClamAVFileScan(models.Model):
    """Represents a ClamAV virus scan performed for an uploaded file."""

    class Result(models.TextChoices):
        CLEAN = 'CLEAN'
        INFECTED = 'INFECTED'
        ERROR = 'ERROR'

    file_name = models.TextField()
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
        help_text='The resulting DataFile object if this scan was clean',
        null=True,
        on_delete=models.SET_NULL,
        related_name='av_scans'
    )

    objects = ClamAVFileScanManager()
