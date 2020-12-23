"""Add STTs and Regions to Django Admin."""

from django.contrib import admin
from .models import STT, Region


admin.site.register(STT)
admin.site.register(Region)
