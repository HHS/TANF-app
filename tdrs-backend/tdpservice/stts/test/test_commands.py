"""Commands tests."""

from django.core.management import call_command
import json

import pytest

from tdpservice.stts.models import STT, Region


@pytest.mark.django_db
def test_populating_regions_stts():
    """Test the command for populating regions and STTs."""
    call_command("populate_stts")
    assert Region.objects.filter(id=10).exists()
    assert STT.objects.filter(postal_code="WA", type=STT.EntityType.STATE).exists()
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


@pytest.mark.django_db
def test_apply_overrides(tmp_path, stts):
    """Overrides should update existing STTs when requested."""
    # Rhode Island starts without SSP
    rhode_island = STT.objects.get(name="Rhode Island")
    rhode_island.ssp = False
    rhode_island.save()

    overrides_file = tmp_path / "overrides.json"
    overrides_file.write_text(
      json.dumps([{"name": "Rhode Island", "ssp": True}])
    )

    call_command("populate_stts", apply_overrides=True, overrides=str(overrides_file))

    rhode_island.refresh_from_db()
    assert rhode_island.ssp is True
