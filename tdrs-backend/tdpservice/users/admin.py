"""UserAdmin Model Declaration."""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User


@admin.register(User)
class UserAdmin(UserAdmin):
    """Default pass for testing."""

    pass
