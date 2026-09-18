"""Add STTs and Regions to Django Admin."""

from django.contrib import admin

from ..core.utils import ReadOnlyAdminMixin
from .models import STT, Region, SttProgramParticipation


@admin.register(STT)
class STTAdmin(ReadOnlyAdminMixin, admin.ModelAdmin):
    """Read-only Admin class for STT models."""

    search_fields = ["name", "stt_code"]

    list_display = [
        "id",
        "type",
        "postal_code",
        "name",
        "region",
        "filenames",
        "stt_code",
        "has_state",
        "ssp",
        "sample",
    ]

    def has_state(self, obj):
        """If Type is tribe do not show state."""
        if obj.type == "tribe":
            return obj.state
        return None

    has_state.short_description = "State"
    has_state.admin_order_field = "state"


@admin.register(Region)
class RegionAdmin(ReadOnlyAdminMixin, admin.ModelAdmin):
    """Read-only Admin class for STT models."""

    list_display = [field.name for field in Region._meta.fields]


@admin.register(SttProgramParticipation)
class SttProgramParticipationAdmin(ReadOnlyAdminMixin, admin.ModelAdmin):
    """Read-only Admin class for SttProgramParticipation models."""

    search_fields = ["stt__name", "stt__stt_code", "program__slug", "program__name"]
    list_display = ["id", "stt", "program", "status"]
    list_filter = ["program", "status"]
    list_select_related = ["stt", "program"]
