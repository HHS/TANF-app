"""Admin classes for core app models."""
from django.contrib import admin
from django.contrib.admin.models import LogEntry
from django.forms import ModelForm
from django.urls import reverse
from django.utils.html import escape
from django.utils.safestring import mark_safe
from django_json_widget.widgets import JSONEditorWidget

from tdpservice.core.models import FeatureFlag
from tdpservice.core.utils import ReadOnlyAdminMixin

# LogEntry needs to be de-registered first before registering a custom Admin Model below.
admin.site.unregister(LogEntry)


@admin.register(LogEntry)
class LogEntryAdmin(ReadOnlyAdminMixin, admin.ModelAdmin):
    """Customize and restrict the LogEntry table in Django Admin."""

    date_hierarchy = "action_time"

    list_filter = ["user", "content_type", "action_flag"]

    search_fields = ["object_repr", "change_message"]

    list_display = [
        "action_time",
        "user",
        "content_type",
        "object_link",
        "action_flag",
        "change_message",
    ]

    exclude = ["object_id"]

    def object_link(self, obj):
        """Create a link to to corresponding objects for a given LogEntry."""
        ct = obj.content_type
        link = '<a href="%s">%s</a>' % (
            reverse(
                "admin:%s_%s_change" % (ct.app_label, ct.model), args=[obj.object_id]
            ),
            escape(obj.object_repr),
        )
        return mark_safe(link)

    object_link.admin_order_field = "object_repr"
    object_link.short_description = "object"


class FeatureFlagAdminForm(ModelForm):
    """Custom form for FeatureFlag admin with JSON editor widget."""

    class Meta:
        """Metadata."""

        model = FeatureFlag
        fields = '__all__'
        widgets = {
            'config': JSONEditorWidget(options={
                'mode': 'code',
                'modes': ['code', 'tree'],
                'search': True
            })
        }


@admin.register(FeatureFlag)
class FeatureFlagAdmin(admin.ModelAdmin):
    """Admin interface for FeatureFlag model."""

    form = FeatureFlagAdminForm

    list_display = ['feature_name', 'enabled', 'updated_at']
    list_filter = ['enabled', 'created_at', 'updated_at']
    search_fields = ['feature_name', 'description']
    readonly_fields = ['created_at', 'updated_at']

    fieldsets = (
        ('Feature Identity', {
            'fields': ('feature_name', 'description')
        }),
        ('Configuration', {
            'fields': ('enabled', 'config'),
            'description': 'Toggle the feature on/off and configure feature-specific settings'
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def has_delete_permission(self, request, obj=None):
        """Only allow superusers to delete feature flags."""
        return request.user.is_superuser
