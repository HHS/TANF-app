"""Module for testing the user model."""
import pytest


@pytest.mark.django_db
def test_string_representation(user):
    """Test user string representation."""
    assert str(user) == user.username
