"""Custom logging handler that sends logs to an S3 bucket."""

import logging.handlers
import boto3
import logging
from botocore.exceptions import ClientError
from django.conf import settings

logger = logging.getLogger(__name__)

# SET TO GET THESE FROM ENV VARS IN SETTINGS
AWS_ACCESS_KEY_ID = settings.AWS_S3_DATAFILES_ACCESS_KEY
AWS_SECRET_ACCESS_KEY = settings.AWS_S3_DATAFILES_SECRET_KEY
AWS_REGION = settings.AWS_S3_DATAFILES_REGION_NAME
AWS_S3_BUCKET_NAME = settings.AWS_S3_DATAFILES_BUCKET_NAME
AWS_S3_LOGS_PREFIX = "LOGS"

BOTO3_CLIENT_CONFIG = {
    "service_name": "s3",
    "aws_access_key_id": AWS_ACCESS_KEY_ID,
    "aws_secret_access_key": AWS_SECRET_ACCESS_KEY,
    "region_name": AWS_REGION,
}
if settings.USE_LOCALSTACK:
    BOTO3_CLIENT_CONFIG["endpoint_url"] = "http://host.docker.internal:4566"

def change_log_filename(logger, new_filename):
    """Change the filename of the log file handler."""
    handlers = getattr(logger, 'handlers', [])
    for handler in handlers:
        if isinstance(handler, S3FileHandler):
            handler.close()
            handler.filename = new_filename
            handler.stream = open(new_filename, 'a')


class S3FileHandler(logging.FileHandler):
    """Custom logging handler that sends logs to an S3 bucket."""

    def __init__(self, filename, mode='a', encoding=None, delay=False, errors=None):
        self.filename = filename
        try:
            with open(filename, "x") as file: # noqa
                pass  # No content is written, so it's an empty file
        except FileExistsError:
            pass
        super().__init__(
            filename, mode='a', encoding=None, delay=False, errors=None
        )
        self.s3_client = boto3.client(**BOTO3_CLIENT_CONFIG)
        self.bucket_name = AWS_S3_BUCKET_NAME
        self.logs_prefix = AWS_S3_LOGS_PREFIX
        if not self.logs_prefix.endswith("/"):
            self.logs_prefix += "/"

    def doRollover(self, datafile):
        """Rollover happens before closing the file."""
        try:
            key = f"{AWS_S3_LOGS_PREFIX}/{datafile.id}/{datafile.year}/{datafile.quarter}/" \
                  f"{datafile.stt}/{datafile.section}/{datafile.filename}"
            self.s3_client.upload_file(
                Filename=self.filename,
                Bucket=AWS_S3_BUCKET_NAME,
                Key=key)
            logger.info(f"Log file {self.filename} uploaded to S3.")
        except ClientError as e:
            logger.info(f"Error sending log to S3: {e}")
        self.close()
