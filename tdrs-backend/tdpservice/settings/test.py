"""Define configuration settings for local environment."""
import os
from os.path import dirname, join

from .common import Common

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class Test(Common):
    """Define class for test configuration settings."""

    DEBUG = True
    # Testing
    INSTALLED_APPS = Common.INSTALLED_APPS

    # Mail
    EMAIL_HOST = "localhost"
    EMAIL_PORT = 1025
    EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

    BASE64_DECODE_JWT_KEY = False
