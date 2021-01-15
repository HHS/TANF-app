"""Define configuration settings for local environment."""
import os
from os.path import dirname, join

from dotenv import load_dotenv

from .common import Common

# load env vars from .env file and override any system environment variables
dotenv_path = join(dirname(__file__), "./env_vars/.env.local")
load_dotenv(dotenv_path)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class Local(Common):
    """Define class for local configuration settings."""

    DEBUG = True
    # Testing
    INSTALLED_APPS = Common.INSTALLED_APPS

    # Mail
    EMAIL_HOST = "localhost"
    EMAIL_PORT = 1025
    EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
