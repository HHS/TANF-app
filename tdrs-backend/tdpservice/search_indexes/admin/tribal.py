"""ModelAdmin classes for parsed TRIBAL data files."""
from tdpservice.search_indexes.admin.multiselect_filter import MultiSelectDropdownFilter

from .filters import CreationDateFilter, STTFilter
from .mixins import CsvExportAdminMixin, ReadOnlyAdminMixin


class Tribal_TANF_T1Admin(ReadOnlyAdminMixin, CsvExportAdminMixin):
    """ModelAdmin class for parsed Tribal_T1 data files."""

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


class Tribal_TANF_T2Admin(ReadOnlyAdminMixin, CsvExportAdminMixin):
    """ModelAdmin class for parsed Tribal_T2 data files."""

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


class Tribal_TANF_T3Admin(ReadOnlyAdminMixin, CsvExportAdminMixin):
    """ModelAdmin class for parsed Tribal_T3 data files."""

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


class Tribal_TANF_T4Admin(ReadOnlyAdminMixin, CsvExportAdminMixin):
    """ModelAdmin class for parsed Tribal_T4 data files."""

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


class Tribal_TANF_T5Admin(ReadOnlyAdminMixin, CsvExportAdminMixin):
    """ModelAdmin class for parsed Tribal_T5 data files."""

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


class Tribal_TANF_T6Admin(ReadOnlyAdminMixin, CsvExportAdminMixin):
    """ModelAdmin class for parsed Tribal T6 data files."""

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


class Tribal_TANF_T7Admin(ReadOnlyAdminMixin, CsvExportAdminMixin):
    """ModelAdmin class for parsed Tribal T7 data files."""

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
