"""Commands tests."""

from django.core.management import call_command
import pytest
from ..models import Region, STT


@pytest.mark.django_db
def test_populating_regions_stts():
    """Test the command for populating regions and STTs."""
    call_command("populate_stts")
    assert Region.objects.filter(id=10).exists()
    assert STT.objects.filter(code="WA", type=STT.EntityType.STATE).exists()
    assert STT.objects.filter(
        name="Puerto Rico", type=STT.EntityType.TERRITORY
    ).exists()
    assert STT.objects.filter(
        name="Santo Domingo Pueblo", type=STT.EntityType.TRIBE
    ).exists()


@pytest.mark.django_db
def test_no_double_population(stts):
    """Test the population command doesn't create extra objects."""
    original_stt_count = STT.objects.count()
    call_command("populate_stts")
    assert STT.objects.count() == original_stt_count
