"""Module testing for report file model."""
import pytest
from ..models import ReportFile

@pytest.mark.django_db
def test_create_new_report_version(report):
    """Test version incrementing logic for report files."""
    new_version = ReportFile.create_new_version({
        "year": report.year,
        "quarter": report.quarter,
        "section": report.section,
        "stt": report.stt,
        "original_filename": report.original_filename,
        "slug": report.slug,
        "extension": report.extension,
        "user": report.user,
    })
    assert new_version.version == report.version + 1

@pytest.mark.django_db
def test_find_latest_version(report):
    """Test method to find latest version"""
    new_report = ReportFile.create_new_version({
        "year": report.year,
        "quarter": report.quarter,
        "section": report.section,
        "stt": report.stt,
        "original_filename": report.original_filename,
        "slug": report.slug,
        "extension": report.extension,
        "user": report.user,
    })
    latest_report = ReportFile.find_latest_version(
        year=report.year,
        quarter=report.quarter,
        section=report.section,
        stt=report.stt.id
    )
    assert latest_report.version == new_report.version


@pytest.mark.django_db
def test_find_latest_version_number(report):
    """Test method to find latest version number."""
    new_report = ReportFile.create_new_version({
        "year": report.year,
        "quarter": report.quarter,
        "section": report.section,
        "stt": report.stt,
        "original_filename": report.original_filename,
        "slug": report.slug,
        "extension": report.extension,
        "user": report.user,
    })
    latest_version = ReportFile.find_latest_version_number(
        year=report.year,
        quarter=report.quarter,
        section=report.section,
        stt=report.stt.id
    )
    assert latest_version == new_report.version

