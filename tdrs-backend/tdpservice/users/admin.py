"""Add users to Django Admin."""

from django import forms
from django.contrib import admin
from .models import User
from rest_framework.authtoken.models import TokenProxy
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


class UserForm(forms.ModelForm):
    """Customize the user admin form."""

    class Meta:
        """Define customizations."""

        model = User
        exclude = ['password', 'user_permissions']
        readonly_fields = ['last_login', 'date_joined', 'login_gov_uuid', 'hhs_id']
 

class UserAdmin(admin.ModelAdmin):
    """Customize the user admin functions."""

    exclude = ['password', 'user_permissions', 'is_active']
    readonly_fields = ['last_login', 'date_joined', 'login_gov_uuid', 'hhs_id']
    form = UserForm
    # def save_model(self, request, obj, form, change):
    #     try:
    #         obj.save()
    #     except ValidationError as e:
            
    #         raise forms.ValidationError(_(str(e)))


admin.site.register(User, UserAdmin)
admin.site.unregister(TokenProxy)
