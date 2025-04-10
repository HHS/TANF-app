"""Utility functions for DataFile views."""
from django.db import models
from django.utils.translation import gettext_lazy as _


class ParserErrorCategoryChoices(models.TextChoices):
    """Enum of ParserError error_type."""

    PRE_CHECK = "1", _("File pre-check")
    FIELD_VALUE = "2", _("Record value invalid")
    VALUE_CONSISTENCY = "3", _("Record value consistency")
    CASE_CONSISTENCY = "4", _("Case consistency")
    SECTION_CONSISTENCY = "5", _("Section consistency")
    HISTORICAL_CONSISTENCY = "6", _("Historical consistency")
