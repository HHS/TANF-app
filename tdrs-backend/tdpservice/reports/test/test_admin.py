"""Tests for reports admin query behavior."""

from django.contrib.admin.sites import AdminSite
from django.db import connection
from django.test import RequestFactory
from django.test.utils import CaptureQueriesContext

import pytest

from tdpservice.reports.admin import ReportFileAdmin, ReportSourceAdmin
from tdpservice.reports.models import ReportFile, ReportSource
from tdpservice.reports.test.factories import ReportFileFactory, ReportSourceFactory


@pytest.mark.django_db
def test_report_file_admin_changelist_relations_are_eager_loaded():
    """The report file admin should not query per row for displayed relations."""
    ReportFileFactory.create_batch(3)
    request = RequestFactory().get("/admin/reports/reportfile/")
    model_admin = ReportFileAdmin(ReportFile, AdminSite())

    report_files = list(model_admin.get_queryset(request))

    with CaptureQueriesContext(connection) as captured_queries:
        for report_file in report_files:
            str(report_file.stt)
            str(report_file.user)

    assert len(captured_queries) == 0


@pytest.mark.django_db
def test_report_source_admin_changelist_relations_are_eager_loaded():
    """The report source admin should not query per row for displayed relations."""
    ReportSourceFactory.create_batch(3)
    request = RequestFactory().get("/admin/reports/reportsource/")
    model_admin = ReportSourceAdmin(ReportSource, AdminSite())

    report_sources = list(model_admin.get_queryset(request))

    with CaptureQueriesContext(connection) as captured_queries:
        for report_source in report_sources:
            str(report_source.uploaded_by)

    assert len(captured_queries) == 0
