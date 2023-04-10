"""ModelAdmin classes for parsed SSP data files."""
from django.contrib import admin


class SSP_M1Admin(admin.ModelAdmin):
    """ModelAdmin class for parsed M1 data files."""

    list_display = [
        'RecordType',
        'RPT_MONTH_YEAR',
        'CASE_NUMBER',
        'COUNTY_FIPS_CODE',
        'ZIP_CODE',
        'STRATUM',
    ]

    list_filter = [
        'RPT_MONTH_YEAR',
        'ZIP_CODE',
        'STRATUM',
    ]


class SSP_M2Admin(admin.ModelAdmin):
    """ModelAdmin class for parsed M2 data files."""

    list_display = [
        'record',
        'rpt_month_year',
        'case_number',
    ]

    list_filter = [
        'rpt_month_year',
    ]


class SSP_M3Admin(admin.ModelAdmin):
    """ModelAdmin class for parsed M3 data files."""

    list_display = [
        'record',
        'rpt_month_year',
        'case_number',
    ]

    list_filter = [
        'rpt_month_year',
    ]