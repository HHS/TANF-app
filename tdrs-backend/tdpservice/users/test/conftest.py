"""User fixtures."""

import uuid

import pytest


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
