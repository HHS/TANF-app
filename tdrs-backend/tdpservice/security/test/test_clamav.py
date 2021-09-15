"""Integration test(s) for clamav-rest operations."""
from requests.sessions import Session
import pytest

from rest_framework.status import HTTP_400_BAD_REQUEST

from tdpservice.security.clients import ClamAVClient
from tdpservice.security.models import ClamAVFileScan


@pytest.fixture
def clamav_client():
    """HTTP Client used to send files to ClamAV-REST."""
    return ClamAVClient()


@pytest.fixture
def mock_clamav_response(mocker):
    """Mock the ClamAV post request to return a 400 Bad Request."""
    mock_post = mocker.patch('requests.sessions.Session.post')
    mock_post.return_value.status_code = HTTP_400_BAD_REQUEST
    return mock_post


@pytest.fixture
def invalid_clamav_client():
    """Override the ClamAVClient endpoint_url with an invalid value."""
    return ClamAVClient(endpoint_url='http://invalid')


def test_clamav_endpoint_url(clamav_client, settings):
    """Test that the client has the appropriate endpoint URL set."""
    actual_url = clamav_client.endpoint_url
    expected_url = settings.AV_SCAN_URL
    assert actual_url == expected_url
    assert isinstance(clamav_client.session, Session)


@pytest.mark.django_db
def test_clamav_accepts_files(
    clamav_client,
    fake_file,
    fake_file_name,
    user
):
    """Test that ClamAV is configured and accessible by this application."""
    # Send a fake file to ClamAV to ensure it is accessible and accepts files.
    is_file_clean = clamav_client.scan_file(fake_file, fake_file_name, user)
    assert is_file_clean is True

    # Ensure that a CLEAN file scan result is recorded in the database.
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
    user
):
    """Test that ClamAV will reject files that match infection signatures."""
    # Send a test file that will be treated as "infected"
    is_file_clean = clamav_client.scan_file(infected_file, fake_file_name, user)
    assert is_file_clean is False

    # Ensure that an INFECTED scan result is recorded in the database.
    assert ClamAVFileScan.objects.filter(
        file_name=fake_file_name,
        result=ClamAVFileScan.Result.INFECTED,
        uploaded_by=user
    ).exists()


@pytest.mark.django_db
@pytest.mark.usefixtures('mock_clamav_response')
def test_clamav_scan_error(
    clamav_client,
    fake_file,
    fake_file_name,
    user
):
    """Test that ClamAV records scan errors caused by file/user errors."""
    is_file_clean = clamav_client.scan_file(fake_file, fake_file_name, user)
    assert is_file_clean is False

    # Ensure that an ERROR scan result is recorded in the database.
    assert ClamAVFileScan.objects.filter(
        file_name=fake_file_name,
        result=ClamAVFileScan.Result.ERROR,
        uploaded_by=user
    ).exists()


@pytest.mark.django_db
def test_clamav_connection_error(
    invalid_clamav_client,
    fake_file,
    fake_file_name,
    user
):
    """Test that the appropriate error is raised when ClamAV is inaccessible."""
    with pytest.raises(ClamAVClient.ServiceUnavailable):
        invalid_clamav_client.scan_file(fake_file, fake_file_name, user)
