"""Storage backends available for use within tdpservice."""
from django.conf import settings
from storages.backends.s3boto3 import S3Boto3Storage


class OverriddenCredentialsS3Storage(S3Boto3Storage):
    """An S3 storage class that overrides default settings with explicit values.

    This is needed because S3Boto3Storage does not support using different
    credentials and regions between different S3 storage classes.
    """

    def get_default_settings(self):
        """Override the base class method to use specific credentials/region."""
        return {
            **super().get_default_settings(),
            'access_key': self.access_key,
            'endpoint_url': self.endpoint_url,
            'region_name': self.region_name,
            'secret_key': self.secret_key
        }


class DataFilesS3Storage(OverriddenCredentialsS3Storage):
    """An S3 backed storage provider for user uploaded Data Files."""

    # Use distinct credentials for the tdp-datafiles service
    access_key = settings.AWS_S3_DATAFILES_ACCESS_KEY
    secret_key = settings.AWS_S3_DATAFILES_SECRET_KEY

    # Ensure that the appropriate datafiles bucket is used
    bucket_name = settings.AWS_S3_DATAFILES_BUCKET_NAME

    # Ensure correct endpoint URL is used
    endpoint_url = settings.AWS_S3_DATAFILES_ENDPOINT

    # Use distinct region for the tdp-datafiles service
    region_name = settings.AWS_S3_DATAFILES_REGION_NAME


class StaticFilesS3Storage(OverriddenCredentialsS3Storage):
    """An S3 backed storage provider for Django Admin staticfiles."""

    # Copied from s3boto3.S3StaticStorage - Querystring auth must be disabled so
    # that url() returns a consistent output.
    querystring_auth = False

    # Use distinct credentials for the tdp-staticfiles service
    access_key = settings.AWS_S3_STATICFILES_ACCESS_KEY
    secret_key = settings.AWS_S3_STATICFILES_SECRET_KEY

    # Ensure that the appropriate staticfiles bucket is used
    bucket_name = settings.AWS_S3_STATICFILES_BUCKET_NAME

    # Ensure correct endpoint URL is used
    endpoint_url = settings.AWS_S3_STATICFILES_ENDPOINT

    # Use distinct region for the tdp-staticfiles service
    region_name = settings.AWS_S3_STATICFILES_REGION_NAME
