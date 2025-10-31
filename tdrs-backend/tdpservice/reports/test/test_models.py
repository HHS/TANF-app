"""Tests for ReportFile model logic (versioning helpers etc.)."""

import pytest
from tdpservice.reports.models import ReportFile


@pytest.mark.django_db
def test_create_new_version_increments(report_file_instance):
    """ReportFile.create_new_version should auto-increment version."""
    base = report_file_instance

    new_row = ReportFile.create_new_version(
        {
            "year": base.year,
            "quarter": base.quarter,
            "stt": base.stt,
            "original_filename": base.original_filename,
            "slug": base.slug,
            "extension": base.extension,
            "user": base.user,
            "file": base.file,
        }
    )

    # new row version should be +1
    assert new_row.version == base.version + 1
    assert new_row.stt == base.stt
    assert new_row.user == base.user
    # sanity: new row got created
    assert new_row.pk is not None


@pytest.mark.django_db
def test_find_latest_version_number(report_file_instance):
    """find_latest_version_number returns the max version for a group."""
    base = report_file_instance

    # create another version with version+1
    newer = ReportFile.create_new_version(
        {
            "year": base.year,
            "quarter": base.quarter,
            "stt": base.stt,
            "original_filename": base.original_filename,
            "slug": base.slug,
            "extension": base.extension,
            "user": base.user,
            "file": base.file,
        }
    )

    latest_version_number = ReportFile.find_latest_version_number(
        year=base.year,
        quarter=base.quarter,
        stt=base.stt,
    )

    assert latest_version_number == newer.version


@pytest.mark.django_db
def test_find_latest_version(report_file_instance):
    """find_latest_version should return the row with the highest version."""
    base = report_file_instance

    newer = ReportFile.create_new_version(
        {
            "year": base.year,
            "quarter": base.quarter,
            "stt": base.stt,
            "original_filename": base.original_filename,
            "slug": base.slug,
            "extension": base.extension,
            "user": base.user,
            "file": base.file,
        }
    )

    latest_obj = ReportFile.find_latest_version(
        year=base.year,
        quarter=base.quarter,
        stt=base.stt,
    )

    assert latest_obj.id == newer.id
    assert latest_obj.version == newer.version
