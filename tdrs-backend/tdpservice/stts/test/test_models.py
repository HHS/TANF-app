"""Module for testing the stt and region models."""
import pytest

from tdpservice.stts.models import STT, Region


@pytest.mark.django_db
def test_region_string_representation(stts):
    """Test region string representation."""
    first_region = Region.objects.first()
    assert str(first_region) == f"Region {first_region.id} (Boston)"


@pytest.mark.django_db
def test_stt_string_representation(stts):
    """Test STT string representation."""
    first_stt = STT.objects.filter(type=STT.EntityType.STATE).first()
    assert str(first_stt) == f"{first_stt.name} ({first_stt.stt_code})"


@pytest.mark.django_db
@pytest.mark.parametrize(
    "filenames, expected_num_sections",
    [
        (
            {
                "Active Case Data": "active.txt",
                "Closed Case Data": "closed.txt",
                "Aggregate Data": "aggregate.txt",
            },
            3,
        ),
        (
            {
                "Active Case Data": "tanf-active.txt",
                "Closed Case Data": "tanf-closed.txt",
                "SSP Active Case Data": "ssp-active.txt",
                "SSP Closed Case Data": "ssp-closed.txt",
            },
            2,
        ),
    ],
)
def test_stt_num_sections_counts_unique_sections(filenames, expected_num_sections):
    """num_sections counts sections, not program-prefixed filename keys."""
    stt = STT.objects.create(name="Section Count Test", filenames=filenames, ssp=True)

    assert stt.num_sections == expected_num_sections


@pytest.mark.django_db
def test_stt_has_timezone_field(stts):
    """Test that STT model has timezone field with a valid IANA timezone."""
    stt = STT.objects.get(name="Alaska")
    assert stt.timezone == "America/Anchorage"


@pytest.mark.django_db
def test_stt_timezone_default():
    """Test that STT timezone defaults to America/New_York."""
    region = Region.objects.create(id=9999)
    stt = STT.objects.create(name="Test STT", region=region, stt_code="99")
    assert stt.timezone == "America/New_York"


@pytest.mark.django_db
def test_stt_timezone_populated_for_states(stts):
    """Test that populate_stts sets timezones for states."""
    arizona = STT.objects.get(name="Arizona")
    assert arizona.timezone == "America/Phoenix"

    california = STT.objects.get(name="California")
    assert california.timezone == "America/Los_Angeles"

    illinois = STT.objects.get(name="Illinois")
    assert illinois.timezone == "America/Chicago"


@pytest.mark.django_db
def test_stt_timezone_populated_for_territories(stts):
    """Test that populate_stts sets timezones for territories."""
    guam = STT.objects.get(name="Guam")
    assert guam.timezone == "Pacific/Guam"

    puerto_rico = STT.objects.get(name="Puerto Rico")
    assert puerto_rico.timezone == "America/Puerto_Rico"


@pytest.mark.django_db
def test_stt_timezone_populated_for_tribes(stts):
    """Test that tribes get their own timezone, not inherited from state."""
    # Navajo Nation is in Arizona but observes DST (America/Denver)
    navajo = STT.objects.get(name="Navajo Nation")
    assert navajo.timezone == "America/Denver"

    # Hopi Tribe is in Arizona and does NOT observe DST (America/Phoenix)
    hopi = STT.objects.get(name="Hopi Tribe")
    assert hopi.timezone == "America/Phoenix"
