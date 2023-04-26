"""Django admin customizations for the parser models."""
from django.contrib import admin
from . import models


# Register your models here.
class ParserErrorAdmin(admin.ModelAdmin):
    """ModelAdmin class for parsed M1 data files."""

    list_display = [
        'row_number',
        'field_name',
        'category',
        'error_type',
        'error_message',
    ]


admin.site.register(models.ParserError, ParserErrorAdmin)
