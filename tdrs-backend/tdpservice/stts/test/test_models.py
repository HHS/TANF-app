"""Module for testing the stt and region models."""
import pytest

from tdpservice.stts.models import STT, Region


@pytest.mark.django_db
def test_region_string_representation(stts):
    """Test region string representation."""
    first_region = Region.objects.first()
    assert str(first_region) == f"Region {first_region.id}"


@pytest.mark.django_db
def test_stt_string_representation(stts):
    """Test STT string representation."""
    first_stt = STT.objects.filter(type=STT.EntityType.STATE).first()
    assert str(first_stt) == first_stt.name
