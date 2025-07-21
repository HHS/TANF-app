"""Custom logging handler that sends logs to an S3 bucket."""

import logging
import logging.handlers
import os

from django.conf import settings

import boto3
from botocore.exceptions import ClientError

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


def change_log_filename(logger, datafile):
    """Change the filename of the log file handler."""
    handlers = getattr(logger, "handlers", [])
    new_filename = (
        f"/tmp/{datafile.year}_{datafile.quarter}_"
        f"{datafile.stt}_{datafile.section}.log"
    )
    for handler in handlers:
        if isinstance(handler, S3FileHandler):
            handler.close()
            handler.filename = new_filename
            handler.stream = open(new_filename, "a")


class S3FileHandler(logging.FileHandler):
    """Custom logging handler that sends logs to an S3 bucket."""

    def __init__(
        self, filename="temp.txt", mode="a", encoding=None, delay=False, errors=None
    ):
        self.filename = filename
        try:
            with open(filename, "x") as file:  # noqa
                pass  # No content is written, so it's an empty file
        except FileExistsError:
            pass
        super().__init__(filename, mode=mode, encoding=None, delay=False, errors=None)
        self.s3_client = boto3.client(**BOTO3_CLIENT_CONFIG)
        self.bucket_name = AWS_S3_BUCKET_NAME
        self.logs_prefix = AWS_S3_LOGS_PREFIX
        if not self.logs_prefix.endswith("/"):
            self.logs_prefix += "/"

    def doRollover(self, datafile):
        """Rollover happens before closing the file."""
        with open(self.filename, "a") as file:
            file.write("\n ___ END OF LOG ___\n\n\n")
        try:
            key = (
                f"{AWS_S3_LOGS_PREFIX}/{datafile.year}/{datafile.quarter}/"
                f"{datafile.stt}/{datafile.section}"
            )
            self.s3_client.upload_file(
                Filename=self.filename, Bucket=AWS_S3_BUCKET_NAME, Key=key
            )
            logger.info(f"Log file {self.filename} uploaded to S3.")
        except ClientError as e:
            logger.info(f"Error sending log to S3: {e}")
        self.close()

    @staticmethod
    def download_file(key):
        """Download a file from s3. Specify the path, file name, and version id."""
        try:
            s3_client = boto3.client(**BOTO3_CLIENT_CONFIG)
            logs_prefix = AWS_S3_LOGS_PREFIX
            if not logs_prefix.endswith("/"):
                logs_prefix += "/"
            key = logs_prefix + key
            s3_client.download_file(
                Bucket=AWS_S3_BUCKET_NAME, Key=key, Filename="temp.logs"
            )
            response = open("temp.logs", "r")
            os.remove("temp.logs")
            return response
        except Exception as e:
            logger.error(f"Error downloading file from S3: {e}")
            return None
