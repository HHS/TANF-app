"""Models representing parser error."""

import datetime
from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

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
    rpt_month_year = models.IntegerField(null=True,  blank=False)
    case_number = models.TextField(null=True, max_length=128)

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
