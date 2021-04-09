from io import StringIO
import pytest
import requests

from django.conf import settings
from factory.faker import faker

_faker = faker.Faker()


@pytest.fixture
def fake_file_name():
    """A random but valid filename ending in .txt"""
    return _faker.file_name(extension='txt')


@pytest.fixture
def fake_file(fake_file_name):
    """Generate an in-memory file-like object with random contents."""
    return StringIO(_faker.sentence())


def test_clamav_accepts_files(fake_file, fake_file_name):
    """Test that ClamAV is configured and accessible by this application."""
    # Confirm that the setting for AV_SCAN_URL is configured
    clamav_url = settings.AV_SCAN_URL
    assert clamav_url is not None

    # Send a fake file to ClamAV to ensure it is accessible and accepts files.
    response = requests.post(
        clamav_url,
        files={'file': fake_file},
        data={'name': fake_file_name}
    )
    assert response.status_code == 200
