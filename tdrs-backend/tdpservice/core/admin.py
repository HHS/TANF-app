"""Admin class for LogEntry objects."""
from django.contrib import admin
from django.contrib.admin.models import LogEntry
from django.utils.html import escape
from django.urls import reverse
from django.utils.safestring import mark_safe

admin.site.unregister(LogEntry)


@admin.register(LogEntry)
class LogEntryAdmin(admin.ModelAdmin):
    """Customize and restrict the LogEntry table in Django Admin."""

    date_hierarchy = 'action_time'

    list_filter = [
        'user',
        'content_type',
        'action_flag'
    ]

    search_fields = [
        'object_repr',
        'change_message'
    ]

    list_display = [
        'action_time',
        'user',
        'content_type',
        'object_link',
        'action_flag',
    ]

    def has_add_permission(self, request):
        """Deny the user permission to create LogEntry objects in Django Admin."""
        return False

    def has_change_permission(self, request, obj=None):
        """Deny the user permission to update LogEntry objects in Django Admin."""
        return False

    def has_delete_permission(self, request, obj=None):
        """Deny the user permission to delete LogEntry objects in Django Admin."""
        return False

    def has_view_permission(self, request, obj=None):
        """Only allow superusers to be able to view the LogEntry table."""
        return request.user.is_superuser

    def object_link(self, obj):
        """Create a link to to corresponding objects for a given LogEntry."""
        ct = obj.content_type
        link = '<a href="%s">%s</a>' % (
            reverse('admin:%s_%s_change' % (ct.app_label, ct.model),
                    args=[obj.object_id]),
            escape(obj.object_repr),
        )
        return mark_safe(link)

    object_link.admin_order_field = "object_repr"
    object_link.short_description = "object"
