"""Commands tests."""

import json

from django.core.management import call_command

import pytest

from tdpservice.data_files.models import Program
from tdpservice.stts.models import STT, Region, SttProgramParticipation


def _program(code):
    return Program.objects.get(code=code)


def _participation(stt, program_code):
    return SttProgramParticipation.objects.get(
        stt=stt,
        program=_program(program_code),
    )


def _participation_section_names(stt, program_code):
    return set(
        _participation(stt, program_code).sections.values_list("name", flat=True)
    )


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
    new_york = STT.objects.get(name="New York")
    assert _participation(new_york, "SSP").status == (
        SttProgramParticipation.Status.ACTIVE
    )
    assert _participation_section_names(new_york, "TAN") == {
        "Active Case Data",
        "Closed Case Data",
        "Aggregate Data",
        "Stratum Data",
    }
    assert _participation_section_names(new_york, "SSP") == {
        "Active Case Data",
        "Closed Case Data",
        "Aggregate Data",
        "Stratum Data",
    }
    assert _participation_section_names(
        STT.objects.get(name="Puerto Rico"), "TAN"
    ) == {
        "Active Case Data",
        "Closed Case Data",
        "Aggregate Data",
        "Stratum Data",
    }
    assert _participation_section_names(
        STT.objects.get(name="Santo Domingo Pueblo"), "TRIBAL"
    ) == {"Active Case Data", "Closed Case Data", "Aggregate Data"}
    rhode_island = STT.objects.get(name="Rhode Island")
    assert not SttProgramParticipation.objects.filter(
        stt=rhode_island, program=_program("SSP")
    ).exists()
    assert not SttProgramParticipation.objects.filter(program__code="FRA").exists()


@pytest.mark.django_db
def test_no_double_population(stts):
    """Test the population command doesn't create extra objects."""
    original_stt_count = STT.objects.count()
    original_participation_count = SttProgramParticipation.objects.count()
    original_participation_ids = {
        (participation.stt_id, participation.program_id): participation.id
        for participation in SttProgramParticipation.objects.all()
    }
    _participation(STT.objects.get(name="New York"), "SSP").sections.clear()
    call_command("populate_stts")
    assert STT.objects.count() == original_stt_count
    assert SttProgramParticipation.objects.count() == original_participation_count
    assert {
        (participation.stt_id, participation.program_id): participation.id
        for participation in SttProgramParticipation.objects.all()
    } == original_participation_ids
    assert _participation_section_names(STT.objects.get(name="New York"), "SSP") == {
        "Active Case Data",
        "Closed Case Data",
        "Aggregate Data",
        "Stratum Data",
    }


@pytest.mark.django_db
def test_apply_overrides(tmp_path, stts):
    """Overrides should update existing STTs when requested."""
    # Rhode Island starts without SSP
    rhode_island = STT.objects.get(name="Rhode Island")
    rhode_island.ssp = False
    rhode_island.save()

    overrides_file = tmp_path / "overrides.json"
    overrides_file.write_text(
        json.dumps(
            [
                {
                    "name": "Rhode Island",
                    "ssp": True,
                    "filenames": {
                        **rhode_island.filenames,
                        "SSP Active Case Data": "ssp-active.txt",
                        "SSP Closed Case Data": "ssp-closed.txt",
                        "SSP Aggregate Data": "ssp-aggregate.txt",
                    },
                }
            ]
        )
    )

    call_command("populate_stts", apply_overrides=True, overrides=str(overrides_file))

    rhode_island.refresh_from_db()
    assert rhode_island.ssp is True
    assert _participation(rhode_island, "SSP").status == (
        SttProgramParticipation.Status.ACTIVE
    )
    assert _participation_section_names(rhode_island, "SSP") == {
        "Active Case Data",
        "Closed Case Data",
        "Aggregate Data",
    }


@pytest.mark.django_db
def test_apply_ssp_former_override(tmp_path, stts):
    """False SSP overrides should mark an STT as a former SSP participant."""
    new_york = STT.objects.get(name="New York")
    assert _participation(new_york, "SSP").status == (
        SttProgramParticipation.Status.ACTIVE
    )

    overrides_file = tmp_path / "overrides.json"
    overrides_file.write_text(json.dumps([{"name": "New York", "ssp": False}]))

    call_command("populate_stts", apply_overrides=True, overrides=str(overrides_file))

    new_york.refresh_from_db()
    assert new_york.ssp is False
    assert _participation(new_york, "SSP").status == (
        SttProgramParticipation.Status.FORMER
    )
    assert _participation_section_names(new_york, "SSP") == {
        "Active Case Data",
        "Closed Case Data",
        "Aggregate Data",
        "Stratum Data",
    }


@pytest.mark.django_db
def test_apply_ssp_never_override(tmp_path, stts):
    """NEVER SSP overrides should remove an STT's SSP participation row."""
    new_york = STT.objects.get(name="New York")
    assert _participation(new_york, "SSP").status == (
        SttProgramParticipation.Status.ACTIVE
    )

    overrides_file = tmp_path / "overrides.json"
    overrides_file.write_text(json.dumps([{"name": "New York", "ssp": "NEVER"}]))

    call_command("populate_stts", apply_overrides=True, overrides=str(overrides_file))

    new_york.refresh_from_db()
    assert new_york.ssp is False
    assert not SttProgramParticipation.objects.filter(
        stt=new_york, program=_program("SSP")
    ).exists()


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
