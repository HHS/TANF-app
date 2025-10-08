"""Test cases for reparse functions."""

import os
import time
from datetime import timedelta

from django.conf import settings
from django.contrib.admin.models import ADDITION, LogEntry
from django.db.utils import DatabaseError
from django.utils import timezone

import pytest

from tdpservice.data_files.models import ReparseFileMeta
from tdpservice.parsers import util
from tdpservice.parsers.factory import ParserFactory
from tdpservice.parsers.test.factories import DataFileSummaryFactory
from tdpservice.scheduling.management.commands import backup_db
from tdpservice.search_indexes.management.commands import clean_and_reparse
from tdpservice.search_indexes.models.reparse_meta import ReparseMeta
from tdpservice.search_indexes.tasks import prettify_time_delta
from tdpservice.search_indexes.utils import (
    assert_sequential_execution,
    backup,
    calculate_timeout,
    count_total_num_records,
    delete_associated_models,
)
from tdpservice.users.models import User


@pytest.fixture
def cat4_edge_case_file(stt_user, stt):
    """Fixture for cat_4_edge_case.txt."""
    cat4_edge_case_file = util.create_test_datafile(
        "cat_4_edge_case.txt", stt_user, stt
    )
    cat4_edge_case_file.year = 2024
    cat4_edge_case_file.quarter = "Q1"
    cat4_edge_case_file.save()
    return cat4_edge_case_file


@pytest.fixture
def big_file(stt_user, stt):
    """Fixture for ADS.E2J.FTP1.TS06."""
    return util.create_test_datafile("ADS.E2J.FTP1.TS06", stt_user, stt)


@pytest.fixture
def small_ssp_section1_datafile(stt_user, stt):
    """Fixture for small_ssp_section1."""
    small_ssp_section1_datafile = util.create_test_datafile(
        "small_ssp_section1.txt", stt_user, stt, "SSP Active Case Data"
    )
    small_ssp_section1_datafile.year = 2024
    small_ssp_section1_datafile.quarter = "Q1"
    small_ssp_section1_datafile.save()
    return small_ssp_section1_datafile


@pytest.fixture
def tribal_section_1_file(stt_user, stt):
    """Fixture for ADS.E2J.FTP4.TS06."""
    tribal_section_1_file = util.create_test_datafile(
        "ADS.E2J.FTP1.TS142", stt_user, stt, "Tribal Active Case Data"
    )
    tribal_section_1_file.year = 2022
    tribal_section_1_file.quarter = "Q1"
    tribal_section_1_file.save()
    return tribal_section_1_file


@pytest.fixture
def dfs():
    """Fixture for DataFileSummary."""
    return DataFileSummaryFactory.build()


@pytest.fixture
def log_context():
    """Fixture for logger context."""
    system_user, created = User.objects.get_or_create(username="system")
    context = {
        "user_id": system_user.id,
        "action_flag": ADDITION,
        "object_repr": "Test Clean and Reparse",
    }
    return context


def parse_files(summary, f1, f2, f3, f4):
    """Parse all files."""
    summary.datafile = f1
    parser = ParserFactory.get_instance(
        datafile=f1, dfs=summary, section=f1.section, program_type=f1.program_type
    )
    parser.parse_and_validate()

    summary.datafile = f2
    parser = ParserFactory.get_instance(
        datafile=f2, dfs=summary, section=f2.section, program_type=f2.program_type
    )
    parser.parse_and_validate()

    summary.datafile = f3
    parser = ParserFactory.get_instance(
        datafile=f3, dfs=summary, section=f3.section, program_type=f3.program_type
    )
    parser.parse_and_validate()

    summary.datafile = f4
    parser = ParserFactory.get_instance(
        datafile=f4, dfs=summary, section=f4.section, program_type=f4.program_type
    )
    parser.parse_and_validate()

    f1.save()
    f2.save()
    f3.save()
    f4.save()
    return [f1.pk, f2.pk, f3.pk, f4.pk]


@pytest.mark.django_db
def test_count_total_num_records(
    log_context,
    dfs,
    cat4_edge_case_file,
    big_file,
    small_ssp_section1_datafile,
    tribal_section_1_file,
):
    """Count total number of records in DB."""
    parse_files(
        dfs,
        cat4_edge_case_file,
        big_file,
        small_ssp_section1_datafile,
        tribal_section_1_file,
    )

    assert 3104 == count_total_num_records(log_context)
    cat4_edge_case_file.delete()
    assert 3096 == count_total_num_records(log_context)


@pytest.mark.django_db
def test_reparse_backup_succeed(
    log_context,
    dfs,
    cat4_edge_case_file,
    big_file,
    small_ssp_section1_datafile,
    tribal_section_1_file,
):
    """Verify a backup is created with the correct size."""
    parse_files(
        dfs,
        cat4_edge_case_file,
        big_file,
        small_ssp_section1_datafile,
        tribal_section_1_file,
    )

    file_name = "/tmp/test_reparse.pg"
    backup(file_name, log_context)
    time.sleep(10)

    file_size = os.path.getsize(file_name)
    assert file_size > 180000


@pytest.mark.django_db
def test_reparse_backup_fail(
    mocker,
    log_context,
    dfs,
    cat4_edge_case_file,
    big_file,
    small_ssp_section1_datafile,
    tribal_section_1_file,
):
    """Verify a backup is created with the correct size."""
    parse_files(
        dfs,
        cat4_edge_case_file,
        big_file,
        small_ssp_section1_datafile,
        tribal_section_1_file,
    )

    mocker.patch(
        "tdpservice.search_indexes.utils.backup",
        side_effect=Exception("Backup exception"),
    )
    file_name = "/tmp/test_reparse.pg"
    with pytest.raises(Exception):
        backup(file_name, log_context)
        assert os.path.exists(file_name) is False
        exception_msg = LogEntry.objects.latest("pk").change_message
        assert exception_msg == (
            "Database backup FAILED. Clean and reparse NOT executed. Database "
            "is CONSISTENT!"
        )


@pytest.mark.django_db
def test_delete_associated_models(
    log_context,
    dfs,
    cat4_edge_case_file,
    big_file,
    small_ssp_section1_datafile,
    tribal_section_1_file,
):
    """Verify all records and models are deleted."""
    ids = parse_files(
        dfs,
        cat4_edge_case_file,
        big_file,
        small_ssp_section1_datafile,
        tribal_section_1_file,
    )

    assert 3104 == count_total_num_records(log_context)

    class Fake:
        pass

    fake_meta = Fake()
    delete_associated_models(fake_meta, ids, log_context)

    assert count_total_num_records(log_context) == 0


@pytest.mark.parametrize(
    ("exc_msg, exception_type"),
    [
        (
            (
                "Encountered a DatabaseError while deleting DataFileSummary from Postgres. The database "
                "is INCONSISTENT! Restore the DB from the backup as soon as possible!"
            ),
            DatabaseError,
        ),
        (
            (
                "Caught generic exception while deleting DataFileSummary. The database is INCONSISTENT! "
                "Restore the DB from the backup as soon as possible!"
            ),
            Exception,
        ),
    ],
)
@pytest.mark.django_db
def test_delete_summaries_exceptions(mocker, log_context, exc_msg, exception_type):
    """Test summary exception handling."""
    mocked_delete_summaries = mocker.patch(
        "tdpservice.search_indexes.utils.delete_summaries",
        side_effect=exception_type("Summary delete exception"),
    )
    with pytest.raises(exception_type):
        mocked_delete_summaries([], log_context)
        exception_msg = LogEntry.objects.latest("pk").change_message
        assert exception_msg == exc_msg


@pytest.mark.parametrize(
    ("exc_msg, exception_type"),
    [
        (
            (
                "Encountered a DatabaseError while deleting ParserErrors from Postgres. The database "
                "is INCONSISTENT! Restore the DB from the backup as soon as possible!"
            ),
            DatabaseError,
        ),
        (
            (
                "Caught generic exception while deleting ParserErrors. The database is INCONSISTENT! "
                "Restore the DB from the backup as soon as possible!"
            ),
            Exception,
        ),
    ],
)
@pytest.mark.django_db
def test_delete_errors_exceptions(mocker, log_context, exc_msg, exception_type):
    """Test error exception handling."""
    mocked_delete_errors = mocker.patch(
        "tdpservice.search_indexes.utils.delete_errors",
        side_effect=exception_type("Error delete exception"),
    )
    with pytest.raises(exception_type):
        mocked_delete_errors([], log_context)
        exception_msg = LogEntry.objects.latest("pk").change_message
        assert exception_msg == exc_msg


@pytest.mark.parametrize(
    ("exc_msg, exception_type"),
    [
        (
            (
                "Encountered a DatabaseError while re-creating datafiles. The database "
                "is INCONSISTENT! Restore the DB from the backup as soon as possible!"
            ),
            DatabaseError,
        ),
        (
            (
                "Caught generic exception in _handle_datafiles. Database is INCONSISTENT! "
                "Restore the DB from the backup as soon as possible!"
            ),
            Exception,
        ),
    ],
)
@pytest.mark.django_db
def test_handle_files_exceptions(mocker, log_context, exc_msg, exception_type):
    """Test error exception handling."""
    mocked_handle_datafiles = mocker.patch(
        "tdpservice.search_indexes.reparse.handle_datafiles",
        side_effect=exception_type("Files exception"),
    )
    with pytest.raises(exception_type):
        mocked_handle_datafiles([], None, log_context)
        exception_msg = LogEntry.objects.latest("pk").change_message
        assert exception_msg == exc_msg


@pytest.mark.django_db
def test_timeout_calculation(
    log_context,
    dfs,
    cat4_edge_case_file,
    big_file,
    small_ssp_section1_datafile,
    tribal_section_1_file,
):
    """Verify calculated timeout."""
    ids = parse_files(
        dfs,
        cat4_edge_case_file,
        big_file,
        small_ssp_section1_datafile,
        tribal_section_1_file,
    )

    num_records = count_total_num_records(log_context)

    assert calculate_timeout(len(ids), num_records).seconds == 43

    assert calculate_timeout(len(ids), 50).seconds == 40


@pytest.mark.django_db
def test_reparse_dunce():
    """Test reparse no args."""
    cmd = clean_and_reparse.Command()
    assert None is cmd.handle()
    assert ReparseMeta.objects.count() == 0


@pytest.mark.django_db
def test_reparse_sequential(log_context, big_file):
    """Test reparse _assert_sequential_execution."""
    assert True is assert_sequential_execution(log_context)

    meta = ReparseMeta.objects.create(timeout_at=None)
    assert False is assert_sequential_execution(log_context)
    timeout_entry = LogEntry.objects.latest("pk")
    assert timeout_entry.change_message == (
        f"The latest ReparseMeta model's (ID: {meta.pk}) timeout_at field is None. Cannot "
        "safely execute reparse, please fix manually."
    )

    big_file.reparses.add(meta)
    meta.timeout_at = timezone.now() + timedelta(seconds=100)
    meta.save()
    assert False is assert_sequential_execution(log_context)
    not_seq_entry = LogEntry.objects.latest("pk")
    assert not_seq_entry.change_message == (
        "A previous execution of the reparse command is RUNNING. "
        "Cannot execute in parallel, exiting."
    )

    meta.timeout_at = timezone.now()
    meta.save()

    assert True is assert_sequential_execution(log_context)
    timeout_entry = LogEntry.objects.latest("pk")
    assert timeout_entry.change_message == (
        "Previous reparse has exceeded the timeout. Allowing "
        "execution of the command."
    )


@pytest.mark.django_db()
def test_reparse_quarter_and_year(
    mocker,
    dfs,
    cat4_edge_case_file,
    big_file,
    small_ssp_section1_datafile,
    tribal_section_1_file,
):
    """Test reparse with year and quarter."""
    parse_files(
        dfs,
        cat4_edge_case_file,
        big_file,
        small_ssp_section1_datafile,
        tribal_section_1_file,
    )
    cmd = clean_and_reparse.Command()

    mocker.patch("tdpservice.scheduling.parser_task.parse", return_value=None)

    opts = {"fiscal_quarter": "Q1", "fiscal_year": 2021, "testing": True}
    cmd.handle(**opts)

    latest = ReparseMeta.objects.select_for_update().latest("pk")
    assert latest.num_files == 1
    assert latest.num_records_deleted == 3073


@pytest.mark.django_db()
def test_reparse_quarter(
    mocker,
    dfs,
    cat4_edge_case_file,
    big_file,
    small_ssp_section1_datafile,
    tribal_section_1_file,
):
    """Test reparse with quarter."""
    parse_files(
        dfs,
        cat4_edge_case_file,
        big_file,
        small_ssp_section1_datafile,
        tribal_section_1_file,
    )
    cmd = clean_and_reparse.Command()

    mocker.patch("tdpservice.scheduling.parser_task.parse", return_value=None)

    opts = {"fiscal_quarter": "Q1", "testing": True}
    cmd.handle(**opts)

    latest = ReparseMeta.objects.select_for_update().latest("pk")
    assert latest.num_files == 4
    assert latest.num_records_deleted == 3104


@pytest.mark.django_db()
def test_reparse_year(
    mocker,
    dfs,
    cat4_edge_case_file,
    big_file,
    small_ssp_section1_datafile,
    tribal_section_1_file,
):
    """Test reparse year."""
    parse_files(
        dfs,
        cat4_edge_case_file,
        big_file,
        small_ssp_section1_datafile,
        tribal_section_1_file,
    )
    cmd = clean_and_reparse.Command()

    mocker.patch("tdpservice.scheduling.parser_task.parse", return_value=None)

    opts = {"fiscal_year": 2024, "testing": True}
    cmd.handle(**opts)

    latest = ReparseMeta.objects.select_for_update().latest("pk")
    assert latest.num_files == 2
    assert latest.num_records_deleted == 27


@pytest.mark.django_db()
def test_reparse_all(
    mocker,
    dfs,
    cat4_edge_case_file,
    big_file,
    small_ssp_section1_datafile,
    tribal_section_1_file,
):
    """Test reparse all."""
    parse_files(
        dfs,
        cat4_edge_case_file,
        big_file,
        small_ssp_section1_datafile,
        tribal_section_1_file,
    )
    cmd = clean_and_reparse.Command()

    mocker.patch("tdpservice.scheduling.parser_task.parse", return_value=None)

    opts = {"all": True, "testing": True}
    cmd.handle(**opts)

    latest = ReparseMeta.objects.select_for_update().latest("pk")
    assert latest.num_files == 4
    assert latest.num_records_deleted == 3104


@pytest.mark.django_db()
def test_reparse_no_files(mocker):
    """Test reparse with no files in query."""
    cmd = clean_and_reparse.Command()

    mocker.patch("tdpservice.scheduling.parser_task.parse", return_value=None)

    opts = {"fiscal_year": 2025, "testing": True}
    res = cmd.handle(**opts)

    assert ReparseMeta.objects.count() == 0
    assert res is None
    assert LogEntry.objects.latest("pk").change_message == (
        "No files available for the selected Fiscal Year: 2025 and "
        "Quarter: Q1-4. Nothing to do."
    )


@pytest.mark.django_db()
def test_mm_all_files_done(big_file):
    """Test meta model all files done."""
    meta_model = ReparseMeta.objects.create()
    big_file.reparses.add(meta_model)
    assert ReparseMeta.assert_all_files_done(meta_model) is False

    fm = ReparseFileMeta.objects.get(
        data_file_id=big_file.pk, reparse_meta_id=meta_model.pk
    )
    fm.finished = True
    fm.save()
    assert ReparseMeta.assert_all_files_done(meta_model) is True


@pytest.mark.django_db()
def test_mm_files_completed(big_file):
    """Test meta model increment files completed."""
    meta_model = ReparseMeta.objects.create(all=True)
    big_file.reparses.add(meta_model)
    big_file.save()

    meta_model = ReparseMeta.get_latest()
    assert meta_model.is_finished is False
    assert meta_model.num_files == 1
    assert meta_model.num_files_completed == 0
    assert meta_model.num_files_failed == 0
    assert ReparseMeta.assert_all_files_done(meta_model) is False

    fm = ReparseFileMeta.objects.get(
        data_file_id=big_file.pk, reparse_meta_id=meta_model.pk
    )
    fm.finished = True
    fm.success = True
    fm.save()
    meta_model = ReparseMeta.get_latest()
    assert meta_model.is_finished is True
    assert meta_model.num_files == 1
    assert meta_model.num_files_completed == 1
    assert meta_model.num_files_failed == 0

    assert meta_model.is_success is True

    assert ReparseMeta.assert_all_files_done(meta_model) is True


@pytest.mark.django_db()
def test_mm_files_failed(big_file):
    """Test meta model increment files failed."""
    meta_model = ReparseMeta.objects.create(all=True)
    big_file.reparses.add(meta_model)
    big_file.save()

    meta_model = ReparseMeta.get_latest()
    assert meta_model.is_finished is False
    assert meta_model.num_files_completed == 0
    assert meta_model.num_files_failed == 0
    assert ReparseMeta.assert_all_files_done(meta_model) is False

    fm = ReparseFileMeta.objects.get(
        data_file_id=big_file.pk, reparse_meta_id=meta_model.pk
    )
    fm.finished = True
    fm.save()
    meta_model = ReparseMeta.get_latest()
    assert meta_model.is_finished is True
    assert meta_model.num_files_completed == 1
    assert meta_model.num_files_failed == 1

    assert meta_model.is_success is False

    assert ReparseMeta.assert_all_files_done(meta_model) is True


@pytest.mark.django_db()
def test_mm_increment_records_created(big_file):
    """Test meta model increment records created."""
    meta_model = ReparseMeta.objects.create(all=True)
    big_file.reparses.add(meta_model)
    big_file.save()

    meta_model = ReparseMeta.get_latest()
    assert meta_model.num_records_created == 0

    fm = ReparseFileMeta.objects.get(
        data_file_id=big_file.pk, reparse_meta_id=meta_model.pk
    )
    fm.finished = True
    fm.success = True
    fm.num_records_created = 1388
    fm.save()
    meta_model = ReparseMeta.get_latest()
    assert meta_model.num_records_created == 1388


@pytest.mark.django_db()
def test_mm_get_latest():
    """Test get latest meta model."""
    assert ReparseMeta.get_latest() is None
    meta1 = ReparseMeta.objects.create()
    assert ReparseMeta.get_latest() == meta1

    ReparseMeta.objects.create()
    assert ReparseMeta.get_latest() != meta1


@pytest.mark.django_db()
def test_mm_file_counts_match(big_file):
    """Test meta model file counts match."""
    meta_model = ReparseMeta.objects.create()
    big_file.reparses.add(meta_model)
    big_file.save()
    assert ReparseMeta.file_counts_match(meta_model) is False

    fm = ReparseFileMeta.objects.get(
        data_file_id=big_file.pk, reparse_meta_id=meta_model.pk
    )
    fm.finished = True
    fm.save()
    assert ReparseMeta.file_counts_match(meta_model) is True


@pytest.mark.django_db
def test_prettify_time_delta():
    """Test prettify_time_delta."""
    start = timezone.now()
    end = start + timedelta(seconds=100)

    assert prettify_time_delta(start.timestamp(), end.timestamp()) == (1, 40)


@pytest.mark.django_db
def test_db_backup_cloud(mocker):
    """Test DB backup fail without localstack."""
    settings.USE_LOCALSTACK = False

    cmd = backup_db.Command()
    opts = {"file": "fake_file.pg"}

    with pytest.raises(Exception):
        cmd.handle(**opts)
    settings.USE_LOCALSTACK = True


@pytest.mark.django_db()
def test_reparse_finished_success_false_before_file_queue(big_file):
    """Test is_finished and is_success are False if no files added."""
    meta_model = ReparseMeta.objects.create()
    assert meta_model.is_finished is False
    assert meta_model.is_success is False

    big_file.reparses.add(meta_model)
    big_file.save()
    assert meta_model.is_finished is False
    assert meta_model.is_success is False

    fm = ReparseFileMeta.objects.get(
        data_file_id=big_file.pk, reparse_meta_id=meta_model.pk
    )
    fm.finished = True
    fm.save()
    assert meta_model.is_finished is True
    assert meta_model.is_success is False

    fm.success = True
    fm.save()
    assert meta_model.is_finished is True
    assert meta_model.is_success is True
