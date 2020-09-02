"""Test user serializers."""
from django.contrib.auth.hashers import check_password

import pytest

from ..serializers import CreateUserSerializer


def test_serializer_with_empty_data():
    """If an empty serialized request is returned it should not be valid."""
    serializer = CreateUserSerializer(data={})
    assert serializer.is_valid() is False


@pytest.mark.django_db
def test_serializer_with_valid_data(user_data):
    """If a serializer has valid data it will return a valid object."""
    serializer = CreateUserSerializer(data=user_data)
    assert serializer.is_valid() is True


@pytest.mark.django_db
def test_serializer_hashes_password(user_data):
    """The serializer should hash the user's password."""
    serializer = CreateUserSerializer(data=user_data)
    assert serializer.is_valid() is True

    user = serializer.save()
    assert check_password(user_data["password"], user.password) is True
