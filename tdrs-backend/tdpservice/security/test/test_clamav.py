"""Integration test(s) for clamav-rest operations."""
from django.conf import settings
import pytest

from tdpservice.security.clients import ClamAVClient
from tdpservice.security.models import ClamAVFileScan


@pytest.fixture
def clamav_client(clamav_url):
    """HTTP Client used to send files to ClamAV-REST."""
    av_client = ClamAVClient(endpoint_url=clamav_url)
    return av_client


@pytest.fixture
def clamav_url():
    """URL that can be used to reach ClamAV-REST."""
    return settings.AV_SCAN_URL


def assert_clamav_url(clamav_url):
    """Ensure that the provided setting for AV_SCAN_URL is configured."""
    assert clamav_url is not None


@pytest.mark.django_db
def test_clamav_accepts_files(
    clamav_client,
    clamav_url,
    fake_file,
    fake_file_name,
    user
):
    """Test that ClamAV is configured and accessible by this application."""
    assert_clamav_url(clamav_url)

    # Send a fake file to ClamAV to ensure it is accessible and accepts files.
    is_file_clean = clamav_client.scan_file(fake_file, fake_file_name, user)
    assert is_file_clean is True

    av_scan = ClamAVFileScan.objects.get(
        file_name=fake_file_name,
        uploaded_by=user
    )
    assert av_scan is not None
    assert av_scan.result == ClamAVFileScan.Result.CLEAN


@pytest.mark.django_db
def test_clamav_rejects_infected_files(
    clamav_client,
    clamav_url,
    infected_file,
    fake_file_name,
    user
):
    """Test that ClamAV will reject files that match infection signatures."""
    assert_clamav_url(clamav_url)

    # Send a test file that will be treated as "infected"
    is_file_clean = clamav_client.scan_file(infected_file, fake_file_name, user)
    assert is_file_clean is False

    av_scan = ClamAVFileScan.objects.get(
        file_name=fake_file_name,
        uploaded_by=user
    )
    assert av_scan is not None
    assert av_scan.result == ClamAVFileScan.Result.INFECTED
