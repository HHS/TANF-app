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
    column_number = models.IntegerField(null=True)
    item_number = models.IntegerField(null=True)
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

    # TODO: worth adding more fields here or ???
    #named program schema
    #named models schema via rowschema
    #named section via datafile

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


    def get_status(errors):
        """Set and return the status field based on errors and models associated with datafile."""
        if errors is None:
            return DataFileSummary.Status.PENDING

        if type(errors) != dict:
            raise TypeError("errors parameter must be a dictionary.")

        if errors == {}:
            return DataFileSummary.Status.ACCEPTED
        elif DataFileSummary.find_precheck(errors):
            return DataFileSummary.Status.REJECTED
        else:
            return DataFileSummary.Status.ACCEPTED_WITH_ERRORS

    def find_precheck(errors):
        """Check for pre-parsing errors.

        @param errors: dict of errors keyed by location in datafile.
        e.g.
        errors =
        {
            "trailer": [ParserError, ...],
            "header": [ParserError, ...],
            "document": [ParserError, ...],
            "123": [ParserError, ...],
            ...
        }
        """
        for key in errors.keys():
            if key == 'trailer':
                continue
            for parserError in errors[key]:
                if type(parserError) is ParserError and parserError.error_type == ParserErrorCategoryChoices.PRE_CHECK:
                    return True
        return False
