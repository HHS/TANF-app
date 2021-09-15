"""External client services related to security auditing."""
from requests.adapters import HTTPAdapter
from requests.exceptions import ConnectionError
from requests.packages.urllib3.util.retry import Retry
from requests.sessions import Session
import logging

from django.conf import settings
from django.core.files.base import File

from tdpservice.security.models import ClamAVFileScan
from tdpservice.users.models import User

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
        """Create a new request session that can retry failed connections."""
        session = Session()
        retries = Retry(
            backoff_factor=settings.AV_SCAN_BACKOFF_FACTOR,
            status_forcelist=self.SCAN_CODES['ERROR'],
            total=settings.AV_SCAN_MAX_RETRIES
        )
        session.mount(self.endpoint_url, HTTPAdapter(max_retries=retries))
        return session

    def scan_file(self, file: File, file_name: str, uploaded_by: User) -> bool:
        """Scan a file for virus infections.

        :param file:
            The file or file-like object that should be scanned
        :param file_name:
            The string name of the file.
        :param uploaded_by:
            The User that uploaded the given file.
        :returns is_file_clean:
            A boolean indicating whether or not the file passed the ClamAV scan
        :raises ClamAVClient.ServiceUnavailable:
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
            logger.error(f'ClamAV connection failure: {err}')
            raise self.ServiceUnavailable()

        if scan_response.status_code in self.SCAN_CODES['CLEAN']:
            msg = f'File scan marked as CLEAN for file: {file_name}'
            scan_result = ClamAVFileScan.Result.CLEAN

        elif scan_response.status_code in self.SCAN_CODES['INFECTED']:
            msg = f'File scan marked as INFECTED for file: {file_name}'
            scan_result = ClamAVFileScan.Result.INFECTED

        else:
            msg = f'Unable to scan file with name: {file_name}'
            scan_result = ClamAVFileScan.Result.ERROR

        # Log and create audit records with the results of this scan
        logger.debug(msg)
        ClamAVFileScan.objects.record_scan(
            file,
            file_name,
            msg,
            scan_result,
            uploaded_by
        )

        return True if scan_result == ClamAVFileScan.Result.CLEAN else False
