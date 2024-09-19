"""ModelAdmin classes for parsed TANF data files."""
from .filters import CreationDateFilter, STTFilter
from .mixins import CsvExportAdminMixin, ReadOnlyAdminMixin
from tdpservice.search_indexes.admin.multiselect_filter import MultiSelectDropdownFilter


class TANF_T1Admin(ReadOnlyAdminMixin, CsvExportAdminMixin):
    """ModelAdmin class for parsed T1 data files."""

    list_display = [
        'RecordType',
        'RPT_MONTH_YEAR',
        'datafile',
        'stt_name',
    ]

    list_filter = [
        ('datafile__year', MultiSelectDropdownFilter),
        ('datafile__quarter', MultiSelectDropdownFilter),
        ('datafile__stt__name', STTFilter),
        CreationDateFilter,
    ]


class TANF_T2Admin(ReadOnlyAdminMixin, CsvExportAdminMixin):
    """ModelAdmin class for parsed T2 data files."""

    list_display = [
        'RecordType',
        'RPT_MONTH_YEAR',
        'datafile',
        'stt_name',
    ]

    list_filter = [
        ('datafile__year', MultiSelectDropdownFilter),
        ('datafile__quarter', MultiSelectDropdownFilter),
        ('datafile__stt__name', STTFilter),
        CreationDateFilter,
    ]


class TANF_T3Admin(ReadOnlyAdminMixin, CsvExportAdminMixin):
    """ModelAdmin class for parsed T3 data files."""

    list_display = [
        'RecordType',
        'RPT_MONTH_YEAR',
        'datafile',
        'stt_name',
    ]

    list_filter = [
        ('datafile__year', MultiSelectDropdownFilter),
        ('datafile__quarter', MultiSelectDropdownFilter),
        ('datafile__stt__name', STTFilter),
        CreationDateFilter,
    ]


class TANF_T4Admin(ReadOnlyAdminMixin, CsvExportAdminMixin):
    """ModelAdmin class for parsed T4 data files."""

    list_display = [
        'RecordType',
        'RPT_MONTH_YEAR',
        'datafile',
        'stt_name',
    ]

    list_filter = [
        ('datafile__year', MultiSelectDropdownFilter),
        ('datafile__quarter', MultiSelectDropdownFilter),
        ('datafile__stt__name', STTFilter),
        CreationDateFilter,
    ]


class TANF_T5Admin(ReadOnlyAdminMixin, CsvExportAdminMixin):
    """ModelAdmin class for parsed T5 data files."""

    list_display = [
        'RecordType',
        'RPT_MONTH_YEAR',
        'datafile',
        'stt_name',
    ]

    list_filter = [
        ('datafile__year', MultiSelectDropdownFilter),
        ('datafile__quarter', MultiSelectDropdownFilter),
        ('datafile__stt__name', STTFilter),
        CreationDateFilter,
    ]


class TANF_T6Admin(ReadOnlyAdminMixin, CsvExportAdminMixin):
    """ModelAdmin class for parsed T6 data files."""

    list_display = [
        'RecordType',
        'CALENDAR_QUARTER',
        'datafile',
        'stt_name',
    ]

    list_filter = [
        ('datafile__year', MultiSelectDropdownFilter),
        ('datafile__quarter', MultiSelectDropdownFilter),
        ('datafile__stt__name', STTFilter),
        CreationDateFilter,
    ]


class TANF_T7Admin(ReadOnlyAdminMixin, CsvExportAdminMixin):
    """ModelAdmin class for parsed T7 data files."""

    list_display = [
        'RecordType',
        'CALENDAR_QUARTER',
        'RPT_MONTH_YEAR',
        'TDRS_SECTION_IND',
        'STRATUM',
        'FAMILIES_MONTH',
        'datafile',
        'stt_name',
    ]

    list_filter = [
        ('datafile__year', MultiSelectDropdownFilter),
        ('datafile__quarter', MultiSelectDropdownFilter),
        ('datafile__stt__name', STTFilter),
        CreationDateFilter,
    ]
