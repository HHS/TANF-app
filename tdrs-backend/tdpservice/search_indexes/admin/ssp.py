"""ModelAdmin classes for parsed SSP data files."""
from tdpservice.search_indexes.admin.multiselect_filter import MultiSelectDropdownFilter

from .filters import CreationDateFilter, STTFilter
from .mixins import CsvExportAdminMixin, ReadOnlyAdminMixin


class SSP_M1Admin(ReadOnlyAdminMixin, CsvExportAdminMixin):
    """ModelAdmin class for parsed M1 data files."""

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


class SSP_M2Admin(ReadOnlyAdminMixin, CsvExportAdminMixin):
    """ModelAdmin class for parsed M2 data files."""

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


class SSP_M3Admin(ReadOnlyAdminMixin, CsvExportAdminMixin):
    """ModelAdmin class for parsed M3 data files."""

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


class SSP_M4Admin(ReadOnlyAdminMixin, CsvExportAdminMixin):
    """ModelAdmin class for parsed M3 data files."""

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


class SSP_M5Admin(ReadOnlyAdminMixin, CsvExportAdminMixin):
    """ModelAdmin class for parsed M3 data files."""

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


class SSP_M6Admin(ReadOnlyAdminMixin, CsvExportAdminMixin):
    """ModelAdmin class for parsed M6 data files."""

    list_display = [
        "RecordType",
        "CALENDAR_QUARTER",
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


class SSP_M7Admin(ReadOnlyAdminMixin, CsvExportAdminMixin):
    """ModelAdmin class for parsed M7 data files."""

    list_display = [
        "RecordType",
        "CALENDAR_QUARTER",
        "RPT_MONTH_YEAR",
        "TDRS_SECTION_IND",
        "STRATUM",
        "FAMILIES_MONTH",
        "datafile",
        "stt_name",
    ]

    list_filter = [
        ("datafile__year", MultiSelectDropdownFilter),
        ("datafile__quarter", MultiSelectDropdownFilter),
        ("datafile__stt__name", STTFilter),
        CreationDateFilter,
    ]
