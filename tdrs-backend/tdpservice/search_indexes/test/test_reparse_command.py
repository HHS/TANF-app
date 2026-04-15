"""Tests for search index reparse command helpers."""

import datetime

import pytest
from django.db.utils import DatabaseError

from tdpservice.data_files.test.factories import DataFileFactory
from tdpservice.search_indexes.models.reparse_meta import ReparseMeta
from tdpservice.search_indexes.reparse import clean_reparse, handle_datafiles


@pytest.fixture
def log_context():
    """Return a stubbed log context."""
    return {"user_id": 1, "action_flag": 1, "object_repr": "Test"}


@pytest.mark.django_db
def test_handle_datafiles_adds_reparse_and_queues(monkeypatch, stt, log_context):
    """Ensure datafiles are associated and queued for parsing."""
    meta_model = ReparseMeta.objects.create(db_backup_location="s3://backup")
    file_one = DataFileFactory(stt=stt, version=1)
    file_two = DataFileFactory(stt=stt, version=2)

    calls = []

    def fake_delay(file_id, reparse_id):
        calls.append((file_id, reparse_id))

    monkeypatch.setattr(
        "tdpservice.search_indexes.reparse.parser_task.parse.delay", fake_delay
    )

    handle_datafiles([file_one, file_two], meta_model, log_context)

    assert file_one.reparses.filter(pk=meta_model.pk).exists()
    assert file_two.reparses.filter(pk=meta_model.pk).exists()
    assert calls == [
        (file_one.pk, meta_model.pk),
        (file_two.pk, meta_model.pk),
    ]


@pytest.mark.django_db
def test_handle_datafiles_database_error(monkeypatch, stt, log_context):
    """Raise DatabaseError when reparse association fails."""
    meta_model = ReparseMeta.objects.create(db_backup_location="s3://backup")
    datafile = DataFileFactory(stt=stt, version=1)

    def raise_db_error(*args, **kwargs):
        raise DatabaseError("boom")

    monkeypatch.setattr(datafile, "save", raise_db_error)
    monkeypatch.setattr("tdpservice.search_indexes.reparse.log", lambda *a, **k: None)

    with pytest.raises(DatabaseError):
        handle_datafiles([datafile], meta_model, log_context)


@pytest.mark.django_db
def test_handle_datafiles_generic_error(monkeypatch, stt, log_context):
    """Raise generic exception when queueing fails."""
    meta_model = ReparseMeta.objects.create(db_backup_location="s3://backup")
    datafile = DataFileFactory(stt=stt, version=1)

    def raise_generic(*args, **kwargs):
        raise RuntimeError("boom")

    monkeypatch.setattr(
        "tdpservice.search_indexes.reparse.parser_task.parse.delay", raise_generic
    )
    monkeypatch.setattr("tdpservice.search_indexes.reparse.log", lambda *a, **k: None)

    with pytest.raises(RuntimeError):
        handle_datafiles([datafile], meta_model, log_context)


@pytest.mark.django_db
def test_clean_reparse_single_file_updates_meta(monkeypatch, stt):
    """Ensure clean_reparse populates metadata and queues datafiles."""
    datafile = DataFileFactory(stt=stt, version=1, quarter="Q2", year=2023)

    calls = {}

    def fake_handle(files, meta, context):
        calls["files"] = list(files)
        calls["meta"] = meta
        calls["context"] = context

    monkeypatch.setattr(
        "tdpservice.search_indexes.reparse.handle_datafiles", fake_handle
    )
    monkeypatch.setattr("tdpservice.search_indexes.reparse.log", lambda *a, **k: None)
    monkeypatch.setattr(
        "tdpservice.search_indexes.reparse.get_number_of_records", lambda files: 10
    )
    monkeypatch.setattr(
        "tdpservice.search_indexes.reparse.calculate_timeout",
        lambda count, total: datetime.timedelta(minutes=5),
    )
    monkeypatch.setattr("tdpservice.search_indexes.reparse.backup", lambda *a, **k: None)
    monkeypatch.setattr(
        "tdpservice.search_indexes.reparse.count_total_num_records",
        lambda *a, **k: 123,
    )
    monkeypatch.setattr(
        "tdpservice.search_indexes.reparse.delete_associated_models",
        lambda *a, **k: None,
    )
    monkeypatch.setattr(
        "tdpservice.search_indexes.reparse.get_log_context",
        lambda user: {"user_id": user.id},
    )
    monkeypatch.setattr(
        "tdpservice.search_indexes.reparse.assert_sequential_execution",
        lambda *a, **k: True,
    )

    clean_reparse([str(datafile.id)])

    meta = ReparseMeta.objects.latest("pk")
    assert meta.fiscal_year == 2023
    assert meta.fiscal_quarter == "Q2"
    assert meta.total_num_records_initial == 123
    assert meta.timeout_at == meta.created_at + datetime.timedelta(minutes=5)
    assert f"_rpv{meta.pk}_" in meta.db_backup_location
    assert meta.db_backup_location.startswith("/tmp/reparsing_backup")

    assert calls["meta"].pk == meta.pk
    assert calls["files"][0].pk == datafile.pk


@pytest.mark.django_db
def test_clean_reparse_requires_sequential_execution(monkeypatch, stt):
    """Raise when reparse is not sequentially safe."""
    datafile = DataFileFactory(stt=stt, version=1)

    monkeypatch.setattr("tdpservice.search_indexes.reparse.log", lambda *a, **k: None)
    monkeypatch.setattr(
        "tdpservice.search_indexes.reparse.assert_sequential_execution",
        lambda *a, **k: False,
    )

    with pytest.raises(Exception, match="Sequential execution required"):
        clean_reparse([str(datafile.id)])

    assert ReparseMeta.objects.count() == 0
