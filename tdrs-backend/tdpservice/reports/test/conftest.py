"""Report file fixtures."""

import pytest

@pytest.fixture
def report_data(user):
    """Return report creation data."""
    return {
        "original_filename": "report.txt",
        "slug": "report-txt-slug",
        "extension": "txt",
        "section": "Active Case Data",
        "user": str(user.id),
        "quarter": "Q1",
        "year": "2020",
        "stt": "Michigan"
    }
