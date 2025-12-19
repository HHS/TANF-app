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
    process_report_source,
)
from tdpservice.reports.models import ReportFile, ReportSource
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
        report_source_zip = zipfile.ZipFile(zip_buffer)

        # Get file infos for STT "1"
        file_infos = [
            info for info in report_source_zip.infolist()
            if not info.is_dir() and "2025/Region_1/1/" in info.filename
        ]

        # Bundle the files
        bundled = bundle_stt_files(report_source_zip, file_infos, "1")

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
        report_source_zip = zipfile.ZipFile(zip_buffer)

        file_infos = [
            info for info in report_source_zip.infolist()
            if not info.is_dir() and "2025/Region_1/1/" in info.filename
        ]

        bundled = bundle_stt_files(report_source_zip, file_infos, "1")

        # Check that file is flattened (no path)
        bundled_zip = zipfile.ZipFile(io.BytesIO(bundled.read()))
        names = bundled_zip.namelist()

        assert names[0] == "report1.pdf"  # Not "2025/Region_1/1/report1.pdf"


@pytest.mark.django_db
class TestProcessReportSource:
    """Tests for process_report_source task."""

    @patch('tdpservice.reports.tasks.timezone.now')
    def test_process_valid_report_source_zip(self, mock_now, ofa_admin):
        """Should successfully process a valid report source zip."""
        from tdpservice.stts.models import Region, STT

        # Create region and STT with stt_code="1" directly
        region = Region.objects.create(id=9001, name="Test Region")
        STT.objects.create(
            id=8001,
            stt_code="1",
            name="Test STT 1",
            region=region,
            postal_code="T1",
            type="STATE"
        )

        # Mock timezone to return a Q1 date
        mock_now.return_value = timezone.make_aware(datetime(2025, 2, 1))

        # Create source record with nested zip
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
            "report_source.zip",
            zip_buffer.read(),
            content_type="application/zip"
        )

        source = ReportSource.objects.create(
            uploaded_by=ofa_admin,
            original_filename="report_source.zip",
            slug="report_source.zip",
            file=uploaded_file,
            created_at=timezone.make_aware(datetime(2025, 2, 1))
        )

        # Process the source
        process_report_source(source.id)

        # Reload source
        source.refresh_from_db()

        # Verify success
        assert source.status == ReportSource.Status.SUCCEEDED
        assert source.num_reports_created == 1
        assert source.processed_at is not None

        # Verify ReportFile was created
        report_files = ReportFile.objects.filter(source=source)
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
        STT.objects.create(
            id=8002,
            stt_code="1",
            name="Test STT 1",
            region=region,
            postal_code="T1",
            type="STATE"
        )
        STT.objects.create(
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
            "report_source.zip",
            zip_buffer.read(),
            content_type="application/zip"
        )

        source = ReportSource.objects.create(
            uploaded_by=ofa_admin,
            original_filename="report_source.zip",
            slug="report_source.zip",
            file=uploaded_file,
            created_at=timezone.make_aware(datetime(2025, 5, 1))
        )

        process_report_source(source.id)

        source.refresh_from_db()
        assert source.status == ReportSource.Status.SUCCEEDED
        assert source.num_reports_created == 2

        # Verify both ReportFiles were created
        report_files = ReportFile.objects.filter(source=source)
        assert report_files.count() == 2

        stt_codes = {rf.stt.stt_code for rf in report_files}
        assert stt_codes == {"1", "2"}

    def test_process_invalid_zip(self, ofa_admin):
        """Should fail gracefully with invalid zip file."""
        from django.core.files.uploadedfile import SimpleUploadedFile
        uploaded_file = SimpleUploadedFile(
            "report_source.zip",
            b"not a zip file",
            content_type="application/zip"
        )

        source = ReportSource.objects.create(
            uploaded_by=ofa_admin,
            original_filename="report_source.zip",
            slug="report_source.zip",
            file=uploaded_file,
        )

        process_report_source(source.id)

        source.refresh_from_db()
        assert source.status == ReportSource.Status.FAILED
        assert "not a valid zip" in source.error_message

    def test_process_quarter_q2(self, ofa_admin):
        """Should successfully process with Q2 upload date (March)."""
        from tdpservice.stts.models import Region, STT

        # Create region and STT
        region = Region.objects.create(id=9003, name="Test Region 3")
        STT.objects.create(
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
            "report_source.zip",
            zip_buffer.read(),
            content_type="application/zip"
        )

        # Create with Q2 date (March 15)
        source = ReportSource.objects.create(
            uploaded_by=ofa_admin,
            original_filename="report_source.zip",
            slug="report_source.zip",
            file=uploaded_file,
        )

        # Update created_at to Q2 window
        source.created_at = timezone.make_aware(datetime(2025, 3, 15))
        source.save(update_fields=["created_at"])

        process_report_source(source.id)

        source.refresh_from_db()
        assert source.status == ReportSource.Status.SUCCEEDED
        assert source.num_reports_created == 1

        # Verify quarter is Q2
        report_file = ReportFile.objects.filter(source=source).first()
        assert report_file.quarter == "Q2"

    def test_process_with_provided_quarter(self, ofa_admin):
        """Should use provided quarter instead of calculating from date."""
        from tdpservice.stts.models import Region, STT

        # Create region and STT
        region = Region.objects.create(id=9004, name="Test Region 4")
        STT.objects.create(
            id=8005,
            stt_code="1",
            name="Test STT 1",
            region=region,
            postal_code="T1",
            type="STATE"
        )

        structure = {
            "2025": {
                "9004": {
                    "1": ["report1.pdf"]
                }
            }
        }
        zip_buffer = create_nested_zip(structure)

        from django.core.files.uploadedfile import SimpleUploadedFile
        uploaded_file = SimpleUploadedFile(
            "report_source.zip",
            zip_buffer.read(),
            content_type="application/zip"
        )

        # Create with provided quarter Q3 (but upload date would be Q2 if calculated)
        source = ReportSource.objects.create(
            uploaded_by=ofa_admin,
            original_filename="report_source.zip",
            slug="report_source.zip",
            file=uploaded_file,
            quarter="Q3",  # Explicitly provided
        )

        # Set created_at to Q2 window (March)
        source.created_at = timezone.make_aware(datetime(2025, 3, 15))
        source.save(update_fields=["created_at"])

        process_report_source(source.id)

        source.refresh_from_db()
        assert source.status == ReportSource.Status.SUCCEEDED
        assert source.num_reports_created == 1

        # Verify quarter is Q3 (provided), not Q2 (calculated)
        report_file = ReportFile.objects.filter(source=source).first()
        assert report_file.quarter == "Q3"

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
            "report_source.zip",
            zip_buffer.read(),
            content_type="application/zip"
        )

        source = ReportSource.objects.create(
            uploaded_by=ofa_admin,
            original_filename="report_source.zip",
            slug="report_source.zip",
            file=uploaded_file,
        )

        # Update created_at after creation (auto_now_add prevents setting on create)
        source.created_at = timezone.make_aware(datetime(2025, 2, 1))
        source.save(update_fields=["created_at"])

        process_report_source(source.id)

        source.refresh_from_db()
        assert source.status == ReportSource.Status.FAILED
        assert "STT code '999' not found" in source.error_message

    def test_process_with_provided_year_overrides_zip_structure(self, ofa_admin):
        """Should use provided year instead of zip structure year for ReportFile records."""
        from tdpservice.stts.models import Region, STT

        # Create region and STT
        region = Region.objects.create(id=9005, name="Test Region 5")
        STT.objects.create(
            id=8006,
            stt_code="1",
            name="Test STT 1",
            region=region,
            postal_code="T1",
            type="STATE"
        )

        # Zip has 2025 structure, but we'll provide year=2024
        structure = {
            "2025": {
                "9005": {
                    "1": ["report1.pdf"]
                }
            }
        }
        zip_buffer = create_nested_zip(structure)

        from django.core.files.uploadedfile import SimpleUploadedFile
        uploaded_file = SimpleUploadedFile(
            "report_source.zip",
            zip_buffer.read(),
            content_type="application/zip"
        )

        # Create with provided year=2024 and quarter=Q4
        source = ReportSource.objects.create(
            uploaded_by=ofa_admin,
            original_filename="report_source.zip",
            slug="report_source.zip",
            file=uploaded_file,
            quarter="Q4",  # Explicitly provided
            year=2024,  # Explicitly provided - different from zip structure (2025)
        )

        source.created_at = timezone.make_aware(datetime(2025, 3, 15))
        source.save(update_fields=["created_at"])

        process_report_source(source.id)

        source.refresh_from_db()
        assert source.status == ReportSource.Status.SUCCEEDED
        assert source.num_reports_created == 1

        # Verify year is 2024 (provided), not 2025 (from zip structure)
        report_file = ReportFile.objects.filter(source=source).first()
        assert report_file.year == 2024
        assert report_file.quarter == "Q4"


@pytest.mark.django_db
class TestProcessReportSourceEmailNotification:
    """Tests for email notification when ReportFile is created."""

    @patch('tdpservice.reports.tasks.send_feedback_report_available_email')
    @patch('tdpservice.reports.tasks.timezone.now')
    def test_sends_email_when_report_file_created(
        self, mock_now, mock_send_email, ofa_admin
    ):
        """Test that email is sent when a ReportFile is created."""
        from django.contrib.auth.models import Group
        from tdpservice.stts.models import Region, STT
        from tdpservice.users.models import User, AccountApprovalStatusChoices

        # Create region and STT
        region = Region.objects.create(id=9010, name="Test Region 10")
        stt = STT.objects.create(
            id=8010,
            stt_code="1",
            name="Test STT Email",
            region=region,
            postal_code="TE",
            type="STATE"
        )

        # Create a Data Analyst for this STT
        data_analyst_group, _ = Group.objects.get_or_create(name="Data Analyst")
        data_analyst = User.objects.create(
            username="test_analyst",
            email="test_analyst@example.com",
            stt=stt,
            account_approval_status=AccountApprovalStatusChoices.APPROVED,
        )
        data_analyst.groups.add(data_analyst_group)

        # Mock timezone
        mock_now.return_value = timezone.make_aware(datetime(2025, 2, 1))

        # Create source record
        structure = {"2025": {"Region_1": {"1": ["report.pdf"]}}}
        zip_buffer = create_nested_zip(structure)

        from django.core.files.uploadedfile import SimpleUploadedFile
        uploaded_file = SimpleUploadedFile(
            "report_source.zip",
            zip_buffer.read(),
            content_type="application/zip"
        )

        source = ReportSource.objects.create(
            uploaded_by=ofa_admin,
            original_filename="report_source.zip",
            slug="report_source.zip",
            file=uploaded_file,
            created_at=timezone.make_aware(datetime(2025, 2, 1))
        )

        process_report_source(source.id)

        # Verify email was called
        mock_send_email.assert_called_once()

        # Verify the ReportFile and recipients
        call_args = mock_send_email.call_args[0]
        assert isinstance(call_args[0], ReportFile)
        assert "test_analyst@example.com" in call_args[1]

    @patch('tdpservice.reports.tasks.send_feedback_report_available_email')
    @patch('tdpservice.reports.tasks.timezone.now')
    def test_does_not_send_email_when_no_data_analysts(
        self, mock_now, mock_send_email, ofa_admin
    ):
        """Test that no email is sent when no Data Analysts exist for STT."""
        from tdpservice.stts.models import Region, STT

        # Create region and STT with no Data Analysts
        region = Region.objects.create(id=9011, name="Test Region 11")
        STT.objects.create(
            id=8011,
            stt_code="1",
            name="Test STT No Analysts",
            region=region,
            postal_code="TN",
            type="STATE"
        )

        mock_now.return_value = timezone.make_aware(datetime(2025, 2, 1))

        structure = {"2025": {"Region_1": {"1": ["report.pdf"]}}}
        zip_buffer = create_nested_zip(structure)

        from django.core.files.uploadedfile import SimpleUploadedFile
        uploaded_file = SimpleUploadedFile(
            "report_source.zip",
            zip_buffer.read(),
            content_type="application/zip"
        )

        source = ReportSource.objects.create(
            uploaded_by=ofa_admin,
            original_filename="report_source.zip",
            slug="report_source.zip",
            file=uploaded_file,
            created_at=timezone.make_aware(datetime(2025, 2, 1))
        )

        process_report_source(source.id)

        # Verify email was not called (empty list of recipients)
        mock_send_email.assert_not_called()

    @patch('tdpservice.reports.tasks.send_feedback_report_available_email')
    @patch('tdpservice.reports.tasks.timezone.now')
    def test_sends_email_to_multiple_data_analysts(
        self, mock_now, mock_send_email, ofa_admin
    ):
        """Test that email is sent to all Data Analysts for the STT."""
        from django.contrib.auth.models import Group
        from tdpservice.stts.models import Region, STT
        from tdpservice.users.models import User, AccountApprovalStatusChoices

        # Create region and STT
        region = Region.objects.create(id=9012, name="Test Region 12")
        stt = STT.objects.create(
            id=8012,
            stt_code="1",
            name="Test STT Multiple Analysts",
            region=region,
            postal_code="TM",
            type="STATE"
        )

        # Create multiple Data Analysts for this STT
        data_analyst_group, _ = Group.objects.get_or_create(name="Data Analyst")
        analysts = []
        for i in range(3):
            analyst = User.objects.create(
                username=f"analyst{i}",
                email=f"analyst{i}@example.com",
                stt=stt,
                account_approval_status=AccountApprovalStatusChoices.APPROVED,
            )
            analyst.groups.add(data_analyst_group)
            analysts.append(analyst)

        mock_now.return_value = timezone.make_aware(datetime(2025, 2, 1))

        structure = {"2025": {"Region_1": {"1": ["report.pdf"]}}}
        zip_buffer = create_nested_zip(structure)

        from django.core.files.uploadedfile import SimpleUploadedFile
        uploaded_file = SimpleUploadedFile(
            "report_source.zip",
            zip_buffer.read(),
            content_type="application/zip"
        )

        source = ReportSource.objects.create(
            uploaded_by=ofa_admin,
            original_filename="report_source.zip",
            slug="report_source.zip",
            file=uploaded_file,
            created_at=timezone.make_aware(datetime(2025, 2, 1))
        )

        process_report_source(source.id)

        # Verify email was called with all analysts
        mock_send_email.assert_called_once()
        call_args = mock_send_email.call_args[0]
        recipients = call_args[1]

        for analyst in analysts:
            assert analyst.email in recipients

    @patch('tdpservice.reports.tasks.send_feedback_report_available_email')
    @patch('tdpservice.reports.tasks.timezone.now')
    def test_only_sends_to_approved_data_analysts(
        self, mock_now, mock_send_email, ofa_admin
    ):
        """Test that email is only sent to approved Data Analysts."""
        from django.contrib.auth.models import Group
        from tdpservice.stts.models import Region, STT
        from tdpservice.users.models import User, AccountApprovalStatusChoices

        # Create region and STT
        region = Region.objects.create(id=9013, name="Test Region 13")
        stt = STT.objects.create(
            id=8013,
            stt_code="1",
            name="Test STT Approved Only",
            region=region,
            postal_code="TA",
            type="STATE"
        )

        data_analyst_group, _ = Group.objects.get_or_create(name="Data Analyst")

        # Create approved analyst
        approved_analyst = User.objects.create(
            username="approved_analyst",
            email="approved@example.com",
            stt=stt,
            account_approval_status=AccountApprovalStatusChoices.APPROVED,
        )
        approved_analyst.groups.add(data_analyst_group)

        # Create pending analyst (should NOT receive email)
        pending_analyst = User.objects.create(
            username="pending_analyst",
            email="pending@example.com",
            stt=stt,
            account_approval_status=AccountApprovalStatusChoices.PENDING,
        )
        pending_analyst.groups.add(data_analyst_group)

        mock_now.return_value = timezone.make_aware(datetime(2025, 2, 1))

        structure = {"2025": {"Region_1": {"1": ["report.pdf"]}}}
        zip_buffer = create_nested_zip(structure)

        from django.core.files.uploadedfile import SimpleUploadedFile
        uploaded_file = SimpleUploadedFile(
            "report_source.zip",
            zip_buffer.read(),
            content_type="application/zip"
        )

        source = ReportSource.objects.create(
            uploaded_by=ofa_admin,
            original_filename="report_source.zip",
            slug="report_source.zip",
            file=uploaded_file,
            created_at=timezone.make_aware(datetime(2025, 2, 1))
        )

        process_report_source(source.id)

        # Verify only approved analyst received email
        mock_send_email.assert_called_once()
        call_args = mock_send_email.call_args[0]
        recipients = call_args[1]

        assert "approved@example.com" in recipients
        assert "pending@example.com" not in recipients
