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
        'change_message',
    ]

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
