"""Tests for ReportFile model logic (versioning helpers etc.)."""

import pytest
from tdpservice.reports.models import ReportFile, ReportType
from tdpservice.reports.test.factories import (
    FRAReportFileFactory,
    FRAReportSourceFactory,
    TribalTANFReportFileFactory,
    TribalTANFReportSourceFactory,
)


@pytest.mark.django_db
def test_create_new_version_increments(report_file_instance):
    """ReportFile.create_new_version should auto-increment version."""
    base = report_file_instance

    new_row = ReportFile.create_new_version(
        {
            "year": base.year,
            "date_extracted_on": base.date_extracted_on,
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
            "date_extracted_on": base.date_extracted_on,
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
        date_extracted_on=base.date_extracted_on,
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
            "date_extracted_on": base.date_extracted_on,
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
        date_extracted_on=base.date_extracted_on,
        stt=base.stt,
    )

    assert latest_obj.id == newer.id
    assert latest_obj.version == newer.version


@pytest.mark.django_db
def test_default_report_type_is_tanf_ssp(report_file_instance):
    """New ReportFile records should default to TANF_SSP report_type."""
    assert report_file_instance.report_type == ReportType.TANF_SSP


@pytest.mark.django_db
def test_unique_constraint_allows_different_report_types(report_file_instance):
    """Same (version, date_extracted_on, year, stt) should be allowed with different report_type."""
    base = report_file_instance

    fra_report = ReportFile.objects.create(
        version=base.version,
        date_extracted_on=base.date_extracted_on,
        year=base.year,
        stt=base.stt,
        report_type=ReportType.FRA,
        original_filename=base.original_filename,
        slug=base.slug,
        extension=base.extension,
        user=base.user,
        file=base.file,
    )

    assert fra_report.pk is not None
    assert fra_report.report_type == ReportType.FRA
    assert base.report_type == ReportType.TANF_SSP

    tribal_tanf_report = ReportFile.objects.create(
        version=base.version,
        date_extracted_on=base.date_extracted_on,
        year=base.year,
        stt=base.stt,
        report_type=ReportType.TRIBAL_TANF,
        original_filename=base.original_filename,
        slug=base.slug,
        extension=base.extension,
        user=base.user,
        file=base.file,
    )

    assert tribal_tanf_report.pk is not None
    assert tribal_tanf_report.report_type == ReportType.TRIBAL_TANF


@pytest.mark.django_db
def test_create_new_version_respects_report_type(report_file_instance):
    """create_new_version should version independently per report_type."""
    base = report_file_instance

    # Create an FRA report — should get version 1 (independent of existing TANF_SSP)
    fra_report = ReportFile.create_new_version(
        {
            "year": base.year,
            "date_extracted_on": base.date_extracted_on,
            "stt": base.stt,
            "report_type": ReportType.FRA,
            "original_filename": base.original_filename,
            "slug": base.slug,
            "extension": base.extension,
            "user": base.user,
            "file": base.file,
        }
    )

    assert fra_report.version == 1
    assert fra_report.report_type == ReportType.FRA

    tribal_tanf_report = ReportFile.create_new_version(
        {
            "year": base.year,
            "date_extracted_on": base.date_extracted_on,
            "stt": base.stt,
            "report_type": ReportType.TRIBAL_TANF,
            "original_filename": base.original_filename,
            "slug": base.slug,
            "extension": base.extension,
            "user": base.user,
            "file": base.file,
        }
    )

    assert tribal_tanf_report.version == 1
    assert tribal_tanf_report.report_type == ReportType.TRIBAL_TANF


@pytest.mark.django_db
def test_find_latest_version_number_filters_by_report_type(report_file_instance):
    """find_latest_version_number should only consider records with matching report_type."""
    base = report_file_instance

    # Create a v2 TANF_SSP report
    ReportFile.create_new_version(
        {
            "year": base.year,
            "date_extracted_on": base.date_extracted_on,
            "stt": base.stt,
            "original_filename": base.original_filename,
            "slug": base.slug,
            "extension": base.extension,
            "user": base.user,
            "file": base.file,
        }
    )

    # FRA should have no versions yet
    fra_version = ReportFile.find_latest_version_number(
        year=base.year,
        date_extracted_on=base.date_extracted_on,
        stt=base.stt,
        report_type=ReportType.FRA,
    )
    assert fra_version is None

    tribal_tanf_version = ReportFile.find_latest_version_number(
        year=base.year,
        date_extracted_on=base.date_extracted_on,
        stt=base.stt,
        report_type=ReportType.TRIBAL_TANF,
    )
    assert tribal_tanf_version is None

    # TANF_SSP should have version 2
    tanf_version = ReportFile.find_latest_version_number(
        year=base.year,
        date_extracted_on=base.date_extracted_on,
        stt=base.stt,
        report_type=ReportType.TANF_SSP,
    )
    assert tanf_version == 2


@pytest.mark.django_db
def test_fra_report_file_factory():
    """Test FRAReportFileFactory creates a ReportFile with report_type=FRA."""
    fra_report = FRAReportFileFactory.create()

    assert fra_report.pk is not None
    assert fra_report.report_type == ReportType.FRA


@pytest.mark.django_db
def test_fra_report_source_factory():
    """Test FRAReportSourceFactory creates a ReportSource with report_type=FRA."""
    fra_source = FRAReportSourceFactory.create()

    assert fra_source.pk is not None
    assert fra_source.report_type == ReportType.FRA


@pytest.mark.django_db
def test_tribal_tanf_report_file_factory():
    """Test TribalTANFReportFileFactory creates a ReportFile with report_type=TRIBAL_TANF."""
    tribal_tanf_report = TribalTANFReportFileFactory.create()

    assert tribal_tanf_report.pk is not None
    assert tribal_tanf_report.report_type == ReportType.TRIBAL_TANF


@pytest.mark.django_db
def test_tribal_tanf_report_source_factory():
    """Test TribalTANFReportSourceFactory creates a ReportSource with report_type=TRIBAL_TANF."""
    tribal_tanf_source = TribalTANFReportSourceFactory.create()

    assert tribal_tanf_source.pk is not None
    assert tribal_tanf_source.report_type == ReportType.TRIBAL_TANF
