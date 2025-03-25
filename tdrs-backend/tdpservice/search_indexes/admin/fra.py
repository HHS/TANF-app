"""ModelAdmin classes for parsed FRA data files."""
from .filters import CreationDateFilter, STTFilter
from .mixins import CsvExportAdminMixin, ReadOnlyAdminMixin
from tdpservice.search_indexes.admin.multiselect_filter import MultiSelectDropdownFilter


class TANF_Exiter1Admin(ReadOnlyAdminMixin, CsvExportAdminMixin):
    """ModelAdmin class for parsed TE1 records."""

    list_display = [
        'RecordType',
        'EXIT_DATE',
        'datafile',
        'stt_name',
    ]

    list_filter = [
        ('datafile__year', MultiSelectDropdownFilter),
        ('datafile__quarter', MultiSelectDropdownFilter),
        ('datafile__stt__name', STTFilter),
        CreationDateFilter,
    ]
