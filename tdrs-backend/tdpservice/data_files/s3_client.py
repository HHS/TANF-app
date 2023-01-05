import boto3
from django.conf import settings

class S3Client():
    def __init__(self):
        self.client = boto3.client(
            's3',
            aws_access_key_id=settings.AWS_S3_DATAFILES_ACCESS_KEY,
            aws_secret_access_key=settings.AWS_S3_DATAFILES_SECRET_KEY,
            endpoint_url=settings.AWS_S3_DATAFILES_ENDPOINT,
            region_name=settings.AWS_S3_DATAFILES_REGION_NAME
        )