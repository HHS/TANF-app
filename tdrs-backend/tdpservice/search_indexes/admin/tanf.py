"""ModelAdmin classes for parsed TANF data files."""
from django.contrib import admin
from .filter import CreationDateFilter
from .mixins import ExportCsvMixin


class TANF_T1Admin(admin.ModelAdmin, ExportCsvMixin):
    """ModelAdmin class for parsed T1 data files."""

    actions = ["export_as_csv"]

    list_display = [
        'RecordType',
        'RPT_MONTH_YEAR',
        'CASE_NUMBER',
        'COUNTY_FIPS_CODE',
        'ZIP_CODE',
        'STRATUM',
        'datafile',
    ]

    list_filter = [
        CreationDateFilter,
        'RPT_MONTH_YEAR',
        'ZIP_CODE',
        'STRATUM',
    ]


class TANF_T2Admin(admin.ModelAdmin):
    """ModelAdmin class for parsed T2 data files."""

    list_display = [
        'RecordType',
        'RPT_MONTH_YEAR',
        'CASE_NUMBER',
        'datafile',
    ]

    list_filter = [
        CreationDateFilter,
        'RPT_MONTH_YEAR',
    ]


class TANF_T3Admin(admin.ModelAdmin):
    """ModelAdmin class for parsed T3 data files."""

    list_display = [
        'RecordType',
        'RPT_MONTH_YEAR',
        'CASE_NUMBER',
        'datafile',
    ]

    list_filter = [
        CreationDateFilter,
        'RPT_MONTH_YEAR',
    ]


class TANF_T4Admin(admin.ModelAdmin):
    """ModelAdmin class for parsed T4 data files."""

    list_display = [
        'RecordType',
        'RPT_MONTH_YEAR',
        'CASE_NUMBER',
        'datafile',
    ]

    list_filter = [
        CreationDateFilter,
        'RPT_MONTH_YEAR',
    ]


class TANF_T5Admin(admin.ModelAdmin):
    """ModelAdmin class for parsed T5 data files."""

    list_display = [
        'RecordType',
        'RPT_MONTH_YEAR',
        'CASE_NUMBER',
        'datafile',
    ]

    list_filter = [
        CreationDateFilter,
        'RPT_MONTH_YEAR',
    ]


class TANF_T6Admin(admin.ModelAdmin):
    """ModelAdmin class for parsed T6 data files."""

    list_display = [
        'RecordType',
        'CALENDAR_QUARTER',
        'RPT_MONTH_YEAR',
        'datafile',
    ]

    list_filter = [
        'CALENDAR_QUARTER',
        CreationDateFilter,
        'RPT_MONTH_YEAR'
    ]


class TANF_T7Admin(admin.ModelAdmin):
    """ModelAdmin class for parsed T7 data files."""

    list_display = [
        'RecordType',
        'CALENDAR_QUARTER',
        'RPT_MONTH_YEAR',
        'TDRS_SECTION_IND',
        'STRATUM',
        'FAMILIES_MONTH',
        'datafile',
    ]

    list_filter = [
        'CALENDAR_QUARTER',
        CreationDateFilter,
        'RPT_MONTH_YEAR',
    ]
