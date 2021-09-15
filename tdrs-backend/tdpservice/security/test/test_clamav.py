"""Integration test(s) for clamav-rest operations."""
from os import remove
from requests.sessions import Session
import pytest

from django.contrib.admin import site as admin_site
from django.core.files.base import File
from rest_framework.status import HTTP_400_BAD_REQUEST

from tdpservice.security.admin import ClamAVFileScanAdmin
from tdpservice.security.clients import ClamAVClient
from tdpservice.security.models import ClamAVFileScan


@pytest.fixture
def chunky_file(chunky_file_name) -> File:
    """Return a file that is large enough to be broken into chunks on read."""
    with open(chunky_file_name, 'wb') as f:
        num_chars = 1024 * 1024  # 1 MB
        content = ('0' * num_chars).encode('utf-8')
        f.write(content)
        file = File(f)

    yield file

    # Clean up the generated file after the test completes
    remove(chunky_file_name)


@pytest.fixture
def chunky_file_name() -> str:
    """Return a static string to allow safely removing file after test runs."""
    return 'chunky_file_test.txt'


@pytest.fixture
def clamav_client():
    """HTTP Client used to send files to ClamAV-REST."""
    return ClamAVClient()


@pytest.fixture
def invalid_clamav_client():
    """Override the ClamAVClient endpoint_url with an invalid value."""
    return ClamAVClient(endpoint_url='http://invalid')


@pytest.fixture
def mock_clamav_response(mocker):
    """Mock the ClamAV post request to return a 400 Bad Request."""
    mock_post = mocker.patch('requests.sessions.Session.post')
    mock_post.return_value.status_code = HTTP_400_BAD_REQUEST
    return mock_post


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


@pytest.mark.django_db
def test_clamav_shasum_large_file(chunky_file, chunky_file_name, user):
    """Test that the file_shasum is correctly generated for large files."""
    # The file should be large enough to split into multiple chunks.
    assert chunky_file.multiple_chunks()

    av_scan = ClamAVFileScan.objects.record_scan(
        file=chunky_file,
        file_name=chunky_file_name,
        msg='CLEAN',
        result=ClamAVFileScan.Result.CLEAN,
        uploaded_by=user
    )

    assert av_scan.file_shasum != 'INVALID'


@pytest.mark.django_db
def test_clamav_shasum_invalid(fake_file, fake_file_name, mocker, user):
    """Test that a failure to derive sha256 hash of file is handled."""
    mocker.patch(
        'tdpservice.security.models.get_file_shasum',
        side_effect=AttributeError()
    )

    av_scan = ClamAVFileScan.objects.record_scan(
        file=fake_file,
        file_name=fake_file_name,
        msg='CLEAN',
        result=ClamAVFileScan.Result.CLEAN,
        uploaded_by=user
    )

    assert av_scan.file_shasum == 'INVALID'


@pytest.mark.django_db
@pytest.mark.parametrize('file_size, expected_value', [
    (1, '1.00B'),
    (1024, '1.00KB'),
    (1048576, '1.00MB'),
    (1073741824, '1.00GB'),
    (1099511627776, '1.00TB')
])
def test_clamav_file_scan_file_size_display(
    expected_value,
    fake_file_name,
    file_size,
    user
):
    """Test that the admin displays a human readable file size."""
    av_scan = ClamAVFileScan.objects.create(
        file_name=fake_file_name,
        file_size=file_size,
        file_shasum='TEST',
        result=ClamAVFileScan.Result.CLEAN,
        uploaded_by=user
    )
    assert av_scan.file_size_humanized == expected_value

    # Ensure that the Admin site returns the expected value
    av_admin = ClamAVFileScanAdmin(ClamAVFileScan, admin_site)
    admin_file_size = av_admin.file_size_human(av_scan)
    assert admin_file_size == expected_value
