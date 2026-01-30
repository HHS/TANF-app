"""Tests for ReportFileViewSet."""

import pytest
from rest_framework import status

from tdpservice.reports.models import ReportFile, ReportSource


@pytest.mark.django_db
class TestReportFileViewAsOFAAdmin:
    """Tests for an OFA Admin user interacting with /v1/reports/ endpoints."""

    root_url = "/v1/reports/"

    @pytest.fixture
    def api_client_logged_in(self, api_client, ofa_admin):
        """Return an API client authenticated as an admin user."""

        api_client.login(username=ofa_admin.username, password="test_password")
        return api_client

    def test_create_report_file(
        self,
        api_client_logged_in,
        report_file_data,
    ):
        """Admin can POST a single zip to create a ReportFile row."""

        resp = api_client_logged_in.post(
            self.root_url, report_file_data, format="multipart"
        )
        assert resp.status_code in [status.HTTP_201_CREATED, status.HTTP_200_OK]

        # make sure we actually inserted a row
        pk = resp.data["id"]
        created = ReportFile.objects.get(id=pk)
        assert created.original_filename == report_file_data["original_filename"]
        assert created.extension == "zip"
        assert created.file

    def test_report_source_upload(
        self,
        api_client_logged_in,
        fiscal_year_report_source_zip,
    ):
        """Admin can POST to /report_source with a nested fiscal year zip."""

        resp = api_client_logged_in.post(
            f"{self.root_url}report-sources/",
            data={"file": fiscal_year_report_source_zip},
            format="multipart",
        )

        assert resp.status_code == status.HTTP_201_CREATED

        source_id = resp.data["id"]
        source_obj = ReportSource.objects.get(id=source_id)

        assert source_obj.original_filename == "report_source.zip"
        assert source_obj.status == ReportSource.Status.PENDING

    def test_download_report_file(self, api_client_logged_in, report_file_instance):
        """Stream report file to caller."""
        resp = api_client_logged_in.get(
            f"{self.root_url}{report_file_instance.id}/download/"
        )

        assert resp.status_code == status.HTTP_200_OK
        assert b"".join(resp.streaming_content) == report_file_instance.file.read()


@pytest.mark.django_db
class TestReportFileViewAsDataAnalyst:
    """Tests for a Data Analyst user (non-admin)."""

    root_url = "/v1/reports/"

    @pytest.fixture
    def api_client_logged_in(self, api_client, data_analyst):
        """Return an API client authenticated as an data analyst user."""

        api_client.login(username=data_analyst.username, password="test_password")
        return api_client

    def test_get_report_file(self, api_client_logged_in, report_file_instance):
        """Test that Data Analyst can get report file associated with their STT."""
        resp = api_client_logged_in.get(self.root_url)

        assert resp.status_code == status.HTTP_200_OK
        assert resp.data["count"] >= 1

        returned_ids = [row["id"] for row in resp.data["results"]]
        assert report_file_instance.id in returned_ids

    def test_data_analyst_only_sees_own_stt_reports(
        self, api_client_logged_in, data_analyst, report_file_instance
    ):
        """Test that Data Analyst only sees reports for their assigned STT."""
        import datetime
        from tdpservice.stts.models import STT, Region
        from tdpservice.reports.test.factories import ReportFileFactory

        # Create another STT (Alabama)
        other_region, _ = Region.objects.get_or_create(id=4)
        other_stt, _ = STT.objects.get_or_create(
            name="Alabama", region=other_region, stt_code="01"
        )

        # Create report files for the other STT (should NOT be visible)
        other_report_1 = ReportFileFactory.create(
            stt=other_stt, user=data_analyst, year=2024, date_extracted_on=datetime.date(2024, 1, 31)
        )
        other_report_2 = ReportFileFactory.create(
            stt=other_stt, user=data_analyst, year=2024, date_extracted_on=datetime.date(2024, 3, 31)
        )

        # Create an additional report for data analyst's own STT (should be visible)
        own_report = ReportFileFactory.create(
            stt=data_analyst.stt, user=data_analyst, year=2024, date_extracted_on=datetime.date(2024, 6, 30)
        )

        # Make request to list endpoint
        resp = api_client_logged_in.get(self.root_url)

        assert resp.status_code == status.HTTP_200_OK

        # Get all returned report IDs
        returned_ids = [row["id"] for row in resp.data["results"]]

        # Verify data analyst sees their own STT's reports
        assert report_file_instance.id in returned_ids
        assert own_report.id in returned_ids

        # Verify data analyst does NOT see other STT's reports
        assert other_report_1.id not in returned_ids
        assert other_report_2.id not in returned_ids

        # Verify the count matches (should only see reports for their STT)
        expected_count = 2  # report_file_instance + own_report
        assert resp.data["count"] == expected_count

    def test_data_analyst_create_report_file_disallowed(
        self, api_client_logged_in, report_file_data
    ):
        """Data Analysts cannot create report files."""
        resp = api_client_logged_in.post(
            self.root_url, report_file_data, format="multipart"
        )

        assert resp.status_code == status.HTTP_403_FORBIDDEN

    def test_download_report_file(self, api_client_logged_in, report_file_instance):
        """Stream report file to caller."""
        resp = api_client_logged_in.get(
            f"{self.root_url}{report_file_instance.id}/download/"
        )

        assert resp.status_code == status.HTTP_200_OK
        assert b"".join(resp.streaming_content) == report_file_instance.file.read()

    def test_data_analyst_report_source_upload_disallowed(
        self, api_client_logged_in, fiscal_year_report_source_zip
    ):
        """Data Analysts cannot create report source zip files."""
        resp = api_client_logged_in.post(
            f"{self.root_url}report_source/",
            data={"file": fiscal_year_report_source_zip},
            format="multipart",
        )

        assert resp.status_code == status.HTTP_403_FORBIDDEN

    def test_latest_param_returns_single_report(
        self, api_client_logged_in, data_analyst, report_file_instance
    ):
        """Test that latest=true returns only the most recent report."""
        import datetime
        from django.utils import timezone
        from datetime import timedelta
        from tdpservice.reports.test.factories import ReportFileFactory

        # Create additional reports for the same STT with different dates
        older_report = ReportFileFactory.create(
            stt=data_analyst.stt, user=data_analyst, year=2025, date_extracted_on=datetime.date(2025, 1, 31)
        )
        older_report.created_at = timezone.now() - timedelta(days=10)
        older_report.save()

        newest_report = ReportFileFactory.create(
            stt=data_analyst.stt, user=data_analyst, year=2025, date_extracted_on=datetime.date(2025, 3, 31)
        )
        newest_report.created_at = timezone.now() + timedelta(days=1)
        newest_report.save()

        # Request with latest=true
        resp = api_client_logged_in.get(f"{self.root_url}?latest=true")

        assert resp.status_code == status.HTTP_200_OK
        assert len(resp.data["results"]) == 1
        assert resp.data["results"][0]["id"] == newest_report.id

    def test_latest_param_with_year_filter(
        self, api_client_logged_in, data_analyst
    ):
        """Test that latest=true works with year filter."""
        import datetime
        from django.utils import timezone
        from datetime import timedelta
        from tdpservice.reports.test.factories import ReportFileFactory

        # Create multiple reports for the same year with different versions
        # (unique constraint on version, date_extracted_on, year, stt)
        older_report = ReportFileFactory.create(
            stt=data_analyst.stt, user=data_analyst, year=2025, date_extracted_on=datetime.date(2025, 1, 31), version=1
        )
        older_report.created_at = timezone.now() - timedelta(days=5)
        older_report.save()

        newer_report = ReportFileFactory.create(
            stt=data_analyst.stt, user=data_analyst, year=2025, date_extracted_on=datetime.date(2025, 1, 31), version=2
        )
        newer_report.created_at = timezone.now()
        newer_report.save()

        # Create a report for a different year (should not be returned)
        other_year_report = ReportFileFactory.create(
            stt=data_analyst.stt, user=data_analyst, year=2024, date_extracted_on=datetime.date(2024, 3, 31), version=1
        )
        other_year_report.created_at = timezone.now() + timedelta(days=1)
        other_year_report.save()

        # Request latest for specific year
        resp = api_client_logged_in.get(
            f"{self.root_url}?year=2025&latest=true"
        )

        assert resp.status_code == status.HTTP_200_OK
        assert len(resp.data["results"]) == 1
        assert resp.data["results"][0]["id"] == newer_report.id

    def test_latest_param_returns_empty_when_no_reports(
        self, api_client_logged_in, data_analyst
    ):
        """Test that latest=true returns empty list when no reports exist."""
        # Clear any existing reports for this STT
        ReportFile.objects.filter(stt=data_analyst.stt).delete()

        resp = api_client_logged_in.get(f"{self.root_url}?latest=true")

        assert resp.status_code == status.HTTP_200_OK
        assert len(resp.data["results"]) == 0
