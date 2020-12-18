from django.contrib import admin
from .models import User
from rest_framework.authtoken.models import Token


admin.site.register(User)
