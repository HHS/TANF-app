"""Test DataFileAdmin methods."""
from datetime import datetime, timedelta, timezone

from django.contrib.admin.sites import AdminSite
from django.db import connection
from django.test import RequestFactory
from django.test.utils import CaptureQueriesContext

import pytest

from tdpservice.data_files.admin import admin as data_file_admin_module
from tdpservice.data_files.admin.admin import (
    DataFileAdmin,
    DataFileStateTransitionInline,
    ShadowDataFileAdmin,
)
from tdpservice.data_files.enums import SubmissionState
from tdpservice.data_files.models import (
    DataFile,
    DataFileStateTransition,
    ShadowDataFile,
    create_or_update_shadow_data_file,
)
from tdpservice.data_files.parser_error_choices import ParserErrorCategoryChoices
from tdpservice.data_files.test.factories import DataFileFactory
from tdpservice.parsers.models import DataFileSummary, ParserError
from tdpservice.parsers.test.factories import DataFileSummaryFactory


@pytest.mark.django_db
def test_DataFileAdmin_status():
    """Test DataFileAdmin status method."""
    data_file = DataFileFactory()
    data_file_summary = DataFileSummaryFactory(datafile=data_file)
    data_file_admin = DataFileAdmin(DataFile, AdminSite())

    assert data_file_admin.status(data_file) == data_file_summary.status
    assert data_file_admin.case_totals(data_file) == data_file_summary.case_aggregates


def test_DataFileAdmin_exposes_canonical_classification_in_admin():
    """Test DataFileAdmin surfaces state and canonical classification details."""
    data_file_admin = DataFileAdmin(DataFile, AdminSite())
    properties_fieldset = next(
        fieldset
        for fieldset in data_file_admin.fieldsets
        if fieldset[0] == "Properties"
    )

    assert "parsing_state" in data_file_admin.list_display
    assert "parsing_state" in properties_fieldset[1]["fields"]
    assert "section" in properties_fieldset[1]["fields"]
    assert "program" in properties_fieldset[1]["fields"]
    assert "program_type" not in properties_fieldset[1]["fields"]
    assert "section_ref" not in properties_fieldset[1]["fields"]
    assert data_file_admin.inlines[0] is DataFileStateTransitionInline


@pytest.mark.parametrize("model", [DataFile, ShadowDataFile])
def test_DataFileStateTransitionInline_is_read_only(model):
    """State transition history should be visible but not editable in admin."""
    inline = DataFileStateTransitionInline(model, AdminSite())

    assert inline.ordering == ["-created_at", "-id"]
    assert inline.has_view_permission(None) is True
    assert inline.has_add_permission(None) is False
    assert inline.has_change_permission(None) is False
    assert inline.has_delete_permission(None) is False


@pytest.mark.django_db
@pytest.mark.parametrize("shadow", [False, True])
def test_state_transition_inline_separates_production_and_shadow(admin_user, shadow):
    """Identical file IDs must show only the history for the selected model."""
    data_file = DataFileFactory()
    shadow_file = create_or_update_shadow_data_file(data_file)
    transitions = [
        DataFileStateTransition.objects.create_for_object(
            obj,
            previous_state=SubmissionState.PARSE_STARTED,
            next_state=SubmissionState.PARSE_COMPLETED,
        )
        for obj in (data_file, shadow_file)
    ]
    obj = shadow_file if shadow else data_file
    admin_class = ShadowDataFileAdmin if shadow else DataFileAdmin
    model_admin = admin_class(type(obj), AdminSite())
    request = RequestFactory().get("/admin/")
    request.user = admin_user

    inline = next(
        item
        for item in model_admin.get_inline_instances(request, obj)
        if isinstance(item, DataFileStateTransitionInline)
    )
    formset = inline.get_formset(request, obj)(instance=obj)

    assert list(formset.get_queryset()) == [transitions[int(shadow)]]


@pytest.mark.django_db
def test_DataFileAdmin_parsing_state_uses_choice_label():
    """Test DataFileAdmin displays friendly submission state labels."""
    data_file = DataFileFactory(state=SubmissionState.PARSE_FAILED)
    data_file_admin = DataFileAdmin(DataFile, AdminSite())

    assert data_file_admin.parsing_state(data_file) == "Parse failed"


@pytest.mark.django_db
def test_DataFileAdmin_changelist_summary_is_eager_loaded(
    admin_user,
):
    """The data file admin should not query per row for summary links."""
    for _ in range(3):
        data_file = DataFileFactory()
        DataFileSummaryFactory(
            datafile=data_file,
            status=DataFileSummary.Status.ACCEPTED,
        )
        ParserError.objects.create(
            file=data_file,
            error_type=ParserErrorCategoryChoices.PRE_CHECK,
        )

    request = RequestFactory().get("/admin/data_files/datafile/")
    request.user = admin_user
    data_file_admin = DataFileAdmin(DataFile, AdminSite())

    data_files = list(data_file_admin.get_queryset(request))

    with CaptureQueriesContext(connection) as captured_queries:
        for data_file in data_files:
            str(data_file.stt)
            data_file_admin.program(data_file)
            data_file_admin.status(data_file)
            data_file_admin.case_totals(data_file)
            data_file_admin.data_file_summary(data_file)

    assert len(captured_queries) == 0


@pytest.mark.django_db
@pytest.mark.parametrize("all_versions", [False, True])
def test_DataFileAdmin_changelist_does_not_query_parser_errors(
    admin_user, all_versions: bool
) -> None:
    """Pagination and latest-version selection must not scan parser errors."""
    old_file = DataFileFactory(version=1)
    latest_file = DataFileFactory(stt=old_file.stt, version=2)
    for data_file in (old_file, latest_file):
        DataFileSummaryFactory(datafile=data_file)
        ParserError.objects.create(
            file=data_file,
            error_type=ParserErrorCategoryChoices.PRE_CHECK,
        )

    params = {"created_at": "1"} if all_versions else {}
    request = RequestFactory().get("/admin/data_files/datafile/", params)
    request.user = admin_user
    model_admin = DataFileAdmin(DataFile, AdminSite())

    with CaptureQueriesContext(connection) as queries:
        changelist = model_admin.get_changelist_instance(request)
        result_ids = {data_file.pk for data_file in changelist.result_list}

    expected_ids = {old_file.pk, latest_file.pk} if all_versions else {latest_file.pk}
    assert result_ids == expected_ids
    assert changelist.result_count == len(expected_ids)
    assert changelist.full_result_count == 2
    assert "error_report_link" not in changelist.list_display
    assert queries.captured_queries
    assert all(
        ParserError._meta.db_table not in query["sql"]
        for query in queries.captured_queries
    )


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
    transition = DataFileStateTransition.objects.for_object(ready_file).get()
    assert transition.previous_state == SubmissionState.PARSE_COMPLETED
    assert transition.next_state == SubmissionState.REPARSE_REQUESTED
    assert str(transition.actor_id) == str(admin_user.id)
    assert transition.source == "django_admin"


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
    transitions = list(DataFileStateTransition.objects.for_object(ready_file))
    assert [transition.next_state for transition in transitions] == [
        SubmissionState.PARSE_COMPLETED,
        SubmissionState.REPARSE_REQUESTED,
    ]
    assert all(
        str(transition.actor_id) == str(admin_user.id) for transition in transitions
    )
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
