"""Add users to Django Admin."""

from django.contrib import admin
from .models import User
from rest_framework.authtoken.models import TokenProxy


admin.site.register(User)
admin.site.unregister(TokenProxy)
