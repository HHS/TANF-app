"""Add Reports to Django Admin."""


from django.contrib import admin

from tdpservice.core.utils import ReadOnlyAdminMixin

from .models import ReportFile


@admin.register(ReportFile)
class ReportFileAdmin(ReadOnlyAdminMixin, admin.ModelAdmin):
    """Read-only Admin class for Report models."""

    list_display = [
        "id",
        "stt",
        "user",
        "version",
        "year",
        "section",
    ]

