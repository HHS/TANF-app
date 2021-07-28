"""Module testing for data file model."""
import pytest
from ..models import DataFile


@pytest.mark.django_db
def test_create_new_data_file_version(data_file):
    """Test version incrementing logic for data files."""
    new_version = DataFile.create_new_version({
        "year": data_file.year,
        "quarter": data_file.quarter,
        "section": data_file.section,
        "stt": data_file.stt,
        "original_filename": data_file.original_filename,
        "slug": data_file.slug,
        "extension": data_file.extension,
        "user": data_file.user,
    })
    assert new_version.version == data_file.version + 1


@pytest.mark.django_db
def test_find_latest_version(data_file):
    """Test method to find latest version."""
    new_data_file = DataFile.create_new_version({
        "year": data_file.year,
        "quarter": data_file.quarter,
        "section": data_file.section,
        "stt": data_file.stt,
        "original_filename": data_file.original_filename,
        "slug": data_file.slug,
        "extension": data_file.extension,
        "user": data_file.user,
    })
    latest_data_file = DataFile.find_latest_version(
        year=data_file.year,
        quarter=data_file.quarter,
        section=data_file.section,
        stt=data_file.stt.id
    )
    assert latest_data_file.version == new_data_file.version


@pytest.mark.django_db
def test_find_latest_version_number(data_file):
    """Test method to find latest version number."""
    new_data_file = DataFile.create_new_version({
        "year": data_file.year,
        "quarter": data_file.quarter,
        "section": data_file.section,
        "stt": data_file.stt,
        "original_filename": data_file.original_filename,
        "slug": data_file.slug,
        "extension": data_file.extension,
        "user": data_file.user,
    })
    latest_version = DataFile.find_latest_version_number(
        year=data_file.year,
        quarter=data_file.quarter,
        section=data_file.section,
        stt=data_file.stt.id
    )
    assert latest_version == new_data_file.version
