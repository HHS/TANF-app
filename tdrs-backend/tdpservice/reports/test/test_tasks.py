"""Tests for report processing tasks."""

import io
import zipfile
from datetime import datetime
from unittest.mock import patch

import pytest
from django.utils import timezone

from tdpservice.reports.tasks import (
    calculate_quarter_from_date,
    extract_fiscal_year,
    find_stt_folders,
    bundle_stt_files,
    process_report_ingest,
)
from tdpservice.reports.models import ReportFile, ReportIngest
from tdpservice.reports.test.conftest import create_nested_zip


class TestCalculateQuarterFromDate:
    """Tests for calculate_quarter_from_date function."""

    # Q1: October 15 - February 14
    def test_q1_october_start(self):
        """Q1: October 15th (start of Q1 window)."""
        date = datetime(2025, 10, 15)
        assert calculate_quarter_from_date(date) == "Q1"

    def test_q1_november(self):
        """Q1: November dates should return Q1."""
        date = datetime(2025, 11, 15)
        assert calculate_quarter_from_date(date) == "Q1"

    def test_q1_december(self):
        """Q1: December dates should return Q1."""
        date = datetime(2025, 12, 15)
        assert calculate_quarter_from_date(date) == "Q1"

    def test_q1_january(self):
        """Q1: January dates should return Q1."""
        date = datetime(2025, 1, 15)
        assert calculate_quarter_from_date(date) == "Q1"

    def test_q1_february_before_deadline(self):
        """Q1: February before 14th should return Q1."""
        date = datetime(2025, 2, 10)
        assert calculate_quarter_from_date(date) == "Q1"

    def test_q1_february_deadline(self):
        """Q1: February 14th (end of Q1 window)."""
        date = datetime(2025, 2, 14)
        assert calculate_quarter_from_date(date) == "Q1"

    # Q2: February 15 - May 15
    def test_q2_february_start(self):
        """Q2: February 15th (start of Q2 window)."""
        date = datetime(2025, 2, 15)
        assert calculate_quarter_from_date(date) == "Q2"

    def test_q2_march(self):
        """Q2: March dates should return Q2."""
        date = datetime(2025, 3, 15)
        assert calculate_quarter_from_date(date) == "Q2"

    def test_q2_april(self):
        """Q2: April dates should return Q2."""
        date = datetime(2025, 4, 20)
        assert calculate_quarter_from_date(date) == "Q2"

    def test_q2_may_before_deadline(self):
        """Q2: May before 15th should return Q2."""
        date = datetime(2025, 5, 10)
        assert calculate_quarter_from_date(date) == "Q2"

    def test_q2_may_deadline(self):
        """Q2: May 15th (end of Q2 window)."""
        date = datetime(2025, 5, 15)
        assert calculate_quarter_from_date(date) == "Q2"

    # Q3: May 16 - August 14
    def test_q3_may_start(self):
        """Q3: May 16th (start of Q3 window)."""
        date = datetime(2025, 5, 16)
        assert calculate_quarter_from_date(date) == "Q3"

    def test_q3_june(self):
        """Q3: June dates should return Q3."""
        date = datetime(2025, 6, 15)
        assert calculate_quarter_from_date(date) == "Q3"

    def test_q3_july(self):
        """Q3: July dates should return Q3."""
        date = datetime(2025, 7, 20)
        assert calculate_quarter_from_date(date) == "Q3"

    def test_q3_august_before_deadline(self):
        """Q3: August before 14th should return Q3."""
        date = datetime(2025, 8, 10)
        assert calculate_quarter_from_date(date) == "Q3"

    def test_q3_august_deadline(self):
        """Q3: August 14th (end of Q3 window)."""
        date = datetime(2025, 8, 14)
        assert calculate_quarter_from_date(date) == "Q3"

    # Q4: August 15 - October 14
    def test_q4_august_start(self):
        """Q4: August 15th (start of Q4 window)."""
        date = datetime(2025, 8, 15)
        assert calculate_quarter_from_date(date) == "Q4"

    def test_q4_september(self):
        """Q4: September dates should return Q4."""
        date = datetime(2025, 9, 15)
        assert calculate_quarter_from_date(date) == "Q4"

    def test_q4_october_before_deadline(self):
        """Q4: October before 14th should return Q4."""
        date = datetime(2025, 10, 10)
        assert calculate_quarter_from_date(date) == "Q4"

    def test_q4_october_deadline(self):
        """Q4: October 14th (end of Q4 window)."""
        date = datetime(2025, 10, 14)
        assert calculate_quarter_from_date(date) == "Q4"


class TestExtractFiscalYear:
    """Tests for extract_fiscal_year function."""

    def test_valid_fiscal_year(self):
        """Should extract fiscal year from top-level folder."""
        structure = {
            "2025": {
                "Region_1": {
                    "1": ["report.pdf"]
                }
            }
        }
        zip_buffer = create_nested_zip(structure)
        zip_file = zipfile.ZipFile(zip_buffer)

        year = extract_fiscal_year(zip_file)
        assert year == 2025

    def test_invalid_fiscal_year_not_numeric(self):
        """Should raise ValueError if folder name is not numeric."""
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w') as zf:
            zf.writestr("202a/Region_1/1/report.pdf", b"content")
        zip_buffer.seek(0)
        zip_file = zipfile.ZipFile(zip_buffer)

        with pytest.raises(ValueError, match="Fiscal year folder '202a' is invalid"):
            extract_fiscal_year(zip_file)

    def test_invalid_fiscal_year_wrong_length(self):
        """Should raise ValueError if folder name is not 4 digits."""
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w') as zf:
            zf.writestr("25/Region_1/1/report.pdf", b"content")
        zip_buffer.seek(0)
        zip_file = zipfile.ZipFile(zip_buffer)

        with pytest.raises(ValueError, match="Fiscal year folder '25' is invalid"):
            extract_fiscal_year(zip_file)

    def test_multiple_top_level_folders(self):
        """Should raise ValueError if multiple top-level folders exist."""
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w') as zf:
            zf.writestr("2025/Region_1/1/report.pdf", b"content")
            zf.writestr("2024/Region_1/1/report.pdf", b"content")
        zip_buffer.seek(0)
        zip_file = zipfile.ZipFile(zip_buffer)

        with pytest.raises(ValueError, match="Multiple top-level folders found"):
            extract_fiscal_year(zip_file)

    def test_no_folders(self):
        """Should raise ValueError if no folders found."""
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w') as zf:
            zf.writestr("report.pdf", b"content")
        zip_buffer.seek(0)
        zip_file = zipfile.ZipFile(zip_buffer)

        with pytest.raises(ValueError, match="No top-level folder found"):
            extract_fiscal_year(zip_file)


class TestFindSttFolders:
    """Tests for find_stt_folders function."""

    def test_single_stt(self):
        """Should find files for a single STT."""
        structure = {
            "2025": {
                "Region_1": {
                    "1": ["report1.pdf", "report2.pdf"]
                }
            }
        }
        zip_buffer = create_nested_zip(structure)
        zip_file = zipfile.ZipFile(zip_buffer)

        stt_files = find_stt_folders(zip_file, "2025")

        assert "1" in stt_files
        assert len(stt_files["1"]) == 2

    def test_multiple_stts(self):
        """Should find files for multiple STTs."""
        structure = {
            "2025": {
                "Region_1": {
                    "1": ["report1.pdf"],
                    "2": ["report2.pdf", "report3.pdf"]
                }
            }
        }
        zip_buffer = create_nested_zip(structure)
        zip_file = zipfile.ZipFile(zip_buffer)

        stt_files = find_stt_folders(zip_file, "2025")

        assert "1" in stt_files
        assert "2" in stt_files
        assert len(stt_files["1"]) == 1
        assert len(stt_files["2"]) == 2

    def test_multiple_regions(self):
        """Should find files across multiple regions."""
        structure = {
            "2025": {
                "Region_1": {
                    "1": ["report1.pdf"]
                },
                "Region_2": {
                    "2": ["report2.pdf"]
                }
            }
        }
        zip_buffer = create_nested_zip(structure)
        zip_file = zipfile.ZipFile(zip_buffer)

        stt_files = find_stt_folders(zip_file, "2025")

        assert "1" in stt_files
        assert "2" in stt_files

    def test_no_stt_folders(self):
        """Should raise ValueError if no STT folders found."""
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w') as zf:
            zf.writestr("2025/report.pdf", b"content")
        zip_buffer.seek(0)
        zip_file = zipfile.ZipFile(zip_buffer)

        with pytest.raises(ValueError, match="No STT folders found"):
            find_stt_folders(zip_file, "2025")


class TestBundleSttFiles:
    """Tests for bundle_stt_files function."""

    def test_bundle_multiple_files(self):
        """Should bundle multiple files into a single zip."""
        structure = {
            "2025": {
                "Region_1": {
                    "1": ["report1.pdf", "report2.pdf"]
                }
            }
        }
        zip_buffer = create_nested_zip(structure)
        master_zip = zipfile.ZipFile(zip_buffer)

        # Get file infos for STT "1"
        file_infos = [
            info for info in master_zip.infolist()
            if not info.is_dir() and "2025/Region_1/1/" in info.filename
        ]

        # Bundle the files
        bundled = bundle_stt_files(master_zip, file_infos, "1")

        # Verify the bundle
        assert bundled.name == "stt_1_reports.zip"

        # Open the bundled zip and check contents
        bundled_zip = zipfile.ZipFile(io.BytesIO(bundled.read()))
        names = bundled_zip.namelist()

        assert "report1.pdf" in names
        assert "report2.pdf" in names
        assert len(names) == 2

    def test_bundle_flattens_structure(self):
        """Should flatten folder structure when bundling."""
        structure = {
            "2025": {
                "Region_1": {
                    "1": ["report1.pdf"]
                }
            }
        }
        zip_buffer = create_nested_zip(structure)
        master_zip = zipfile.ZipFile(zip_buffer)

        file_infos = [
            info for info in master_zip.infolist()
            if not info.is_dir() and "2025/Region_1/1/" in info.filename
        ]

        bundled = bundle_stt_files(master_zip, file_infos, "1")

        # Check that file is flattened (no path)
        bundled_zip = zipfile.ZipFile(io.BytesIO(bundled.read()))
        names = bundled_zip.namelist()

        assert names[0] == "report1.pdf"  # Not "2025/Region_1/1/report1.pdf"


@pytest.mark.django_db
class TestProcessReportIngest:
    """Tests for process_report_ingest task."""

    @patch('tdpservice.reports.tasks.timezone.now')
    def test_process_valid_master_zip(self, mock_now, ofa_admin):
        """Should successfully process a valid master zip."""
        from tdpservice.stts.test.factories import STTFactory
        from tdpservice.stts.models import Region, STT

        # Create region and STT with stt_code="1" directly
        region = Region.objects.create(id=9001, name="Test Region")
        stt = STT.objects.create(
            id=8001,
            stt_code="1",
            name="Test STT 1",
            region=region,
            postal_code="T1",
            type="STATE"
        )

        # Mock timezone to return a Q1 date
        mock_now.return_value = timezone.make_aware(datetime(2025, 2, 1))

        # Create ingest record with nested zip
        structure = {
            "2025": {
                "Region_1": {
                    "1": ["report1.pdf", "report2.pdf"]
                }
            }
        }
        zip_buffer = create_nested_zip(structure)

        from django.core.files.uploadedfile import SimpleUploadedFile
        uploaded_file = SimpleUploadedFile(
            "master.zip",
            zip_buffer.read(),
            content_type="application/zip"
        )

        ingest = ReportIngest.objects.create(
            uploaded_by=ofa_admin,
            original_filename="master.zip",
            slug="master.zip",
            file=uploaded_file,
            created_at=timezone.make_aware(datetime(2025, 2, 1))
        )

        # Process the ingest
        process_report_ingest(ingest.id)

        # Reload ingest
        ingest.refresh_from_db()

        # Verify success
        assert ingest.status == ReportIngest.Status.SUCCEEDED
        assert ingest.num_reports_created == 1
        assert ingest.processed_at is not None

        # Verify ReportFile was created
        report_files = ReportFile.objects.filter(ingest=ingest)
        assert report_files.count() == 1

        report_file = report_files.first()
        assert report_file.year == 2025
        assert report_file.quarter == "Q1"
        assert report_file.stt.stt_code == "1"
        assert report_file.version == 1

    @patch('tdpservice.reports.tasks.timezone.now')
    def test_process_multiple_stts(self, mock_now, ofa_admin):
        """Should create multiple ReportFiles for multiple STTs."""
        from tdpservice.stts.models import Region, STT

        # Create a shared region for both STTs
        region = Region.objects.create(id=9002, name="Test Region 2")

        # Create STTs with stt_code="1" and "2"
        stt1 = STT.objects.create(
            id=8002,
            stt_code="1",
            name="Test STT 1",
            region=region,
            postal_code="T1",
            type="STATE"
        )
        stt2 = STT.objects.create(
            id=8003,
            stt_code="2",
            name="Test STT 2",
            region=region,
            postal_code="T2",
            type="STATE"
        )

        mock_now.return_value = timezone.make_aware(datetime(2025, 5, 1))

        structure = {
            "2025": {
                "Region_1": {
                    "1": ["report1.pdf"],
                    "2": ["report2.pdf"]
                }
            }
        }
        zip_buffer = create_nested_zip(structure)

        from django.core.files.uploadedfile import SimpleUploadedFile
        uploaded_file = SimpleUploadedFile(
            "master.zip",
            zip_buffer.read(),
            content_type="application/zip"
        )

        ingest = ReportIngest.objects.create(
            uploaded_by=ofa_admin,
            original_filename="master.zip",
            slug="master.zip",
            file=uploaded_file,
            created_at=timezone.make_aware(datetime(2025, 5, 1))
        )

        process_report_ingest(ingest.id)

        ingest.refresh_from_db()
        assert ingest.status == ReportIngest.Status.SUCCEEDED
        assert ingest.num_reports_created == 2

        # Verify both ReportFiles were created
        report_files = ReportFile.objects.filter(ingest=ingest)
        assert report_files.count() == 2

        stt_codes = {rf.stt.stt_code for rf in report_files}
        assert stt_codes == {"1", "2"}

    def test_process_invalid_zip(self, ofa_admin):
        """Should fail gracefully with invalid zip file."""
        from django.core.files.uploadedfile import SimpleUploadedFile
        uploaded_file = SimpleUploadedFile(
            "master.zip",
            b"not a zip file",
            content_type="application/zip"
        )

        ingest = ReportIngest.objects.create(
            uploaded_by=ofa_admin,
            original_filename="master.zip",
            slug="master.zip",
            file=uploaded_file,
        )

        process_report_ingest(ingest.id)

        ingest.refresh_from_db()
        assert ingest.status == ReportIngest.Status.FAILED
        assert "not a valid zip" in ingest.error_message

    def test_process_quarter_q2(self, ofa_admin):
        """Should successfully process with Q2 upload date (March)."""
        from tdpservice.stts.models import Region, STT

        # Create region and STT
        region = Region.objects.create(id=9003, name="Test Region 3")
        stt = STT.objects.create(
            id=8004,
            stt_code="1",
            name="Test STT 1",
            region=region,
            postal_code="T1",
            type="STATE"
        )

        structure = {
            "2025": {
                "9003": {
                    "1": ["report1.pdf"]
                }
            }
        }
        zip_buffer = create_nested_zip(structure)

        from django.core.files.uploadedfile import SimpleUploadedFile
        uploaded_file = SimpleUploadedFile(
            "master.zip",
            zip_buffer.read(),
            content_type="application/zip"
        )

        # Create with Q2 date (March 15)
        ingest = ReportIngest.objects.create(
            uploaded_by=ofa_admin,
            original_filename="master.zip",
            slug="master.zip",
            file=uploaded_file,
        )

        # Update created_at to Q2 window
        ingest.created_at = timezone.make_aware(datetime(2025, 3, 15))
        ingest.save(update_fields=["created_at"])

        process_report_ingest(ingest.id)

        ingest.refresh_from_db()
        assert ingest.status == ReportIngest.Status.SUCCEEDED
        assert ingest.num_reports_created == 1

        # Verify quarter is Q2
        report_file = ReportFile.objects.filter(ingest=ingest).first()
        assert report_file.quarter == "Q2"

    def test_process_invalid_stt_code(self, ofa_admin):
        """Should fail with non-existent STT code."""
        structure = {
            "2025": {
                "Region_1": {
                    "999": ["report1.pdf"]  # Invalid STT code
                }
            }
        }
        zip_buffer = create_nested_zip(structure)

        from django.core.files.uploadedfile import SimpleUploadedFile
        uploaded_file = SimpleUploadedFile(
            "master.zip",
            zip_buffer.read(),
            content_type="application/zip"
        )

        ingest = ReportIngest.objects.create(
            uploaded_by=ofa_admin,
            original_filename="master.zip",
            slug="master.zip",
            file=uploaded_file,
        )

        # Update created_at after creation (auto_now_add prevents setting on create)
        ingest.created_at = timezone.make_aware(datetime(2025, 2, 1))
        ingest.save(update_fields=["created_at"])

        process_report_ingest(ingest.id)

        ingest.refresh_from_db()
        assert ingest.status == ReportIngest.Status.FAILED
        assert "STT code '999' not found" in ingest.error_message
