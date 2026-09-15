"""Tests for submission lifecycle helpers."""

import uuid

import pytest

from tdpservice.core.models import BaseLog
from tdpservice.data_files import submission_lifecycle
from tdpservice.data_files.enums import SubmissionState
from tdpservice.data_files.models import (
    DataFileStateTransition,
    create_or_update_shadow_data_file,
)
from tdpservice.data_files.submission_lifecycle import (
    InvalidScanResult,
    InvalidTransition,
    ReparsePreparationError,
    allowed_next_states,
    complete_datafile_av_scan,
    force_transition_datafile,
    prepare_datafile_for_reparse,
    revert_reparse_request,
    transition_datafile,
    validate_transition,
)
from tdpservice.data_files.test.factories import DataFileFactory
from tdpservice.etl.models import ETLPipelineRun
from tdpservice.etl.pipelines.sources import SOURCE_DATAFILE_IDS_KEY


def _active_pipeline_run_for_datafile(data_file):
    """Create an active ETL run that has snapshotted the DataFile."""
    return ETLPipelineRun.objects.create(
        pipeline_key="test_pipeline",
        pipeline_version="1",
        status=ETLPipelineRun.Status.RUNNING,
        parameters={},
        output_scope={"pipeline": "test_pipeline", "test_id": data_file.id},
        output_scope_key=f"test-{data_file.id}",
        metadata={SOURCE_DATAFILE_IDS_KEY: {"test": [data_file.id]}},
        trigger_source=ETLPipelineRun.TriggerSource.ADMIN,
    )


def _state_transitions_for(data_file):
    """Return state transition logs attached to a DataFile."""
    return DataFileStateTransition.objects.for_object(data_file)


def test_valid_transitions_succeed():
    """Test allowed state transitions validate successfully."""
    first = validate_transition(
        SubmissionState.UPLOADED, SubmissionState.VIRUS_SCAN_STARTED
    )
    second = validate_transition(
        SubmissionState.VIRUS_SCAN_STARTED, SubmissionState.VIRUS_SCAN_COMPLETED
    )

    assert first.previous_state == SubmissionState.UPLOADED
    assert first.next_state == SubmissionState.VIRUS_SCAN_STARTED
    assert second.previous_state == SubmissionState.VIRUS_SCAN_STARTED
    assert second.next_state == SubmissionState.VIRUS_SCAN_COMPLETED
    assert allowed_next_states(SubmissionState.UPLOADED) == {
        SubmissionState.VIRUS_SCAN_STARTED,
        SubmissionState.CANCELED,
    }


def test_invalid_transition_raises():
    """Test invalid transitions raise InvalidTransition."""
    with pytest.raises(InvalidTransition, match="uploaded to parse_completed"):
        validate_transition(SubmissionState.UPLOADED, SubmissionState.PARSE_COMPLETED)


@pytest.mark.parametrize(
    "state",
    [
        SubmissionState.COMPLETED,
        SubmissionState.CANCELED,
    ],
)
def test_terminal_states_cannot_transition(state):
    """Test terminal states reject further transitions."""
    with pytest.raises(InvalidTransition, match=f"{state.value} to uploaded"):
        validate_transition(state, SubmissionState.UPLOADED)


@pytest.mark.django_db
def test_transition_datafile_updates_state():
    """Test transition_datafile persists the expected state."""
    data_file = DataFileFactory(state=SubmissionState.UPLOADED)

    transition_datafile(
        data_file,
        SubmissionState.VIRUS_SCAN_STARTED,
        note="Picked up by AV scan worker",
    )
    data_file.refresh_from_db()

    assert data_file.state == SubmissionState.VIRUS_SCAN_STARTED


@pytest.mark.django_db
def test_transition_datafile_creates_state_transition_record():
    """Test transition_datafile persists audit context for state changes."""
    data_file = DataFileFactory(state=SubmissionState.UPLOADED)
    event_id = uuid.uuid4()

    transition_datafile(
        data_file,
        SubmissionState.VIRUS_SCAN_STARTED,
        note="Picked up by AV scan worker",
        actor=data_file.user,
        source="api",
        event_id=event_id,
        log_fields={"scan_result": "QUEUED", "custom": {"step": 1}},
    )

    transition = _state_transitions_for(data_file).get()
    base_log = BaseLog.objects.get(pk=transition.pk)
    assert transition.previous_state == SubmissionState.UPLOADED
    assert transition.next_state == SubmissionState.VIRUS_SCAN_STARTED
    assert transition.content_object == data_file
    assert transition.event_id == event_id
    assert transition.event_type == DataFileStateTransition.EVENT_TYPE
    assert transition.note == "Picked up by AV scan worker"
    assert str(transition.actor_id) == str(data_file.user_id)
    assert transition.source == "api"
    assert transition.metadata["scan_result"] == "QUEUED"
    assert transition.metadata["custom"] == {"step": 1}
    assert transition.metadata["previous_state"] == SubmissionState.UPLOADED.value
    assert transition.metadata["next_state"] == SubmissionState.VIRUS_SCAN_STARTED.value
    assert base_log.event_id == event_id
    assert base_log.event_type == DataFileStateTransition.EVENT_TYPE


@pytest.mark.django_db(transaction=True)
@pytest.mark.parametrize("shadow", [False, True])
def test_transition_datafile_state_update_and_transition_record_are_atomic(
    monkeypatch, shadow
):
    """State updates roll back if transition persistence fails."""
    data_file = DataFileFactory(state=SubmissionState.UPLOADED)
    if shadow:
        data_file = create_or_update_shadow_data_file(data_file)

    def broken_persist(*_args, **_kwargs):
        raise RuntimeError("audit insert failed")

    monkeypatch.setattr(
        submission_lifecycle,
        "persist_datafile_state_transition",
        broken_persist,
    )

    with pytest.raises(RuntimeError, match="audit insert failed"):
        transition_datafile(data_file, SubmissionState.VIRUS_SCAN_STARTED)

    data_file.refresh_from_db()
    assert data_file.state == SubmissionState.UPLOADED
    assert _state_transitions_for(data_file).count() == 0


@pytest.mark.django_db
def test_shadow_and_production_transitions_share_event_but_keep_separate_histories():
    """One parser run can correlate both file histories without mixing them."""
    data_file = DataFileFactory(state=SubmissionState.VIRUS_SCAN_COMPLETED)
    shadow_file = create_or_update_shadow_data_file(data_file)
    event_id = uuid.uuid4()
    for obj, source in ((data_file, "python_parser"), (shadow_file, "go_parser")):
        transition_datafile(
            obj, SubmissionState.PARSE_STARTED, source=source, event_id=event_id
        )

    production_transition = _state_transitions_for(data_file).get()
    shadow_transition = _state_transitions_for(shadow_file).get()
    assert production_transition.content_object == data_file
    assert shadow_transition.content_object == shadow_file
    assert production_transition.content_type_id != shadow_transition.content_type_id
    assert production_transition.event_id == shadow_transition.event_id == event_id
    assert BaseLog.objects.filter(event_id=event_id).count() == 2


@pytest.mark.django_db
def test_transition_datafile_uses_locked_database_state_for_previous_state():
    """Transition audits should reflect the locked DB row, not a stale instance."""
    data_file = DataFileFactory(state=SubmissionState.UPLOADED)
    type(data_file).objects.filter(pk=data_file.pk).update(
        state=SubmissionState.VIRUS_SCAN_STARTED
    )

    transition_datafile(data_file, SubmissionState.VIRUS_SCAN_COMPLETED)

    data_file.refresh_from_db()
    transition = _state_transitions_for(data_file).get()
    assert data_file.state == SubmissionState.VIRUS_SCAN_COMPLETED
    assert transition.previous_state == SubmissionState.VIRUS_SCAN_STARTED
    assert transition.next_state == SubmissionState.VIRUS_SCAN_COMPLETED


@pytest.mark.django_db
def test_transition_record_survives_datafile_delete():
    """Audit rows should retain data_file_id after the parent DataFile is deleted."""
    data_file = DataFileFactory(state=SubmissionState.UPLOADED)
    data_file_id = data_file.id

    transition_datafile(data_file, SubmissionState.VIRUS_SCAN_STARTED)
    data_file.delete()

    transition = DataFileStateTransition.objects.get(object_id=str(data_file_id))
    assert transition.previous_state == SubmissionState.UPLOADED
    assert transition.next_state == SubmissionState.VIRUS_SCAN_STARTED
    assert transition.data_file_id == data_file_id
    assert transition.content_object is None


@pytest.mark.django_db
def test_transition_datafile_calls_logger_hook():
    """Test transition_datafile emits structured payloads to a logger hook."""
    data_file = DataFileFactory(state=SubmissionState.PARSE_STARTED)
    payloads = []

    transition_datafile(
        data_file,
        SubmissionState.PARSE_COMPLETED,
        note="Parser completed successfully",
        logger_hook=payloads.append,
    )

    assert payloads == [
        {
            "data_file_id": data_file.id,
            "previous_state": SubmissionState.PARSE_STARTED.value,
            "next_state": SubmissionState.PARSE_COMPLETED.value,
            "note": "Parser completed successfully",
        }
    ]


@pytest.mark.django_db
def test_transition_datafile_integration_persists_sequential_state_changes():
    """Test sequential persisted transitions on a real DataFile instance."""
    data_file = DataFileFactory(state=SubmissionState.UPLOADED)
    payloads = []

    transition_datafile(
        data_file,
        SubmissionState.VIRUS_SCAN_STARTED,
        note="Virus scan worker picked up the file",
        logger_hook=payloads.append,
    )
    data_file.refresh_from_db()

    assert data_file.state == SubmissionState.VIRUS_SCAN_STARTED

    transition_datafile(
        data_file,
        SubmissionState.VIRUS_SCAN_COMPLETED,
        note="Virus scan passed",
        logger_hook=payloads.append,
    )
    data_file.refresh_from_db()

    assert data_file.state == SubmissionState.VIRUS_SCAN_COMPLETED
    assert payloads == [
        {
            "data_file_id": data_file.id,
            "previous_state": SubmissionState.UPLOADED.value,
            "next_state": SubmissionState.VIRUS_SCAN_STARTED.value,
            "note": "Virus scan worker picked up the file",
        },
        {
            "data_file_id": data_file.id,
            "previous_state": SubmissionState.VIRUS_SCAN_STARTED.value,
            "next_state": SubmissionState.VIRUS_SCAN_COMPLETED.value,
            "note": "Virus scan passed",
        },
    ]


@pytest.mark.django_db
def test_transition_datafile_supports_parse_failed_state():
    """Test transition_datafile persists parse failures caused by exceptions."""
    data_file = DataFileFactory(state=SubmissionState.PARSE_STARTED)

    transition_datafile(
        data_file,
        SubmissionState.PARSE_FAILED,
        note="Parser raised an unexpected exception",
    )
    data_file.refresh_from_db()

    assert data_file.state == SubmissionState.PARSE_FAILED
    transition = _state_transitions_for(data_file).get()
    assert transition.previous_state == SubmissionState.PARSE_STARTED
    assert transition.next_state == SubmissionState.PARSE_FAILED
    assert transition.note == "Parser raised an unexpected exception"


@pytest.mark.parametrize(
    "state",
    [
        SubmissionState.PARSE_FAILED,
        SubmissionState.PARSED_WITH_ERRORS,
        SubmissionState.PARSE_COMPLETED,
    ],
)
def test_parse_outcome_states_can_reparse(state):
    """Test parsed files can transition back to parse_started for reparse."""
    transition = validate_transition(state, SubmissionState.PARSE_STARTED)

    assert transition.previous_state == state
    assert transition.next_state == SubmissionState.PARSE_STARTED


def test_reparse_requested_can_transition_to_parse_started():
    """Test requested reparses can transition to parse_started."""
    transition = validate_transition(
        SubmissionState.REPARSE_REQUESTED,
        SubmissionState.PARSE_STARTED,
    )

    assert transition.previous_state == SubmissionState.REPARSE_REQUESTED
    assert transition.next_state == SubmissionState.PARSE_STARTED


@pytest.mark.parametrize(
    "state",
    [
        SubmissionState.VIRUS_SCAN_COMPLETED,
        SubmissionState.PARSE_FAILED,
        SubmissionState.PARSED_WITH_ERRORS,
        SubmissionState.PARSE_COMPLETED,
    ],
)
def test_safe_states_can_request_reparse(state):
    """Test safe states can transition to reparse_requested."""
    transition = validate_transition(state, SubmissionState.REPARSE_REQUESTED)

    assert transition.previous_state == state
    assert transition.next_state == SubmissionState.REPARSE_REQUESTED


@pytest.mark.parametrize(
    "state",
    [
        SubmissionState.VIRUS_SCAN_COMPLETED,
        SubmissionState.PARSE_FAILED,
        SubmissionState.PARSED_WITH_ERRORS,
        SubmissionState.PARSE_COMPLETED,
    ],
)
@pytest.mark.django_db
def test_prepare_datafile_for_reparse_requests_reparse_for_safe_states(state):
    """Test safe states are moved to reparse_requested before queueing."""
    data_file = DataFileFactory(state=state)
    payloads = []

    prepared_file, reparse_requested = prepare_datafile_for_reparse(
        data_file,
        logger_hook=payloads.append,
    )

    assert prepared_file == data_file
    assert reparse_requested is True
    data_file.refresh_from_db()
    assert data_file.state == SubmissionState.REPARSE_REQUESTED
    transition = _state_transitions_for(data_file).get()
    assert transition.previous_state == state
    assert transition.next_state == SubmissionState.REPARSE_REQUESTED
    assert transition.note == "admin reparse requested"
    assert transition.event_id is not None
    assert payloads == [
        {
            "data_file_id": data_file.id,
            "previous_state": state.value,
            "next_state": SubmissionState.REPARSE_REQUESTED.value,
            "note": "admin reparse requested",
            "event_id": str(transition.event_id),
        }
    ]


@pytest.mark.django_db
def test_prepare_datafile_for_reparse_is_idempotent_for_reparse_requested():
    """Test files already marked for reparse are still eligible for queueing."""
    data_file = DataFileFactory(state=SubmissionState.REPARSE_REQUESTED)

    prepared_file, reparse_requested = prepare_datafile_for_reparse(data_file)

    assert prepared_file == data_file
    assert reparse_requested is False
    data_file.refresh_from_db()
    assert data_file.state == SubmissionState.REPARSE_REQUESTED
    assert _state_transitions_for(data_file).count() == 0


@pytest.mark.django_db
def test_revert_reparse_request_creates_state_transition_record():
    """Recovery reverts should persist transition history despite bypassing validation."""
    data_file = DataFileFactory(state=SubmissionState.PARSE_COMPLETED)
    prepare_datafile_for_reparse(data_file)
    reparse_event_id = _state_transitions_for(data_file).get().event_id

    reverted = revert_reparse_request(
        data_file,
        SubmissionState.PARSE_COMPLETED,
        note="broker enqueue failed",
        actor=data_file.user,
        source="django_admin",
    )

    data_file.refresh_from_db()
    transition = _state_transitions_for(data_file).filter(
        next_state=SubmissionState.PARSE_COMPLETED
    ).get()
    assert reverted is True
    assert data_file.state == SubmissionState.PARSE_COMPLETED
    assert transition.previous_state == SubmissionState.REPARSE_REQUESTED
    assert transition.next_state == SubmissionState.PARSE_COMPLETED
    assert transition.note == "broker enqueue failed"
    assert str(transition.actor_id) == str(data_file.user_id)
    assert transition.event_id == reparse_event_id
    assert transition.source == "django_admin"


@pytest.mark.django_db
def test_force_transition_datafile_creates_state_transition_record():
    """Forced recovery transitions should persist audit history."""
    data_file = DataFileFactory(state=SubmissionState.VIRUS_SCAN_COMPLETED)

    force_transition_datafile(
        data_file,
        SubmissionState.PARSE_FAILED,
        note="Go parser post-parse received parse_error",
        source="go_parser",
        task_name="tdpservice.scheduling.parser_task.post_parse",
        reparse_meta_id=7,
        log_fields={"parse_error": "pipeline failed"},
    )

    data_file.refresh_from_db()
    transition = _state_transitions_for(data_file).get()
    assert data_file.state == SubmissionState.PARSE_FAILED
    assert transition.previous_state == SubmissionState.VIRUS_SCAN_COMPLETED
    assert transition.next_state == SubmissionState.PARSE_FAILED
    assert transition.source == "go_parser"
    assert transition.task_name == "tdpservice.scheduling.parser_task.post_parse"
    assert transition.reparse_meta_id == 7
    assert transition.metadata["parse_error"] == "pipeline failed"


@pytest.mark.django_db
def test_force_transition_datafile_uses_locked_database_state_for_previous_state():
    """Forced transitions should audit the locked DB row, not a stale instance."""
    data_file = DataFileFactory(state=SubmissionState.VIRUS_SCAN_COMPLETED)
    type(data_file).objects.filter(pk=data_file.pk).update(
        state=SubmissionState.PARSE_STARTED
    )

    force_transition_datafile(
        data_file,
        SubmissionState.PARSE_FAILED,
        note="forced parser failure",
    )

    transition = _state_transitions_for(data_file).get()
    assert transition.previous_state == SubmissionState.PARSE_STARTED
    assert transition.next_state == SubmissionState.PARSE_FAILED


@pytest.mark.django_db
def test_revert_reparse_request_noops_using_locked_database_state():
    """Reverts should not overwrite a row that has already moved forward."""
    data_file = DataFileFactory(state=SubmissionState.REPARSE_REQUESTED)
    type(data_file).objects.filter(pk=data_file.pk).update(
        state=SubmissionState.PARSE_STARTED
    )

    reverted = revert_reparse_request(data_file, SubmissionState.PARSE_COMPLETED)

    data_file.refresh_from_db()
    assert reverted is False
    assert data_file.state == SubmissionState.PARSE_STARTED
    assert _state_transitions_for(data_file).count() == 0


@pytest.mark.django_db
def test_prepare_datafile_for_reparse_rejects_uploaded_file():
    """Test uploaded files require separate legacy data repair before reparse."""
    data_file = DataFileFactory(state=SubmissionState.UPLOADED)

    with pytest.raises(ReparsePreparationError, match="state uploaded"):
        prepare_datafile_for_reparse(data_file)


@pytest.mark.django_db
def test_prepare_datafile_for_reparse_rejects_active_pipeline_source():
    """Reparse cannot take a DataFile already snapshotted by active ETL."""
    data_file = DataFileFactory(state=SubmissionState.PARSE_COMPLETED)
    _active_pipeline_run_for_datafile(data_file)

    with pytest.raises(ReparsePreparationError, match="active ETL pipeline"):
        prepare_datafile_for_reparse(data_file)

    data_file.refresh_from_db()
    assert data_file.state == SubmissionState.PARSE_COMPLETED


@pytest.mark.parametrize(
    "state",
    [
        SubmissionState.VIRUS_SCAN_STARTED,
        SubmissionState.VIRUS_SCAN_FAILED,
        SubmissionState.PARSE_STARTED,
        SubmissionState.COMPLETED,
        SubmissionState.CANCELED,
        SubmissionState.STUCK,
    ],
)
@pytest.mark.django_db
def test_prepare_datafile_for_reparse_rejects_unsafe_states(state):
    """Test unsafe states are not prepared or queued for reparse."""
    data_file = DataFileFactory(state=state)

    with pytest.raises(ReparsePreparationError, match=f"state {state.value}"):
        prepare_datafile_for_reparse(data_file)


@pytest.mark.django_db
def test_complete_datafile_av_scan_clean_transitions_to_virus_scan_completed():
    """Clean AV completion should move a DataFile into virus scan completed."""
    data_file = DataFileFactory(state=SubmissionState.VIRUS_SCAN_STARTED)
    payloads = []

    result_file, transition_occurred = complete_datafile_av_scan(
        data_file,
        scan_result="clean",
        note="AV callback reported clean file",
        logger_hook=payloads.append,
    )
    data_file.refresh_from_db()

    assert transition_occurred is True
    assert result_file.id == data_file.id
    assert data_file.state == SubmissionState.VIRUS_SCAN_COMPLETED
    assert payloads == [
        {
            "data_file_id": data_file.id,
            "previous_state": SubmissionState.VIRUS_SCAN_STARTED.value,
            "next_state": SubmissionState.VIRUS_SCAN_COMPLETED.value,
            "scan_result": "CLEAN",
            "note": "AV callback reported clean file",
        }
    ]


@pytest.mark.django_db
def test_complete_datafile_av_scan_fail_transitions_to_virus_scan_failed():
    """Infected/failed AV completion should move a DataFile into scan failed."""
    data_file = DataFileFactory(state=SubmissionState.VIRUS_SCAN_STARTED)
    payloads = []

    result_file, transition_occurred = complete_datafile_av_scan(
        data_file,
        scan_result="infected",
        note="AV callback reported infection",
        logger_hook=payloads.append,
    )
    data_file.refresh_from_db()

    assert transition_occurred is True
    assert result_file.id == data_file.id
    assert data_file.state == SubmissionState.VIRUS_SCAN_FAILED
    assert payloads == [
        {
            "data_file_id": data_file.id,
            "previous_state": SubmissionState.VIRUS_SCAN_STARTED.value,
            "next_state": SubmissionState.VIRUS_SCAN_FAILED.value,
            "scan_result": "INFECTED",
            "note": "AV callback reported infection",
        }
    ]


@pytest.mark.django_db
def test_complete_datafile_av_scan_normalizes_scan_result_values():
    """Scan result handling should be case-insensitive and trim whitespace."""
    data_file = DataFileFactory(state=SubmissionState.VIRUS_SCAN_STARTED)

    result_file, transition_occurred = complete_datafile_av_scan(
        data_file, scan_result="  CLEAN  "
    )
    data_file.refresh_from_db()

    assert transition_occurred is True
    assert result_file.id == data_file.id
    assert data_file.state == SubmissionState.VIRUS_SCAN_COMPLETED


@pytest.mark.django_db
def test_complete_datafile_av_scan_out_of_order_noops_with_log_payload():
    """Out-of-order completion should no-op and emit structured context."""
    data_file = DataFileFactory(state=SubmissionState.PARSE_STARTED)
    payloads = []

    result_file, transition_occurred = complete_datafile_av_scan(
        data_file,
        scan_result="clean",
        logger_hook=payloads.append,
    )
    data_file.refresh_from_db()

    assert transition_occurred is False
    assert result_file.id == data_file.id
    assert data_file.state == SubmissionState.PARSE_STARTED
    assert _state_transitions_for(data_file).count() == 0
    assert payloads == [
        {
            "data_file_id": data_file.id,
            "previous_state": SubmissionState.PARSE_STARTED.value,
            "next_state": SubmissionState.VIRUS_SCAN_COMPLETED.value,
            "scan_result": "CLEAN",
            "note": "Ignoring out-of-order AV completion result for DataFile.",
        }
    ]


@pytest.mark.django_db
def test_complete_datafile_av_scan_duplicate_result_noops_with_log_payload():
    """Repeated callbacks with the same terminal result should be idempotent."""
    data_file = DataFileFactory(state=SubmissionState.VIRUS_SCAN_COMPLETED)
    payloads = []

    result_file, transition_occurred = complete_datafile_av_scan(
        data_file,
        scan_result="clean",
        logger_hook=payloads.append,
    )
    data_file.refresh_from_db()

    assert transition_occurred is False
    assert result_file.id == data_file.id
    assert data_file.state == SubmissionState.VIRUS_SCAN_COMPLETED
    assert _state_transitions_for(data_file).count() == 0
    assert payloads == [
        {
            "data_file_id": data_file.id,
            "previous_state": SubmissionState.VIRUS_SCAN_COMPLETED.value,
            "next_state": SubmissionState.VIRUS_SCAN_COMPLETED.value,
            "scan_result": "CLEAN",
            "note": "Duplicate AV completion result; no-op.",
        }
    ]


@pytest.mark.django_db
def test_complete_datafile_av_scan_duplicate_uses_locked_database_state():
    """A stale callback instance should still detect the committed duplicate result."""
    data_file = DataFileFactory(state=SubmissionState.VIRUS_SCAN_STARTED)
    stale_data_file = DataFileFactory._meta.model.objects.get(pk=data_file.pk)
    data_file.state = SubmissionState.VIRUS_SCAN_COMPLETED
    data_file.save(update_fields=["state"])
    payloads = []

    result_file, transition_occurred = complete_datafile_av_scan(
        stale_data_file,
        scan_result="clean",
        logger_hook=payloads.append,
    )

    assert transition_occurred is False
    assert result_file.state == SubmissionState.VIRUS_SCAN_COMPLETED
    assert _state_transitions_for(data_file).count() == 0
    assert payloads[0]["previous_state"] == SubmissionState.VIRUS_SCAN_COMPLETED


@pytest.mark.django_db
def test_complete_datafile_av_scan_strict_out_of_order_raises():
    """Strict mode should raise for out-of-order callbacks."""
    data_file = DataFileFactory(state=SubmissionState.PARSE_STARTED)

    with pytest.raises(
        InvalidTransition,
        match="Cannot apply AV scan completion while DataFile is in parse_started",
    ):
        complete_datafile_av_scan(data_file, scan_result="clean", strict=True)


def test_complete_datafile_av_scan_rejects_unknown_scan_result():
    """Unknown scan result values should fail fast."""
    data_file = DataFileFactory.build(state=SubmissionState.VIRUS_SCAN_STARTED)

    with pytest.raises(InvalidScanResult, match="Unsupported AV scan result"):
        complete_datafile_av_scan(data_file, scan_result="MAYBE")
