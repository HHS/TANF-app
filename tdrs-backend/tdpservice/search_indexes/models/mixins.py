"""Mixin classes."""

from django.db import models


class RecordMixin(models.Model):
    """Base mixin for parsed records."""

    class Meta:
        """Meta for mixin."""

        abstract = True

    line_number = models.IntegerField(null=True, blank=True)
