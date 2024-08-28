"""ModelAdmin classes for parsed SSP data files."""
from .mixins import ReadOnlyAdminMixin
from tdpservice.data_files.admin.admin import DataFileInline


class ReparseMetaAdmin(ReadOnlyAdminMixin):
    """ModelAdmin class for parsed M1 data files."""

    inlines = [DataFileInline]

    list_display = [
        'id',
        'created_at',
        'timeout_at',
        'success',
        'finished',
        'db_backup_location',
    ]

    list_filter = [
        'success',
        'finished',
        'fiscal_year',
        'fiscal_quarter',
    ]
