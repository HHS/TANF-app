"""Integration test(s) for clamav-rest operations."""
import pytest

from rest_framework.status import HTTP_400_BAD_REQUEST

from tdpservice.security.clients import ClamAVClient
from tdpservice.security.models import ClamAVFileScan


@pytest.fixture
def clamav_client():
    """HTTP Client used to send files to ClamAV-REST."""
    av_client = ClamAVClient()
    return av_client


@pytest.fixture
def mock_clamav_response(mocker):
    mock_post = mocker.patch('requests.sessions.Session.post')
    mock_post.return_value.status_code = HTTP_400_BAD_REQUEST
    return mock_post


@pytest.fixture
def patch_invalid_clamav_url(settings):
    settings.AV_SCAN_URL = 'http://invalid'


def assert_clamav_url(clamav_url):
    """Ensure that the provided setting for AV_SCAN_URL is configured."""
    assert clamav_url is not None


@pytest.mark.django_db
def test_clamav_accepts_files(
    clamav_client,
    fake_file,
    fake_file_name,
    settings,
    user
):
    """Test that ClamAV is configured and accessible by this application."""
    assert_clamav_url(settings.AV_SCAN_URL)

    # Send a fake file to ClamAV to ensure it is accessible and accepts files.
    is_file_clean = clamav_client.scan_file(fake_file, fake_file_name, user)
    assert is_file_clean is True

    assert ClamAVFileScan.objects.filter(
        file_name=fake_file_name,
        result=ClamAVFileScan.Result.CLEAN,
        uploaded_by=user
    ).exists()


@pytest.mark.django_db
def test_clamav_rejects_infected_files(
    clamav_client,
    infected_file,
    fake_file_name,
    settings,
    user
):
    """Test that ClamAV will reject files that match infection signatures."""
    assert_clamav_url(settings.AV_SCAN_URL)

    # Send a test file that will be treated as "infected"
    is_file_clean = clamav_client.scan_file(infected_file, fake_file_name, user)
    assert is_file_clean is False

    assert ClamAVFileScan.objects.filter(
        file_name=fake_file_name,
        result=ClamAVFileScan.Result.INFECTED,
        uploaded_by=user
    ).exists()


@pytest.mark.django_db
def test_clamav_scan_error(
    clamav_client,
    fake_file,
    fake_file_name,
    mock_clamav_response,
    user
):
    """Test that ClamAV records scan errors caused by file/user errors."""
    is_file_clean = clamav_client.scan_file(fake_file, fake_file_name, user)
    assert is_file_clean is False

    assert ClamAVFileScan.objects.filter(
        file_name=fake_file_name,
        result=ClamAVFileScan.Result.ERROR,
        uploaded_by=user
    ).exists()


@pytest.mark.django_db
def test_clamav_connection_error(
    patch_invalid_clamav_url,
    clamav_client,
    fake_file,
    fake_file_name,
    user
):
    """Test that the appropriate error is raised when ClamAV is inaccessible."""
    with pytest.raises(ClamAVClient.ServiceUnavailable):
        clamav_client.scan_file(fake_file, fake_file_name, user)
