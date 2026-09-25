"""Tests for search index admin filters."""

import pytest

from tdpservice.search_indexes.admin.filters import _ssp_participating_stts
from tdpservice.data_files.models import Program
from tdpservice.stts.models import STT, Region, SttProgramParticipation


def _create_stt(name):
    region, _ = Region.objects.get_or_create(id=9999)
    return STT.objects.create(name=name, region=region, stt_code=name[:3])


def _create_ssp_participation(stt, status):
    program, _ = Program.objects.get_or_create(
        slug="ssp", defaults={"code": "SSP", "name": "SSP"}
    )
    return SttProgramParticipation.objects.create(
        stt=stt,
        program=program,
        status=status,
    )


@pytest.mark.django_db
def test_ssp_participating_stts_includes_active_and_former_stts():
    """SSP admin filters include STTs with viewable SSP participation."""
    active_stt = _create_stt("Active SSP")
    former_stt = _create_stt("Former SSP")
    never_stt = _create_stt("Never SSP")
    _create_ssp_participation(active_stt, SttProgramParticipation.Status.ACTIVE)
    _create_ssp_participation(former_stt, SttProgramParticipation.Status.FORMER)
    _create_ssp_participation(never_stt, SttProgramParticipation.Status.NEVER)

    stt_names = set(_ssp_participating_stts(STT.objects.all()).values_list("name", flat=True))

    assert stt_names == {"Active SSP", "Former SSP"}
