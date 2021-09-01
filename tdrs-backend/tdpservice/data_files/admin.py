"""Admin class for DataFile objects."""
from django.contrib import admin
from .models import DataFile


@admin.register(DataFile)
class DataFileAdmin(admin.ModelAdmin):
    """Enforce read-only on the Data File admin form."""

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
