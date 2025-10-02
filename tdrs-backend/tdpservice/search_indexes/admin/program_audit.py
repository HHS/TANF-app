"""ModelAdmin classes for parsed TANF Program Audit data files."""
from tdpservice.search_indexes.admin.multiselect_filter import MultiSelectDropdownFilter

from .filters import CreationDateFilter, STTFilter
from .mixins import CsvExportAdminMixin, ReadOnlyAdminMixin


class ProgramAudit_T1Admin(ReadOnlyAdminMixin, CsvExportAdminMixin):
    """ModelAdmin class for parsed T1 data files."""

    list_display = [
        "RecordType",
        "RPT_MONTH_YEAR",
        "datafile",
        "stt_name",
    ]

    list_filter = [
        ("datafile__year", MultiSelectDropdownFilter),
        ("datafile__quarter", MultiSelectDropdownFilter),
        ("datafile__stt__name", STTFilter),
        CreationDateFilter,
    ]


class ProgramAudit_T2Admin(ReadOnlyAdminMixin, CsvExportAdminMixin):
    """ModelAdmin class for parsed T2 data files."""

    list_display = [
        "RecordType",
        "RPT_MONTH_YEAR",
        "datafile",
        "stt_name",
    ]

    list_filter = [
        ("datafile__year", MultiSelectDropdownFilter),
        ("datafile__quarter", MultiSelectDropdownFilter),
        ("datafile__stt__name", STTFilter),
        CreationDateFilter,
    ]


class ProgramAudit_T3Admin(ReadOnlyAdminMixin, CsvExportAdminMixin):
    """ModelAdmin class for parsed T3 data files."""

    list_display = [
        "RecordType",
        "RPT_MONTH_YEAR",
        "datafile",
        "stt_name",
    ]

    list_filter = [
        ("datafile__year", MultiSelectDropdownFilter),
        ("datafile__quarter", MultiSelectDropdownFilter),
        ("datafile__stt__name", STTFilter),
        CreationDateFilter,
    ]
