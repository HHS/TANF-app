"""ModelAdmin classes for parsed data files."""

from django.contrib import admin
from .models import T1, T2, T3, T4, T5, T6, T7

# Register your models here.


class T1Admin(admin.ModelAdmin):
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


admin.site.register(T1, T1Admin)


class T2Admin(admin.ModelAdmin):
    """ModelAdmin class for parsed T2 data files."""

    list_display = [
        'record',
        'rpt_month_year',
        'case_number',
    ]

    list_filter = [
        'rpt_month_year',
    ]


admin.site.register(T2, T2Admin)


class T3Admin(admin.ModelAdmin):
    """ModelAdmin class for parsed T3 data files."""

    list_display = [
        'record',
        'rpt_month_year',
        'case_number',
    ]

    list_filter = [
        'rpt_month_year',
    ]


admin.site.register(T3, T3Admin)


class T4Admin(admin.ModelAdmin):
    """ModelAdmin class for parsed T4 data files."""

    list_display = [
        'record',
        'rpt_month_year',
        'case_number',
    ]

    list_filter = [
        'rpt_month_year',
    ]


admin.site.register(T4, T4Admin)


class T5Admin(admin.ModelAdmin):
    """ModelAdmin class for parsed T5 data files."""

    list_display = [
        'record',
        'rpt_month_year',
        'case_number',
    ]

    list_filter = [
        'rpt_month_year',
    ]


admin.site.register(T5, T5Admin)


class T6Admin(admin.ModelAdmin):
    """ModelAdmin class for parsed T6 data files."""

    list_display = [
        'record',
        'rpt_month_year',
    ]

    list_filter = [
        'rpt_month_year',
    ]


admin.site.register(T6, T6Admin)


class T7Admin(admin.ModelAdmin):
    """ModelAdmin class for parsed T7 data files."""

    list_display = [
        'record',
        'rpt_month_year',
    ]

    list_filter = [
        'rpt_month_year',
    ]


admin.site.register(T7, T7Admin)
