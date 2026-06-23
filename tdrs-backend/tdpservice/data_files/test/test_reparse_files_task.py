"""Test reparse_files celery task error handling."""

import pytest

from tdpservice.data_files import tasks as data_file_tasks
from tdpservice.data_files.enums import SubmissionState
from tdpservice.data_files.test.factories import DataFileFactory
from tdpservice.search_indexes.reparse import ReparseDestructiveCleanupStarted


@pytest.mark.django_db
def test_reparse_files_reverts_state_when_clean_reparse_fails(monkeypatch):
    """If clean_reparse raises, files revert from REPARSE_REQUESTED to original."""
    file_a = DataFileFactory(state=SubmissionState.REPARSE_REQUESTED)
    file_b = DataFileFactory(state=SubmissionState.REPARSE_REQUESTED)

    def broken_clean_reparse(_args):
        raise RuntimeError("assert_sequential_execution failed")

    monkeypatch.setattr(data_file_tasks, "clean_reparse", broken_clean_reparse)

    original_states = {
        file_a.id: SubmissionState.PARSE_COMPLETED.value,
        file_b.id: SubmissionState.PARSED_WITH_ERRORS.value,
    }

    with pytest.raises(RuntimeError):
        data_file_tasks.reparse_files([file_a.id, file_b.id], original_states)

    file_a.refresh_from_db()
    file_b.refresh_from_db()
    assert file_a.state == SubmissionState.PARSE_COMPLETED
    assert file_b.state == SubmissionState.PARSED_WITH_ERRORS


@pytest.mark.django_db
def test_reparse_files_revert_handles_celery_string_keys(monkeypatch):
    """Celery JSON serialization turns int keys to strings; revert must still work."""
    data_file = DataFileFactory(state=SubmissionState.REPARSE_REQUESTED)

    def broken_clean_reparse(_args):
        raise RuntimeError("backup failed")

    monkeypatch.setattr(data_file_tasks, "clean_reparse", broken_clean_reparse)

    # Simulate the dict as it arrives from Celery's JSON-serialized payload.
    original_states = {str(data_file.id): SubmissionState.PARSE_FAILED.value}

    with pytest.raises(RuntimeError):
        data_file_tasks.reparse_files([data_file.id], original_states)

    data_file.refresh_from_db()
    assert data_file.state == SubmissionState.PARSE_FAILED


@pytest.mark.django_db
def test_reparse_files_skips_revert_when_file_moved_on(monkeypatch):
    """If a file has already left REPARSE_REQUESTED, leave it alone."""
    data_file = DataFileFactory(state=SubmissionState.PARSE_STARTED)

    def broken_clean_reparse(_args):
        raise RuntimeError("late failure")

    monkeypatch.setattr(data_file_tasks, "clean_reparse", broken_clean_reparse)

    with pytest.raises(RuntimeError):
        data_file_tasks.reparse_files(
            [data_file.id],
            {data_file.id: SubmissionState.PARSE_COMPLETED.value},
        )

    data_file.refresh_from_db()
    # State must not be clobbered backwards from PARSE_STARTED.
    assert data_file.state == SubmissionState.PARSE_STARTED


@pytest.mark.django_db
def test_reparse_files_success_does_not_revert(monkeypatch):
    """On success, no revert path runs and DB state is left to clean_reparse."""
    data_file = DataFileFactory(state=SubmissionState.REPARSE_REQUESTED)
    called = []

    def ok_clean_reparse(args):
        called.append(args)

    monkeypatch.setattr(data_file_tasks, "clean_reparse", ok_clean_reparse)

    data_file_tasks.reparse_files(
        [data_file.id],
        {data_file.id: SubmissionState.PARSE_COMPLETED.value},
    )

    data_file.refresh_from_db()
    assert data_file.state == SubmissionState.REPARSE_REQUESTED
    assert called == [[str(data_file.id)]]


@pytest.mark.django_db
def test_reparse_files_does_not_revert_after_destructive_cleanup(monkeypatch):
    """Destructive-cleanup failures must NOT trigger a state revert.

    Reverting after destructive cleanup would lie about the data: the file
    would look like its prior parsed state but its summary/errors are gone.
    The task must leave state at REPARSE_REQUESTED and re-raise so the
    inconsistent-DB recovery path (restore from backup) applies.
    """
    data_file = DataFileFactory(state=SubmissionState.REPARSE_REQUESTED)

    def destructive_failure(_args):
        raise ReparseDestructiveCleanupStarted(RuntimeError("DB now inconsistent"))

    monkeypatch.setattr(data_file_tasks, "clean_reparse", destructive_failure)

    with pytest.raises(ReparseDestructiveCleanupStarted):
        data_file_tasks.reparse_files(
            [data_file.id],
            {data_file.id: SubmissionState.PARSE_COMPLETED.value},
        )

    data_file.refresh_from_db()
    assert data_file.state == SubmissionState.REPARSE_REQUESTED


@pytest.mark.django_db
def test_reparse_files_reverts_state_when_clean_reparse_calls_sys_exit(monkeypatch):
    """count_total_num_records cancels via exit(1); revert must still run.

    The pre-destructive helper ``count_total_num_records`` in
    ``search_indexes.utils`` raises ``SystemExit`` (via ``exit(1)``) rather
    than a normal exception. A plain ``except Exception`` would let that
    escape unhandled and strand the file in REPARSE_REQUESTED.
    """
    data_file = DataFileFactory(state=SubmissionState.REPARSE_REQUESTED)

    def sys_exit_clean_reparse(_args):
        # Mirrors the behavior of count_total_num_records on DB error.
        exit(1)

    monkeypatch.setattr(data_file_tasks, "clean_reparse", sys_exit_clean_reparse)

    with pytest.raises(SystemExit):
        data_file_tasks.reparse_files(
            [data_file.id],
            {data_file.id: SubmissionState.PARSE_COMPLETED.value},
        )

    data_file.refresh_from_db()
    assert data_file.state == SubmissionState.PARSE_COMPLETED
