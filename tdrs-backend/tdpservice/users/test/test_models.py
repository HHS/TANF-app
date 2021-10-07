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
        regional_user.save()

@pytest.mark.django_db
def test_data_analyst_cannot_have_region(data_analyst, region):
    """Test that an error will be thrown if a region is set on a data analyst user."""
    with pytest.raises(ValidationError):
        data_analyst.region = region
        data_analyst.save()

@pytest.mark.django_db
def test_is_data_analyst_property(data_analyst, regional_user):
    """Test that short hand property correctly indicates that user is a data analyst."""
    assert data_analyst.is_data_analyst is True
    assert regional_user.is_data_analyst is False

@pytest.mark.django_db
def test_is_regional_user_property(data_analyst, regional_user):
    """Test that short hand property correctly indicates that user is regional staff."""
    assert data_analyst.is_regional_staff is False
    assert regional_user.is_regional_staff is True
