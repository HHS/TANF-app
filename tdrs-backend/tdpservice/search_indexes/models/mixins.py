"""Mixin classes."""

from django.db import models
from django.utils.translation import gettext_lazy as _


class LineNumberMixin(models.Model):
    """Mixin for models that have a line number."""

    class Meta:
        """Meta for mixin."""

        abstract = True

    line_number = models.IntegerField(null=True, blank=True)
