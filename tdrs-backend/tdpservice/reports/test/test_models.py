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
