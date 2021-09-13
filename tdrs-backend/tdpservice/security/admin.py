from django.contrib import admin

from tdpservice.security.models import ClamAVFileScan


@admin.register(ClamAVFileScan)
class ClamAVFileScanAdmin(admin.ModelAdmin):

    list_display = [
        'scanned_at',
        'file_name',
        'file_shasum',
        'result',
        'uploaded_by',
    ]

    list_filter = [
        'result',
        'uploaded_by',
    ]
