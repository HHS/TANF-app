"""Report file fixtures."""

import uuid
import pytest

@pytest.fixture
def report_data():
    """Return report creation data."""
    return {
        "id": uuid.uuid4(),
        "original_filename": "report.txt",
        "slug": "report-txt-slug",
        "extension": "txt",
        "section": "Active Case Data",
        "quarter": "Q1",
        "year": "2020",
        "version": 1,
        "stt": "New Jersey"
    }
