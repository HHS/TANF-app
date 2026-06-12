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
def test_DataFileAdmin_reparse_requests_reparse_for_safe_files(
    monkeypatch,
    admin_user,
):
    """Test admin reparse moves safe files to reparse_requested before queueing."""
    ready_file = DataFileFactory(state=SubmissionState.PARSE_COMPLETED)
    uploaded_file = DataFileFactory(state=SubmissionState.UPLOADED)
    unsafe_file = DataFileFactory(state=SubmissionState.VIRUS_SCAN_FAILED)
    queued_calls = []
    messages = []
    data_file_admin = DataFileAdmin(DataFile, AdminSite())
    request = RequestFactory().post("/admin/data_files/datafile/")
    request.user = admin_user
    monkeypatch.setattr(
        data_file_admin_module.reparse_files,
        "delay",
        lambda *args, **kwargs: queued_calls.append((args, kwargs)),
    )
    monkeypatch.setattr(
        data_file_admin,
        "message_user",
        lambda request, message, level=None: messages.append((message, level)),
    )

    data_file_admin.reparse(
        request,
        DataFile.objects.filter(
            id__in=[ready_file.id, uploaded_file.id, unsafe_file.id]
        ).order_by("id"),
    )

    ready_file.refresh_from_db()
    uploaded_file.refresh_from_db()
    unsafe_file.refresh_from_db()
    assert ready_file.state == SubmissionState.REPARSE_REQUESTED
    assert uploaded_file.state == SubmissionState.UPLOADED
    assert unsafe_file.state == SubmissionState.VIRUS_SCAN_FAILED
    assert len(queued_calls) == 1
    queued_args, _ = queued_calls[0]
    assert queued_args[0] == [ready_file.id]
    # Worker also receives the pre-transition state so it can revert on failure.
    assert queued_args[1] == {ready_file.id: str(SubmissionState.PARSE_COMPLETED)}
    assert any("1 file successfully submitted" in message for message, _ in messages)
    assert any(
        "3 file(s) selected. 2 file(s) could not be moved" in message
        for message, _ in messages
    )
    assert any("1 file was moved to reparse requested" in message for message, _ in messages)
    assert any(
        f"Skipped 2 file(s): {uploaded_file.id}" in message for message, _ in messages
    )


@pytest.mark.django_db
def test_DataFileAdmin_reparse_skips_when_no_files_can_request_reparse(
    monkeypatch,
    admin_user,
):
    """Test admin reparse reports selected files that cannot move to reparse."""
    uploaded_file = DataFileFactory(state=SubmissionState.UPLOADED)
    queued_calls = []
    messages = []
    data_file_admin = DataFileAdmin(DataFile, AdminSite())
    request = RequestFactory().post("/admin/data_files/datafile/")
    request.user = admin_user
    monkeypatch.setattr(
        data_file_admin_module.reparse_files,
        "delay",
        lambda *args, **kwargs: queued_calls.append((args, kwargs)),
    )
    monkeypatch.setattr(
        data_file_admin,
        "message_user",
        lambda request, message, level=None: messages.append((message, level)),
    )

    data_file_admin.reparse(request, DataFile.objects.filter(id=uploaded_file.id))

    uploaded_file.refresh_from_db()
    assert uploaded_file.state == SubmissionState.UPLOADED
    assert queued_calls == []
    assert any("No selected files were eligible" in message for message, _ in messages)
    assert any(
        "1 file(s) selected. 1 file(s) could not be moved" in message
        for message, _ in messages
    )
    assert any("state uploaded" in message for message, _ in messages)


@pytest.mark.django_db(transaction=True)
def test_DataFileAdmin_reparse_rolls_back_state_when_queue_fails(
    monkeypatch,
    admin_user,
):
    """If reparse_files.delay raises, state must be reverted to its original value.

    The enqueue is deferred until after the state-transition transaction
    commits (so a Celery worker can never race with an uncommitted row).
    A post-commit broker failure therefore requires a manual revert rather
    than a DB rollback; the end state must still be the pre-reparse value.
    """
    ready_file = DataFileFactory(state=SubmissionState.PARSE_COMPLETED)
    messages = []
    data_file_admin = DataFileAdmin(DataFile, AdminSite())
    request = RequestFactory().post("/admin/data_files/datafile/")
    request.user = admin_user

    def broken_delay(*_args, **_kwargs):
        raise RuntimeError("broker unreachable")

    monkeypatch.setattr(data_file_admin_module.reparse_files, "delay", broken_delay)
    monkeypatch.setattr(
        data_file_admin,
        "message_user",
        lambda request, message, level=None: messages.append((message, level)),
    )

    data_file_admin.reparse(
        request,
        DataFile.objects.filter(id=ready_file.id),
    )

    ready_file.refresh_from_db()
    assert ready_file.state == SubmissionState.PARSE_COMPLETED
    assert any("Could not queue the reparse task" in message for message, _ in messages)
    assert not any(
        "file successfully submitted for reparsing" in message
        for message, _ in messages
    )


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
