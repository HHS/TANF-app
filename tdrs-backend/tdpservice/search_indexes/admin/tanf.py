"""ModelAdmin classes for parsed TANF data files."""
from django.contrib import admin


class TANF_T1Admin(admin.ModelAdmin):
    """ModelAdmin class for parsed T1 data files."""

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


class TANF_T2Admin(admin.ModelAdmin):
    """ModelAdmin class for parsed T2 data files."""

    list_display = [
        'record',
        'rpt_month_year',
        'case_number',
    ]

    list_filter = [
        'rpt_month_year',
    ]


class TANF_T3Admin(admin.ModelAdmin):
    """ModelAdmin class for parsed T3 data files."""

    list_display = [
        'record',
        'rpt_month_year',
        'case_number',
    ]

    list_filter = [
        'rpt_month_year',
    ]


class TANF_T4Admin(admin.ModelAdmin):
    """ModelAdmin class for parsed T4 data files."""

    list_display = [
        'record',
        'rpt_month_year',
        'case_number',
    ]

    list_filter = [
        'rpt_month_year',
    ]


class TANF_T5Admin(admin.ModelAdmin):
    """ModelAdmin class for parsed T5 data files."""

    list_display = [
        'record',
        'rpt_month_year',
        'case_number',
    ]

    list_filter = [
        'rpt_month_year',
    ]


class TANF_T6Admin(admin.ModelAdmin):
    """ModelAdmin class for parsed T6 data files."""

    list_display = [
        'record',
        'rpt_month_year',
    ]

    list_filter = [
        'rpt_month_year',
    ]


class TANF_T7Admin(admin.ModelAdmin):
    """ModelAdmin class for parsed T7 data files."""

    list_display = [
        'record',
        'rpt_month_year',
    ]

    list_filter = [
        'rpt_month_year',
    ]
