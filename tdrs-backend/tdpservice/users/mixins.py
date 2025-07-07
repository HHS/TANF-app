"""Mixin classes."""

from django.db import models
from django.utils.translation import gettext_lazy as _

class ReviewerMixin(models.Model):
    """Mixin for models that can be reviewed."""

    class Meta:
        """Meta for mixin."""

        abstract = True

    reviewed_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text=_('When this feedback was reviewed')
    )
    reviewed_by = models.ForeignKey(
        'users.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reviewed_feedback',
        help_text=_('The admin who reviewed this feedback')
    )
