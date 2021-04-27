"""Integration test(s) for clamav-rest operations."""
from io import StringIO
import pytest
import requests

from django.conf import settings
from factory.faker import faker

_faker = faker.Faker()


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
        'X5O!P%@AP[4\\PZX54(P^)7CC)7}$EICAR-STANDARD-ANTIVIRUS-TEST-FILE!$H+H*'
    )


def _send_file_to_clamav(clamav_url, file, file_name):
    """Send a file over HTTP to ClamAV-REST."""
    return requests.post(
        clamav_url,
        files={'file': file},
        data={'name': file_name}
    )


def assert_clamav_url(clamav_url):
    """Ensure that the provided setting for AV_SCAN_URL is configured."""
    assert clamav_url is not None


def test_clamav_accepts_files(clamav_url, fake_file, fake_file_name):
    """Test that ClamAV is configured and accessible by this application."""
    assert_clamav_url(clamav_url)

    # Send a fake file to ClamAV to ensure it is accessible and accepts files.
    response = _send_file_to_clamav(clamav_url, fake_file, fake_file_name)
    assert response.status_code == 200  # ClamAV returns 200 for a "clean" file


def test_clamav_rejects_infected_files(
    clamav_url,
    infected_file,
    fake_file_name
):
    """Test that ClamAV will reject files that match infection signatures."""
    assert_clamav_url(clamav_url)

    # Send a test file that will be treated as "infected"
    response = _send_file_to_clamav(clamav_url, infected_file, fake_file_name)
    assert response.status_code == 406  # ClamAV returns 406 for infected files
