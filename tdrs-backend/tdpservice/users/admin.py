"""Add users to Django Admin."""

import logging

from django import forms
from django.contrib import admin, messages
from django.core.exceptions import ValidationError
from django.http import HttpResponseRedirect
from django.urls import path, reverse
from django.utils import timezone
from django.utils.safestring import mark_safe
from django.utils.html import format_html
from rest_framework.authtoken.models import TokenProxy
from tdpservice.users.models import User, UserChangeRequest, ChangeRequestAuditLog, Feedback
from tdpservice.core.utils import ReadOnlyAdminMixin

logger = logging.getLogger()


class UserForm(forms.ModelForm):
    """Customize the user admin form."""

    class Meta:
        """Define customizations."""

        model = User
        exclude = ['password']
        readonly_fields = ['last_login', 'date_joined', 'login_gov_uuid', 'hhs_id', 'access_request']

    def clean(self):
        """Add extra validation for locations based on roles."""
        cleaned_data = super().clean()
        groups = cleaned_data["groups"]
        if len(groups) > 1:
            raise ValidationError("User should not have multiple groups")

        feature_flags = cleaned_data.get("feature_flags", {})
        if not feature_flags:
            feature_flags = {}
        cleaned_data["feature_flags"] = feature_flags

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

    exclude = ['password', 'is_active']
    readonly_fields = ['last_login', 'date_joined', 'login_gov_uuid', 'hhs_id', 'access_request', 'deactivated']

    form = UserForm
    list_filter = ("account_approval_status", "stt")
    list_display = [
        "username",
        "access_requested_date",
        "stt",
        "account_approval_status",
    ]
    autocomplete_fields = ["stt"]

    inlines = [RegionInline]

    def has_add_permission(self, request):
        """Disable User object creation through Django Admin."""
        return False


class ChangeRequestAuditLogInline(admin.TabularInline):
    """Inline admin for audit logs."""

    model = ChangeRequestAuditLog
    extra = 0
    can_delete = False
    readonly_fields = ['action', 'performed_by', 'timestamp', 'details']
    verbose_name = "Audit Log Entry"
    verbose_name_plural = "Audit Log Entries"

    def has_add_permission(self, request, obj=None):
        """Disable adding audit logs through admin."""
        return False

class UserChangeRequestAdmin(admin.ModelAdmin):
    """Admin interface for user change requests."""

    list_display = [
        'id', 'get_user_url', 'field_name', 'display_current_value',
        'display_requested_value', 'status_with_indicator',
        'requested_at', 'quick_actions'
    ]
    list_filter = ['status', 'field_name', 'requested_at', 'user__username', 'reviewed_by']
    readonly_fields = [
        'user', 'requested_by', 'field_name', 'current_value',
        'requested_value', 'requested_at'
    ]
    inlines = [ChangeRequestAuditLogInline]
    actions = ['approve_selected_requests', 'reject_selected_requests']
    change_form_template = 'admin/user_change_request_form.html'

    fieldsets = (
        ('Request Information', {
            'fields': (
                'user', 'requested_by', 'field_name',
                'current_value', 'requested_value', 'requested_at'
            )
        }),
        ('Review Information', {
            'fields': ('status', 'reviewed_by', 'reviewed_at', 'notes')
        }),
    )

    @admin.display(description="User URL")
    def get_user_url(self, obj):
        """Generate URL to the user detail page."""
        if obj.user:
            return format_html('<a href="{}">{}</a>', reverse('admin:users_user_change', args=[obj.user.pk]), obj.user)
        return '#'

    def get_actions(self, request):
        """Override get_action to remove delete action."""
        actions = super().get_actions(request)
        if 'delete_selected' in actions:
            del actions['delete_selected']
        return actions

    def display_current_value(self, obj):
        """Display truncated current value."""
        return obj.current_value[:50] + '...' if len(obj.current_value) > 50 else obj.current_value
    display_current_value.short_description = 'Current Value'

    def display_requested_value(self, obj):
        """Display truncated requested value."""
        return obj.requested_value[:50] + '...' if len(obj.requested_value) > 50 else obj.requested_value
    display_requested_value.short_description = 'Requested Value'

    def status_with_indicator(self, obj):
        """Display status with color indicator."""
        colors = {
            'pending': 'orange',
            'approved': 'green',
            'rejected': 'red',
        }
        return mark_safe(
            f'<span style="color: {colors[obj.status]};">{obj.get_status_display()}</span>'
        )
    status_with_indicator.short_description = 'Status'

    def quick_actions(self, obj):
        """Display quick action buttons for pending requests."""
        if obj.status == 'pending':
            return mark_safe(
                f'<a href="{reverse("admin:approve_change_request", args=[obj.pk])}" '
                f'class="button" style="background-color: #28a745; color: white; padding: 5px; '
                f'margin-right: 5px; text-decoration: none;">Approve</a> '
                f'<a href="{reverse("admin:reject_change_request", args=[obj.pk])}" '
                f'class="button" style="background-color: #dc3545; color: white; padding: 5px; '
                f'text-decoration: none;">Reject</a>'
            )
        return '-'
    quick_actions.short_description = 'Actions'

    def get_urls(self):
        """Add custom URLs for approve/reject actions."""
        urls = super().get_urls()
        custom_urls = [
            path(
                '<path:object_id>/approve/',
                self.admin_site.admin_view(self.approve_view),
                name='approve_change_request',
            ),
            path(
                '<path:object_id>/reject/',
                self.admin_site.admin_view(self.reject_view),
                name='reject_change_request',
            )
        ]
        return custom_urls + urls

    def approve_view(self, request, object_id):
        """Handle approval of a change request."""
        change_request = self.get_object(request, object_id)
        if change_request and change_request.status == 'pending':
            ChangeRequestAuditLog.objects.create(
                change_request=change_request,
                action='approved',
                performed_by=request.user,
                details={
                    'field': change_request.field_name,
                    'new_value': change_request.requested_value
                }
            )

            success = change_request.approve(request.user)
            if success:
                self.message_user(
                    request,
                    f"Change request for {change_request.field_name} has been approved.",
                    messages.SUCCESS
                )
            else:
                self.message_user(
                    request,
                    "Could not approve change request. It may have already been processed.",
                    messages.ERROR
                )

        return HttpResponseRedirect(
            reverse('admin:users_userchangerequest_changelist')
        )

    def reject_view(self, request, object_id):
        """Handle rejection of a change request."""
        change_request = self.get_object(request, object_id)
        if change_request and change_request.status == 'pending':
            ChangeRequestAuditLog.objects.create(
                change_request=change_request,
                action='rejected',
                performed_by=request.user,
                details={'field': change_request.field_name}
            )

            success = change_request.reject(request.user)
            if success:
                self.message_user(
                    request,
                    f"Change request for {change_request.field_name} has been rejected.",
                    messages.SUCCESS
                )
            else:
                self.message_user(
                    request,
                    "Could not reject change request. It may have already been processed.",
                    messages.ERROR
                )

        return HttpResponseRedirect(
            reverse('admin:users_userchangerequest_changelist')
        )

    def approve_selected_requests(self, request, queryset):
        """Bulk approve selected change requests."""
        updated = 0
        for change_request in queryset.filter(status='pending'):
            ChangeRequestAuditLog.objects.create(
                change_request=change_request,
                action='approved',
                performed_by=request.user,
                details={
                    'field': change_request.field_name,
                    'new_value': change_request.requested_value,
                    'bulk_action': True
                }
            )

            if change_request.approve(request.user):
                updated += 1

        self.message_user(
            request,
            f"{updated} change request(s) were successfully approved.",
            messages.SUCCESS if updated > 0 else messages.WARNING
        )
    approve_selected_requests.short_description = "Approve selected change requests"

    def reject_selected_requests(self, request, queryset):
        """Bulk reject selected change requests."""
        updated = 0
        for change_request in queryset.filter(status='pending'):
            ChangeRequestAuditLog.objects.create(
                change_request=change_request,
                action='rejected',
                performed_by=request.user,
                details={
                    'field': change_request.field_name,
                    'bulk_action': True
                }
            )

            if change_request.reject(request.user):
                updated += 1

        self.message_user(
            request,
            f"{updated} change request(s) were successfully rejected.",
            messages.SUCCESS if updated > 0 else messages.WARNING
        )
    reject_selected_requests.short_description = "Reject selected change requests"

    def save_model(self, request, obj, form, change):
        """Handle status changes when saving the model."""
        if change and 'status' in form.changed_data:
            original_obj = self.model.objects.get(pk=obj.pk)

            # Only process if changing from pending to approved/rejected
            if original_obj.status == 'pending' and obj.status in ['approved', 'rejected']:
                action = f'status_changed_to_{obj.status}'
                ChangeRequestAuditLog.objects.create(
                    change_request=obj,
                    action=action,
                    performed_by=request.user,
                    details={'field': obj.field_name}
                )

                obj.reviewed_by = request.user
                obj.reviewed_at = timezone.now()

                if obj.status == 'approved':
                    user = obj.user
                    field_name = obj.field_name
                    new_value = obj.requested_value

                    setattr(user, field_name, new_value)
                    user.save()

        super().save_model(request, obj, form, change)


class ChangeRequestAuditLogAdmin(ReadOnlyAdminMixin, admin.ModelAdmin):
    """Admin interface for change request audit logs."""

    list_display = ['id', 'action', 'performed_by', 'timestamp']
    list_filter = ['action', 'timestamp']
    search_fields = ['change_request__user__username', 'performed_by__username', 'action']
    readonly_fields = ['change_request', 'action', 'performed_by', 'timestamp', 'details']


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
    change_form_template = "feedback_admin_template.html"
    actions = ["ack_selected_feedback"]

    class Meta:
        """Meta for admin view."""

        verbose_name = "Feedback"
        verbose_name_plural = "Feedback"

    def get_urls(self):
        """Add custom URLs for acknowledge action."""
        urls = super().get_urls()
        custom_urls = [
            path(
                "<path:object_id>/acknowledge/",
                self.admin_site.admin_view(self.acknowledge_feedback),
                name="acknowledge_feedback",
            ),
        ]
        return custom_urls + urls

    def acknowledge_feedback(self, request, object_id):
        """Acknowledge the feedback."""
        feedback = self.get_object(request, object_id)
        feedback.acknowledge(request.user)
        return HttpResponseRedirect(reverse("admin:users_feedback_changelist"))

    def user_list_display(self, obj):
        """Handle user display."""
        return (
            obj.user.username
            if not obj.anonymous and obj.user is not None
            else "Anonymous"
        )

    user_list_display.short_description = "User"

    def feedback_list_display(self, obj):
        """Display truncated version of feedback."""
        return obj.feedback[:50] + "..." if len(obj.feedback) > 50 else obj.feedback

    feedback_list_display.short_description = "Feedback"

    def quick_ack(self, obj):
        """Display quick action button for unacknowledged feedback."""
        if not obj.acked:
            return mark_safe(
                f'<a href="{reverse("admin:acknowledge_feedback", args=[obj.pk])}" '
                f'class="button" style="background-color: #28a745; color: white; padding: 5px; '
                f'margin-right: 5px; text-decoration: none;">Acknowledge</a>'
            )
        return "-"

    quick_ack.short_description = "Acknowledge"

    def ack_selected_feedback(self, request, queryset):
        """Bulk approve selected change requests."""
        updated = 0
        feedback = queryset.filter(acked=False)

        for f in feedback:
            f.acked = True
            f.reviewed_at = timezone.now()
            f.reviewed_by = request.user
            updated += 1

        Feedback.objects.bulk_update(feedback, ["acked", "reviewed_at", "reviewed_by"])

        self.message_user(
            request,
            f"{updated} feedback(s) were successfully acknowledged.",
            messages.SUCCESS if updated > 0 else messages.WARNING,
        )

    ack_selected_feedback.short_description = "Acknowledge selected feedback"


admin.site.register(User, UserAdmin)
admin.site.register(Feedback, FeedbackAdmin)
admin.site.unregister(TokenProxy)
admin.site.register(UserChangeRequest, UserChangeRequestAdmin)
admin.site.register(ChangeRequestAuditLog, ChangeRequestAuditLogAdmin)
