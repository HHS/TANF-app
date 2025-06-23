"""Add users to Django Admin."""

from django import forms
from django.contrib import admin, messages
from django.core.exceptions import ValidationError
from django.http import HttpResponseRedirect
from django.urls import path, reverse
from django.utils.safestring import mark_safe
from django.utils import timezone

from rest_framework.authtoken.models import TokenProxy

from tdpservice.users.models import User, Feedback
from tdpservice.core.utils import ReadOnlyAdminMixin

import logging
logger = logging.getLogger()

class UserForm(forms.ModelForm):
    """Customize the user admin form."""

    class Meta:
        """Define customizations."""

        model = User
        exclude = ['password', 'user_permissions']
        readonly_fields = ['last_login', 'date_joined', 'login_gov_uuid', 'hhs_id', 'access_request']

    def clean(self):
        """Add extra validation for locations based on roles."""
        cleaned_data = super().clean()
        groups = cleaned_data['groups']
        if len(groups) > 1:
            raise ValidationError("User should not have multiple groups")

        feature_flags = cleaned_data.get('feature_flags', {})
        if not feature_flags:
            feature_flags = {}
        cleaned_data['feature_flags'] = feature_flags

        return cleaned_data

class RegionInline(admin.TabularInline):
    """Inline model for many to many relationship."""

    model = User.regions.through
    verbose_name = "Regions"
    verbose_name_plural = "Regions"
    can_delete = True
    ordering = ["-pk"]


class UserAdmin(admin.ModelAdmin):
    """Customize the user admin functions."""

    exclude = ['password', 'user_permissions', 'is_active']
    readonly_fields = ['last_login', 'date_joined', 'login_gov_uuid', 'hhs_id', 'access_request', 'deactivated']
    form = UserForm
    list_filter = ('account_approval_status', 'stt')
    list_display = [
        "username",
        'access_requested_date',
        "stt",
        "account_approval_status",
    ]
    autocomplete_fields = ['stt']

    inlines = [RegionInline]

    def has_add_permission(self, request):
        """Disable User object creation through Django Admin."""
        return False


class FeedbackAdmin(ReadOnlyAdminMixin, admin.ModelAdmin):
    """Customize the feedback admin functions."""

    list_display = [
        "user_list_display",
        "created_at",
        "rating",
        "feedback_list_display",
        "acked",
        "quick_ack",
    ]
    list_filter = ["created_at", "rating", "acked"]
    change_form_template = 'feedback_admin_template.html'
    actions = ['ack_selected_feedback']

    class Meta:
        """Meta for admin view."""

        verbose_name = "Feedback"
        verbose_name_plural = "Feedback"

    def get_urls(self):
        """Add custom URLs for acknowledge action."""
        urls = super().get_urls()
        custom_urls = [
            path(
                '<path:object_id>/acknowledge/',
                self.admin_site.admin_view(self.acknowledge_feedback),
                name='acknowledge_feedback',
            ),
        ]
        return custom_urls + urls

    def acknowledge_feedback(self, request, object_id):
        """Acknowledge the feedback."""
        feedback = self.get_object(request, object_id)
        feedback.acknowledge(request.user)
        return HttpResponseRedirect(
            reverse('admin:users_feedback_changelist')
        )

    def user_list_display(self, obj):
        """Handle user display."""
        return obj.user.username if obj.user is not None else "Anonymous"
    user_list_display.short_description = "User"

    def feedback_list_display(self, obj):
        """Display truncated version of feedback."""
        return obj.feedback[:50] + "..." if len(obj.feedback) > 50 else obj.feedback
    feedback_list_display.short_description = 'Feedback'

    def quick_ack(self, obj):
        """Display quick action button for unacknowledged feedback."""
        if not obj.acked:
            return mark_safe(
                f'<a href="{reverse("admin:acknowledge_feedback", args=[obj.pk])}" '
                f'class="button" style="background-color: #28a745; color: white; padding: 5px; '
                f'margin-right: 5px; text-decoration: none;">Acknowledge</a>'
            )
        return '-'
    quick_ack.short_description = 'Acknowledge'

    def ack_selected_feedback(self, request, queryset):
        """Bulk approve selected change requests."""
        updated = 0
        feedback = queryset.filter(acked=False)

        for f in feedback:
            f.acked = True
            f.reviewed_at = timezone.now()
            f.reviewed_by = request.user
            updated += 1

        Feedback.objects.bulk_update(feedback, ['acked', 'reviewed_at', 'reviewed_by'])

        self.message_user(
            request,
            f"{updated} feedback(s) were successfully acknowledged.",
            messages.SUCCESS if updated > 0 else messages.WARNING
        )
    ack_selected_feedback.short_description = "Acknowledge selected feedback"


admin.site.register(User, UserAdmin)
admin.site.register(Feedback, FeedbackAdmin)
admin.site.unregister(TokenProxy)
