from django.db import models
from django.contrib.auth.models import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.utils import timezone
from django.conf import settings

from .managers import TANFUserManager


# Create your models here.

class TANFUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField('email address', unique=True)
    password = None
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    date_joined = models.DateTimeField(default=timezone.now)
    last_login = models.DateTimeField(default=timezone.now)
    stt_code = models.CharField('State, Tribe, or Territory code', max_length=32, default='')

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = TANFUserManager()

    def __str__(self):
        return self.email

    def has_perm(self, perm, obj=None):
        "Does the user have a specific permission?"

        # if we are staff, then we can admin everything!
        return self.is_staff

    def check_password(self, pw=None):
        "if we are not doing login.gov, then say they are fine every time"
        if settings.NOLOGINGOV:
            return True
        else:
            return False
