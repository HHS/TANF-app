"""Add Reports to Django Admin."""

from django.contrib import admin
from django.db.models import OuterRef, Subquery
from django.utils.translation import ugettext_lazy as _

from tdpservice.core.filters import MostRecentVersionFilter
from tdpservice.core.utils import ReadOnlyAdminMixin

from .models import ReportFile, ReportSource


class VersionFilter(MostRecentVersionFilter):
    """Simple filter class to show newest created report file record."""

    title = _("Version")
    parameter_name = "created_at"

    def queryset(self, request, queryset):
        """Sort queryset to show latest records."""
        if self.value() is None and queryset.exists():
            # Subquery to find the latest version for each group
            versions = queryset.filter(
                stt__stt_code=OuterRef("stt__stt_code"),
                year=OuterRef("year"),
                date_extracted_on=OuterRef("date_extracted_on"),
            ).order_by("-version")

            # Filter to only records with the latest version
            return queryset.filter(version=Subquery(versions.values("version")[:1]))

        return queryset


@admin.register(ReportFile)
class ReportFileAdmin(ReadOnlyAdminMixin, admin.ModelAdmin):
    """Read-only Admin class for Report File model."""

    list_display = [
        "id",
        "year",
        "date_extracted_on",
        "stt",
        "version",
        "user",
    ]
    list_filter = [
        "stt",
        "year",
        "date_extracted_on",
        "user",
        VersionFilter
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
