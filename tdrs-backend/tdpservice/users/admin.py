"""Add users to Django Admin."""

from django import forms
from django.contrib import admin
from django.core.exceptions import ValidationError

from rest_framework.authtoken.models import TokenProxy

from .models import User


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

        return cleaned_data


class UserAdmin(admin.ModelAdmin):
    """Customize the user admin functions."""

    exclude = ['password', 'user_permissions', 'is_active']
    readonly_fields = ['last_login', 'date_joined', 'login_gov_uuid', 'hhs_id', 'access_request', 'deactivated']
    form = UserForm
    list_filter = ('account_approval_status', 'region', 'stt')
    list_display = [
        "username",
        'access_requested_date',
        "region",
        "stt",
        "account_approval_status",
    ]
    autocomplete_fields = ['stt']

    def has_add_permission(self, request):
        """Disable User object creation through Django Admin."""
        return False


admin.site.register(User, UserAdmin)
admin.site.unregister(TokenProxy)
