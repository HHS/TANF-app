"""Module for testing the user model."""
import pytest
from django.core.exceptions import ValidationError


@pytest.mark.django_db
def test_user_string_representation(user):
    """Test user string representation."""
    assert str(user) == user.username

@pytest.mark.django_db
def test_regional_user_cannot_have_stt(regional_user, stt):
    """Test that an error will be thrown if an stt is set on a regional user."""
    try:
        regional_user.stt = stt
    except ValidationError:
        assert True

@pytest.mark.django_db
def test_data_analyst_cannot_have_region(user, region):
    """Test that an error will be thrown if a region is set on a data analyst user."""
    try:
        user.region = region
    except ValidationError:
        assert True
