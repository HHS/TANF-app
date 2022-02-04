"""Add users to Django Admin."""

from django import forms
from django.contrib import admin
from .models import User
from rest_framework.authtoken.models import TokenProxy


class UserForm(forms.ModelForm):
    """Customize the user admin form."""

    class Meta:
        """Define customizations."""

        model = User
        exclude = ['password', 'user_permissions']
        readonly_fields = ['last_login', 'date_joined', 'login_gov_uuid', 'hhs_id', 'access_request']


class UserAdmin(admin.ModelAdmin):
    """Customize the user admin functions."""

    exclude = ['password', 'user_permissions', 'is_active']
    readonly_fields = ['last_login', 'date_joined', 'login_gov_uuid', 'hhs_id', 'access_request']
    form = UserForm
    list_filter = ('access_request',)


admin.site.register(User, UserAdmin)
admin.site.unregister(TokenProxy)
