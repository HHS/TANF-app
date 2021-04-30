"""Integration test(s) for clamav-rest operations."""
from io import StringIO
import pytest

from django.conf import settings
from factory.faker import faker

from tdpservice.clients import ClamAVClient

_faker = faker.Faker()


@pytest.fixture
def clamav_client(clamav_url):
    av_client = ClamAVClient(endpoint_url=clamav_url)
    return av_client


@pytest.fixture
def clamav_url():
    """URL that can be used to reach ClamAV-REST."""
    return settings.AV_SCAN_URL


@pytest.fixture
def fake_file_name():
    """Generate a random, but valid file name ending in .txt."""
    return _faker.file_name(extension='txt')


@pytest.fixture
def fake_file():
    """Generate an in-memory file-like object with random contents."""
    return StringIO(_faker.sentence())


@pytest.fixture
def infected_file():
    """Generate an EICAR test file that will be treated as an infected file.

    https://en.wikipedia.org/wiki/EICAR_test_file
    """
    return StringIO(
        r'X5O!P%@AP[4\PZX54(P^)7CC)7}$EICAR-STANDARD-ANTIVIRUS-TEST-FILE!$H+H*'
    )


def assert_clamav_url(clamav_url):
    """Ensure that the provided setting for AV_SCAN_URL is configured."""
    assert clamav_url is not None


def test_clamav_accepts_files(
    clamav_client,
    clamav_url,
    fake_file,
    fake_file_name
):
    """Test that ClamAV is configured and accessible by this application."""
    assert_clamav_url(clamav_url)

    # Send a fake file to ClamAV to ensure it is accessible and accepts files.
    is_file_clean = clamav_client.scan_file(fake_file, fake_file_name)
    assert is_file_clean is True


def test_clamav_rejects_infected_files(
    clamav_client,
    clamav_url,
    infected_file,
    fake_file_name
):
    """Test that ClamAV will reject files that match infection signatures."""
    assert_clamav_url(clamav_url)

    # Send a test file that will be treated as "infected"
    is_file_clean = clamav_client.scan_file(infected_file, fake_file_name)
    assert is_file_clean is False


def test_clamav_rejects_invalid_files():
    """TODO"""
    pass
