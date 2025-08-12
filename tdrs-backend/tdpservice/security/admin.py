"""Admin classes for the tdpservice.security app."""
from django.contrib import admin

from tdpservice.core.admin import ReadOnlyAdminMixin
from tdpservice.security.models import ClamAVFileScan, OwaspZapScan, SecurityEventToken


@admin.register(ClamAVFileScan)
class ClamAVFileScanAdmin(ReadOnlyAdminMixin, admin.ModelAdmin):
    """Admin interface for Clam AV File Scan instances."""

    list_display = [
        "scanned_at",
        "result",
        "uploaded_by",
        "file_name",
        "file_size_human",
        "file_shasum",
    ]

    list_filter = [
        "scanned_at",
        "result",
        "uploaded_by",
    ]

    @admin.display(description="File Size")
    def file_size_human(self, obj):
        """Return human friendly file size, converted to appropriate unit."""
        return obj.file_size_humanized


@admin.register(OwaspZapScan)
class OwaspZapScanAdmin(ReadOnlyAdminMixin, admin.ModelAdmin):
    """Admin interface for OWASP Zap Scan reports."""

    list_display = [
        "scanned_at",
        "result",
        "app_target",
        "pass_count",
        "fail_count",
        "warn_count",
    ]

    list_filter = [
        "scanned_at",
        "app_target",
    ]


@admin.register(SecurityEventToken)
class SecurityEventTokenAdmin(admin.ModelAdmin, ReadOnlyAdminMixin):
    """Admin interface for Security Event Tokens."""

    list_display = (
        "event_type",
        "user",
        "email",
        "issued_at",
        "received_at",
        "processed",
    )
    list_filter = ("user", "event_type", "processed", "received_at")
    search_fields = ("user__username", "user__email", "email", "event_type")
    readonly_fields = (
        "id",
        "jwt_id",
        "issuer",
        "issued_at",
        "received_at",
        "event_data",
    )
    date_hierarchy = "received_at"

    def get_actions(self, request):
        """Override get_action to remove delete action."""
        actions = super().get_actions(request)
        if "delete_selected" in actions:
            del actions["delete_selected"]
        return actions
