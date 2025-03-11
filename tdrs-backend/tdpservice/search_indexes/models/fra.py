"""Model representing parsed FRA data file records submitted to TDP."""

import uuid
from django.db import models
from tdpservice.data_files.models import DataFile
from tdpservice.stts.models import STT


class TANF_Exiter1(models.Model):
    """Parsed record representing an FRA data submission."""

    class Meta:
        """Meta class for the model."""

        verbose_name = 'TANF Exiter 1'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    datafile = models.ForeignKey(
        DataFile,
        blank=True,
        help_text='The parent file from which this record was created.',
        null=True,
        on_delete=models.CASCADE,
        related_name='tanf_exiter_1_parent'
    )
    stt = models.ForeignKey(
        STT, on_delete=models.DO_NOTHING, related_name="te1_stt_ref", blank=False, null=False
    )

    RecordType = models.CharField(max_length=25, null=True, blank=False, default='TE1')
    EXIT_DATE = models.IntegerField(null=True, blank=False)
    SSN = models.CharField(max_length=9, null=True, blank=False)
