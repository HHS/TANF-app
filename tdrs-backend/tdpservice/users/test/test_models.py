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
    with pytest.raises(ValidationError):
        regional_user.stt = stt

@pytest.mark.django_db
def test_data_analyst_cannot_have_region(user, region):
    """Test that an error will be thrown if a region is set on a data analyst user."""
    with pytest.raises(ValidationError):
        user.region = region
