"""Add users to Django Admin."""

from django import forms
from django.contrib import admin
from django.core.exceptions import ValidationError

from rest_framework.authtoken.models import TokenProxy

from .models import User

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
    can_delete = False
    ordering = ["-pk"]

    def has_change_permission(self, request, obj=None):
        """Read only permissions."""
        return False


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


admin.site.register(User, UserAdmin)
admin.site.unregister(TokenProxy)
