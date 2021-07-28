"""Admin class for DataFile objects."""
from django.contrib import admin
from .models import DataFile


@admin.register(DataFile)
class DataFileAdmin(admin.ModelAdmin):
    """Enforce read-only on the Data File admin form."""

    def has_add_permission(self, request):
        """Deny the user permission to create Data Files in Django Admin."""
        return False

    def has_change_permission(self, request, obj=None):
        """Deny the user permission to update Data Files in Django Admin."""
        return False

    def has_delete_permission(self, request, obj=None):
        """Deny the user permission to delete Data Files in Django Admin."""
        return False

    def has_view_permission(self, request, obj=None):
        """Only allow superusers to be able to view Data Files."""
        return request.user.is_superuser
