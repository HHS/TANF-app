"""Pytest fixtures for the reports app."""
import pytest

from tdpservice.conftest import create_temporary_file
from tdpservice.reports.test.factories import ReportFileFactory


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
        "section": "Active Case Data",
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
        "section": "Active Case Data",
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
def master_zip_file(fake_file):
    """Generate a fake master zipfile."""
    return create_temporary_file(fake_file, "master.zip")


@pytest.fixture
def bad_master_zip_file(fake_file, fake_file_name):
    """Generate a base master zipfile."""
    return create_temporary_file(fake_file, fake_file_name)


@pytest.fixture
def report_ingest_data(master_zip_file):
    """Return report ingest creation data."""
    return {
        "master_zip": master_zip_file,
        "original_filename": "master.zip",
        "s3_key": "test",
    }


@pytest.fixture
def bad_report_ingest_data(bad_master_zip_file, fake_file_name):
    """Return bad report ingest creation data."""
    return {
        "master_zip": bad_master_zip_file,
        "original_filename": fake_file_name,
        "s3_key": "test",
    }
