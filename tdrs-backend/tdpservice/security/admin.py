"""Admin classes for the tdpservice.security app."""
from django.contrib import admin

from tdpservice.security.models import ClamAVFileScan


@admin.register(ClamAVFileScan)
class ClamAVFileScanAdmin(admin.ModelAdmin):
    """Admin interface for Clam AV File Scan instances."""

    list_display = [
        'scanned_at',
        'result',
        'uploaded_by',
        'file_name',
        'file_size_human',
        'file_shasum',
    ]

    list_filter = [
        'result',
        'uploaded_by',
    ]

    @admin.display(description='File Size')
    def file_size_human(self, obj):
        """Return human friendly file size, converted to appropriate unit."""
        return obj.file_size_humanized
