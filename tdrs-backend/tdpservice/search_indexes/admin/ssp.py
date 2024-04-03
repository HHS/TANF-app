"""ModelAdmin classes for parsed SSP data files."""
from .filters import CreationDateFilter, FiscalPeriodFilter, STTFilter
from .mixins import DisableDeleteActionMixin, ExportCsvMixin, SttCodeMixin


class SSP_M1Admin(DisableDeleteActionMixin, ExportCsvMixin, SttCodeMixin):
    """ModelAdmin class for parsed M1 data files."""

    actions = ["export_as_csv"]
    ordering = ['datafile__stt__stt_code']

    list_display = [
        'RecordType',
        'RPT_MONTH_YEAR',
        'CASE_NUMBER',
        'COUNTY_FIPS_CODE',
        'ZIP_CODE',
        'STRATUM',
        'datafile',
        'stt_code',
    ]

    list_filter = [
        FiscalPeriodFilter,
        CreationDateFilter,
        STTFilter,
        'RPT_MONTH_YEAR',
        'ZIP_CODE',
        'STRATUM',
    ]


class SSP_M2Admin(DisableDeleteActionMixin, ExportCsvMixin, SttCodeMixin):
    """ModelAdmin class for parsed M2 data files."""

    actions = ["export_as_csv"]
    ordering = ['datafile__stt__stt_code']

    list_display = [
        'RecordType',
        'RPT_MONTH_YEAR',
        'CASE_NUMBER',
        'datafile',
        'stt_code',
    ]

    list_filter = [
        FiscalPeriodFilter,
        CreationDateFilter,
        STTFilter,
        'RPT_MONTH_YEAR',
    ]


class SSP_M3Admin(DisableDeleteActionMixin, ExportCsvMixin, SttCodeMixin):
    """ModelAdmin class for parsed M3 data files."""

    actions = ["export_as_csv"]
    ordering = ['datafile__stt__stt_code']

    list_display = [
        'RecordType',
        'RPT_MONTH_YEAR',
        'CASE_NUMBER',
        'datafile',
        'stt_code',
    ]

    list_filter = [
        FiscalPeriodFilter,
        CreationDateFilter,
        STTFilter,
        'RPT_MONTH_YEAR',
    ]

class SSP_M4Admin(DisableDeleteActionMixin, ExportCsvMixin, SttCodeMixin):
    """ModelAdmin class for parsed M3 data files."""

    actions = ["export_as_csv"]
    ordering = ['datafile__stt__stt_code']

    list_display = [
        'RecordType',
        'RPT_MONTH_YEAR',
        'CASE_NUMBER',
        'datafile',
        'stt_code',
    ]

    list_filter = [
        FiscalPeriodFilter,
        CreationDateFilter,
        STTFilter,
        'RPT_MONTH_YEAR',
    ]

class SSP_M5Admin(DisableDeleteActionMixin, ExportCsvMixin, SttCodeMixin):
    """ModelAdmin class for parsed M3 data files."""

    actions = ["export_as_csv"]
    ordering = ['datafile__stt__stt_code']

    list_display = [
        'RecordType',
        'RPT_MONTH_YEAR',
        'CASE_NUMBER',
        'datafile',
        'stt_code',
    ]

    list_filter = [
        FiscalPeriodFilter,
        CreationDateFilter,
        STTFilter,
        'RPT_MONTH_YEAR',
    ]

class SSP_M6Admin(DisableDeleteActionMixin, ExportCsvMixin, SttCodeMixin):
    """ModelAdmin class for parsed M6 data files."""

    actions = ["export_as_csv"]
    ordering = ['datafile__stt__stt_code']

    list_display = [
        'RecordType',
        'CALENDAR_QUARTER',
        'RPT_MONTH_YEAR',
        'datafile',
        'stt_code',
    ]

    list_filter = [
        'CALENDAR_QUARTER',
        FiscalPeriodFilter,
        CreationDateFilter,
        STTFilter,
        'RPT_MONTH_YEAR'
    ]

class SSP_M7Admin(DisableDeleteActionMixin, ExportCsvMixin, SttCodeMixin):
    """ModelAdmin class for parsed M7 data files."""

    actions = ["export_as_csv"]
    ordering = ['datafile__stt__stt_code']

    list_display = [
        'RecordType',
        'CALENDAR_QUARTER',
        'RPT_MONTH_YEAR',
        'TDRS_SECTION_IND',
        'STRATUM',
        'FAMILIES_MONTH',
        'datafile',
        'stt_code',
    ]

    list_filter = [
        'CALENDAR_QUARTER',
        FiscalPeriodFilter,
        CreationDateFilter,
        STTFilter,
        'RPT_MONTH_YEAR',
    ]
