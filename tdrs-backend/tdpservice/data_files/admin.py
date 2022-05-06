"""Admin class for DataFile objects."""
from django.contrib import admin
from .models import DataFile, LegacyFileTransfer, LegacyFileTransferManager
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

@admin.register(LegacyFileTransfer)
class LegacyFileTransferAdmin(ReadOnlyAdminMixin, admin.ModelAdmin):
    """Admin class for LegacyFileTransfer models."""

    list_display = [
        'id',
        'sent_at',
        'result',
        'uploaded_by',
        'file_name',
        'file_shasum',
    ]

    list_filter = [
        'sent_at',
        'result',
        'uploaded_by',
        'file_name',
        'file_shasum',
    ]
