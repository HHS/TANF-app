"""Define configuration settings for local environment."""
import os
import logging
import django

from distutils.util import strtobool

from .common import Common

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class Local(Common):
    """Define class for local configuration settings."""

    # Default DEBUG to True in local environments
    DEBUG = strtobool(os.getenv("DJANGO_DEBUG", "yes"))

    # Whether to use localstack in place of a live AWS S3 environment
    # NOTE: Defaults to True when this settings module is in use
    USE_LOCALSTACK = bool(strtobool(os.getenv("USE_LOCALSTACK", "yes")))

    # Overwrite CORS allowed origins to allow for local development
    CORS_ALLOWED_ORIGINS = ['http://localhost:3000', 'http://localhost:3001']

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

    if os.getenv("ENABLE_SENTRY", "no") == "yes":
        # SENTRY
        import sentry_sdk
        from sentry_sdk.integrations.django import DjangoIntegration
        from sentry_sdk.integrations.logging import LoggingIntegration
        sentry_sdk.init(
            dsn="http://43ebf8abe1434ec6aea2c7b92c465a0e@host.docker.internal:9001/2",
            # Set traces_sample_rate to 1.0 to capture 100%
            # of transactions for performance monitoring.
            integrations=[
                DjangoIntegration(
                    transaction_style='url',
                    middleware_spans=True,
                    signals_spans=True,
                    signals_denylist=[
                        django.db.models.signals.pre_init,
                        django.db.models.signals.post_init,
                    ],
                    cache_spans=False,
                ),
                LoggingIntegration(level=logging.DEBUG, event_level=logging.DEBUG)
            ],
            traces_sample_rate=1.0,
        )
