"""Tests for report processing tasks."""

import io
import zipfile
from datetime import date, datetime
from unittest.mock import patch

import pytest
from django.utils import timezone

from tdpservice.reports.tasks import (
    find_stt_folders,
    bundle_stt_files,
    process_report_source,
)
from tdpservice.reports.models import ReportFile, ReportSource
from tdpservice.reports.test.conftest import create_nested_zip


class TestFindSttFolders:
    """Tests for find_stt_folders function."""

    def test_single_stt(self):
        """Should find files for a single STT."""
        structure = {
            "FY2025": {
                "R01": {
                    "F1": ["report1.pdf", "report2.pdf"]
                }
            }
        }
        zip_buffer = create_nested_zip(structure)
        zip_file = zipfile.ZipFile(zip_buffer)

        stt_files = find_stt_folders(zip_file)

        assert "1" in stt_files
        assert len(stt_files["1"]) == 2

    def test_multiple_stts(self):
        """Should find files for multiple STTs."""
        structure = {
            "FY2025": {
                "R01": {
                    "F1": ["report1.pdf"],
                    "F2": ["report2.pdf", "report3.pdf"]
                }
            }
        }
        zip_buffer = create_nested_zip(structure)
        zip_file = zipfile.ZipFile(zip_buffer)

        stt_files = find_stt_folders(zip_file)

        assert "1" in stt_files
        assert "2" in stt_files
        assert len(stt_files["1"]) == 1
        assert len(stt_files["2"]) == 2

    def test_multiple_regions(self):
        """Should find files across multiple regions."""
        structure = {
            "FY2025": {
                "R01": {
                    "F1": ["report1.pdf"]
                },
                "R02": {
                    "F2": ["report2.pdf"]
                }
            }
        }
        zip_buffer = create_nested_zip(structure)
        zip_file = zipfile.ZipFile(zip_buffer)

        stt_files = find_stt_folders(zip_file)

        assert "1" in stt_files
        assert "2" in stt_files

    def test_no_stt_folders(self):
        """Should raise ValueError if no STT folders found."""
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w') as zf:
            zf.writestr("FY2025/report.pdf", b"content")
        zip_buffer.seek(0)
        zip_file = zipfile.ZipFile(zip_buffer)

        with pytest.raises(ValueError, match="No STT folders found"):
            find_stt_folders(zip_file)


class TestBundleSttFiles:
    """Tests for bundle_stt_files function."""

    def test_bundle_multiple_files(self):
        """Should bundle multiple files into a single zip."""
        structure = {
            "FY2025": {
                "R01": {
                    "F1": ["report1.pdf", "report2.pdf"]
                }
            }
        }
        zip_buffer = create_nested_zip(structure)
        report_source_zip = zipfile.ZipFile(zip_buffer)

        # Get file infos for STT "F1" (which maps to stt_code "1")
        file_infos = [
            info for info in report_source_zip.infolist()
            if not info.is_dir() and "FY2025/R01/F1/" in info.filename
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
            "FY2025": {
                "R01": {
                    "F1": ["report1.pdf"]
                }
            }
        }
        zip_buffer = create_nested_zip(structure)
        report_source_zip = zipfile.ZipFile(zip_buffer)

        file_infos = [
            info for info in report_source_zip.infolist()
            if not info.is_dir() and "FY2025/R01/F1/" in info.filename
        ]

        bundled = bundle_stt_files(report_source_zip, file_infos, "1")

        # Check that file is flattened (no path)
        bundled_zip = zipfile.ZipFile(io.BytesIO(bundled.read()))
        names = bundled_zip.namelist()

        assert names[0] == "report1.pdf"  # Not "FY2025/R01/F1/report1.pdf"


@pytest.mark.django_db
class TestProcessReportSource:
    """Tests for process_report_source task."""

    @patch('tdpservice.reports.tasks.timezone.now')
    def test_process_valid_report_source_zip(self, mock_now, ofa_admin):
        """Should successfully process a valid report source zip."""
        from tdpservice.stts.models import Region, STT

        # Create region and STT with stt_code="01" directly
        region = Region.objects.create(id=9001, name="Test Region")
        STT.objects.create(
            id=8001,
            stt_code="01",
            name="Test STT 1",
            region=region,
            postal_code="T1",
            type="STATE"
        )

        mock_now.return_value = timezone.make_aware(datetime(2025, 2, 1))

        # Create source record with nested zip
        structure = {
            "FY2025": {
                "R01": {
                    "F1": ["report1.pdf", "report2.pdf"]
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
            year=2025,
            date_extracted_on=date(2025, 1, 31),
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
        assert report_file.date_extracted_on == date(2025, 1, 31)
        assert report_file.stt.stt_code == "01"
        assert report_file.version == 1

    @patch('tdpservice.reports.tasks.timezone.now')
    def test_process_multiple_stts(self, mock_now, ofa_admin):
        """Should create multiple ReportFiles for multiple STTs."""
        from tdpservice.stts.models import Region, STT

        # Create a shared region for both STTs
        region = Region.objects.create(id=9002, name="Test Region 2")

        # Create STTs with stt_code="01" and "2"
        STT.objects.create(
            id=8002,
            stt_code="01",
            name="Test STT 1",
            region=region,
            postal_code="T1",
            type="STATE"
        )
        STT.objects.create(
            id=8003,
            stt_code="02",
            name="Test STT 2",
            region=region,
            postal_code="T2",
            type="STATE"
        )

        mock_now.return_value = timezone.make_aware(datetime(2025, 5, 1))

        structure = {
            "FY2025": {
                "R01": {
                    "F1": ["report1.pdf"],
                    "F2": ["report2.pdf"]
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
            year=2025,
            date_extracted_on=date(2025, 4, 30),
        )

        process_report_source(source.id)

        source.refresh_from_db()
        assert source.status == ReportSource.Status.SUCCEEDED
        assert source.num_reports_created == 2

        # Verify both ReportFiles were created
        report_files = ReportFile.objects.filter(source=source)
        assert report_files.count() == 2

        stt_codes = {rf.stt.stt_code for rf in report_files}
        assert stt_codes == {"01", "02"}

        # Verify date_extracted_on is copied to all ReportFiles
        for rf in report_files:
            assert rf.date_extracted_on == date(2025, 4, 30)

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
            year=2025,
            date_extracted_on=date(2025, 1, 31),
        )

        process_report_source(source.id)

        source.refresh_from_db()
        assert source.status == ReportSource.Status.FAILED
        assert "not a valid zip" in source.error_message

    def test_process_invalid_stt_code(self, ofa_admin):
        """Should fail with non-existent STT code."""
        structure = {
            "FY2025": {
                "R01": {
                    "F999": ["report1.pdf"]  # Invalid STT code
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
            year=2025,
            date_extracted_on=date(2025, 1, 31),
        )

        process_report_source(source.id)

        source.refresh_from_db()
        assert source.status == ReportSource.Status.FAILED
        assert "STT code '999' not found" in source.error_message

    def test_process_uses_source_year(self, ofa_admin):
        """Should use year from source model for ReportFile records."""
        from tdpservice.stts.models import Region, STT

        # Create region and STT
        region = Region.objects.create(id=9005, name="Test Region 5")
        STT.objects.create(
            id=8006,
            stt_code="01",
            name="Test STT 1",
            region=region,
            postal_code="T1",
            type="STATE"
        )

        # Zip has FY2025 structure, but source.year=2024
        structure = {
            "FY2025": {
                "R9005": {
                    "F1": ["report1.pdf"]
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

        # Create with year=2024 (different from zip structure which has 2025)
        source = ReportSource.objects.create(
            uploaded_by=ofa_admin,
            original_filename="report_source.zip",
            slug="report_source.zip",
            file=uploaded_file,
            year=2024,
            date_extracted_on=date(2024, 9, 30),
        )

        process_report_source(source.id)

        source.refresh_from_db()
        assert source.status == ReportSource.Status.SUCCEEDED
        assert source.num_reports_created == 1

        # Verify year is 2024 (from source), not 2025 (from zip structure)
        report_file = ReportFile.objects.filter(source=source).first()
        assert report_file.year == 2024
        assert report_file.date_extracted_on == date(2024, 9, 30)


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
            stt_code="01",
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
        structure = {"FY2025": {"R01": {"F1": ["report.pdf"]}}}
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
            year=2025,
            date_extracted_on=date(2025, 1, 31),
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
            stt_code="01",
            name="Test STT No Analysts",
            region=region,
            postal_code="TN",
            type="STATE"
        )

        mock_now.return_value = timezone.make_aware(datetime(2025, 2, 1))

        structure = {"FY2025": {"R01": {"F1": ["report.pdf"]}}}
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
            year=2025,
            date_extracted_on=date(2025, 1, 31),
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
            stt_code="01",
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

        structure = {"FY2025": {"R01": {"F1": ["report.pdf"]}}}
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
            year=2025,
            date_extracted_on=date(2025, 1, 31),
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
            stt_code="01",
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

        structure = {"FY2025": {"R01": {"F1": ["report.pdf"]}}}
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
            year=2025,
            date_extracted_on=date(2025, 1, 31),
        )

        process_report_source(source.id)

        # Verify only approved analyst received email
        mock_send_email.assert_called_once()
        call_args = mock_send_email.call_args[0]
        recipients = call_args[1]

        assert "approved@example.com" in recipients
        assert "pending@example.com" not in recipients
