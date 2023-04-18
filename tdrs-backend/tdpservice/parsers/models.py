"""Models representing parser error."""

import datetime
from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from tdpservice.data_files.models import DataFile

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
    column_number = models.IntegerField(null=False)
    item_number = models.IntegerField(null=False)
    field_name = models.TextField(null=False, max_length=128)
    category = models.IntegerField(null=False, default=1)
    case_number = models.TextField(null=True, max_length=128)
    rpt_month_year = models.IntegerField(null=True, blank=False)

    error_message = models.TextField(null=True, max_length=512)
    error_type = models.TextField(max_length=128)         # out of range, pre-parsing, etc.

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
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
        return f"ParserError {self.id}"

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

    #  eventually needs a breakdown of cases (accepted, rejected, total) per month
    #  elif qtr2 jan-mar
    #  elif qtr3 apr-jun
    #  elif qtr4 jul-sept

    case_aggregates = models.JSONField(null=True, blank=False)
    """
    # Do these queries only once, save result during creation of this model
    # or do we grab this data during parsing and bubble it up during create call?
    {
        "Jan": {
            "accepted": 100,
            "rejected": 10,
            "total": 110
        },
        "Feb": {
            "accepted": 100,
            "rejected": 10,
            "total": 110
        },
        "Mar": {
            "accepted": 100,
            "rejected": 10,
            "total": 110
        }
    """

    def set_status(self, errors):
        """Set and return the status field based on errors and models associated with datafile."""
        # to set rejected, we would need to have raised an exception during (pre)parsing
        # else if there are errors, we can set to accepted with errors
        # else we can set to accepted (default)
        if errors == {}:  # This feels better than running len() on `errors`
            self.status = self.Status.ACCEPTED
        elif errors:
            self.status = self.Status.ACCEPTED_WITH_ERRORS
        elif errors == {'document': ['No headers found.']}:  # we need a signal for unacceptable errors. Another func?
            self.status = self.Status.REJECTED

        return self.status
