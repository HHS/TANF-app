"""Tests for parser task helpers and flow control."""

import io
from types import SimpleNamespace

import pytest
from django.db.utils import DatabaseError

from tdpservice.data_files.models import DataFile, ReparseFileMeta
from tdpservice.data_files.test.factories import DataFileFactory
from tdpservice.parsers.models import DataFileSummary
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

    def fake_update_dfs(dfs, data_file):
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
        staticmethod(lambda data_file: DummyReport()),
    )
    return handlers


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

    monkeypatch.setattr(parser_task, "fra_total_errors", lambda df: {"fra": 1})

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

    monkeypatch.setattr(parser_task, "case_aggregates_by_month", lambda *a: {"case": 2})
    monkeypatch.setattr(
        parser_task,
        "total_errors_by_month",
        lambda *a: pytest.fail("total_errors_by_month should not be used"),
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
        lambda *a: pytest.fail("case_aggregates_by_month should not be used"),
    )
    monkeypatch.setattr(
        parser_task, "total_errors_by_month", lambda *a: {"total": 3}
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
def test_parse_success_sends_email(monkeypatch, data_analyst):
    """Send notification email on successful parse."""
    datafile = DataFileFactory(stt=data_analyst.stt, version=4)
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

    def fake_send(dfs, recipients):
        captured["recipients"] = list(recipients)

    monkeypatch.setattr(parser_task, "send_data_submitted_email", fake_send)

    parser_task.parse(datafile.id)

    assert dummy_parser.called is True
    assert data_analyst.username in captured["recipients"]
    assert handlers[2].called is True


@pytest.mark.django_db
def test_parse_success_reparse_updates_file_meta(monkeypatch, stt):
    """Update reparse metadata on success."""
    datafile = DataFileFactory(stt=stt, version=5)
    ensure_stt_filenames(datafile.stt)
    dfs = DataFileSummary.objects.create(
        datafile=datafile, status=DataFileSummary.Status.PENDING
    )
    meta_model = ReparseMeta.objects.create(db_backup_location="s3://backup")
    file_meta = ReparseFileMeta.objects.create(
        data_file=datafile, reparse_meta=meta_model
    )
    setup_parse_mocks(monkeypatch, dfs=dfs)
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

    parser_task.parse(datafile.id, reparse_id=meta_model.pk)

    file_meta.refresh_from_db()
    assert file_meta.finished is True
    assert file_meta.success is True
    assert file_meta.cat_4_errors_generated == 2
    assert file_meta.finished_at is not None


@pytest.mark.django_db
def test_parse_decoder_unknown_sets_reparse_failed(monkeypatch, stt):
    """Set rejected status and failed reparse state on decode errors."""
    datafile = DataFileFactory(stt=stt, version=6)
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
    dfs = DataFileSummary.objects.get(datafile=datafile)
    assert dfs.status == DataFileSummary.Status.REJECTED
    assert file_meta.finished is True
    assert file_meta.success is False


@pytest.mark.django_db
def test_parse_database_error_sets_reparse_failed(monkeypatch, stt):
    """Mark reparse failed on database error."""
    datafile = DataFileFactory(stt=stt, version=7)
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
    assert file_meta.finished is True
    assert file_meta.success is False


@pytest.mark.django_db
def test_parse_generic_exception_rejects_and_logs(monkeypatch, stt):
    """Create error and reject on unexpected exceptions."""
    datafile = DataFileFactory(stt=stt, version=8)
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
    assert dfs.status == DataFileSummary.Status.REJECTED
    assert saved["called"] is True
    assert file_meta.finished is True
    assert file_meta.success is False
