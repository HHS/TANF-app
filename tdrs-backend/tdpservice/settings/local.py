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
        localstack_dummy_key = "test"
        DEFAULT_FILE_STORAGE = 'tdpservice.backends.DataFilesS3Storage'
        AWS_S3_DATAFILES_ACCESS_KEY = localstack_dummy_key
        AWS_S3_DATAFILES_SECRET_KEY = localstack_dummy_key
        AWS_S3_DATAFILES_BUCKET_NAME = 'tdp-datafiles-localstack'
        AWS_S3_DATAFILES_ENDPOINT = 'http://localstack:4566'
        AWS_S3_DATAFILES_REGION_NAME = 'us-gov-west-1'

    Common.LOGGING['loggers']['root'] = {
        'level': 'DEBUG',
        'handlers': ['console']
    }
