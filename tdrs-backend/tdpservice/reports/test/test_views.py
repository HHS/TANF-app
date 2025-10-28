"""Tests for ReportFileViewSet."""

import pytest
from rest_framework import status

from tdpservice.reports.models import ReportFile, ReportIngest


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
        assert created.section == report_file_data["section"]
        assert created.extension == "zip"
        assert created.file

    def test_master_upload(
        self,
        api_client_logged_in,
        master_zip_file,
        # mock_storage_save,
        # mock_celery_delay,
    ):
        """Admin can POST to /master with a zip."""

        resp = api_client_logged_in.post(
            f"{self.root_url}master/",
            data={"master_zip": master_zip_file},
            format="multipart",
        )

        assert resp.status_code == status.HTTP_202_ACCEPTED

        ingest_id = resp.data["id"]
        ingest_obj = ReportIngest.objects.get(id=ingest_id)

        assert ingest_obj.original_filename == "master.zip"
        assert ingest_obj.status == ReportIngest.Status.PENDING
        # assert ingest_obj.s3_key == mock_storage_save.return_value

        # celery dispatched with ingest id
        # mock_celery_delay.assert_called_once_with(ingest_obj.id)

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

    def test_data_analyst_master_upload_disallowed(
        self, api_client_logged_in, master_zip_file
    ):
        """Data Analysts cannot create master zip files."""
        resp = api_client_logged_in.post(
            f"{self.root_url}master/",
            data={"master_zip": master_zip_file},
            format="multipart",
        )

        assert resp.status_code == status.HTTP_403_FORBIDDEN
