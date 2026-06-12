"""Tests for parser task helpers and flow control."""

import io
from types import SimpleNamespace

from django.contrib.admin.models import LogEntry
from django.db.utils import DatabaseError
from django.test import override_settings

import pytest

from tdpservice.data_files.enums import SubmissionState
from tdpservice.data_files.models import (
    DataFile,
    ReparseFileMeta,
    create_or_update_shadow_data_file,
)
from tdpservice.data_files.test.factories import DataFileFactory
from tdpservice.parsers.models import (
    DataFileSummary,
    ParserError,
    ShadowDataFileSummary,
    ShadowParserError,
)
from tdpservice.parsers.util import DecoderUnknownException
from tdpservice.scheduling import parser_task
from tdpservice.search_indexes.models.reparse_meta import ReparseMeta


class DummyHandler:
    """Logger handler stub to capture rollover calls."""

    def __init__(self):
        self.called = False
        self.level = 0

    def doRollover(self, data_file):
        """Record rollover invocation."""
        self.called = True

    def handle(self, record):
        """No-op handler for logger internals."""
        return True


class DummyParser:
    """Parser stub used for flow control tests."""

    def __init__(self, exc=None):
        self.exc = exc
        self.called = False

    def parse_and_validate(self):
        """Invoke a configured exception or no-op."""
        self.called = True
        if self.exc is not None:
            raise self.exc


DEFAULT_FILENAMES = {
    DataFile.Section.ACTIVE_CASE_DATA: "ADS.E2J.FTP1.TS72",
    DataFile.Section.CLOSED_CASE_DATA: "ADS.E2J.FTP2.TS72",
    DataFile.Section.AGGREGATE_DATA: "ADS.E2J.FTP3.TS72",
    DataFile.Section.STRATUM_DATA: "ADS.E2J.FTP4.TS72",
    DataFile.Section.FRA_WORK_OUTCOME_TANF_EXITERS: "ADS.FRA.FTP1.TS72",
    DataFile.Section.FRA_SECONDRY_SCHOOL_ATTAINMENT: "ADS.FRA.FTP2.TS72",
    DataFile.Section.FRA_SUPPLEMENT_WORK_OUTCOMES: "ADS.FRA.FTP3.TS72",
}


def ensure_stt_filenames(stt):
    """Set default STT filenames when missing to unblock parse logging."""
    if not stt.filenames:
        stt.filenames = DEFAULT_FILENAMES.copy()
        stt.save(update_fields=["filenames"])


def setup_parse_mocks(monkeypatch, dfs=None):
    """Patch common dependencies for parser_task.parse tests."""
    handlers = [DummyHandler(), DummyHandler(), DummyHandler()]
    monkeypatch.setattr(parser_task.logger, "handlers", handlers, raising=False)
    monkeypatch.setattr(parser_task, "change_log_filename", lambda *a, **k: None)

    def fake_update_dfs(dfs, data_file, **kwargs):
        dfs.save()

    monkeypatch.setattr(parser_task, "update_dfs", fake_update_dfs)
    monkeypatch.setattr(parser_task, "set_error_report", lambda *a, **k: None)
    if dfs is not None:
        monkeypatch.setattr(
            parser_task.DataFileSummary.objects, "create", lambda **kwargs: dfs
        )

    class DummyReport:
        def generate(self):
            return io.BytesIO(b"report")

    monkeypatch.setattr(
        parser_task.ErrorReportFactory,
        "get_error_report_generator",
        staticmethod(lambda data_file, parser_error_model=None: DummyReport()),
    )
    return handlers


def test_queue_go_parse_sends_shadow_task(monkeypatch):
    """Queue Go parser task with the expected Celery task name and payload."""
    calls = []

    def fake_send_task(name, args=None, queue=None, ignore_result=False):
        calls.append(
            {
                "name": name,
                "args": args,
                "queue": queue,
                "ignore_result": ignore_result,
            }
        )

    monkeypatch.setattr(
        parser_task,
        "current_app",
        SimpleNamespace(send_task=fake_send_task),
    )

    parser_task.queue_go_parse(42)

    assert calls == [
        {
            "name": parser_task.GO_PARSER_TASK_NAME,
            "args": [42, 0],
            "queue": parser_task.GO_PARSER_QUEUE,
            "ignore_result": True,
        }
    ]


def test_queue_go_parse_sends_reparse_id(monkeypatch):
    """Queue Go parser reparses with the reparse metadata id."""
    calls = []

    monkeypatch.setattr(
        parser_task,
        "current_app",
        SimpleNamespace(
            send_task=lambda name, args=None, queue=None, ignore_result=False: calls.append(
                args
            )
        ),
    )

    parser_task.queue_go_parse(42, reparse_id=7)

    assert calls == [[42, 7]]


@pytest.mark.django_db
def test_queue_go_parse_logs_submit_failure_to_admin(monkeypatch, stt):
    """Write Go parser queue submission failures to Django admin logs."""
    datafile = DataFileFactory(stt=stt, version=1)

    def fake_send_task(*args, **kwargs):
        raise RuntimeError("redis down")

    monkeypatch.setattr(
        parser_task,
        "current_app",
        SimpleNamespace(send_task=fake_send_task),
    )

    parser_task.queue_go_parse(datafile.id)

    entry = LogEntry.objects.latest("pk")
    assert str(entry.user_id) == datafile.user_id
    assert entry.object_id == str(datafile.pk)
    assert entry.change_message == (
        f"Failed to submit Go parser shadow task for datafile {datafile.id}."
    )


def test_queue_parse_queues_python_and_go(monkeypatch):
    """Queue production Python parse and companion Go shadow parse."""
    calls = []

    monkeypatch.setattr(
        parser_task,
        "parse",
        SimpleNamespace(
            delay=lambda data_file_id, reparse_id=None: calls.append(
                ("python", data_file_id, reparse_id)
            )
        ),
    )
    monkeypatch.setattr(
        parser_task,
        "queue_go_parse",
        lambda data_file_id, reparse_id=None: calls.append(
            ("go", data_file_id, reparse_id)
        ),
    )

    parser_task.queue_parse(42, reparse_id=7)

    assert calls == [
        ("python", 42, 7),
        ("go", 42, 7),
    ]


@override_settings(GO_PARSER_SHADOW_MODE=False)
def test_queue_parse_skips_go_when_shadow_mode_off(monkeypatch):
    """Queue only the production Python parser when Go shadow mode is disabled."""
    calls = []

    monkeypatch.setattr(
        parser_task,
        "parse",
        SimpleNamespace(
            delay=lambda data_file_id, reparse_id=None: calls.append(
                ("python", data_file_id, reparse_id)
            )
        ),
    )
    monkeypatch.setattr(
        parser_task,
        "queue_go_parse",
        lambda data_file_id, reparse_id=None: calls.append(
            ("go", data_file_id, reparse_id)
        ),
    )

    parser_task.queue_parse(42, reparse_id=7)

    assert calls == [
        ("python", 42, 7),
    ]


@pytest.mark.django_db
def test_update_dfs_uses_fra_aggregates(monkeypatch, stt):
    """Use FRA aggregates for FRA program types."""
    datafile = DataFileFactory(
        stt=stt,
        version=1,
        program_type=DataFile.ProgramType.FRA,
        section=DataFile.Section.FRA_WORK_OUTCOME_TANF_EXITERS,
    )
    dfs = DataFileSummary.objects.create(
        datafile=datafile, status=DataFileSummary.Status.ACCEPTED
    )

    monkeypatch.setattr(
        parser_task, "fra_total_errors", lambda df, **kwargs: {"fra": 1}
    )

    parser_task.update_dfs(dfs, datafile)

    dfs.refresh_from_db()
    assert dfs.case_aggregates == {"fra": 1}


@pytest.mark.django_db
def test_update_dfs_uses_case_aggregates(monkeypatch, stt):
    """Use case aggregates for case data sections."""
    datafile = DataFileFactory(
        stt=stt,
        version=2,
        program_type=DataFile.ProgramType.TANF,
        section=DataFile.Section.ACTIVE_CASE_DATA,
    )
    dfs = DataFileSummary.objects.create(
        datafile=datafile, status=DataFileSummary.Status.ACCEPTED
    )

    monkeypatch.setattr(
        parser_task, "case_aggregates_by_month", lambda *a, **kwargs: {"case": 2}
    )
    monkeypatch.setattr(
        parser_task,
        "total_errors_by_month",
        lambda *a, **kwargs: pytest.fail("total_errors_by_month should not be used"),
    )

    parser_task.update_dfs(dfs, datafile)

    dfs.refresh_from_db()
    assert dfs.case_aggregates == {"case": 2}


@pytest.mark.django_db
def test_update_dfs_uses_total_errors(monkeypatch, stt):
    """Use total errors for non-case data sections."""
    datafile = DataFileFactory(
        stt=stt,
        version=3,
        program_type=DataFile.ProgramType.TANF,
        section=DataFile.Section.AGGREGATE_DATA,
    )
    dfs = DataFileSummary.objects.create(
        datafile=datafile, status=DataFileSummary.Status.ACCEPTED
    )

    monkeypatch.setattr(
        parser_task,
        "case_aggregates_by_month",
        lambda *a, **kwargs: pytest.fail("case_aggregates_by_month should not be used"),
    )
    monkeypatch.setattr(
        parser_task, "total_errors_by_month", lambda *a, **kwargs: {"total": 3}
    )

    parser_task.update_dfs(dfs, datafile)

    dfs.refresh_from_db()
    assert dfs.case_aggregates == {"total": 3}


def test_set_error_report_sets_filename():
    """Set error report file name based on original filename."""

    class DummyDataFile:
        original_filename = "sample.txt"

    class DummySummary:
        def __init__(self):
            self.datafile = DummyDataFile()
            self.error_report = None
            self.saved = False

        def save(self):
            self.saved = True

    dfs = DummySummary()

    parser_task.set_error_report(dfs, io.BytesIO(b"report"))

    assert dfs.saved is True
    assert dfs.error_report.name == "sample.txt_error_report"


@pytest.mark.django_db
def test_post_parse_finalizes_shadow_summary_only(monkeypatch, stt):
    """Finalize Go parser output using only shadow parser tables."""
    datafile = DataFileFactory(
        stt=stt,
        version=4,
        state=SubmissionState.VIRUS_SCAN_COMPLETED,
        section=DataFile.Section.AGGREGATE_DATA,
    )
    shadow_datafile = create_or_update_shadow_data_file(datafile)
    shadow_summary = ShadowDataFileSummary.objects.create(
        datafile=shadow_datafile,
        status=DataFileSummary.Status.PENDING,
    )
    production_summary = DataFileSummary.objects.create(
        datafile=datafile,
        status=DataFileSummary.Status.PENDING,
    )
    ShadowParserError.objects.create(
        file=shadow_datafile,
        row_number=1,
        column_number="1",
        item_number="1",
        field_name="FIELD",
        rpt_month_year=201910,
        case_number="CASE",
        error_message="FIELD is invalid",
        error_type=parser_task.ParserErrorCategoryChoices.FIELD_VALUE,
        fields_json={"friendly_name": {"FIELD": "Field"}},
    )

    sent = {"called": False}
    monkeypatch.setattr(
        parser_task,
        "send_data_submitted_email",
        lambda *args, **kwargs: sent.update(called=True),
    )

    parser_task.post_parse(datafile.id)

    shadow_summary.refresh_from_db()
    production_summary.refresh_from_db()
    datafile.refresh_from_db()

    assert shadow_summary.status == DataFileSummary.Status.ACCEPTED_WITH_ERRORS
    assert shadow_summary.case_aggregates == {
        "months": [
            {"month": "Oct", "total_errors": 1},
            {"month": "Nov", "total_errors": 0},
            {"month": "Dec", "total_errors": 0},
        ]
    }
    assert "data_file.txt_shadow_error_report" in shadow_summary.error_report.name
    assert production_summary.status == DataFileSummary.Status.PENDING
    assert datafile.state == SubmissionState.VIRUS_SCAN_COMPLETED
    assert sent["called"] is False


@pytest.mark.django_db
def test_post_parse_parse_error_rejects_shadow_summary(stt):
    """Technical parse failures reject only the shadow summary."""
    datafile = DataFileFactory(
        stt=stt,
        version=4,
        state=SubmissionState.VIRUS_SCAN_COMPLETED,
    )
    shadow_datafile = create_or_update_shadow_data_file(datafile)
    shadow_summary = ShadowDataFileSummary.objects.create(
        datafile=shadow_datafile,
        status=DataFileSummary.Status.PENDING,
    )

    parser_task.post_parse(datafile.id, parse_error="pipeline failed")

    shadow_summary.refresh_from_db()
    shadow_datafile.refresh_from_db()
    datafile.refresh_from_db()

    assert shadow_summary.status == DataFileSummary.Status.REJECTED
    assert shadow_datafile.state == SubmissionState.PARSE_FAILED
    assert datafile.state == SubmissionState.VIRUS_SCAN_COMPLETED


@pytest.mark.django_db
@override_settings(GO_PARSER_SHADOW_MODE=False)
def test_post_parse_can_finalize_production_summary(monkeypatch, stt):
    """Finalize Go parser production output when shadow mode is disabled."""
    datafile = DataFileFactory(
        stt=stt,
        version=4,
        state=SubmissionState.VIRUS_SCAN_COMPLETED,
        section=DataFile.Section.AGGREGATE_DATA,
    )
    summary = DataFileSummary.objects.create(
        datafile=datafile,
        status=DataFileSummary.Status.PENDING,
    )
    ParserError.objects.create(
        file=datafile,
        row_number=1,
        column_number="1",
        item_number="1",
        field_name="FIELD",
        rpt_month_year=201910,
        case_number="CASE",
        error_message="FIELD is invalid",
        error_type=parser_task.ParserErrorCategoryChoices.FIELD_VALUE,
        fields_json={"friendly_name": {"FIELD": "Field"}},
    )

    sent = {"called": False}
    monkeypatch.setattr(
        parser_task,
        "send_data_submitted_email",
        lambda *args, **kwargs: sent.update(called=True),
    )

    parser_task.post_parse(datafile.id)

    summary.refresh_from_db()
    datafile.refresh_from_db()

    assert summary.status == DataFileSummary.Status.ACCEPTED_WITH_ERRORS
    assert summary.case_aggregates == {
        "months": [
            {"month": "Oct", "total_errors": 1},
            {"month": "Nov", "total_errors": 0},
            {"month": "Dec", "total_errors": 0},
        ]
    }
    assert "data_file.txt_error_report" in summary.error_report.name
    assert datafile.state == SubmissionState.VIRUS_SCAN_COMPLETED
    assert sent["called"] is False


@pytest.mark.django_db
@override_settings(GO_PARSER_SHADOW_MODE=False)
def test_post_parse_can_finalize_production_reparse(monkeypatch, stt):
    """Update reparse metadata after Go parser production output finalizes."""
    datafile = DataFileFactory(
        stt=stt,
        version=5,
        state=SubmissionState.VIRUS_SCAN_COMPLETED,
        section=DataFile.Section.AGGREGATE_DATA,
    )
    summary = DataFileSummary.objects.create(
        datafile=datafile,
        status=DataFileSummary.Status.PENDING,
    )
    meta_model = ReparseMeta.objects.create(db_backup_location="s3://backup")
    file_meta = ReparseFileMeta.objects.create(
        data_file=datafile,
        reparse_meta=meta_model,
    )
    monkeypatch.setattr(
        parser_task.ReparseMeta, "set_total_num_records_post", lambda *a, **k: None
    )

    parser_task.post_parse(datafile.id, reparse_id=meta_model.pk)

    summary.refresh_from_db()
    file_meta.refresh_from_db()

    assert summary.status == DataFileSummary.Status.ACCEPTED
    assert file_meta.finished is True
    assert file_meta.success is True
    assert file_meta.num_records_created == summary.total_number_of_records_created
    assert file_meta.finished_at is not None


@pytest.mark.django_db
def test_finalize_reparse_sets_total_num_records_post_when_last_file_finishes(
    monkeypatch, stt
):
    """Persist the post-reparse total after the last file is marked finished."""
    datafile = DataFileFactory(stt=stt, version=5)
    summary = DataFileSummary.objects.create(
        datafile=datafile,
        status=DataFileSummary.Status.ACCEPTED,
        total_number_of_records_created=7,
    )
    meta_model = ReparseMeta.objects.create(db_backup_location="s3://backup")
    file_meta = ReparseFileMeta.objects.create(
        data_file=datafile,
        reparse_meta=meta_model,
        finished=False,
        success=False,
    )
    monkeypatch.setattr(
        "tdpservice.search_indexes.models.reparse_meta.count_all_records",
        lambda: 42,
    )

    parser_task._finalize_reparse(
        datafile.id,
        meta_model.pk,
        file_meta,
        summary,
        reparse_success=True,
    )

    meta_model.refresh_from_db()
    file_meta.refresh_from_db()

    assert file_meta.finished is True
    assert file_meta.success is True
    assert file_meta.num_records_created == 7
    assert meta_model.total_num_records_post == 42


@pytest.mark.django_db
def test_parse_success_sends_email(monkeypatch, data_analyst):
    """Send notification email on successful parse."""
    datafile = DataFileFactory(
        stt=data_analyst.stt, version=4, state=SubmissionState.VIRUS_SCAN_COMPLETED
    )
    ensure_stt_filenames(datafile.stt)
    dfs = DataFileSummary.objects.create(
        datafile=datafile, status=DataFileSummary.Status.PENDING
    )
    handlers = setup_parse_mocks(monkeypatch, dfs=dfs)
    dummy_parser = DummyParser()

    monkeypatch.setattr(
        parser_task.ParserFactory, "get_instance", lambda **kwargs: dummy_parser
    )

    captured = {}

    def fake_send(dfs, recipients, is_reprocessed=False):
        captured["recipients"] = list(recipients)

    monkeypatch.setattr(parser_task, "send_data_submitted_email", fake_send)

    parser_task.parse(datafile.id)

    assert dummy_parser.called is True
    assert data_analyst.username in captured["recipients"]
    assert handlers[2].called is True

    datafile.refresh_from_db()
    assert datafile.state == SubmissionState.PARSE_STARTED


@pytest.mark.django_db
def test_parse_success_reparse_updates_file_meta(monkeypatch, data_analyst):
    """Update reparse metadata on success."""
    datafile = DataFileFactory(
        stt=data_analyst.stt, version=5, state=SubmissionState.PARSE_COMPLETED
    )
    ensure_stt_filenames(datafile.stt)
    dfs = DataFileSummary.objects.create(
        datafile=datafile, status=DataFileSummary.Status.PENDING
    )
    meta_model = ReparseMeta.objects.create(db_backup_location="s3://backup")
    file_meta = ReparseFileMeta.objects.create(
        data_file=datafile, reparse_meta=meta_model
    )
    handlers = setup_parse_mocks(monkeypatch, dfs=dfs)
    dummy_parser = DummyParser()

    monkeypatch.setattr(
        parser_task.ParserFactory, "get_instance", lambda **kwargs: dummy_parser
    )
    monkeypatch.setattr(
        parser_task.ParserError.objects,
        "filter",
        lambda *a, **k: SimpleNamespace(count=lambda: 2),
    )
    monkeypatch.setattr(
        parser_task.ReparseMeta, "set_total_num_records_post", lambda *a, **k: None
    )

    def fake_update_dfs(dfs, data_file, **kwargs):
        dfs.status = DataFileSummary.Status.ACCEPTED
        dfs.save()

    monkeypatch.setattr(parser_task, "update_dfs", fake_update_dfs)

    captured = {}

    def fake_send(dfs, recipients, is_reprocessed=False):
        captured["recipients"] = list(recipients)

    monkeypatch.setattr(parser_task, "send_data_submitted_email", fake_send)

    parser_task.parse(datafile.id, reparse_id=meta_model.pk)

    datafile.refresh_from_db()
    file_meta.refresh_from_db()
    assert datafile.state == SubmissionState.PARSE_COMPLETED
    assert file_meta.finished is True
    assert file_meta.success is True
    assert file_meta.cat_4_errors_generated == 2
    assert file_meta.finished_at is not None

    assert dummy_parser.called is True
    assert data_analyst.username in captured["recipients"]
    assert handlers[2].called is True


@pytest.mark.django_db
def test_parse_success_reparse_suppresses_email_for_accepted_to_accepted(
    monkeypatch, data_analyst
):
    """Do not send a reparse email when Accepted remains Accepted."""
    datafile = DataFileFactory(stt=data_analyst.stt, version=6)
    datafile.state = SubmissionState.PARSE_COMPLETED
    datafile.save()
    ensure_stt_filenames(datafile.stt)
    dfs = DataFileSummary.objects.create(
        datafile=datafile, status=DataFileSummary.Status.PENDING
    )
    meta_model = ReparseMeta.objects.create(db_backup_location="s3://backup")
    ReparseFileMeta.objects.create(
        data_file=datafile,
        reparse_meta=meta_model,
        previous_summary_status=DataFileSummary.Status.ACCEPTED,
    )
    handlers = setup_parse_mocks(monkeypatch, dfs=dfs)
    dummy_parser = DummyParser()

    monkeypatch.setattr(
        parser_task.ParserFactory, "get_instance", lambda **kwargs: dummy_parser
    )
    monkeypatch.setattr(
        parser_task,
        "update_dfs",
        lambda dfs, data_file, **kwargs: setattr(
            dfs, "status", DataFileSummary.Status.ACCEPTED
        ),
    )
    monkeypatch.setattr(
        parser_task.ParserError.objects,
        "filter",
        lambda *a, **k: SimpleNamespace(count=lambda: 0),
    )
    monkeypatch.setattr(
        parser_task.ReparseMeta, "set_total_num_records_post", lambda *a, **k: None
    )

    called = {"sent": False}

    def fake_send(dfs, recipients, is_reprocessed=False):
        called["sent"] = True

    monkeypatch.setattr(parser_task, "send_data_submitted_email", fake_send)

    parser_task.parse(datafile.id, reparse_id=meta_model.pk)

    assert dummy_parser.called is True
    assert called["sent"] is False
    assert handlers[2].called is True


@pytest.mark.django_db
def test_parse_success_reparse_still_sends_email_for_unchanged_nonaccepted_status(
    monkeypatch, data_analyst
):
    """Still send a reparse email when a non-Accepted status remains unchanged."""
    datafile = DataFileFactory(stt=data_analyst.stt, version=7)
    datafile.state = SubmissionState.PARSED_WITH_ERRORS
    datafile.save()
    ensure_stt_filenames(datafile.stt)
    dfs = DataFileSummary.objects.create(
        datafile=datafile, status=DataFileSummary.Status.PENDING
    )
    meta_model = ReparseMeta.objects.create(db_backup_location="s3://backup")
    ReparseFileMeta.objects.create(
        data_file=datafile,
        reparse_meta=meta_model,
        previous_summary_status=DataFileSummary.Status.ACCEPTED_WITH_ERRORS,
    )
    handlers = setup_parse_mocks(monkeypatch, dfs=dfs)
    dummy_parser = DummyParser()

    monkeypatch.setattr(
        parser_task.ParserFactory, "get_instance", lambda **kwargs: dummy_parser
    )
    monkeypatch.setattr(
        parser_task,
        "update_dfs",
        lambda dfs, data_file, **kwargs: setattr(
            dfs, "status", DataFileSummary.Status.ACCEPTED_WITH_ERRORS
        ),
    )
    monkeypatch.setattr(
        parser_task.ParserError.objects,
        "filter",
        lambda *a, **k: SimpleNamespace(count=lambda: 1),
    )
    monkeypatch.setattr(
        parser_task.ReparseMeta, "set_total_num_records_post", lambda *a, **k: None
    )

    called = {"sent": False}

    def fake_send(dfs, recipients, is_reprocessed=False):
        called["sent"] = True

    monkeypatch.setattr(parser_task, "send_data_submitted_email", fake_send)

    parser_task.parse(datafile.id, reparse_id=meta_model.pk)

    assert dummy_parser.called is True
    assert called["sent"] is True
    assert handlers[2].called is True


@pytest.mark.django_db
def test_parse_decoder_unknown_sets_reparse_failed(monkeypatch, stt):
    """Set rejected status and failed reparse state on decode errors."""
    datafile = DataFileFactory(
        stt=stt, version=6, state=SubmissionState.PARSE_COMPLETED
    )
    ensure_stt_filenames(datafile.stt)
    dfs = DataFileSummary.objects.create(
        datafile=datafile, status=DataFileSummary.Status.PENDING
    )
    meta_model = ReparseMeta.objects.create(db_backup_location="s3://backup")
    file_meta = ReparseFileMeta.objects.create(
        data_file=datafile, reparse_meta=meta_model
    )
    setup_parse_mocks(monkeypatch, dfs=dfs)
    dummy_parser = DummyParser(exc=DecoderUnknownException("decode"))

    monkeypatch.setattr(
        parser_task.ParserFactory, "get_instance", lambda **kwargs: dummy_parser
    )

    parser_task.parse(datafile.id, reparse_id=meta_model.pk)

    file_meta.refresh_from_db()
    datafile.refresh_from_db()
    dfs = DataFileSummary.objects.get(datafile=datafile)
    assert datafile.state == SubmissionState.PARSE_FAILED
    assert dfs.status == DataFileSummary.Status.REJECTED
    assert file_meta.finished is True
    assert file_meta.success is False


@pytest.mark.django_db
def test_parse_database_error_sets_reparse_failed(monkeypatch, stt):
    """Mark reparse failed on database error."""
    datafile = DataFileFactory(
        stt=stt, version=7, state=SubmissionState.PARSE_COMPLETED
    )
    ensure_stt_filenames(datafile.stt)
    dfs = DataFileSummary.objects.create(
        datafile=datafile, status=DataFileSummary.Status.PENDING
    )
    meta_model = ReparseMeta.objects.create(db_backup_location="s3://backup")
    file_meta = ReparseFileMeta.objects.create(
        data_file=datafile, reparse_meta=meta_model
    )
    setup_parse_mocks(monkeypatch, dfs=dfs)
    dummy_parser = DummyParser(exc=DatabaseError("db"))

    monkeypatch.setattr(
        parser_task.ParserFactory, "get_instance", lambda **kwargs: dummy_parser
    )
    monkeypatch.setattr(parser_task, "log_parser_exception", lambda *a, **k: None)

    parser_task.parse(datafile.id, reparse_id=meta_model.pk)

    file_meta.refresh_from_db()
    datafile.refresh_from_db()
    assert datafile.state == SubmissionState.PARSE_FAILED
    assert file_meta.finished is True
    assert file_meta.success is False


@pytest.mark.django_db
def test_parse_generic_exception_rejects_and_logs(monkeypatch, stt):
    """Create error and reject on unexpected exceptions."""
    datafile = DataFileFactory(
        stt=stt, version=8, state=SubmissionState.PARSE_COMPLETED
    )
    ensure_stt_filenames(datafile.stt)
    dfs = DataFileSummary.objects.create(
        datafile=datafile, status=DataFileSummary.Status.PENDING
    )
    meta_model = ReparseMeta.objects.create(db_backup_location="s3://backup")
    file_meta = ReparseFileMeta.objects.create(
        data_file=datafile, reparse_meta=meta_model
    )
    setup_parse_mocks(monkeypatch, dfs=dfs)
    dummy_parser = DummyParser(exc=RuntimeError("boom"))

    monkeypatch.setattr(
        parser_task.ParserFactory, "get_instance", lambda **kwargs: dummy_parser
    )
    monkeypatch.setattr(parser_task, "log_parser_exception", lambda *a, **k: None)

    saved = {"called": False}

    def fake_get_generator(self, generator_type, row_number):
        def generate(generator_args):
            class DummyError:
                def save(self_inner):
                    saved["called"] = True

            return DummyError()

        return generate

    monkeypatch.setattr(
        parser_task.ErrorGeneratorFactory, "get_generator", fake_get_generator
    )

    parser_task.parse(datafile.id, reparse_id=meta_model.pk)

    dfs = DataFileSummary.objects.get(datafile=datafile)
    file_meta.refresh_from_db()
    datafile.refresh_from_db()
    assert datafile.state == SubmissionState.PARSE_FAILED
    assert dfs.status == DataFileSummary.Status.REJECTED
    assert saved["called"] is True
    assert file_meta.finished is True
    assert file_meta.success is False


@pytest.mark.django_db
def test_parse_transitions_to_parse_completed(monkeypatch, data_analyst):
    """Transition to PARSE_COMPLETED when DFS status is ACCEPTED."""
    datafile = DataFileFactory(
        stt=data_analyst.stt, version=10, state=SubmissionState.VIRUS_SCAN_COMPLETED
    )
    ensure_stt_filenames(datafile.stt)
    dfs = DataFileSummary.objects.create(
        datafile=datafile, status=DataFileSummary.Status.PENDING
    )

    def fake_update_dfs(dfs, data_file, **kwargs):
        dfs.status = DataFileSummary.Status.ACCEPTED
        dfs.save()

    setup_parse_mocks(monkeypatch, dfs=dfs)
    monkeypatch.setattr(parser_task, "update_dfs", fake_update_dfs)
    monkeypatch.setattr(
        parser_task.ParserFactory, "get_instance", lambda **kwargs: DummyParser()
    )
    monkeypatch.setattr(parser_task, "send_data_submitted_email", lambda *a, **k: None)

    parser_task.parse(datafile.id)

    datafile.refresh_from_db()
    assert datafile.state == SubmissionState.PARSE_COMPLETED


@pytest.mark.django_db
def test_parse_transitions_to_parsed_with_errors(monkeypatch, data_analyst):
    """Transition to PARSED_WITH_ERRORS when DFS status has errors."""
    datafile = DataFileFactory(
        stt=data_analyst.stt, version=11, state=SubmissionState.VIRUS_SCAN_COMPLETED
    )
    ensure_stt_filenames(datafile.stt)
    dfs = DataFileSummary.objects.create(
        datafile=datafile, status=DataFileSummary.Status.PENDING
    )

    def fake_update_dfs(dfs, data_file, **kwargs):
        dfs.status = DataFileSummary.Status.ACCEPTED_WITH_ERRORS
        dfs.save()

    setup_parse_mocks(monkeypatch, dfs=dfs)
    monkeypatch.setattr(parser_task, "update_dfs", fake_update_dfs)
    monkeypatch.setattr(
        parser_task.ParserFactory, "get_instance", lambda **kwargs: DummyParser()
    )
    monkeypatch.setattr(parser_task, "send_data_submitted_email", lambda *a, **k: None)

    parser_task.parse(datafile.id)

    datafile.refresh_from_db()
    assert datafile.state == SubmissionState.PARSED_WITH_ERRORS


@pytest.mark.django_db
def test_parse_transitions_to_parse_failed_on_exception(monkeypatch, data_analyst):
    """Transition to PARSE_FAILED on decoder exception for initial submission."""
    datafile = DataFileFactory(
        stt=data_analyst.stt, version=12, state=SubmissionState.VIRUS_SCAN_COMPLETED
    )
    ensure_stt_filenames(datafile.stt)
    dfs = DataFileSummary.objects.create(
        datafile=datafile, status=DataFileSummary.Status.PENDING
    )
    setup_parse_mocks(monkeypatch, dfs=dfs)
    monkeypatch.setattr(
        parser_task.ParserFactory,
        "get_instance",
        lambda **kwargs: DummyParser(exc=DecoderUnknownException("fail")),
    )

    parser_task.parse(datafile.id)

    datafile.refresh_from_db()
    assert datafile.state == SubmissionState.PARSE_FAILED


@pytest.mark.django_db
def test_reparse_transitions_to_parse_started(monkeypatch, stt):
    """Reparse runs should mark the DataFile as parsing when the worker starts."""
    datafile = DataFileFactory(
        stt=stt, version=13, state=SubmissionState.PARSE_COMPLETED
    )
    ensure_stt_filenames(datafile.stt)
    dfs = DataFileSummary.objects.create(
        datafile=datafile, status=DataFileSummary.Status.PENDING
    )
    meta_model = ReparseMeta.objects.create(db_backup_location="s3://backup")
    ReparseFileMeta.objects.create(data_file=datafile, reparse_meta=meta_model)
    setup_parse_mocks(monkeypatch, dfs=dfs)
    monkeypatch.setattr(
        parser_task.ParserFactory, "get_instance", lambda **kwargs: DummyParser()
    )
    monkeypatch.setattr(
        parser_task.ParserError.objects,
        "filter",
        lambda *a, **k: SimpleNamespace(count=lambda: 0),
    )
    monkeypatch.setattr(
        parser_task.ReparseMeta, "set_total_num_records_post", lambda *a, **k: None
    )

    parser_task.parse(datafile.id, reparse_id=meta_model.pk)

    datafile.refresh_from_db()
    assert datafile.state == SubmissionState.PARSE_STARTED


@pytest.mark.django_db
def test_parse_pre_dfs_failure_surfaces_original_exception(monkeypatch, stt):
    """Failures before DataFileSummary creation should not be masked by cleanup code."""
    datafile = DataFileFactory(stt=stt, version=14, state=SubmissionState.UPLOADED)
    ensure_stt_filenames(datafile.stt)
    setup_parse_mocks(monkeypatch)

    with pytest.raises(ValueError, match="uploaded to parse_started"):
        parser_task.parse(datafile.id)
