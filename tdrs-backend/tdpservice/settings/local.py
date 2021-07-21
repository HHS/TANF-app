"""Define configuration settings for local environment."""
import os

from .common import Common

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class Local(Common):
    """Define class for local configuration settings."""

    DEBUG = True

    # Mail
    EMAIL_HOST = "localhost"
    EMAIL_PORT = 1025
    EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

    if Common.USE_LOCALSTACK:
        # To get s3 signed URLs to work with localstack we must pass in
        # dummy credentials of `test` per the docs
        # https://github.com/localstack/localstack#setting-up-local-region-and-credentials-to-run-localstack  # noqa
        localstack_dummy_key = "test"
        AWS_S3_DATAFILES_ACCESS_KEY = localstack_dummy_key
        AWS_S3_DATAFILES_SECRET_KEY = localstack_dummy_key

        # These are hard-coded to match the environment variables passed to the
        # localstack container in the base docker-compose
        AWS_S3_DATAFILES_BUCKET_NAME = 'tdp-datafiles-localstack'
        AWS_S3_DATAFILES_REGION_NAME = 'us-gov-west-1'

        # If localstack is in use then we must supply the endpoint URL
        # explicitly to prevent boto3 from auto-generating a live S3 URL
        AWS_S3_DATAFILES_ENDPOINT = 'http://localstack:4566'

    Common.LOGGING['loggers']['root'] = {
        'level': 'DEBUG',
        'handlers': ['console']
    }
