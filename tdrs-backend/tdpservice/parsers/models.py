"""Models representing parser error."""

import datetime
from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from tdpservice.data_files.models import DataFile
from tdpservice.data_files.util import ParserErrorCategoryChoices

import logging

logger = logging.getLogger(__name__)


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
    row_number = models.IntegerField(null=True)
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
    values_json = models.JSONField(null=True)

    deprecated = models.BooleanField(default=False)

    @property
    def rpt_month_name(self):
        """Return the month name."""
        return datetime.datetime.strptime(str(self.rpt_month_year)[4:6], "%m").strftime("%B")

    def __repr__(self):
        """Return a string representation of the model."""
        return f"{{id: {self.id}, file: {self.file.id}, row: {self.row_number}, column: {self.column_number}, " + \
               f"error message: {self.error_message}}}"

    def __str__(self):
        """Return a string representation of the model."""
        return f"ParserError {self.__dict__}"

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
        PARTIALLY_ACCEPTED = "Partially Accepted with Errors"
        REJECTED = "Rejected"

    status = models.CharField(
        max_length=50,
        choices=Status.choices,
        default=Status.PENDING,
    )

    datafile = models.OneToOneField(DataFile, on_delete=models.CASCADE, related_name="summary")

    case_aggregates = models.JSONField(null=True, blank=False)

    total_number_of_records_in_file = models.IntegerField(null=True, blank=False, default=0)
    total_number_of_records_created = models.IntegerField(null=True, blank=False, default=0)

    def set_status(self, status):
        """Set the status on the summary object."""
        match status:
            case DataFileSummary.Status.PENDING:
                self.status = DataFileSummary.Status.PENDING
            case DataFileSummary.Status.ACCEPTED:
                self.status = DataFileSummary.Status.ACCEPTED
            case DataFileSummary.Status.ACCEPTED_WITH_ERRORS:
                self.status = DataFileSummary.Status.ACCEPTED_WITH_ERRORS
            case DataFileSummary.Status.PARTIALLY_ACCEPTED:
                self.status = DataFileSummary.Status.PARTIALLY_ACCEPTED
            case DataFileSummary.Status.REJECTED:
                self.status = DataFileSummary.Status.REJECTED
            case _:
                logger.warning(f"Unknown status: {status} passed into set_status.")

    def get_status(self):
        """Set and return the status field based on errors and models associated with datafile."""
        # Because we introduced a setter for the status for exception handling, we need to
        # check if it has been set before determining a status based on the queries below.
        if self.status != DataFileSummary.Status.PENDING:
            return self.status

        errors = ParserError.objects.filter(file=self.datafile, deprecated=False)

        # excluding row-level pre-checks and trailer pre-checks.
        precheck_errors = errors.filter(error_type=ParserErrorCategoryChoices.PRE_CHECK)\
                                .exclude(field_name="Record_Type")\
                                .exclude(error_message__icontains="trailer")\
                                .exclude(error_message__icontains="Unknown Record_Type was found.")

        case_consistency_errors = errors.filter(error_type=ParserErrorCategoryChoices.CASE_CONSISTENCY)

        row_precheck_errors = errors.filter(error_type=ParserErrorCategoryChoices.PRE_CHECK)\
                                    .filter(field_name="Record_Type")\
                                    .exclude(error_message__icontains="trailer")

        if errors is None:
            return DataFileSummary.Status.PENDING
        elif precheck_errors.count() > 0 or self.total_number_of_records_created == 0:
            return DataFileSummary.Status.REJECTED
        elif errors.count() == 0:
            return DataFileSummary.Status.ACCEPTED
        elif (row_precheck_errors.count() > 0 or case_consistency_errors.count()):
            return DataFileSummary.Status.PARTIALLY_ACCEPTED
        else:
            return DataFileSummary.Status.ACCEPTED_WITH_ERRORS
