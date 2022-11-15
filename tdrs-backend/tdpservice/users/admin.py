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
        group = groups.first()
        location_type = cleaned_data['location_type']
        role_location_type_map = {
            'OFA Regional Staff': 'region',
            'Data Analyst': 'stt',
            'Developer': 'stt'
        }

        # allow saving the user without a group type
        # updating a user's account approval status without assigning a group used to throw an error
        # a group assignment can give the user access to some frontend features regardless of `account_approval_status`
        # users in `Pending` status should not have a group assigned
        if group is not None:
            correct_location_type = role_location_type_map.get(group.name)
            location_based_role = group.name in ('OFA Regional Staff', 'Data Analyst', 'Developer')

            if (location_based_role and (location_type and location_type.name != correct_location_type)):

                raise ValidationError("Incorrect location type for role")

            if not location_based_role and cleaned_data['location_type']:

                raise ValidationError(
                    "Users other than Regional Staff and data analysts do not get assigned a location")

        return cleaned_data


class UserAdmin(admin.ModelAdmin):
    """Customize the user admin functions."""

    exclude = ['password', 'user_permissions', 'is_active']
    readonly_fields = ['last_login', 'date_joined', 'login_gov_uuid', 'hhs_id', 'access_request', 'deactivated']
    form = UserForm
    list_filter = ('account_approval_status',)

    def has_add_permission(self, request):
        """Disable User object creation through Django Admin."""
        return False


admin.site.register(User, UserAdmin)
admin.site.unregister(TokenProxy)
