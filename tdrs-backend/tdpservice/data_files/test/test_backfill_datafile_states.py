"""Behavior of the administrative legacy-state repair and its dry-run entry point."""

import uuid

from django.core.management import call_command

import pytest

from tdpservice.data_files import submission_lifecycle
from tdpservice.data_files.enums import SubmissionState
from tdpservice.data_files.models import DataFileStateTransition
from tdpservice.data_files.submission_lifecycle import backfill_legacy_datafile_state
from tdpservice.data_files.test.factories import DataFileFactory
from tdpservice.parsers.models import DataFileSummary

pytestmark = pytest.mark.django_db


@pytest.mark.parametrize(
    "status, expected",
    [
        (DataFileSummary.Status.ACCEPTED, SubmissionState.PARSE_COMPLETED),
        (DataFileSummary.Status.ACCEPTED_WITH_ERRORS, SubmissionState.PARSED_WITH_ERRORS),
        (DataFileSummary.Status.PARTIALLY_ACCEPTED, SubmissionState.PARSED_WITH_ERRORS),
        (DataFileSummary.Status.REJECTED, SubmissionState.PARSE_FAILED),
    ],
)
def test_backfill_records_one_inferred_repair(status, expected, caplog):
    """Existing summaries determine an audited repair, without fictional events."""
    data_file = DataFileFactory()
    summary = DataFileSummary.objects.create(datafile=data_file, status=status)

    target, reason = backfill_legacy_datafile_state(data_file, apply=True)

    data_file.refresh_from_db()
    summary.refresh_from_db()
    transition = DataFileStateTransition.objects.for_object(data_file).get()
    assert target == data_file.state == expected
    assert summary.status == status
    assert transition.previous_state == SubmissionState.UPLOADED
    assert transition.next_state == expected
    assert transition.note == f"Legacy state backfill: {reason}"
    assert transition.source == "legacy_state_backfill"
    assert transition.metadata["inferred"] is True
    assert transition.metadata["recovery"] == "legacy_state_backfill"
    assert transition.metadata["section"] == data_file.section.name
    assert transition.metadata["program_type"] == data_file.program.code
    assert transition.metadata["event_id"] == str(transition.event_id)
    log = next(r for r in caplog.records if r.message == "DataFile submission state transition")
    assert log.event_id == str(transition.event_id)
    assert backfill_legacy_datafile_state(data_file, apply=True)[0] is None
    assert DataFileStateTransition.objects.for_object(data_file).count() == 1


def test_backfill_script_defaults_to_dry_run(capsys):
    """The documented entry point loads and previews without changing state/history."""
    data_file = DataFileFactory()
    DataFileSummary.objects.create(datafile=data_file, status=DataFileSummary.Status.ACCEPTED)
    previous_timestamp = data_file.state_changed_at

    call_command("runscript", "backfill_datafile_states")

    data_file.refresh_from_db()
    assert data_file.state == SubmissionState.UPLOADED
    assert data_file.state_changed_at == previous_timestamp
    assert not DataFileStateTransition.objects.for_object(data_file).exists()
    output = capsys.readouterr().out
    assert f"WOULD UPDATE {data_file.id}:" in output
    assert "'would_update': 1, 'updated': 0, 'skipped': 0" in output


def test_backfill_script_explicit_apply(capsys):
    """An explicit apply argument uses the same controller and creates history."""
    data_file = DataFileFactory()
    DataFileSummary.objects.create(datafile=data_file, status=DataFileSummary.Status.ACCEPTED)

    call_command("runscript", "backfill_datafile_states", script_args=["apply=true"])

    data_file.refresh_from_db()
    assert data_file.state == SubmissionState.PARSE_COMPLETED
    assert DataFileStateTransition.objects.for_object(data_file).count() == 1
    assert "'would_update': 0, 'updated': 1, 'skipped': 0" in capsys.readouterr().out


@pytest.mark.parametrize("status", [DataFileSummary.Status.PENDING, "Unknown"])
def test_backfill_skips_unresolved_summary(status):
    """Pending or unrecognized summaries must not be treated as finished work."""
    data_file = DataFileFactory()
    DataFileSummary.objects.create(datafile=data_file, status=status)

    assert backfill_legacy_datafile_state(data_file, apply=True)[0] is None

    data_file.refresh_from_db()
    assert data_file.state == SubmissionState.UPLOADED
    assert not DataFileStateTransition.objects.for_object(data_file).exists()


@pytest.mark.parametrize("stored_file_exists", [False, True])
def test_backfill_without_summary_requires_existing_storage(monkeypatch, stored_file_exists):
    """A missing storage object cannot be used as evidence of a completed scan."""
    data_file = DataFileFactory()
    monkeypatch.setattr(data_file.file.storage, "exists", lambda _name: stored_file_exists)

    target, _ = backfill_legacy_datafile_state(data_file, apply=True)

    data_file.refresh_from_db()
    assert target == (SubmissionState.VIRUS_SCAN_COMPLETED if stored_file_exists else None)
    assert data_file.state == (SubmissionState.VIRUS_SCAN_COMPLETED if stored_file_exists else SubmissionState.UPLOADED)
    assert DataFileStateTransition.objects.for_object(data_file).count() == int(stored_file_exists)


def test_backfill_skips_row_without_evidence():
    """Rows without a summary or stored file stay uploaded."""
    data_file = DataFileFactory(file=None)
    assert backfill_legacy_datafile_state(data_file, apply=True)[0] is None
    assert not DataFileStateTransition.objects.for_object(data_file).exists()


@pytest.mark.parametrize(
    "changes",
    [
        {"state": SubmissionState.PARSE_STARTED},
        {"current_parse_token": uuid.UUID("11111111-1111-1111-1111-111111111111")},
    ],
)
def test_backfill_rechecks_state_and_ownership_under_lock(changes):
    """A stale candidate cannot overwrite an advanced state or parser claim."""
    data_file = DataFileFactory()
    DataFileSummary.objects.create(datafile=data_file, status=DataFileSummary.Status.ACCEPTED)
    type(data_file).objects.filter(pk=data_file.pk).update(**changes)

    assert backfill_legacy_datafile_state(data_file, apply=True)[0] is None

    data_file.refresh_from_db()
    for key, value in changes.items():
        assert getattr(data_file, key) == value
    assert not DataFileStateTransition.objects.for_object(data_file).exists()


def test_backfill_rolls_back_when_audit_persistence_fails(monkeypatch):
    """Repair state and history must succeed or fail together."""
    data_file = DataFileFactory()
    DataFileSummary.objects.create(datafile=data_file, status=DataFileSummary.Status.ACCEPTED)
    previous_timestamp = data_file.state_changed_at

    def fail_audit(*_args, **_kwargs):
        raise RuntimeError("audit unavailable")

    monkeypatch.setattr(submission_lifecycle, "persist_datafile_state_transition", fail_audit)
    with pytest.raises(RuntimeError, match="audit unavailable"):
        backfill_legacy_datafile_state(data_file, apply=True)

    data_file.refresh_from_db()
    assert data_file.state == SubmissionState.UPLOADED
    assert data_file.state_changed_at == previous_timestamp
    assert not DataFileStateTransition.objects.for_object(data_file).exists()
