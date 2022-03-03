class ReadOnlyAdminMixin:
    """Mixin to enforce read-only models in Django Admin.
        e.g. => class LogEntryAdmin(ReadOnlyAdminMixin, admin.ModelAdmin)
        This mixin must be first in the param list due to the way Python
        handles Method Order Resolution for multiple inheritance.
    """
    def has_add_permission(self, request):
        """Deny all add permissions."""
        return False

    def has_change_permission(self, request, obj=None):
        """Deny all change permissions."""
        return False

    def has_delete_permission(self, request, obj=None):
        """Deny all delete permissions."""
        return False
