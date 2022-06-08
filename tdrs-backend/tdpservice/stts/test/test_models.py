"""Module for testing the stt and region models."""
import csv
import json
from pathlib import Path

import pytest

from ..models import STT, Region


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


@pytest.mark.django_db
def test_each_stt_has_file_name(stts):
    DATA_DIR = Path(__file__).resolve().parent.parent / "management/commands/data"
    stt_types = ["tribes", "territories", "tribes"]
    for stt_type in stt_types:
        with open(DATA_DIR / f"{stt_type}.csv") as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                stt = STT.objects.get(name=row["Name"])
                assert json.loads(row["filenames"].replace('\'', '"')) == stt.filenames
