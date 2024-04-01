"""ModelAdmin classes for parsed SSP data files."""
from django.contrib import admin
from .filters import CreationDateFilter, FiscalPeriodFilter, STTFilter


class SSP_M1Admin(admin.ModelAdmin):
    """ModelAdmin class for parsed M1 data files."""

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
        STTFilter,
        FiscalPeriodFilter,
        CreationDateFilter,
        'RPT_MONTH_YEAR',
        'ZIP_CODE',
        'STRATUM',
    ]


class SSP_M2Admin(admin.ModelAdmin):
    """ModelAdmin class for parsed M2 data files."""

    list_display = [
        'RecordType',
        'RPT_MONTH_YEAR',
        'CASE_NUMBER',
        'datafile',
    ]

    list_filter = [
        STTFilter,
        FiscalPeriodFilter,
        CreationDateFilter,
        'RPT_MONTH_YEAR',
    ]


class SSP_M3Admin(admin.ModelAdmin):
    """ModelAdmin class for parsed M3 data files."""

    list_display = [
        'RecordType',
        'RPT_MONTH_YEAR',
        'CASE_NUMBER',
        'datafile',
    ]

    list_filter = [
        STTFilter,
        FiscalPeriodFilter,
        CreationDateFilter,
        'RPT_MONTH_YEAR',
    ]

class SSP_M4Admin(admin.ModelAdmin):
    """ModelAdmin class for parsed M3 data files."""

    list_display = [
        'RecordType',
        'RPT_MONTH_YEAR',
        'CASE_NUMBER',
        'datafile',
    ]

    list_filter = [
        STTFilter,
        FiscalPeriodFilter,
        CreationDateFilter,
        'RPT_MONTH_YEAR',
    ]

class SSP_M5Admin(admin.ModelAdmin):
    """ModelAdmin class for parsed M3 data files."""

    list_display = [
        'RecordType',
        'RPT_MONTH_YEAR',
        'CASE_NUMBER',
        'datafile',
    ]

    list_filter = [
        STTFilter,
        FiscalPeriodFilter,
        CreationDateFilter,
        'RPT_MONTH_YEAR',
    ]

class SSP_M6Admin(admin.ModelAdmin):
    """ModelAdmin class for parsed M6 data files."""

    list_display = [
        'RecordType',
        'CALENDAR_QUARTER',
        'RPT_MONTH_YEAR',
        'datafile',
    ]

    list_filter = [
        'CALENDAR_QUARTER',
        STTFilter,
        FiscalPeriodFilter,
        CreationDateFilter,
        'RPT_MONTH_YEAR'
    ]

class SSP_M7Admin(admin.ModelAdmin):
    """ModelAdmin class for parsed M7 data files."""

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
        STTFilter,
        FiscalPeriodFilter,
        CreationDateFilter,
        'RPT_MONTH_YEAR',
    ]
