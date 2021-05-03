"""Define configuration settings for local environment."""
import os

from .common import Common

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

    if Common.USE_LOCALSTACK:
        AWS_ACCESS_KEY_ID = "test"
        AWS_SECRET_ACCESS_KEY = "test"
        AWS_S3_ENDPOINT_URL = "http://localstack:4566"

    Common.LOGGING['loggers']['root'] = {
        'level': 'DEBUG',
        'handlers': ['console']
    }
