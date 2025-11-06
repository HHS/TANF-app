"""Add Reports to Django Admin."""

from django.contrib import admin

from tdpservice.core.utils import ReadOnlyAdminMixin

from .models import ReportFile, ReportSource


@admin.register(ReportFile)
class ReportFileAdmin(ReadOnlyAdminMixin, admin.ModelAdmin):
    """Read-only Admin class for Report File model."""

    list_display = [
        "id",
        "stt",
        "user",
        "version",
        "year",
    ]
    list_filter = [
        "stt",
        "year",
        "quarter",
        "user",
    ]
    search_fields = [
        "original_filename",
        "slug",
    ]

@admin.register(ReportSource)
class ReportSourceAdmin(ReadOnlyAdminMixin, admin.ModelAdmin):
    """Read-only Admin class for Report Source model."""

    list_display = [
        "id",
        "original_filename",
        "uploaded_by",
        "status",
        "created_at",
        "num_reports_created",
    ]
    list_filter = [
        "original_filename",
        "uploaded_by__email",
        "status",
        "created_at",
    ]
    search_fields = [
        "status",
        "created_at",
    ]
