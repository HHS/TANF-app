"""Admin class for DataFile objects."""
from django.contrib import admin

from ..core.utils import ReadOnlyAdminMixin
from .models import DataFile, LegacyFileTransfer

class DataFileSummaryListFilter(admin.SimpleListFilter):
    """Admin class filter for file status (accepted, rejected) for datafile model"""

    title = 'status'
    parameter_name = 'status'

    def lookups(self, request, model_admin):
        """Return a list of tuples."""
        return [
            ('Accepted', 'Accepted'),
            ('Rejected', 'Rejected'),
        ]
    
    def queryset(self, request, queryset):
        """Return a queryset."""
        if self.value():
            return queryset.filter(datafilesummary__status=self.value())
        else:
            return queryset


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
        DataFileSummaryListFilter
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
