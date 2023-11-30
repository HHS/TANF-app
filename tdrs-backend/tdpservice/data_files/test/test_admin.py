"""Test DataFileAdmin methods."""
import pytest
from django.contrib.admin.sites import AdminSite

from tdpservice.data_files.admin import DataFileAdmin
from tdpservice.data_files.models import DataFile
from tdpservice.data_files.test.factories import DataFileFactory
from tdpservice.parsers.test.factories import DataFileSummaryFactory
from django.conf import settings

@pytest.mark.django_db
def test_DataFileAdmin_status():
    """Test DataFileAdmin status method."""
    data_file = DataFileFactory()
    data_file_summary = DataFileSummaryFactory(datafile=data_file)
    data_file_admin = DataFileAdmin(DataFile, AdminSite())

    assert data_file_admin.status(data_file) == data_file_summary.status
    assert data_file_admin.case_totals(data_file) == data_file_summary.case_aggregates
    DOMAIN = settings.FRONTEND_BASE_URL
    assert data_file_admin.error_report_link(data_file) == \
        f"<a href='{DOMAIN}/admin/parsers/parsererror/?file={data_file.id}'>Parser Errors: 0</a>"
