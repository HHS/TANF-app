"""Integration coverage for exclusive submission-state ownership."""

import re
from datetime import timedelta
from pathlib import Path

from django.utils import timezone

import pytest

from tdpservice.data_files.enums import SubmissionState
from tdpservice.data_files.models import DataFileStateTransition, ReparseFileMeta
from tdpservice.data_files.submission_lifecycle import (
    StaleParseOwnership,
    begin_parse,
    complete_datafile_av_scan,
    claim_parse,
    finish_reparse,
    mark_stuck,
    parse_write_scope,
    prepare_datafile_for_reparse,
    record_parse_outcome,
    start_datafile_av_scan,
)
from tdpservice.data_files.tasks import (
    get_stale_lifecycle_files,
    mark_stale_files_stuck,
)
from tdpservice.data_files.test.factories import DataFileFactory
from tdpservice.etl.pipelines.sources import active_reparse_datafile_ids
from tdpservice.parsers.models import DataFileSummary
from tdpservice.search_indexes.models.reparse_meta import ReparseMeta


@pytest.mark.django_db
def test_timeout_stuck_reparse_flow_has_one_current_writer():
    """Exercise upload through timeout and a successful, fenced reparse."""
    data_file = DataFileFactory(state=SubmissionState.UPLOADED)

    start_datafile_av_scan(data_file)
    complete_datafile_av_scan(data_file, "clean")
    stale_token = claim_parse(data_file)
    begin_parse(data_file, stale_token)
    stale_started_at = timezone.now() - timedelta(days=1, minutes=1)
    type(data_file).objects.filter(pk=data_file.pk).update(
        state_changed_at=stale_started_at
    )

    assert list(get_stale_lifecycle_files()) == [data_file]
    assert mark_stale_files_stuck() == 1

    data_file.refresh_from_db()
    assert data_file.state == SubmissionState.STUCK
    assert data_file.current_parse_token is None
    with pytest.raises(StaleParseOwnership, match="may no longer write"):
        with parse_write_scope(data_file.id, stale_token):
            pytest.fail("A timed-out parser regained write ownership.")

    prepare_datafile_for_reparse(data_file)
    reparse = ReparseMeta.objects.create(db_backup_location="s3://test/reparse.sql")
    reparse_file = ReparseFileMeta.objects.create(
        data_file=data_file,
        reparse_meta=reparse,
    )
    assert active_reparse_datafile_ids() == [data_file.id]

    current_token = claim_parse(data_file, reparse_file_meta=reparse_file)
    begin_parse(data_file, current_token, reparse_file)
    with parse_write_scope(data_file.id, current_token):
        DataFileSummary.objects.create(
            datafile=data_file,
            status=DataFileSummary.Status.ACCEPTED,
        )
    record_parse_outcome(
        data_file,
        current_token,
        DataFileSummary.Status.ACCEPTED,
    )
    assert finish_reparse(
        data_file,
        reparse_file,
        success=True,
        num_records_created=10,
        cat_4_errors_generated=0,
    )

    data_file.refresh_from_db()
    reparse_file.refresh_from_db()
    assert data_file.state == SubmissionState.PARSE_COMPLETED
    assert data_file.current_parse_token is None
    assert reparse_file.finished is True
    assert reparse_file.success is True
    assert active_reparse_datafile_ids() == []
    transitions = list(DataFileStateTransition.objects.for_object(data_file).order_by("id"))
    assert [transition.next_state for transition in transitions] == [
        SubmissionState.VIRUS_SCAN_STARTED,
        SubmissionState.VIRUS_SCAN_COMPLETED,
        SubmissionState.PARSE_STARTED,
        SubmissionState.STUCK,
        SubmissionState.REPARSE_REQUESTED,
        SubmissionState.PARSE_STARTED,
        SubmissionState.PARSE_COMPLETED,
    ]
    assert transitions[3].metadata["revoked_parse_token"] == str(stale_token)
    assert transitions[-1].metadata["parse_token"] == str(current_token)


@pytest.mark.django_db
def test_parse_completion_wins_timeout_selection_race():
    """Do not mark a file STUCK if its parser finishes before row locking."""
    data_file = DataFileFactory(state=SubmissionState.VIRUS_SCAN_COMPLETED)
    parse_token = claim_parse(data_file)
    begin_parse(data_file, parse_token)
    type(data_file).objects.filter(pk=data_file.pk).update(
        state_changed_at=timezone.now() - timedelta(days=1, minutes=1)
    )

    selected_as_stale = get_stale_lifecycle_files().get(pk=data_file.pk)
    record_parse_outcome(
        data_file,
        parse_token,
        DataFileSummary.Status.ACCEPTED,
    )
    _, changed = mark_stuck(selected_as_stale)

    data_file.refresh_from_db()
    assert changed is False
    assert data_file.state == SubmissionState.PARSE_COMPLETED
    assert data_file.current_parse_token is None


def test_production_python_state_writes_are_owned_by_controller():
    """Prevent production code from adding a second DataFile state writer."""
    service_root = Path(__file__).resolve().parents[2]
    controller = service_root / "data_files" / "submission_lifecycle.py"
    assignment = re.compile(
        r"\.state\s*=\s*(?:SubmissionState\.|transition\.|target_state|locked\.state)"
    )
    queryset_update = re.compile(r"\.update\([^)]*\bstate\s*=", re.DOTALL)
    violations = []

    for source_file in service_root.rglob("*.py"):
        if source_file == controller or any(
            part in {"migrations", "test", "tests"} for part in source_file.parts
        ):
            continue
        source = source_file.read_text(encoding="utf-8")
        if assignment.search(source) or queryset_update.search(source):
            violations.append(str(source_file.relative_to(service_root)))

    assert violations == [], (
        "Production DataFile state changes must be expressed as an intent in "
        f"data_files/submission_lifecycle.py; found writers in {violations}."
    )
