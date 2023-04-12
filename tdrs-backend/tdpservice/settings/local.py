"""Define configuration settings for local environment."""
import os
from distutils.util import strtobool

from .common import Common

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class Local(Common):
    """Define class for local configuration settings."""

    # Default DEBUG to True in local environments
    DEBUG = strtobool(os.getenv("DJANGO_DEBUG", "yes"))

    # Mail
    EMAIL_HOST = "localhost"
    EMAIL_PORT = 1025
    EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

    # Whether to use localstack in place of a live AWS S3 environment
    # NOTE: Defaults to True when this settings module is in use
    USE_LOCALSTACK = bool(strtobool(os.getenv("USE_LOCALSTACK", "yes")))

    # Overwrite CORS allowed origins to allow for local development
    CORS_ALLOWED_ORIGINS = ['http://localhost:3000']

    if USE_LOCALSTACK:
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

    REDIS_SERVER_LOCAL = bool(strtobool(os.getenv("REDIS_SERVER_LOCAL", "TRUE")))

    # SFTP TEST KEY
    """
    To be able to fit the PRIVATE KEY in one line as environment variable, we replace the EOL
    with an underscore char.
    The next line replaces the _ with EOL before using the PRIVATE KEY
    """
    ACFTITAN_SFTP_PYTEST = os.getenv("ACFTITAN_SFTP_PYTEST").replace('_', '\n')
