"""Admin class for ReportFile objects."""
from django.contrib import admin
from .models import ReportFile


@admin.register(ReportFile)
class ReportFileAdmin(admin.ModelAdmin):
    """Enforce read-only on the Report File admin form."""

    def has_add_permission(self, request):
        """Deny the user permission to create Report Files in Django Admin."""
        return False

    def has_change_permission(self, request, obj=None):
        """Deny the user permission to update Report Files in Django Admin."""
        return False

    def has_delete_permission(self, request, obj=None):
        """Deny the user permission to delete Report Files in Django Admin."""
        return False

    def has_view_permission(self, request, obj=None):
        """Only allow superusers to be able to view Report Files."""
        return request.user.is_superuser
