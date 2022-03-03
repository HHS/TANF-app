"""Admin class for DataFile objects."""
from django.contrib import admin
from .models import DataFile
from ..core.utils import ReadOnlyAdminMixin


@admin.register(DataFile)
class DataFileAdmin(ReadOnlyAdminMixin, admin.ModelAdmin):
    """Admin class for DataFile models."""

    list_display = [
        'id',
        'stt',
        'year',
        'quarter',
        'section',
        'version',
    ]

    list_filter = [
        'quarter',
        'section',
        'stt',
        'user',
        'year',
        'version',
    ]
