"""Add STTs and Regions to Django Admin."""

from django.contrib import admin
from .models import STT, Region
from ..core.utils import ReadOnlyAdminMixin


@admin.register(STT)
class STTAdmin(ReadOnlyAdminMixin, admin.ModelAdmin):
    """Read-only Admin class for STT models."""

    search_fields = ['name', 'stt_code']

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
