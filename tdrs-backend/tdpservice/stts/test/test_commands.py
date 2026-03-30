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


@pytest.mark.django_db
def test_populate_stts_sets_timezones():
    """Test that populate_stts populates timezone from CSV data."""
    call_command("populate_stts")

    alaska = STT.objects.get(name="Alaska", type=STT.EntityType.STATE)
    assert alaska.timezone == "America/Anchorage"

    navajo = STT.objects.get(name="Navajo Nation", type=STT.EntityType.TRIBE)
    assert navajo.timezone == "America/Denver"

    guam = STT.objects.get(name="Guam", type=STT.EntityType.TERRITORY)
    assert guam.timezone == "Pacific/Guam"


@pytest.mark.django_db
def test_apply_timezone_override(tmp_path, stts):
    """Overrides should allow changing an STT's timezone."""
    alaska = STT.objects.get(name="Alaska", type=STT.EntityType.STATE)
    assert alaska.timezone == "America/Anchorage"

    overrides_file = tmp_path / "overrides.json"
    overrides_file.write_text(
        json.dumps([{"name": "Alaska", "timezone": "America/Adak"}])
    )

    # apply_overrides runs _after_ CSV loading, so the override wins
    call_command("populate_stts", apply_overrides=True, overrides=str(overrides_file))

    alaska.refresh_from_db()
    assert alaska.timezone == "America/Adak"
