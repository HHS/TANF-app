"""Test DataFileAdmin methods."""
import pytest
from django.contrib.admin.sites import AdminSite
from datetime import datetime, timezone, timedelta

from tdpservice.data_files.admin.admin import DataFileAdmin
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

@pytest.mark.django_db
def test_SubmissionDateFilter(client):
    """Test SubmissionDateFilter method."""
    client.login(username='admin', password='password')
    # create fake queryset
    fake_query = DataFile.objects.all()
    data_file_admin = DataFileAdmin(DataFile, AdminSite())
    filter = DataFileAdmin.SubmissionDateFilter(None, {'Submission Day/Month/Year': '1'}, DataFile, DataFileAdmin)
    assert data_file_admin.SubmissionDateFilter.title == 'submission date'
    assert data_file_admin.SubmissionDateFilter.parameter_name == 'Submission Day/Month/Year'
    assert data_file_admin.SubmissionDateFilter.lookups(filter, None, None) == [
        ('0', 'Today'), ('1', 'Yesterday'), ('7', 'Past 7 days'), ('30', 'This month'), ('365', 'This year')
        ]
    assert data_file_admin.SubmissionDateFilter.queryset(filter, None, fake_query).exists() is False
    df = DataFileFactory()
    df.created_at = datetime.now(tz=timezone.utc) - timedelta(days=1)
    df.save()
    fake_query = DataFile.objects.all()
    assert data_file_admin.SubmissionDateFilter.queryset(filter, None, fake_query).exists() is True
    df.created_at = datetime.now(tz=timezone.utc) - timedelta(days=2)
    df.save()
    fake_query = DataFile.objects.all()
    assert data_file_admin.SubmissionDateFilter.queryset(filter, None, fake_query).exists() is False

    filter = DataFileAdmin.SubmissionDateFilter(None, {'Submission Day/Month/Year': '0'}, DataFile, DataFileAdmin)
    df.created_at = datetime.now(tz=timezone.utc) - timedelta(days=1)
    df.save()
    fake_query = DataFile.objects.all()
    assert data_file_admin.SubmissionDateFilter.queryset(filter, None, fake_query).exists() is False

    df.created_at = datetime.now(tz=timezone.utc)
    df.save()
    fake_query = DataFile.objects.all()
    assert data_file_admin.SubmissionDateFilter.queryset(filter, None, fake_query).exists() is True
