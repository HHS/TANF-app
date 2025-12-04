"""Models representing parsed Program Audit data file records submitted to TDP."""

import uuid

from django.db import models

from tdpservice.data_files.models import DataFile
from tdpservice.search_indexes.models.mixins import RecordMixin


class ProgramAudit_T1(RecordMixin):
    """Parsed record representing a T1 data submission."""

    class Meta:
        """Meta class for the model."""

        verbose_name = "Program Audit T1"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    datafile = models.ForeignKey(
        DataFile,
        blank=True,
        help_text="The parent file from which this record was created.",
        null=True,
        on_delete=models.CASCADE,
        related_name="program_audit_t1_parent",
    )

    RecordType = models.CharField(max_length=156, null=True, blank=False)
    RPT_MONTH_YEAR = models.IntegerField(null=True, blank=False)
    CASE_NUMBER = models.CharField(max_length=11, null=True, blank=False)
    FUNDING_STREAM = models.IntegerField(null=True, blank=False)
    CASH_AMOUNT = models.IntegerField(null=True, blank=False)


class ProgramAudit_T2(RecordMixin):
    """Parsed record representing a T2 data submission."""

    class Meta:
        """Meta class for the model."""

        verbose_name = "Program Audit T2"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    datafile = models.ForeignKey(
        DataFile,
        blank=True,
        help_text="The parent file from which this record was created.",
        null=True,
        on_delete=models.CASCADE,
        related_name="program_audit_t2_parent",
    )

    RecordType = models.CharField(max_length=156, null=True, blank=False)
    RPT_MONTH_YEAR = models.IntegerField(null=True, blank=False)
    CASE_NUMBER = models.CharField(max_length=11, null=True, blank=False)

    FAMILY_AFFILIATION = models.IntegerField(null=True, blank=False)
    DATE_OF_BIRTH = models.CharField(max_length=8, null=True, blank=False)
    SSN = models.CharField(max_length=9, null=True, blank=False)
    CITIZENSHIP_STATUS = models.IntegerField(null=True, blank=False)


class ProgramAudit_T3(RecordMixin):
    """Parsed record representing a T3 data submission."""

    class Meta:
        """Meta class for the model."""

        verbose_name = "Program Audit T3"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    datafile = models.ForeignKey(
        DataFile,
        blank=True,
        help_text="The parent file from which this record was created.",
        null=True,
        on_delete=models.CASCADE,
        related_name="program_audit_t3_parent",
    )

    RecordType = models.CharField(max_length=156, null=True, blank=False)
    RPT_MONTH_YEAR = models.IntegerField(null=True, blank=False)
    CASE_NUMBER = models.CharField(max_length=11, null=True, blank=False)
    FAMILY_AFFILIATION = models.IntegerField(null=True, blank=False)

    DATE_OF_BIRTH = models.CharField(max_length=8, null=True, blank=False)
    SSN = models.CharField(max_length=9, null=True, blank=False)
    CITIZENSHIP_STATUS = models.IntegerField(null=True, blank=False)
