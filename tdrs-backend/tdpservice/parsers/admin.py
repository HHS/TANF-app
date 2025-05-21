"""Django admin customizations for the parser models."""
from django.contrib import admin
from . import models


# Register your models here.
class ParserErrorAdmin(admin.ModelAdmin):
    """ModelAdmin class for ParserError objects generated in parsing."""

    list_display = [
        'row_number',
        'field_name',
        'error_type',
        'error_message',
    ]

    fields = [
        'file',
        'row_number',
        'column_number',
        'item_number',
        'field_name',
        'rpt_month_year',
        'case_number',
        'error_message',
        'error_type',
    ]


class ParserErrorInline(admin.TabularInline):
    """Inline model for ParserError objects."""

    model = models.ParserError


class DataFileSummaryAdmin(admin.ModelAdmin):
    """ModelAdmin class for DataFileSummary objects generated in parsing."""

    list_display = ['status', 'case_aggregates', 'datafile']


admin.site.register(models.ParserError, ParserErrorAdmin)
admin.site.register(models.DataFileSummary, DataFileSummaryAdmin)
