"""Add users to Django Admin."""

import logging

from django.contrib import admin, messages
from django.http import HttpResponseRedirect
from django.urls import path, reverse
from django.utils import timezone
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from django import forms
from django.core.exceptions import ValidationError

from rest_framework.authtoken.models import TokenProxy

from tdpservice.core.utils import ReadOnlyAdminMixin
from tdpservice.users.filters import ActiveStatusListFilter
from tdpservice.users.forms import UserForm
from tdpservice.users.models import (
    AccountApprovalStatusChoices,
    ChangeRequestAuditLog,
    Feedback,
    User,
    UserChangeRequest,
)

logger = logging.getLogger()

class RegionsInlineFormSet(forms.models.BaseInlineFormSet):
    """Custom formset for region inlines."""

    def clean(self):
        """Validate region inlines."""
        super().clean()
        cleaned_data = self.cleaned_data[0]
        user = cleaned_data.get("user")
        """
        Have to validate regions against existing and new user roles.
        Currently, if form request includes a new region and user roles, then changes
        are validated against only the existing user roles.
        """
        if user:
            regional = user.regions.all().count() + len(cleaned_data.get("regions", []))
            existing_roles_not_regional = (
                not user.is_regional_staff
                and not user.is_data_analyst
                and not user.is_developer
            )
            coming_roles = cleaned_data.get("roles", [])
            coming_roles_not_regional = any(
                role in coming_roles
                for role in ["Regional Staff", "Data Analyst", "Developer"]
            )
            if regional and user.stt:
                raise ValidationError(
                    "A user may only have a Region or STT assigned, not both."
                )
            elif existing_roles_not_regional or coming_roles_not_regional:
                raise ValidationError(
                    "Users other than Regional Staff, Developers, Data Analysts do not get assigned a location."
                )


class RegionInline(admin.TabularInline):
    """Inline model for many to many relationship."""

    model = User.regions.through
    verbose_name = "Regions"
    verbose_name_plural = "Regions"
    can_delete = True
    ordering = ["-pk"]
    formset = RegionsInlineFormSet


class UserAdmin(admin.ModelAdmin):
    """Customize the user admin functions."""

    exclude = ["password", "is_active"]
    readonly_fields = [
        "last_login",
        "date_joined",
        "login_gov_uuid",
        "hhs_id",
    ]

    form = UserForm
    list_filter = ("account_approval_status", "stt", ActiveStatusListFilter)
    list_display = [
        "username",
        "access_requested_date",
        "stt",
        "account_approval_status",
    ]
    autocomplete_fields = ["stt"]

    inlines = [RegionInline]

    actions = ['soft_delete_users']

    def get_object(self, request, object_id, from_field=None):
        """Get the user object, allowing for None if not found."""
        queryset = self.model._base_manager.all()
        return queryset.filter(pk=object_id).first()

    def get_actions(self, request):
        """Override get_action to remove delete action."""
        actions = super().get_actions(request)
        if 'delete_selected' in actions:
            del actions['delete_selected']
        return actions

    @admin.action(description='Soft delete selected users (keep related data)')
    def soft_delete_users(self, request, queryset):
        """Soft delete selected users using deactivated flag."""
        updated = 0
        for user in queryset:
            if not user.is_deactivated:
                user.account_approval_status = AccountApprovalStatusChoices.DEACTIVATED
                user.save()
                updated += 1
        self.message_user(request, f"Soft-deleted {updated} user(s).")

    def has_add_permission(self, request):
        """Disable User object creation through Django Admin."""
        return False

    def get_queryset(self, request):
        """Customize queryset to hide inactive users by default."""
        qs = super().get_queryset(request)
        # Hide inactive by default unless filter is applied
        if "active_status" not in request.GET:
            qs = qs.exclude(account_approval_status=AccountApprovalStatusChoices.DEACTIVATED)
        return qs

    def save_form(self, request, form, change):
        """Override save_form to prevent saving the form when not changing."""
        return form.save(commit=False)

class HasAttachmentFilter(admin.SimpleListFilter):
    """Filter feedback based if it has datafiles associated or not."""

    title = "Has attached data files"
    parameter_name = "has_attachments"

    def lookups(self, request, model_admin):
        """Options for HasAttachmentFilter."""
        return [
            ("yes", "Yes"),
            ("no", "No"),
        ]

    def queryset(self, request, queryset):
        """Select the correct queryset."""
        if self.value() == "yes":
            return queryset.filter(attachments__isnull=False).distinct()
        if self.value() == "no":
            return queryset.filter(attachments__isnull=True)


class ChangeRequestAuditLogInline(admin.TabularInline):
    """Inline admin for audit logs."""

    model = ChangeRequestAuditLog
    extra = 0
    can_delete = False
    readonly_fields = ["action", "performed_by", "timestamp", "details"]
    verbose_name = "Audit Log Entry"
    verbose_name_plural = "Audit Log Entries"

    def has_add_permission(self, request, obj=None):
        """Disable adding audit logs through admin."""
        return False


class UserChangeRequestAdmin(admin.ModelAdmin):
    """Admin interface for user change requests."""

    list_display = [
        "id",
        "get_user_url",
        "field_name",
        "display_current_value",
        "display_requested_value",
        "status_with_indicator",
        "requested_at",
        "quick_actions",
    ]
    list_filter = [
        "status",
        "field_name",
        "requested_at",
        "user__username",
        "reviewed_by",
    ]
    readonly_fields = [
        "user",
        "requested_by",
        "field_name",
        "current_value",
        "requested_value",
        "requested_at",
    ]
    inlines = [ChangeRequestAuditLogInline]
    actions = ["approve_selected_requests", "reject_selected_requests"]
    change_form_template = "admin/user_change_request_form.html"

    fieldsets = (
        (
            "Request Information",
            {
                "fields": (
                    "user",
                    "requested_by",
                    "field_name",
                    "current_value",
                    "requested_value",
                    "requested_at",
                )
            },
        ),
        (
            "Review Information",
            {"fields": ("status", "reviewed_by", "reviewed_at", "notes")},
        ),
    )

    @admin.display(description="User URL")
    def get_user_url(self, obj):
        """Generate URL to the user detail page."""
        if obj.user:
            return format_html(
                '<a href="{}">{}</a>',
                reverse("admin:users_user_change", args=[obj.user.pk]),
                obj.user,
            )
        return "#"

    def get_actions(self, request):
        """Override get_action to remove delete action."""
        actions = super().get_actions(request)
        if "delete_selected" in actions:
            del actions["delete_selected"]
        return actions

    def display_current_value(self, obj):
        """Display truncated current value."""
        return (
            obj.current_value[:50] + "..."
            if len(obj.current_value) > 50
            else obj.current_value
        )

    display_current_value.short_description = "Current Value"

    def display_requested_value(self, obj):
        """Display truncated requested value."""
        return (
            obj.requested_value[:50] + "..."
            if len(obj.requested_value) > 50
            else obj.requested_value
        )

    display_requested_value.short_description = "Requested Value"

    def status_with_indicator(self, obj):
        """Display status with color indicator."""
        colors = {
            "pending": "orange",
            "approved": "green",
            "rejected": "red",
        }
        return mark_safe(
            f'<span style="color: {colors[obj.status]};">{obj.get_status_display()}</span>'
        )

    status_with_indicator.short_description = "Status"

    def quick_actions(self, obj):
        """Display quick action buttons for pending requests."""
        if obj.status == "pending":
            return mark_safe(
                f'<a href="{reverse("admin:approve_change_request", args=[obj.pk])}" '
                f'class="button" style="background-color: #28a745; color: white; padding: 5px; '
                f'margin-right: 5px; text-decoration: none;">Approve</a> '
                f'<a href="{reverse("admin:reject_change_request", args=[obj.pk])}" '
                f'class="button" style="background-color: #dc3545; color: white; padding: 5px; '
                f'text-decoration: none;">Reject</a>'
            )
        return "-"

    quick_actions.short_description = "Actions"

    def get_urls(self):
        """Add custom URLs for approve/reject actions."""
        urls = super().get_urls()
        custom_urls = [
            path(
                "<path:object_id>/approve/",
                self.admin_site.admin_view(self.approve_view),
                name="approve_change_request",
            ),
            path(
                "<path:object_id>/reject/",
                self.admin_site.admin_view(self.reject_view),
                name="reject_change_request",
            ),
        ]
        return custom_urls + urls

    def approve_view(self, request, object_id):
        """Handle approval of a change request."""
        change_request = self.get_object(request, object_id)
        if change_request and change_request.status == "pending":
            ChangeRequestAuditLog.objects.create(
                change_request=change_request,
                action="approved",
                performed_by=request.user,
                details={
                    "field": change_request.field_name,
                    "new_value": change_request.requested_value,
                },
            )

            success = change_request.approve(request.user)
            if success:
                self.message_user(
                    request,
                    f"Change request for {change_request.field_name} has been approved.",
                    messages.SUCCESS,
                )
            else:
                self.message_user(
                    request,
                    "Could not approve change request. It may have already been processed.",
                    messages.ERROR,
                )

        return HttpResponseRedirect(reverse("admin:users_userchangerequest_changelist"))

    def reject_view(self, request, object_id):
        """Handle rejection of a change request."""
        change_request = self.get_object(request, object_id)
        if change_request and change_request.status == "pending":
            ChangeRequestAuditLog.objects.create(
                change_request=change_request,
                action="rejected",
                performed_by=request.user,
                details={"field": change_request.field_name},
            )

            success = change_request.reject(request.user)
            if success:
                self.message_user(
                    request,
                    f"Change request for {change_request.field_name} has been rejected.",
                    messages.SUCCESS,
                )
            else:
                self.message_user(
                    request,
                    "Could not reject change request. It may have already been processed.",
                    messages.ERROR,
                )

        return HttpResponseRedirect(reverse("admin:users_userchangerequest_changelist"))

    def approve_selected_requests(self, request, queryset):
        """Bulk approve selected change requests."""
        updated = 0
        for change_request in queryset.filter(status="pending"):
            ChangeRequestAuditLog.objects.create(
                change_request=change_request,
                action="approved",
                performed_by=request.user,
                details={
                    "field": change_request.field_name,
                    "new_value": change_request.requested_value,
                    "bulk_action": True,
                },
            )

            if change_request.approve(request.user):
                updated += 1

        self.message_user(
            request,
            f"{updated} change request(s) were successfully approved.",
            messages.SUCCESS if updated > 0 else messages.WARNING,
        )

    approve_selected_requests.short_description = "Approve selected change requests"

    def reject_selected_requests(self, request, queryset):
        """Bulk reject selected change requests."""
        updated = 0
        for change_request in queryset.filter(status="pending"):
            ChangeRequestAuditLog.objects.create(
                change_request=change_request,
                action="rejected",
                performed_by=request.user,
                details={"field": change_request.field_name, "bulk_action": True},
            )

            if change_request.reject(request.user):
                updated += 1

        self.message_user(
            request,
            f"{updated} change request(s) were successfully rejected.",
            messages.SUCCESS if updated > 0 else messages.WARNING,
        )

    reject_selected_requests.short_description = "Reject selected change requests"

    def save_model(self, request, obj, form, change):
        """Handle status changes when saving the model."""
        if change and "status" in form.changed_data:
            original_obj = self.model.objects.get(pk=obj.pk)

            # Only process if changing from pending to approved/rejected
            if original_obj.status == "pending" and obj.status in [
                "approved",
                "rejected",
            ]:
                action = f"status_changed_to_{obj.status}"
                ChangeRequestAuditLog.objects.create(
                    change_request=obj,
                    action=action,
                    performed_by=request.user,
                    details={"field": obj.field_name},
                )

                obj.reviewed_by = request.user
                obj.reviewed_at = timezone.now()

                if obj.status == "approved":
                    user = obj.user
                    field_name = obj.field_name
                    new_value = obj.requested_value

                    setattr(user, field_name, new_value)
                    user.save()

        super().save_model(request, obj, form, change)


class ChangeRequestAuditLogAdmin(ReadOnlyAdminMixin, admin.ModelAdmin):
    """Admin interface for change request audit logs."""

    list_display = ["id", "action", "performed_by", "timestamp"]
    list_filter = ["action", "timestamp"]
    search_fields = [
        "change_request__user__username",
        "performed_by__username",
        "action",
    ]
    readonly_fields = [
        "change_request",
        "action",
        "performed_by",
        "timestamp",
        "details",
    ]


class FeedbackAdmin(ReadOnlyAdminMixin, admin.ModelAdmin):
    """Customize the feedback admin functions."""

    list_display = [
        "user_list_display",
        "created_at",
        "rating",
        "feedback_type",
        "feedback_list_display",
        "quick_mark",
    ]
    readonly_fields = ("attached_data_files_list",)
    list_filter = ["created_at", "rating", "read", HasAttachmentFilter]
    change_form_template = "feedback_admin_template.html"
    actions = ["mark_selected_feedback_as_read"]

    class Meta:
        """Meta for admin view."""

        verbose_name = "Feedback"
        verbose_name_plural = "Feedback"

    def get_urls(self):
        """Add custom URLs for mark as read action."""
        urls = super().get_urls()
        custom_urls = [
            path(
                "<path:object_id>/mark-as-read/",
                self.admin_site.admin_view(self.mark_feedback_as_read),
                name="mark_feedback_as_read",
            ),
        ]
        return custom_urls + urls

    def mark_feedback_as_read(self, request, object_id):
        """Mark the feedback as read."""
        feedback = self.get_object(request, object_id)
        feedback.mark_as_read(request.user)
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

    def attached_data_files_list(self, obj):
        """Show a list of data files attached to this feedback."""
        files = obj.attached_data_files()
        if not files:
            return "No attached files"

        links = []
        for f in files:
            # Show file section, year, quarter as a link to its admin change page
            url = reverse("admin:data_files_datafile_change", args=[f.id])
            # url = f"/admin/data_files/datafile/{f.id}/change/"
            label = f"{f.section} ({f.year} {f.quarter})"
            links.append(f"<a href='{url}' target='_blank'>{label}</a>")

        return mark_safe("<br>".join(links))

    attached_data_files_list.short_description = "Attached Data Files"

    def quick_mark(self, obj):
        """Display quick action button for unread feedback."""
        if not obj.read:
            return mark_safe(
                f'<a href="{reverse("admin:mark_feedback_as_read", args=[obj.pk])}" '
                f'class="button" style="background-color: #28a745; color: white; padding: 5px; '
                f'margin-right: 5px; text-decoration: none;">Mark as Read</a>'
            )
        return mark_safe(
            '<img src="/static/admin/img/icon-yes.svg" alt="True" /> <span style="color: #4B8340;">Read</span>'
        )

    quick_mark.short_description = "Status"

    def mark_selected_feedback_as_read(self, request, queryset):
        """Bulk mark feedback as read."""
        updated = 0
        feedback = queryset.filter(read=False)

        for f in feedback:
            f.read = True
            f.reviewed_at = timezone.now()
            f.reviewed_by = request.user
            updated += 1

        Feedback.objects.bulk_update(feedback, ["read", "reviewed_at", "reviewed_by"])

        self.message_user(
            request,
            f"{updated} feedback(s) were successfully marked as read.",
            messages.SUCCESS if updated > 0 else messages.WARNING,
        )

    mark_selected_feedback_as_read.short_description = "Mark selected as read"


admin.site.register(User, UserAdmin)
admin.site.register(Feedback, FeedbackAdmin)
admin.site.unregister(TokenProxy)
admin.site.register(UserChangeRequest, UserChangeRequestAdmin)
admin.site.register(ChangeRequestAuditLog, ChangeRequestAuditLogAdmin)
