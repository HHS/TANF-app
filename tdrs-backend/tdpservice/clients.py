"""Globally available external client services."""
from requests.adapters import HTTPAdapter
from requests.exceptions import ConnectionError
from requests.packages.urllib3.util.retry import Retry
from requests.sessions import Session
import logging

from boto3 import client
from django.conf import settings

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class ClamAVClient:
    """An HTTP client that can be used to send files to a ClamAV REST server."""
    class ServiceUnavailable(Exception):
        """Raised when the target ClamAV REST server is unavailable."""
        pass

    # https://github.com/raft-tech/clamav-rest#status-codes
    SCAN_CODES = {
        'CLEAN': [200],
        'INFECTED': [406],
        'ERROR': [400, 412, 429, 500, 501]
    }

    def __init__(self, endpoint_url=None):
        if not endpoint_url:
            endpoint_url = settings.AV_SCAN_URL

        self.endpoint_url = endpoint_url
        self.session = self.init_session()

    def init_session(self):
        """Create a new requests.Session object that can retry failed
        connection attempts and maintain TCP connections between requests.
        """
        session = Session()
        retries = Retry(
            backoff_factor=settings.AV_SCAN_BACKOFF_FACTOR,
            status_forcelist=self.SCAN_CODES['ERROR'],
            total=settings.AV_SCAN_MAX_RETRIES
        )
        session.mount(self.endpoint_url, HTTPAdapter(max_retries=retries))
        return session

    def scan_file(self, file, file_name) -> bool:
        """Scan a file for virus infections.

        :param file:
            The file or file-like object that should be scanned
        :param file_name:
            The name of the target file (str).
        :returns is_file_clean:
            A boolean indicating whether or not the file passed the ClamAV scan
        """
        logger.debug(f'Initiating virus scan for file: {file_name}')
        try:
            scan_response = self.session.post(
                self.endpoint_url,
                data={'name': file_name},
                files={'file': file},
                timeout=settings.AV_SCAN_TIMEOUT
            )
        except ConnectionError as err:
            logger.debug(f'Encountered error scanning file: {err}')
            raise self.ServiceUnavailable()

        if scan_response.status_code in self.SCAN_CODES['CLEAN']:
            logger.debug(
                f'File scan marked as CLEAN for file: {file_name}'
            )
            return True

        if scan_response.status_code in self.SCAN_CODES['INFECTED']:
            logger.debug(
                f'File scan marked as INFECTED for file: {file_name}'
            )
            return False

        logger.debug(f'Unable to scan file with name: {file_name}')
        return False


def get_s3_client():
    """Return an S3 client that points to localstack or AWS based on settings.

    Intended to be used in place of a direct boto3 client.
    """
    region_name = settings.AWS_REGION_NAME

    # If localstack support is turned on we will return a client that redirects
    # all S3 requests to the localstack container
    if settings.USE_LOCALSTACK:
        # To get s3 signed URLs to work with localstack we must pass in
        # dummy credentials of `test` per the docs
        # https://github.com/localstack/localstack#setting-up-local-region-and-credentials-to-run-localstack  # noqa
        localstack_creds_placeholder = 'test'

        # If localstack is in use then we must supply the endpoint URL
        # explicitly to prevent boto3 from auto-generating a live S3 URL
        localstack_endpoint_url = 'http://localhost:4566'

        return client(
            service_name='s3',
            aws_access_key_id=localstack_creds_placeholder,
            aws_secret_access_key=localstack_creds_placeholder,
            endpoint_url=localstack_endpoint_url,
            region_name=region_name
        )

    # Otherwise, use a live S3 with the credentials configured via env vars
    return client(
        service_name='s3',
        aws_access_key_id=settings.AWS_S3_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_S3_SECRET_ACCESS_KEY,
        region_name=region_name
    )
