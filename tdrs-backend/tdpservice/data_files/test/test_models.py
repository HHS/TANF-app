"""Module testing for data file model."""
import pytest

from tdpservice.stts.models import STT

from tdpservice.data_files.models import DataFile


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

@pytest.mark.django_db
def test_data_files_filename_is_expected(user):
    """Test that the file name matches the file name expected based on the stt of each data file."""
    all_stts = STT.objects.all()

    if (all_stts.count == 0):
        raise Exception("There are no stts, the test is invalid.")
    for stt in all_stts.iterator():
        for section in stt.filenames:
            new_data_file = DataFile.create_new_version({
                "year": 2020,
                "quarter": "Q1",
                "section": section,
                "user": user,
                "stt": stt
            })
            assert new_data_file.filename == stt.filenames[section]

@pytest.mark.django_db
def test_prog_type(data_file_instance):
    """Test propert prog_type."""
    df = DataFile.create_new_version({
        "year": data_file_instance.year,
        "quarter": data_file_instance.quarter,
        "section": data_file_instance.section,
        "stt": data_file_instance.stt,
        "original_filename": data_file_instance.original_filename,
        "slug": data_file_instance.slug,
        "extension": data_file_instance.extension,
        "user": data_file_instance.user,
    })

    assert df.prog_type == "TAN"
    df.section = "SSP Active Case Data"
    assert df.prog_type == "SSP"
    df.section = "Tribal Active Case Data"
    assert df.prog_type == "TAN"

@pytest.mark.django_db
def test_fiscal_year(data_file_instance):
    """Test property fiscal_year."""
    df = DataFile.create_new_version({
        "year": data_file_instance.year,
        "quarter": data_file_instance.quarter,
        "section": data_file_instance.section,
        "stt": data_file_instance.stt,
        "original_filename": data_file_instance.original_filename,
        "slug": data_file_instance.slug,
        "extension": data_file_instance.extension,
        "user": data_file_instance.user,
    })

    assert df.fiscal_year == "2020 - Q1 (Oct - Dec)"
    df.quarter = "Q2"
    assert df.fiscal_year == "2020 - Q2 (Jan - Mar)"
    df.quarter = "Q3"
    assert df.fiscal_year == "2020 - Q3 (Apr - Jun)"
    df.quarter = "Q4"
    assert df.fiscal_year == "2020 - Q4 (Jul - Sep)"
