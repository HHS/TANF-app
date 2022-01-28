"""Add users to Django Admin."""

import logging

from django import forms
from django.contrib import admin
from django.core.exceptions import ValidationError

from rest_framework.authtoken.models import TokenProxy

from .models import User

logger = logging.getLogger()

class UserForm(forms.ModelForm):
    """Customize the user admin form."""

    class Meta:
        """Define customizations."""

        model = User
        exclude = ['password', 'user_permissions']
        readonly_fields = ['last_login', 'date_joined', 'login_gov_uuid', 'hhs_id']

    def clean(self):
        """Add extra validation for locations based on roles."""
        cleaned_data = super().clean()
        groups = cleaned_data['groups']
        logger.info(cleaned_data)
        logger.info(self.instance.groups)
        if len(groups) > 1:
            raise ValidationError("User should not have multiple groups")
        group = groups.first()
        location_type = cleaned_data['location_type']
        role_location_type_map = {
            'OFA Regional Staff': 'region',
            'Data Analyst': 'stt'
        }

        correct_location_type = role_location_type_map.get(group.name)
        location_based_role = (group.name == 'OFA Regional Staff' or group.name == 'Data Analyst')

        if (location_based_role and (location_type and location_type.name != correct_location_type)):

            raise ValidationError("Incorrect location type for role")

        if not location_based_role and cleaned_data['location_type']:

            raise ValidationError(
                "Users other than Regional Staff and data analysts do not get assigned a location")
        return cleaned_data


class UserAdmin(admin.ModelAdmin):
    """Customize the user admin functions."""

    exclude = ['password', 'user_permissions', 'is_active']
    readonly_fields = ['last_login', 'date_joined', 'login_gov_uuid', 'hhs_id']
    form = UserForm


admin.site.register(User, UserAdmin)
admin.site.unregister(TokenProxy)
