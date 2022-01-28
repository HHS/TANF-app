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
        cleaned_data = super().clean()
        # data=self.cleaned_data['groups']
        # if self.cleaned_data['groups'].first().name == 'Data Analyst':
        #     if
        # return data
        groups=cleaned_data['groups']
        logger.info(cleaned_data)
        logger.info(self.instance.groups)
        if len(groups) > 1:
            raise ValidationError("User should not have multiple groups")
        group=groups.first()
        location_type=cleaned_data['location_type']
        role_location_type_map={
            'OFA Regional Staff':'region',
            'Data Analyst':'stt'
        }
        correct_location_type=role_location_type_map.get(group.name)
        location_based_role =(group.name == 'OFA Regional Staff' or group.name == 'Data Analyst')
        if (location_based_role and
            (cleaned_data['location_type'] and cleaned_data['location_type'].name != correct_location_type)):
            raise ValidationError("Incorrect location type for role")

        if (not location_based_role) and  cleaned_data['location_type']:
            raise ValidationError(
                "Users other than Regional Staff and data analysts do not get assigned a location")
        return cleaned_data

    # def save(self, commit=True):
    #     instance = super(UserForm, self).save(commit=False)
    #     groups=self.groups
    #     instance.groups.clear()
    #     instance.location_type=None
    #     instance.location_id=None
    #     instance.save()
    #     instance.groups.add(groups.first())
    #     instance.location_type=self.location_type
    #     instance.location_id=self.location_id
    #     instance.save()
    #     return instance

class UserAdmin(admin.ModelAdmin):
    """Customize the user admin functions."""

    exclude = ['password', 'user_permissions', 'is_active']
    readonly_fields = ['last_login', 'date_joined', 'login_gov_uuid', 'hhs_id']
    form = UserForm


admin.site.register(User, UserAdmin)
admin.site.unregister(TokenProxy)
