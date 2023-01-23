"""S3 client."""
import boto3
from django.conf import settings

class S3Client():
    """A client for downloading files from s3 with boto3."""

    def __init__(self):
        self.client = boto3.client(
            's3',
            aws_access_key_id=settings.AWS_S3_DATAFILES_ACCESS_KEY,
            aws_secret_access_key=settings.AWS_S3_DATAFILES_SECRET_KEY,
            endpoint_url=settings.AWS_S3_DATAFILES_ENDPOINT,
            region_name=settings.AWS_S3_DATAFILES_REGION_NAME
        )

    def file_download(self, key, path, version_id):
        """Download a file from s3. Specify the path, file name, and version id."""
        key = 'dev/' + key

        self.client.download_file(
            settings.AWS_S3_DATAFILES_BUCKET_NAME,
            key,
            path,
            ExtraArgs={'VersionId': version_id}
        )
        f = open(path, 'r')
        return f
