"""Test DataFileAdmin methods."""
from datetime import datetime, timedelta, timezone

from django.conf import settings
from django.contrib.admin.sites import AdminSite
from django.test import RequestFactory

import pytest

from tdpservice.data_files.admin import admin as data_file_admin_module
from tdpservice.data_files.admin.admin import DataFileAdmin
from tdpservice.data_files.enums import SubmissionState
from tdpservice.data_files.models import DataFile
from tdpservice.data_files.test.factories import DataFileFactory
from tdpservice.parsers.test.factories import DataFileSummaryFactory


@pytest.mark.django_db
def test_DataFileAdmin_status():
    """Test DataFileAdmin status method."""
    data_file = DataFileFactory()
    data_file_summary = DataFileSummaryFactory(datafile=data_file)
    data_file_admin = DataFileAdmin(DataFile, AdminSite())

    assert data_file_admin.status(data_file) == data_file_summary.status
    assert data_file_admin.case_totals(data_file) == data_file_summary.case_aggregates
    DOMAIN = settings.FRONTEND_BASE_URL
    assert (
        data_file_admin.error_report_link(data_file)
        == f"<a href='{DOMAIN}/admin/parsers/parsererror/?file={data_file.id}'>Parser Errors: 0</a>"
    )


def test_DataFileAdmin_exposes_state_in_admin():
    """Test DataFileAdmin surfaces state in changelist and detail view."""
    data_file_admin = DataFileAdmin(DataFile, AdminSite())
    properties_fieldset = next(
        fieldset
        for fieldset in data_file_admin.fieldsets
        if fieldset[0] == "Properties"
    )

    assert "parsing_state" in data_file_admin.list_display
    assert "parsing_state" in properties_fieldset[1]["fields"]


@pytest.mark.django_db
def test_DataFileAdmin_parsing_state_uses_choice_label():
    """Test DataFileAdmin displays friendly submission state labels."""
    data_file = DataFileFactory(state=SubmissionState.PARSE_FAILED)
    data_file_admin = DataFileAdmin(DataFile, AdminSite())

    assert data_file_admin.parsing_state(data_file) == "Parse failed"


@pytest.mark.django_db
def test_DataFileAdmin_reparse_prepares_legacy_uploaded_files(
    monkeypatch,
    admin_user,
):
    """Test admin reparse prepares legacy uploaded files before queueing."""
    legacy_file = DataFileFactory(state=SubmissionState.UPLOADED)
    ready_file = DataFileFactory(state=SubmissionState.PARSE_COMPLETED)
    unsafe_file = DataFileFactory(state=SubmissionState.VIRUS_SCAN_FAILED)
    queued_ids = []
    messages = []
    data_file_admin = DataFileAdmin(DataFile, AdminSite())
    request = RequestFactory().post("/admin/data_files/datafile/")
    request.user = admin_user
    monkeypatch.setattr(legacy_file.file.storage, "exists", lambda name: True)
    monkeypatch.setattr(data_file_admin_module.reparse_files, "delay", queued_ids.extend)
    monkeypatch.setattr(
        data_file_admin,
        "message_user",
        lambda request, message, level=None: messages.append((message, level)),
    )

    data_file_admin.reparse(
        request,
        DataFile.objects.filter(
            id__in=[legacy_file.id, ready_file.id, unsafe_file.id]
        ).order_by("id"),
    )

    legacy_file.refresh_from_db()
    assert legacy_file.state == SubmissionState.VIRUS_SCAN_COMPLETED
    assert queued_ids == [legacy_file.id, ready_file.id]
    assert any("2 files successfully submitted" in message for message, _ in messages)
    assert any("1 legacy uploaded file" in message for message, _ in messages)
    assert any(
        f"Skipped 1 file(s): {unsafe_file.id}" in message for message, _ in messages
    )


@pytest.mark.django_db
def test_DataFileAdmin_reparse_skips_uploaded_files_without_storage(
    monkeypatch,
    admin_user,
):
    """Test admin reparse skips legacy uploaded files without stored content."""
    legacy_file = DataFileFactory(state=SubmissionState.UPLOADED)
    queued_ids = []
    messages = []
    data_file_admin = DataFileAdmin(DataFile, AdminSite())
    request = RequestFactory().post("/admin/data_files/datafile/")
    request.user = admin_user
    legacy_file.file = ""
    legacy_file.save(update_fields=["file"])
    monkeypatch.setattr(data_file_admin_module.reparse_files, "delay", queued_ids.extend)
    monkeypatch.setattr(
        data_file_admin,
        "message_user",
        lambda request, message, level=None: messages.append((message, level)),
    )

    data_file_admin.reparse(request, DataFile.objects.filter(id=legacy_file.id))

    legacy_file.refresh_from_db()
    assert legacy_file.state == SubmissionState.UPLOADED
    assert queued_ids == []
    assert any("No selected files were eligible" in message for message, _ in messages)
    assert any("no stored file is attached" in message for message, _ in messages)


@pytest.mark.django_db
def test_SubmissionDateFilter(client):
    """Test SubmissionDateFilter method."""
    client.login(username="admin", password="password")
    # create fake queryset
    fake_query = DataFile.objects.all()
    data_file_admin = DataFileAdmin(DataFile, AdminSite())
    filter = DataFileAdmin.SubmissionDateFilter(
        None, {"Submission Day/Month/Year": "1"}, DataFile, DataFileAdmin
    )
    assert data_file_admin.SubmissionDateFilter.title == "submission date"
    assert (
        data_file_admin.SubmissionDateFilter.parameter_name
        == "Submission Day/Month/Year"
    )
    assert data_file_admin.SubmissionDateFilter.lookups(filter, None, None) == [
        ("0", "Today"),
        ("1", "Yesterday"),
        ("7", "Past 7 days"),
        ("30", "This month"),
        ("365", "This year"),
    ]
    assert (
        data_file_admin.SubmissionDateFilter.queryset(filter, None, fake_query).exists()
        is False
    )
    df = DataFileFactory()
    df.created_at = datetime.now(tz=timezone.utc) - timedelta(days=1)
    df.save()
    fake_query = DataFile.objects.all()
    assert (
        data_file_admin.SubmissionDateFilter.queryset(filter, None, fake_query).exists()
        is True
    )
    df.created_at = datetime.now(tz=timezone.utc) - timedelta(days=2)
    df.save()
    fake_query = DataFile.objects.all()
    assert (
        data_file_admin.SubmissionDateFilter.queryset(filter, None, fake_query).exists()
        is False
    )

    filter = DataFileAdmin.SubmissionDateFilter(
        None, {"Submission Day/Month/Year": "0"}, DataFile, DataFileAdmin
    )
    df.created_at = datetime.now(tz=timezone.utc) - timedelta(days=1)
    df.save()
    fake_query = DataFile.objects.all()
    assert (
        data_file_admin.SubmissionDateFilter.queryset(filter, None, fake_query).exists()
        is False
    )

    df.created_at = datetime.now(tz=timezone.utc)
    df.save()
    fake_query = DataFile.objects.all()
    assert (
        data_file_admin.SubmissionDateFilter.queryset(filter, None, fake_query).exists()
        is True
    )
