"""Tests for Reports Application."""
from rest_framework import status
import pytest

from tdpservice.reports.models import ReportFile


@pytest.mark.usefixtures('db')
class ReportFileAPITestBase:
    """A base test class for tests that interact with the ReportFileViewSet.

    Provides several fixtures and methods that are commonly used between tests.
    Intended to simplify creating tests for different user flows.
    """

    root_url = '/v1/reports/'

    @pytest.fixture
    def user(self):
        """User instance that will be used to log in to the API client.

        This fixture must be overridden in each child test class.
        """
        raise NotImplementedError()

    @pytest.fixture
    def api_client(self, api_client, user):
        """Provide an API client that is logged in with the specified user."""
        api_client.login(username=user.username, password='test_password')
        return api_client

    @staticmethod
    def get_report_record(report_data, version, user):
        """Retrieve a report record using unique constraints"""
        return ReportFile.objects.filter(
            slug=report_data["slug"],
            year=report_data["year"],
            section=report_data["section"],
            version=version,
            user=user,
        )

    @staticmethod
    def assert_report_created(response):
        """Assert that the report was created."""
        assert response.status_code == status.HTTP_201_CREATED

    @staticmethod
    def assert_report_rejected(response):
        """Assert that a given report submission was rejected."""
        assert response.status_code == status.HTTP_403_FORBIDDEN

    @staticmethod
    def assert_report_exists(report_data, version, user):
        """Confirm that a report matching the provided data exists in the DB."""
        assert ReportFile.objects.filter(
            slug=report_data["slug"],
            year=report_data["year"],
            section=report_data["section"],
            version=version,
            user=user,
        ).exists()

    def post_report_file(self, api_client, report_data):
        """Submit a report with the given data."""
        return api_client.post(
            self.root_url,
            report_data,
            format='multipart'
        )

    def get_report_files(self, api_client):
        """Submit a report with the given data."""
        return api_client.get(
            self.root_url
        )

    def get_report_file(self, api_client, report_id):
        """Get report file meta data."""
        return api_client.get(
            f"{self.root_url}{report_id}/"
        )

    def download_file(self, api_client, report_id):
        """Stream a file for download."""
        return api_client.get(f"{self.root_url}{report_id}/download/")

class TestReportFileAPIAsOfaAdmin(ReportFileAPITestBase):
    """Test ReportFileViewSet as an OFA Admin user."""

    @pytest.fixture
    def user(self, ofa_admin):
        """Override the default user with ofa_admin for our tests."""
        return ofa_admin

    def test_get_report_file_meta_data(self, api_client, report_data, user):
        """Assert the meta data the api provides is as expected."""
        response = self.post_report_file(api_client, report_data)
        report_id = response.data['id']
        assert ReportFile.objects.get(id=report_id)
        response = self.get_report_file(api_client, report_id)

        assert response.data['id'] == report_id

        assert str(response.data['user']) == report_data['user']

        assert response.data['quarter'] == report_data['quarter']
        assert response.data['stt'] == report_data['stt']
        assert response.data['year'] == report_data['year']

    def test_download_report_file(self, api_client, report_data, user):
        """Test that the file is transmitted with out errors."""
        response = self.post_report_file(api_client, report_data)
        report_id = response.data['id']
        response = self.download_file(api_client, report_id)

        assert response.status_code == status.HTTP_200_OK

        report_file = ReportFile.objects.get(id=report_id)
        assert b''.join(response.streaming_content) == report_file.file.read()

    def test_create_report_file_entry(self, api_client, report_data, user):
        """Test ability to create report file metadata registry."""
        response = self.post_report_file(api_client, report_data)
        self.assert_report_created(response)
        self.assert_report_exists(report_data, 1, user)

    def test_report_file_version_increment(
        self,
        api_client,
        report_data,
        other_report_data,
        user
    ):
        """Test that report file version numbers incremented."""
        response1 = self.post_report_file(api_client, report_data)
        response2 = self.post_report_file(api_client, other_report_data)

        self.assert_report_created(response1)
        self.assert_report_created(response2)

        self.assert_report_exists(report_data, 1, user)
        self.assert_report_exists(other_report_data, 2, user)


class TestReportFileAPIAsDataPrepper(ReportFileAPITestBase):
    """Test ReportFileViewSet as a Data Prepper user."""

    @pytest.fixture
    def user(self, data_prepper):
        """Override the default user with data_prepper for our tests."""
        return data_prepper

    def test_reports_data_prepper_permission(self, api_client, report_data, user):
        """Test that a Data Prepper is allowed to add reports to their own STT."""
        response = self.post_report_file(api_client, report_data)
        self.assert_report_created(response)
        self.assert_report_exists(report_data, 1, user)

    def test_reports_data_prepper_not_allowed(self, api_client, report_data, user):
        """Test that Data preppers can't add reports to STTs other than their own."""
        report_data['stt'] = report_data['stt'] + 1

        response = self.post_report_file(api_client, report_data)
        self.assert_report_rejected(response)


class TestReportFileAPIAsInactiveUser(ReportFileAPITestBase):
    """Test ReportFileViewSet as an inactive user."""

    @pytest.fixture
    def user(self, inactive_user):
        """Override the default user with inactive_user for our tests."""
        return inactive_user

    def test_reports_inactive_user_not_allowed(
        self,
        api_client,
        inactive_user,
        report_data
    ):
        """Test that an inactive user can't add reports at all."""
        response = self.post_report_file(api_client, report_data)
        self.assert_report_rejected(response)


def multi_year_report_data(user, stt):
    """Return report data that encompasses multiple years."""
    return [{"original_filename": "report.txt",
             "quarter": "Q1",
             "user": user,
             "stt": stt,
             "year": 2020,
             "section": "Active Case Data", },
            {"original_filename": "report.txt",
             "quarter": "Q1",
             "user": user,
             "stt": stt,
             "year": 2021,
             "section": "Active Case Data", },
            {"original_filename": "report.txt",
             "quarter": "Q1",
             "user": user,
             "stt": stt,
             "year": 2022,
             "section": "Active Case Data", }]


@pytest.mark.django_db
def test_list_report_years(api_client, data_prepper):
    """Test list of years for which there exist a report as a data prepper."""
    user = data_prepper

    reports = multi_year_report_data(user, user.stt)

    ReportFile.create_new_version(reports[0])
    ReportFile.create_new_version(reports[1])
    ReportFile.create_new_version(reports[2])

    api_client.login(username=user.username, password="test_password")

    response = api_client.get("/v1/reports/years")

    assert response.status_code == status.HTTP_200_OK
    assert response.data == [
        2020,
        2021,
        2022
    ]


@pytest.mark.django_db
def test_list_ofa_admin_report_years(api_client, ofa_admin, stt):
    """Test list of years for which there exist a report as an OFA admin."""
    user = ofa_admin

    reports = multi_year_report_data(user, stt)

    ReportFile.create_new_version(reports[0])
    ReportFile.create_new_version(reports[1])
    ReportFile.create_new_version(reports[2])

    api_client.login(username=user.username, password="test_password")

    response = api_client.get(f"/v1/reports/years/{stt.id}")

    assert response.status_code == status.HTTP_200_OK
    assert response.data == [
        2020,
        2021,
        2022
    ]


@pytest.mark.django_db
def test_list_ofa_admin_report_years_positional_stt(api_client, ofa_admin, stt):
    """Test list year fail for OFA admin when no STT is provided."""
    user = ofa_admin

    data1, data2, data3 = multi_year_report_data(user, stt)

    ReportFile.create_new_version(data1)
    ReportFile.create_new_version(data2)
    ReportFile.create_new_version(data3)

    api_client.login(username=user.username, password="test_password")

    response = api_client.get("/v1/reports/years")

    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_list_ofa_admin_report_years_no_self_stt(api_client, ofa_admin_stt_user, stt):
    """Test OFA Admin with no stt assigned can view list of years."""
    user = ofa_admin_stt_user

    data1, data2, data3 = multi_year_report_data(user, stt)

    assert user.stt is None

    ReportFile.create_new_version(data1)
    ReportFile.create_new_version(data2)
    ReportFile.create_new_version(data3)

    api_client.login(username=user.username, password="test_password")

    response = api_client.get(f"/v1/reports/years/{stt.id}")

    assert response.status_code == status.HTTP_200_OK

    assert response.data == [
        2020,
        2021,
        2022
    ]
