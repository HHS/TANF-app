from django.conf import settings
from storages.backends.s3boto3 import S3Boto3Storage


class DataFilesS3Storage(S3Boto3Storage):
    """An S3 backed storage provider for user uploaded Data Files.

    This class is used instead of the built-in to allow specifying a distinct
    bucket from the one used to store Django Admin static files.
    """

    bucket_name = settings.DATA_FILES_AWS_STORAGE_BUCKET_NAME


class StaticFilesS3Storage(S3Boto3Storage):
    """An S3 backed storage provider for Django Admin staticfiles."""
    bucket_name = settings.STATICFILES_AWS_STORAGE_BUCKET_NAME
