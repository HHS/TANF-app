"""Models representing parser error."""

import datetime
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from tdpservice.data_files.models import DataFile

class ParserErrorCategoryChoices(models.TextChoices):
    """Enum of ParserError error_type."""

    PRE_CHECK = "1", _("File pre-check")
    FIELD_VALUE = "2", _("Record value invalid")
    VALUE_CONSISTENCY = "3", _("Record value consistency")
    CASE_CONSISTENCY = "4", _("Case consistency")
    SECTION_CONSISTENCY = "5", _("Section consistency")
    HISTORICAL_CONSISTENCY = "6", _("Historical consistency")


class ParserError(models.Model):
    """Model representing a parser error."""

    class Meta:
        """Meta for ParserError."""

        db_table = "parser_error"

    id = models.AutoField(primary_key=True)
    file = models.ForeignKey(
        "data_files.DataFile",
        on_delete=models.CASCADE,
        related_name="parser_errors",
        null=True,
    )
    row_number = models.IntegerField(null=False)
    column_number = models.CharField(null=True, max_length=8)
    item_number = models.CharField(null=True, max_length=8)
    field_name = models.TextField(null=True, max_length=128)
    rpt_month_year = models.IntegerField(null=True,  blank=False)
    case_number = models.TextField(null=True, max_length=128)

    error_message = models.TextField(null=True, max_length=512)
    error_type = models.TextField(max_length=128, choices=ParserErrorCategoryChoices.choices)

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, null=True)
    object_id = models.UUIDField(null=True)
    content_object = GenericForeignKey()

    created_at = models.DateTimeField(auto_now_add=True)
    fields_json = models.JSONField(null=True)

    @property
    def rpt_month_name(self):
        """Return the month name."""
        return datetime.datetime.strptime(str(self.rpt_month_year)[4:6], "%m").strftime("%B")

    def __repr__(self):
        """Return a string representation of the model."""
        return f"ParserError {self.id} for file {self.file} and object key {self.object_id}"

    def __str__(self):
        """Return a string representation of the model."""
        return f"ParserError {self.values()}"

    def _get_error_message(self):
        """Return the error message."""
        return self.error_message

class DataFileSummary(models.Model):
    """Aggregates information about a parsed file."""

    class Status(models.TextChoices):
        """Enum for status of parsed file."""

        PENDING = "Pending"  # file has been uploaded, but not validated
        ACCEPTED = "Accepted"
        ACCEPTED_WITH_ERRORS = "Accepted with Errors"
        REJECTED = "Rejected"

    status = models.CharField(
        max_length=50,
        choices=Status.choices,
        default=Status.PENDING,
    )

    datafile = models.ForeignKey(DataFile, on_delete=models.CASCADE)

    case_aggregates = models.JSONField(null=True, blank=False)

    def get_status(self):
        """Set and return the status field based on errors and models associated with datafile."""
        errors = ParserError.objects.filter(file=self.datafile)

        # excluding row-level pre-checks and trailer pre-checks.
        precheck_errors = errors.filter(error_type=ParserErrorCategoryChoices.PRE_CHECK)\
                                .exclude(field_name="Record_Type")\
                                .exclude(error_message__icontains="trailer")\
                                .exclude(error_message__icontains="Unknown Record_Type was found.")

        if errors is None:
            return DataFileSummary.Status.PENDING
        elif errors.count() == 0:
            return DataFileSummary.Status.ACCEPTED
        elif precheck_errors.count() > 0:
            return DataFileSummary.Status.REJECTED
        else:
            return DataFileSummary.Status.ACCEPTED_WITH_ERRORS
