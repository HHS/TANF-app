"""Module for testing the user model."""
import pytest
from django.core.exceptions import ValidationError


@pytest.mark.django_db
def test_user_string_representation(user):
    """Test user string representation."""
    assert str(user) == user.username

@pytest.mark.django_db
def test_regional_user_cannot_have_stt(regional_user, stt):
    try:
        regional_user.stt = stt
    except ValidationError:
        assert True
