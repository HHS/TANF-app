"""Module testing for data file model."""
import csv
from pathlib import Path

from django.core.management import call_command

import pytest

from tdpservice.stts.models import STT

from ..models import DataFile


@pytest.fixture
def stts():
    """Populate STTs."""
    call_command("populate_stts")

@pytest.mark.django_db
def test_create_new_data_file_version(data_file_instance):
    """Test version incrementing logic for data files."""
    new_version = DataFile.create_new_version({
        "year": data_file_instance.year,
        "quarter": data_file_instance.quarter,
        "section": data_file_instance.section,
        "stt": data_file_instance.stt,
        "original_filename": data_file_instance.original_filename,
        "slug": data_file_instance.slug,
        "extension": data_file_instance.extension,
        "user": data_file_instance.user,
    })
    assert new_version.version == data_file_instance.version + 1


@pytest.mark.django_db
def test_find_latest_version(data_file_instance):
    """Test method to find latest version."""
    new_data_file = DataFile.create_new_version({
        "year": data_file_instance.year,
        "quarter": data_file_instance.quarter,
        "section": data_file_instance.section,
        "stt": data_file_instance.stt,
        "original_filename": data_file_instance.original_filename,
        "slug": data_file_instance.slug,
        "extension": data_file_instance.extension,
        "user": data_file_instance.user,
    })
    latest_data_file = DataFile.find_latest_version(
        year=data_file_instance.year,
        quarter=data_file_instance.quarter,
        section=data_file_instance.section,
        stt=data_file_instance.stt.id
    )
    assert latest_data_file.version == new_data_file.version


@pytest.mark.django_db
def test_find_latest_version_number(data_file_instance):
    """Test method to find latest version number."""
    new_data_file = DataFile.create_new_version({
        "year": data_file_instance.year,
        "quarter": data_file_instance.quarter,
        "section": data_file_instance.section,
        "stt": data_file_instance.stt,
        "original_filename": data_file_instance.original_filename,
        "slug": data_file_instance.slug,
        "extension": data_file_instance.extension,
        "user": data_file_instance.user,
    })
    latest_version = DataFile.find_latest_version_number(
        year=data_file_instance.year,
        quarter=data_file_instance.quarter,
        section=data_file_instance.section,
        stt=data_file_instance.stt.id
    )
    assert latest_version == new_data_file.version

# @pytest.mark.django_db
# def test_create_titan_name(data_file_instance):
#     """Test method to generate filenames."""
#     whaticareabout = data_file_instance.stt
#     print("DF {}".format(whaticareabout))
#     print("DF dir: {}".format(dir(whaticareabout)))
#     print("sttcode {} vs. filenames {}".format(whaticareabout.stt_code, whaticareabout.filenames))
#     assert data_file_instance.create_filename() == "ADS.E2J.blah"

@pytest.mark.django_db
def test_data_files_filename_is_expected(stts, data_analyst):
    """Test the validity of the file names associated with each data file."""
    data_dir = Path(__file__).resolve().parent.parent.parent / "stts/management/commands/data"
    stt_types = ["tribes", "territories", "tribes"]
    for stt_type in stt_types:
        with open(data_dir / f"{stt_type}.csv") as csvfile:
            # In order to avoid mock stts that currently aren't getting their filenames attributes set
            # We are reading from the csv files we generate the stt records from so we only check stts
            # that are supose to be here.
            reader = csv.DictReader(csvfile)
            for row in reader:
                for section in list(DataFile.Section):
                    stt = STT.objects.get(name=row["Name"])
                    new_data_file = DataFile.create_new_version({
                        "year": 2020,
                        "quarter": "Q1",
                        "section": section,
                        "user": data_analyst,
                        "stt": stt
                    })
                    try:
                        assert new_data_file.filename == stt.filenames[section]
                    except KeyError:
                        assert new_data_file.filename == new_data_file.create_filename()
