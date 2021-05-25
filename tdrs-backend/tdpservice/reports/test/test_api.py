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


class TestReportFileAPIAsOfaAdmin(ReportFileAPITestBase):
    """Test ReportFileViewSet as an OFA Admin user."""

    @pytest.fixture
    def user(self, ofa_admin):
        """Override the default user with ofa_admin for our tests."""
        return ofa_admin

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
