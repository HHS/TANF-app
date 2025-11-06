"""Pytest fixtures for the reports app."""
import io
import pytest
import zipfile

from tdpservice.conftest import create_temporary_file
from tdpservice.reports.test.factories import ReportFileFactory


def create_nested_zip(structure):
    """
    Create a nested zip file structure for testing.

    Parameters
    ----------
        structure: dict like {
            "2025": {
                "Region_1": {
                    "1": ["report1.pdf", "report2.pdf"],
                    "2": ["report3.pdf"]
                }
            }
        }

    Returns
    -------
        BytesIO containing the zip file
    """
    zip_buffer = io.BytesIO()

    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zf:
        for year, regions in structure.items():
            for region, stts in regions.items():
                for stt_code, files in stts.items():
                    for filename in files:
                        # Create path: YYYY/Region/STT/filename
                        path = f"{year}/{region}/{stt_code}/{filename}"
                        # Add fake content
                        zf.writestr(path, b"fake file content")

    zip_buffer.seek(0)
    return zip_buffer


@pytest.fixture
def report_file(fake_file):
    """Generate a fake zipfile."""
    return create_temporary_file(fake_file, "report.zip")


@pytest.fixture
def bad_report_file(fake_file, fake_file_name):
    """Generate a a non-zip file."""
    return create_temporary_file(fake_file, fake_file_name)


@pytest.fixture
def report_file_data(report_file, data_analyst):
    """Return report file creation data."""
    return {
        "file": report_file,
        "original_filename": "report.zip",
        "slug": "report.zip",
        "extension": "zip",
        "quarter": "Q1",
        "year": 2024,
        "version": 1,
        "user": str(data_analyst.id),
        "stt": int(data_analyst.stt.id),
    }


@pytest.fixture
def bad_report_file_data(bad_report_file, fake_file_name, data_analyst):
    """Return report file creation data."""
    return {
        "file": bad_report_file,
        "original_filename": fake_file_name,
        "slug": "fake_file_name",
        "extension": "txt",
        "quarter": "Q1",
        "year": 2024,
        "version": 1,
        "user": str(data_analyst.id),
        "stt": int(data_analyst.stt.id),
    }


@pytest.fixture
def report_file_instance(data_analyst):
    """Return a persisted ReportFile tied to the provided STT fixture."""
    # We'll attach the provided STT and a data_analyst-style user to mimic reality.
    return ReportFileFactory.create(
        stt=data_analyst.stt,
        user=data_analyst,
    )


@pytest.fixture
def report_file_instance2(data_analyst):
    """Return a persisted ReportFile tied to the provided STT fixture."""
    # We'll attach the provided STT and a data_analyst-style user to mimic reality.
    return ReportFileFactory.create(stt=data_analyst.stt, user=data_analyst, year=2025)


@pytest.fixture
def report_source_zip_file(fake_file):
    """Generate a fake report source zipfile (old flat structure - deprecated)."""
    return create_temporary_file(fake_file, "report_source.zip")


@pytest.fixture
def fiscal_year_report_source_zip():
    """
    Generate a nested fiscal year report source zip file.

    Structure: 2025/Region_1/1/report1.pdf, report2.pdf
    """
    from django.core.files.uploadedfile import SimpleUploadedFile

    structure = {
        "2025": {
            "Region_1": {
                "1": ["report1.pdf", "report2.pdf"],
            }
        }
    }
    zip_buffer = create_nested_zip(structure)
    return SimpleUploadedFile("report_source.zip", zip_buffer.read(), content_type="application/zip")


@pytest.fixture
def multi_stt_report_source_zip():
    """Generate a nested report source zip with multiple STTs."""
    from django.core.files.uploadedfile import SimpleUploadedFile

    structure = {
        "2025": {
            "Region_1": {
                "1": ["report1.pdf", "report2.pdf"],
                "2": ["report3.pdf"],
            }
        }
    }
    zip_buffer = create_nested_zip(structure)
    return SimpleUploadedFile("report_source.zip", zip_buffer.read(), content_type="application/zip")


@pytest.fixture
def bad_report_source_zip_file(fake_file, fake_file_name):
    """Generate a base report source zipfile."""
    return create_temporary_file(fake_file, fake_file_name)


@pytest.fixture
def report_source_data(report_source_zip_file):
    """Return report source creation data."""
    return {
        "file": report_source_zip_file,
        "original_filename": "report_source.zip",
    }


@pytest.fixture
def bad_report_source_data(bad_report_source_zip_file, fake_file_name):
    """Return bad report source creation data."""
    return {
        "file": bad_report_source_zip_file,
        "original_filename": fake_file_name,
    }
