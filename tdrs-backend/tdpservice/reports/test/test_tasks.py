"""Tests for report processing tasks."""

import io
import zipfile
from datetime import date, datetime
from unittest.mock import patch

from django.utils import timezone

import pytest

from tdpservice.reports.models import ReportFile, ReportSource, ReportType
from tdpservice.reports.tasks import (
    bundle_stt_files,
    find_stt_folders,
    process_report_source,
)
from tdpservice.reports.test.conftest import create_nested_zip


class TestFindSttFolders:
    """Tests for find_stt_folders function."""

    def test_single_stt(self):
        """Should find files for a single STT."""
        structure = {"FY2025": {"RO1": {"F1": ["report1.pdf", "report2.pdf"]}}}
        zip_buffer = create_nested_zip(structure, "FY2025_test")
        zip_file = zipfile.ZipFile(zip_buffer)

        stt_files = find_stt_folders(zip_file)

        assert "1" in stt_files
        assert len(stt_files["1"]) == 2

    def test_multiple_stts(self):
        """Should find files for multiple STTs."""
        structure = {
            "FY2025": {
                "RO1": {"F1": ["report1.pdf"], "F2": ["report2.pdf", "report3.pdf"]}
            }
        }
        zip_buffer = create_nested_zip(structure, "FY2025_test")
        zip_file = zipfile.ZipFile(zip_buffer)

        stt_files = find_stt_folders(zip_file)

        assert "1" in stt_files
        assert "2" in stt_files
        assert len(stt_files["1"]) == 1
        assert len(stt_files["2"]) == 2

    def test_multiple_regions(self):
        """Should find files across multiple regions."""
        structure = {
            "FY2025": {"RO1": {"F1": ["report1.pdf"]}, "RO2": {"F2": ["report2.pdf"]}}
        }
        zip_buffer = create_nested_zip(structure, "FY2025_test")
        zip_file = zipfile.ZipFile(zip_buffer)

        stt_files = find_stt_folders(zip_file)

        assert "1" in stt_files
        assert "2" in stt_files

    def test_no_stt_folders(self):
        """Should raise ValueError if no STT folders found."""
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, "w") as zf:
            # Only 2 levels deep - not enough (need 5: root/FY/RO/F/file)
            zf.writestr("FY2025_test/FY2025/report.pdf", b"content")
        zip_buffer.seek(0)
        zip_file = zipfile.ZipFile(zip_buffer)

        with pytest.raises(ValueError, match="No STT folders found"):
            find_stt_folders(zip_file)


class TestBundleSttFiles:
    """Tests for bundle_stt_files function."""

    def test_bundle_multiple_files(self):
        """Should bundle multiple files into a single zip."""
        structure = {"FY2025": {"RO1": {"F1": ["report1.pdf", "report2.pdf"]}}}
        zip_buffer = create_nested_zip(structure, "FY2025_test")
        report_source_zip = zipfile.ZipFile(zip_buffer)

        # Get file infos for STT "F1" (which maps to stt_code "1")
        file_infos = [
            info
            for info in report_source_zip.infolist()
            if not info.is_dir() and "FY2025_test/FY2025/RO1/F1/" in info.filename
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

    def test_bundle_preserves_paths_relative_to_stt_folder(self):
        """Should preserve folder structure under the STT folder when bundling."""
        structure = {"FY2025": {"RO1": {"F1": ["reports/january/report1.pdf"]}}}
        zip_buffer = create_nested_zip(structure, "FY2025_test")
        report_source_zip = zipfile.ZipFile(zip_buffer)

        file_infos = [
            info
            for info in report_source_zip.infolist()
            if not info.is_dir() and "FY2025_test/FY2025/RO1/F1/" in info.filename
        ]

        bundled = bundle_stt_files(report_source_zip, file_infos, "1")

        bundled_zip = zipfile.ZipFile(io.BytesIO(bundled.read()))
        names = bundled_zip.namelist()

        assert names == ["reports/january/report1.pdf"]

    def test_bundle_retains_duplicate_basenames_in_different_folders(self):
        """Should retain files with the same basename when their relative paths differ."""
        structure = {
            "FY2025": {
                "RO1": {
                    "F1": [
                        "reports/january/summary.pdf",
                        "reports/february/summary.pdf",
                    ]
                }
            }
        }
        zip_buffer = create_nested_zip(structure, "FY2025_test")
        report_source_zip = zipfile.ZipFile(zip_buffer)

        file_infos = [
            info
            for info in report_source_zip.infolist()
            if not info.is_dir() and "FY2025_test/FY2025/RO1/F1/" in info.filename
        ]

        bundled = bundle_stt_files(report_source_zip, file_infos, "1")

        bundled_zip = zipfile.ZipFile(io.BytesIO(bundled.read()))
        names = bundled_zip.namelist()

        assert "reports/january/summary.pdf" in names
        assert "reports/february/summary.pdf" in names
        assert len(names) == 2


@pytest.mark.django_db
class TestProcessReportSource:
    """Tests for process_report_source task."""

    @patch("tdpservice.reports.tasks.timezone.now")
    def test_process_valid_report_source_zip(self, mock_now, ofa_admin):
        """Should successfully process a valid report source zip."""
        from tdpservice.stts.models import STT, Region

        # Create region and STT with stt_code="01" directly
        region = Region.objects.create(id=9001, name="Test Region")
        STT.objects.create(
            id=8001,
            stt_code="01",
            name="Test STT 1",
            region=region,
            postal_code="T1",
            type="STATE",
        )

        mock_now.return_value = timezone.make_aware(datetime(2025, 2, 1))

        # Create source record with nested zip
        structure = {"FY2025": {"RO1": {"F1": ["report1.pdf", "report2.pdf"]}}}
        zip_buffer = create_nested_zip(structure, "FY2025_01312025")

        from django.core.files.uploadedfile import SimpleUploadedFile

        uploaded_file = SimpleUploadedFile(
            "report_source.zip", zip_buffer.read(), content_type="application/zip"
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

    @patch("tdpservice.reports.tasks.timezone.now")
    def test_process_preserves_nested_paths_in_report_file_zip(self, mock_now, ofa_admin):
        """Should preserve STT-relative nested paths in the created ReportFile zip."""
        from tdpservice.stts.models import STT, Region

        region = Region.objects.create(id=9006, name="Test Region 6")
        STT.objects.create(
            id=8007,
            stt_code="12",
            name="Test STT 12",
            region=region,
            postal_code="T2",
            type="STATE",
        )

        mock_now.return_value = timezone.make_aware(datetime(2025, 2, 1))

        structure = {
            "FY2025": {
                "RO1": {
                    "F12": [
                        "reports/january/summary.pdf",
                        "reports/february/summary.pdf",
                        "readme.txt",
                    ]
                }
            }
        }
        zip_buffer = create_nested_zip(structure, "FY2025_01312025")

        from django.core.files.uploadedfile import SimpleUploadedFile

        uploaded_file = SimpleUploadedFile(
            "report_source.zip", zip_buffer.read(), content_type="application/zip"
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
        assert source.status == ReportSource.Status.SUCCEEDED
        assert source.num_reports_created == 1

        report_file = ReportFile.objects.get(source=source)
        report_file.file.open("rb")
        bundled_zip = zipfile.ZipFile(io.BytesIO(report_file.file.read()))
        report_file.file.close()

        names = bundled_zip.namelist()
        assert "reports/january/summary.pdf" in names
        assert "reports/february/summary.pdf" in names
        assert "readme.txt" in names
        assert len(names) == 3

    @patch("tdpservice.reports.tasks.timezone.now")
    def test_process_multiple_stts(self, mock_now, ofa_admin):
        """Should create multiple ReportFiles for multiple STTs."""
        from tdpservice.stts.models import STT, Region

        # Create a shared region for both STTs
        region = Region.objects.create(id=9002, name="Test Region 2")

        # Create STTs with stt_code="01" and "2"
        STT.objects.create(
            id=8002,
            stt_code="01",
            name="Test STT 1",
            region=region,
            postal_code="T1",
            type="STATE",
        )
        STT.objects.create(
            id=8003,
            stt_code="02",
            name="Test STT 2",
            region=region,
            postal_code="T2",
            type="STATE",
        )

        mock_now.return_value = timezone.make_aware(datetime(2025, 5, 1))

        structure = {"FY2025": {"RO1": {"F1": ["report1.pdf"], "F2": ["report2.pdf"]}}}
        zip_buffer = create_nested_zip(structure, "FY2025_04302025")

        from django.core.files.uploadedfile import SimpleUploadedFile

        uploaded_file = SimpleUploadedFile(
            "report_source.zip", zip_buffer.read(), content_type="application/zip"
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
            "report_source.zip", b"not a zip file", content_type="application/zip"
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
        structure = {"FY2025": {"RO1": {"F999": ["report1.pdf"]}}}  # Invalid STT code
        zip_buffer = create_nested_zip(structure, "FY2025_test")

        from django.core.files.uploadedfile import SimpleUploadedFile

        uploaded_file = SimpleUploadedFile(
            "report_source.zip", zip_buffer.read(), content_type="application/zip"
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
        from tdpservice.stts.models import STT, Region

        # Create region and STT
        region = Region.objects.create(id=9005, name="Test Region 5")
        STT.objects.create(
            id=8006,
            stt_code="01",
            name="Test STT 1",
            region=region,
            postal_code="T1",
            type="STATE",
        )

        # Zip has FY2025 structure, but source.year=2024
        structure = {"FY2025": {"RO9005": {"F1": ["report1.pdf"]}}}
        zip_buffer = create_nested_zip(structure, "FY2025_test")

        from django.core.files.uploadedfile import SimpleUploadedFile

        uploaded_file = SimpleUploadedFile(
            "report_source.zip", zip_buffer.read(), content_type="application/zip"
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
class TestProcessReportSourceReportType:
    """Tests for report_type propagation from ReportSource to ReportFile."""

    @patch("tdpservice.reports.tasks.timezone.now")
    def test_fra_source_creates_fra_report_files(self, mock_now, ofa_admin):
        """Verify ReportSource with report_type=FRA produces ReportFiles with report_type=FRA."""
        from tdpservice.stts.models import STT, Region

        region = Region.objects.create(id=9020, name="Test Region RT1")
        STT.objects.create(
            id=8020,
            stt_code="01",
            name="Test STT RT1",
            region=region,
            postal_code="R1",
            type="STATE",
        )

        mock_now.return_value = timezone.make_aware(datetime(2025, 2, 1))

        structure = {"FY2025": {"RO1": {"F1": ["report1.pdf"]}}}
        zip_buffer = create_nested_zip(structure, "FY2025_test")

        from django.core.files.uploadedfile import SimpleUploadedFile

        uploaded_file = SimpleUploadedFile(
            "report_source.zip", zip_buffer.read(), content_type="application/zip"
        )

        source = ReportSource.objects.create(
            uploaded_by=ofa_admin,
            original_filename="report_source.zip",
            slug="report_source.zip",
            file=uploaded_file,
            year=2025,
            date_extracted_on=date(2025, 1, 31),
            report_type=ReportType.FRA,
        )

        process_report_source(source.id)

        source.refresh_from_db()
        assert source.status == ReportSource.Status.SUCCEEDED

        report_file = ReportFile.objects.filter(source=source).first()
        assert report_file.report_type == ReportType.FRA

    @patch("tdpservice.reports.tasks.timezone.now")
    def test_tanf_ssp_source_creates_tanf_ssp_report_files(self, mock_now, ofa_admin):
        """Verify ReportSource with report_type=TANF_SSP produces ReportFiles with report_type=TANF_SSP."""
        from tdpservice.stts.models import STT, Region

        region = Region.objects.create(id=9021, name="Test Region RT2")
        STT.objects.create(
            id=8021,
            stt_code="01",
            name="Test STT RT2",
            region=region,
            postal_code="R2",
            type="STATE",
        )

        mock_now.return_value = timezone.make_aware(datetime(2025, 2, 1))

        structure = {"FY2025": {"RO1": {"F1": ["report1.pdf"]}}}
        zip_buffer = create_nested_zip(structure, "FY2025_test")

        from django.core.files.uploadedfile import SimpleUploadedFile

        uploaded_file = SimpleUploadedFile(
            "report_source.zip", zip_buffer.read(), content_type="application/zip"
        )

        source = ReportSource.objects.create(
            uploaded_by=ofa_admin,
            original_filename="report_source.zip",
            slug="report_source.zip",
            file=uploaded_file,
            year=2025,
            date_extracted_on=date(2025, 1, 31),
            report_type=ReportType.TANF_SSP,
        )

        process_report_source(source.id)

        source.refresh_from_db()
        assert source.status == ReportSource.Status.SUCCEEDED

        report_file = ReportFile.objects.filter(source=source).first()
        assert report_file.report_type == ReportType.TANF_SSP

    @patch("tdpservice.reports.tasks.timezone.now")
    def test_fra_source_multiple_stts_all_inherit_report_type(self, mock_now, ofa_admin):
        """All ReportFiles from an FRA source should have report_type=FRA."""
        from tdpservice.stts.models import STT, Region

        region = Region.objects.create(id=9022, name="Test Region RT3")
        STT.objects.create(
            id=8022,
            stt_code="01",
            name="Test STT RT3a",
            region=region,
            postal_code="R3",
            type="STATE",
        )
        STT.objects.create(
            id=8023,
            stt_code="02",
            name="Test STT RT3b",
            region=region,
            postal_code="R4",
            type="STATE",
        )

        mock_now.return_value = timezone.make_aware(datetime(2025, 2, 1))

        structure = {"FY2025": {"RO1": {"F1": ["report1.pdf"], "F2": ["report2.pdf"]}}}
        zip_buffer = create_nested_zip(structure, "FY2025_test")

        from django.core.files.uploadedfile import SimpleUploadedFile

        uploaded_file = SimpleUploadedFile(
            "report_source.zip", zip_buffer.read(), content_type="application/zip"
        )

        source = ReportSource.objects.create(
            uploaded_by=ofa_admin,
            original_filename="report_source.zip",
            slug="report_source.zip",
            file=uploaded_file,
            year=2025,
            date_extracted_on=date(2025, 1, 31),
            report_type=ReportType.FRA,
        )

        process_report_source(source.id)

        source.refresh_from_db()
        assert source.status == ReportSource.Status.SUCCEEDED
        assert source.num_reports_created == 2

        report_files = ReportFile.objects.filter(source=source)
        for rf in report_files:
            assert rf.report_type == ReportType.FRA


@pytest.mark.django_db
class TestProcessReportSourceEmailNotification:
    """Tests for email notification when ReportFile is created."""

    @patch("tdpservice.reports.tasks.send_feedback_report_available_email")
    @patch("tdpservice.reports.tasks.timezone.now")
    def test_sends_email_when_report_file_created(
        self, mock_now, mock_send_email, ofa_admin
    ):
        """Test that email is sent when a ReportFile is created."""
        mock_now.return_value = timezone.make_aware(datetime(2025, 2, 1))

        from django.contrib.auth.models import Group

        from tdpservice.stts.models import STT, Region
        from tdpservice.users.models import AccountApprovalStatusChoices, User

        # Create region and STT
        region = Region.objects.create(id=9010, name="Test Region 10")
        stt = STT.objects.create(
            id=8010,
            stt_code="01",
            name="Test STT Email",
            region=region,
            postal_code="TE",
            type="STATE",
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

        # Create source record
        structure = {"FY2025": {"RO1": {"F1": ["report.pdf"]}}}
        zip_buffer = create_nested_zip(structure, "FY2025_test")

        from django.core.files.uploadedfile import SimpleUploadedFile

        uploaded_file = SimpleUploadedFile(
            "report_source.zip", zip_buffer.read(), content_type="application/zip"
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

    @patch("tdpservice.reports.tasks.send_feedback_report_available_email")
    @patch("tdpservice.reports.tasks.timezone.now")
    def test_does_not_send_email_when_no_data_analysts(
        self, mock_now, mock_send_email, ofa_admin
    ):
        """Test that no email is sent when no Data Analysts exist for STT."""
        from tdpservice.stts.models import STT, Region

        # Create region and STT with no Data Analysts
        region = Region.objects.create(id=9011, name="Test Region 11")
        STT.objects.create(
            id=8011,
            stt_code="01",
            name="Test STT No Analysts",
            region=region,
            postal_code="TN",
            type="STATE",
        )

        mock_now.return_value = timezone.make_aware(datetime(2025, 2, 1))

        structure = {"FY2025": {"RO1": {"F1": ["report.pdf"]}}}
        zip_buffer = create_nested_zip(structure, "FY2025_test")

        from django.core.files.uploadedfile import SimpleUploadedFile

        uploaded_file = SimpleUploadedFile(
            "report_source.zip", zip_buffer.read(), content_type="application/zip"
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

    @patch("tdpservice.reports.tasks.send_feedback_report_available_email")
    @patch("tdpservice.reports.tasks.timezone.now")
    def test_sends_email_to_multiple_data_analysts(
        self, mock_now, mock_send_email, ofa_admin
    ):
        """Test that email is sent to all Data Analysts for the STT."""
        mock_now.return_value = timezone.make_aware(datetime(2025, 2, 1))

        from django.contrib.auth.models import Group

        from tdpservice.stts.models import STT, Region
        from tdpservice.users.models import AccountApprovalStatusChoices, User

        # Create region and STT
        region = Region.objects.create(id=9012, name="Test Region 12")
        stt = STT.objects.create(
            id=8012,
            stt_code="01",
            name="Test STT Multiple Analysts",
            region=region,
            postal_code="TM",
            type="STATE",
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

        structure = {"FY2025": {"RO1": {"F1": ["report.pdf"]}}}
        zip_buffer = create_nested_zip(structure, "FY2025_test")

        from django.core.files.uploadedfile import SimpleUploadedFile

        uploaded_file = SimpleUploadedFile(
            "report_source.zip", zip_buffer.read(), content_type="application/zip"
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

    @patch("tdpservice.reports.tasks.send_feedback_report_available_email")
    @patch("tdpservice.reports.tasks.timezone.now")
    def test_only_sends_to_approved_data_analysts(
        self, mock_now, mock_send_email, ofa_admin
    ):
        """Test that email is only sent to approved Data Analysts."""
        mock_now.return_value = timezone.make_aware(datetime(2025, 2, 1))

        from django.contrib.auth.models import Group

        from tdpservice.stts.models import STT, Region
        from tdpservice.users.models import AccountApprovalStatusChoices, User

        # Create region and STT
        region = Region.objects.create(id=9013, name="Test Region 13")
        stt = STT.objects.create(
            id=8013,
            stt_code="01",
            name="Test STT Approved Only",
            region=region,
            postal_code="TA",
            type="STATE",
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

        structure = {"FY2025": {"RO1": {"F1": ["report.pdf"]}}}
        zip_buffer = create_nested_zip(structure, "FY2025_test")

        from django.core.files.uploadedfile import SimpleUploadedFile

        uploaded_file = SimpleUploadedFile(
            "report_source.zip", zip_buffer.read(), content_type="application/zip"
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


@pytest.mark.django_db
class TestFeedbackReportEmailContent:
    """Tests for email content being contextual to report_type."""

    def test_tanf_ssp_email_subject(self):
        """TANF_SSP report should produce subject with 'TANF/SSP'."""
        from unittest.mock import patch as mock_patch
        from tdpservice.reports.test.factories import ReportFileFactory
        from tdpservice.email.helpers.feedback_report import (
            send_feedback_report_available_email,
        )

        report = ReportFileFactory.create(report_type=ReportType.TANF_SSP)

        with mock_patch(
            "tdpservice.email.helpers.feedback_report.automated_email"
        ) as mock_email:
            send_feedback_report_available_email(report, ["test@example.com"])

            mock_email.assert_called_once()
            call_kwargs = mock_email.call_args[1]
            assert "TANF/SSP Feedback Report Available" in call_kwargs["subject"]
            assert call_kwargs["email_context"]["report_type_label"] == "TANF/SSP"
            assert call_kwargs["email_context"]["report_type"] == "TANF_SSP"

    def test_fra_email_subject(self):
        """FRA report should produce subject with 'FRA'."""
        from unittest.mock import patch as mock_patch
        from tdpservice.reports.test.factories import ReportFileFactory
        from tdpservice.email.helpers.feedback_report import (
            send_feedback_report_available_email,
        )

        report = ReportFileFactory.create(report_type=ReportType.FRA)

        with mock_patch(
            "tdpservice.email.helpers.feedback_report.automated_email"
        ) as mock_email:
            send_feedback_report_available_email(report, ["test@example.com"])

            mock_email.assert_called_once()
            call_kwargs = mock_email.call_args[1]
            assert "FRA Feedback Report Available" in call_kwargs["subject"]
            assert call_kwargs["email_context"]["report_type_label"] == "FRA"
            assert call_kwargs["email_context"]["report_type"] == "FRA"

    def test_email_text_message_includes_report_type(self):
        """Plain text fallback should include report_type_label."""
        from unittest.mock import patch as mock_patch
        from tdpservice.reports.test.factories import ReportFileFactory
        from tdpservice.email.helpers.feedback_report import (
            send_feedback_report_available_email,
        )

        report = ReportFileFactory.create(report_type=ReportType.FRA)

        with mock_patch(
            "tdpservice.email.helpers.feedback_report.automated_email"
        ) as mock_email:
            send_feedback_report_available_email(report, ["test@example.com"])

            call_kwargs = mock_email.call_args[1]
            assert "FRA feedback report" in call_kwargs["text_message"]

    @patch("tdpservice.reports.tasks.send_feedback_report_available_email")
    @patch("tdpservice.reports.tasks.timezone.now")
    def test_sends_to_regional_staff_in_stt_region(
        self, mock_now, mock_send_email, ofa_admin
    ):
        """Test that email is sent to Regional Staff whose region includes the STT."""
        mock_now.return_value = timezone.make_aware(datetime(2025, 2, 1))

        from django.contrib.auth.models import Group

        from tdpservice.stts.models import STT, Region
        from tdpservice.users.models import AccountApprovalStatusChoices, User

        # Create region and STT
        region = Region.objects.create(id=9014, name="Test Region 14")
        stt = STT.objects.create(
            id=8014,
            stt_code="01",
            name="Test STT Regional Email",
            region=region,
            postal_code="TR",
            type="STATE",
        )

        data_analyst_group, _ = Group.objects.get_or_create(name="Data Analyst")
        regional_group, _ = Group.objects.get_or_create(name="OFA Regional Staff")

        # Create approved Data Analyst for this STT
        analyst = User.objects.create(
            username="analyst_regional_test",
            email="analyst_regional@example.com",
            stt=stt,
            account_approval_status=AccountApprovalStatusChoices.APPROVED,
        )
        analyst.groups.add(data_analyst_group)

        # Create approved Regional Staff in the same region
        regional_user = User.objects.create(
            username="regional_staff_test",
            email="regional@example.com",
            account_approval_status=AccountApprovalStatusChoices.APPROVED,
        )
        regional_user.groups.add(regional_group)
        regional_user.regions.add(region)

        # Create Regional Staff in a different region (should NOT receive email)
        other_region = Region.objects.create(id=9015, name="Test Region 15")
        other_regional = User.objects.create(
            username="other_regional_test",
            email="other_regional@example.com",
            account_approval_status=AccountApprovalStatusChoices.APPROVED,
        )
        other_regional.groups.add(regional_group)
        other_regional.regions.add(other_region)

        structure = {"FY2025": {"RO1": {"F1": ["report.pdf"]}}}
        zip_buffer = create_nested_zip(structure, "FY2025_test")

        from django.core.files.uploadedfile import SimpleUploadedFile

        uploaded_file = SimpleUploadedFile(
            "report_source.zip", zip_buffer.read(), content_type="application/zip"
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

        # Verify both analyst and regional staff received email
        mock_send_email.assert_called_once()
        call_args = mock_send_email.call_args[0]
        recipients = call_args[1]

        assert "analyst_regional@example.com" in recipients
        assert "regional@example.com" in recipients
        assert "other_regional@example.com" not in recipients
