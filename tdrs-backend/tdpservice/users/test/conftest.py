"""User fixtures."""

import uuid
import pytest
from requests.compat import urljoin

@pytest.fixture
def user_data():
    """Return user creation data."""
    return {
        "id": uuid.uuid4(),
        "username": "jsmith",
        "first_name": "John",
        "last_name": "Smith",
        "password": "correcthorsebatterystaple",
        "auth_token": "xxx",
    }

def prepare_url(value):
    """Prepare URL."""
    httpbin_url = value.url.rstrip('/') + '/'

    def inner(*suffix):
        """Join the URL."""
        return urljoin(httpbin_url, '/'.join(suffix))
    return inner

@pytest.fixture
def httpbin(httpbin):
    """Define httpbin."""
    return prepare_url(httpbin)
