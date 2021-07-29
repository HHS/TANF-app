"""Module testing for data file model."""
import pytest
from ..models import DataFile


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
