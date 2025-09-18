"""Mixin classes."""

from django.db import models


class LineNumberMixin(models.Model):
    """Mixin for models that have a line number."""

    class Meta:
        """Meta for mixin."""

        abstract = True

    line_number = models.IntegerField(null=True, blank=True)
