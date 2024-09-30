"""Test cases for reparse functions."""

import pytest
from tdpservice.parsers import util, parse
from tdpservice.parsers.test.factories import DataFileSummaryFactory
from tdpservice.search_indexes.management.commands import clean_and_reparse
from tdpservice.search_indexes.models.reparse_meta import ReparseMeta
from tdpservice.users.models import User

from django.contrib.admin.models import LogEntry, ADDITION
from django.db.utils import DatabaseError
from django.utils import timezone
from elasticsearch.exceptions import ElasticsearchException

from datetime import timedelta
import os
import time

@pytest.fixture
def cat4_edge_case_file(stt_user, stt):
    """Fixture for cat_4_edge_case.txt."""
    cat4_edge_case_file = util.create_test_datafile('cat_4_edge_case.txt', stt_user, stt)
    cat4_edge_case_file.year = 2024
    cat4_edge_case_file.quarter = 'Q1'
    cat4_edge_case_file.save()
    return cat4_edge_case_file

@pytest.fixture
def big_file(stt_user, stt):
    """Fixture for ADS.E2J.FTP1.TS06."""
    return util.create_test_datafile('ADS.E2J.FTP1.TS06', stt_user, stt)

@pytest.fixture
def small_ssp_section1_datafile(stt_user, stt):
    """Fixture for small_ssp_section1."""
    small_ssp_section1_datafile = util.create_test_datafile('small_ssp_section1.txt', stt_user,
                                                            stt, 'SSP Active Case Data')
    small_ssp_section1_datafile.year = 2024
    small_ssp_section1_datafile.quarter = 'Q1'
    small_ssp_section1_datafile.save()
    return small_ssp_section1_datafile

@pytest.fixture
def tribal_section_1_file(stt_user, stt):
    """Fixture for ADS.E2J.FTP4.TS06."""
    tribal_section_1_file = util.create_test_datafile('ADS.E2J.FTP1.TS142', stt_user, stt, "Tribal Active Case Data")
    tribal_section_1_file.year = 2022
    tribal_section_1_file.quarter = 'Q1'
    tribal_section_1_file.save()
    return tribal_section_1_file

@pytest.fixture
def dfs():
    """Fixture for DataFileSummary."""
    return DataFileSummaryFactory.build()

@pytest.fixture
def log_context():
    """Fixture for logger context."""
    system_user, created = User.objects.get_or_create(username='system')
    context = {'user_id': system_user.id,
               'action_flag': ADDITION,
               'object_repr': "Test Clean and Reparse"
               }
    return context

def parse_files(summary, f1, f2, f3, f4):
    """Parse all files."""
    summary.datafile = f1
    parse.parse_datafile(f1, summary)

    summary.datafile = f2
    parse.parse_datafile(f2, summary)

    summary.datafile = f3
    parse.parse_datafile(f3, summary)

    summary.datafile = f4
    parse.parse_datafile(f4, summary)
    f1.save()
    f2.save()
    f3.save()
    f4.save()
    return [f1.pk, f2.pk, f3.pk, f4.pk]

@pytest.mark.django_db
def test_count_total_num_records(log_context, dfs, cat4_edge_case_file, big_file,
                                 small_ssp_section1_datafile, tribal_section_1_file):
    """Count total number of records in DB."""
    parse_files(dfs, cat4_edge_case_file, big_file, small_ssp_section1_datafile, tribal_section_1_file)

    cmd = clean_and_reparse.Command()
    assert 3104 == cmd._count_total_num_records(log_context)
    cat4_edge_case_file.delete()
    assert 3096 == cmd._count_total_num_records(log_context)

@pytest.mark.django_db
def test_reparse_backup_succeed(log_context, dfs, cat4_edge_case_file, big_file, small_ssp_section1_datafile,
                                tribal_section_1_file):
    """Verify a backup is created with the correct size."""
    parse_files(dfs, cat4_edge_case_file, big_file, small_ssp_section1_datafile, tribal_section_1_file)

    cmd = clean_and_reparse.Command()
    file_name = "/tmp/test_reparse.pg"
    cmd._backup(file_name, log_context)
    time.sleep(10)

    file_size = os.path.getsize(file_name)
    assert file_size > 180000

@pytest.mark.django_db
def test_reparse_backup_fail(mocker, log_context, dfs, cat4_edge_case_file, big_file, small_ssp_section1_datafile,
                             tribal_section_1_file):
    """Verify a backup is created with the correct size."""
    parse_files(dfs, cat4_edge_case_file, big_file, small_ssp_section1_datafile, tribal_section_1_file)

    mocker.patch(
        'tdpservice.search_indexes.management.commands.clean_and_reparse.Command._backup',
        side_effect=Exception('Backup exception')
    )
    cmd = clean_and_reparse.Command()
    file_name = "/tmp/test_reparse.pg"
    with pytest.raises(Exception):
        cmd._backup(file_name, log_context)
        assert os.path.exists(file_name) is False
        exception_msg = LogEntry.objects.latest('pk').change_message
        assert exception_msg == ("Database backup FAILED. Clean and reparse NOT executed. Database "
                                 "and Elastic are CONSISTENT!")

@pytest.mark.parametrize(("new_indexes"), [
    (True),
    (False)
])
@pytest.mark.django_db
def test_delete_associated_models(log_context, new_indexes, dfs, cat4_edge_case_file, big_file,
                                  small_ssp_section1_datafile, tribal_section_1_file):
    """Verify all records and models are deleted."""
    ids = parse_files(dfs, cat4_edge_case_file, big_file, small_ssp_section1_datafile, tribal_section_1_file)

    cmd = clean_and_reparse.Command()
    assert 3104 == cmd._count_total_num_records(log_context)

    class Fake:
        pass
    fake_meta = Fake()
    cmd._delete_associated_models(fake_meta, ids, new_indexes, log_context)

    assert cmd._count_total_num_records(log_context) == 0

@pytest.mark.parametrize(("exc_msg, exception_type"), [
    (('Encountered a DatabaseError while deleting DataFileSummary from Postgres. The database '
      'and Elastic are INCONSISTENT! Restore the DB from the backup as soon as possible!'), DatabaseError),
    (('Caught generic exception while deleting DataFileSummary. The database and Elastic are INCONSISTENT! '
      'Restore the DB from the backup as soon as possible!'), Exception)
])
@pytest.mark.django_db
def test_delete_summaries_exceptions(mocker, log_context, exc_msg, exception_type):
    """Test summary exception handling."""
    mocker.patch(
        'tdpservice.search_indexes.management.commands.clean_and_reparse.Command._delete_summaries',
        side_effect=exception_type('Summary delete exception')
    )
    cmd = clean_and_reparse.Command()
    with pytest.raises(exception_type):
        cmd._delete_summaries([], log_context)
        exception_msg = LogEntry.objects.latest('pk').change_message
        assert exception_msg == exc_msg

@pytest.mark.parametrize(("exc_msg, exception_type"), [
    (('Elastic index creation FAILED. Clean and reparse NOT executed. '
      'Database is CONSISTENT, Elastic is INCONSISTENT!'), ElasticsearchException),
    (('Caught generic exception in _handle_elastic. Clean and reparse NOT executed. '
      'Database is CONSISTENT, Elastic is INCONSISTENT!'), Exception)
])
@pytest.mark.django_db
def test_handle_elastic_exceptions(mocker, log_context, exc_msg, exception_type):
    """Test summary exception handling."""
    mocker.patch(
        'tdpservice.search_indexes.management.commands.clean_and_reparse.Command._handle_elastic',
        side_effect=exception_type('Summary delete exception')
    )
    cmd = clean_and_reparse.Command()
    with pytest.raises(exception_type):
        cmd._handle_elastic([], True, log_context)
        exception_msg = LogEntry.objects.latest('pk').change_message
        assert exception_msg == exc_msg

@pytest.mark.parametrize(("exc_msg, exception_type"), [
    (('Elastic document delete failed for type {model}. The database and Elastic are INCONSISTENT! '
      'Restore the DB from the backup as soon as possible!'), ElasticsearchException),
    (('Encountered a DatabaseError while deleting records of type {model} from Postgres. The database '
      'and Elastic are INCONSISTENT! Restore the DB from the backup as soon as possible!'), DatabaseError),
    (('Caught generic exception while deleting records of type {model}. The database and Elastic are '
      'INCONSISTENT! Restore the DB from the backup as soon as possible!'), Exception)
])
@pytest.mark.django_db
def test_delete_records_exceptions(mocker, log_context, exc_msg, exception_type):
    """Test record exception handling."""
    mocker.patch(
        'tdpservice.search_indexes.management.commands.clean_and_reparse.Command._delete_records',
        side_effect=exception_type('Record delete exception')
    )
    cmd = clean_and_reparse.Command()
    with pytest.raises(exception_type):
        cmd._delete_records([], True, log_context)
        exception_msg = LogEntry.objects.latest('pk').change_message
        assert exception_msg == exc_msg

@pytest.mark.parametrize(("exc_msg, exception_type"), [
    (('Encountered a DatabaseError while deleting ParserErrors from Postgres. The database '
      'and Elastic are INCONSISTENT! Restore the DB from the backup as soon as possible!'), DatabaseError),
    (('Caught generic exception while deleting ParserErrors. The database and Elastic are INCONSISTENT! '
      'Restore the DB from the backup as soon as possible!'), Exception)
])
@pytest.mark.django_db
def test_delete_errors_exceptions(mocker, log_context, exc_msg, exception_type):
    """Test error exception handling."""
    mocker.patch(
        'tdpservice.search_indexes.management.commands.clean_and_reparse.Command._delete_errors',
        side_effect=exception_type('Error delete exception')
    )
    cmd = clean_and_reparse.Command()
    with pytest.raises(exception_type):
        cmd._delete_errors([], log_context)
        exception_msg = LogEntry.objects.latest('pk').change_message
        assert exception_msg == exc_msg

@pytest.mark.parametrize(("exc_msg, exception_type"), [
    (('Encountered a DatabaseError while re-creating datafiles. The database '
      'and Elastic are INCONSISTENT! Restore the DB from the backup as soon as possible!'), DatabaseError),
    (('Caught generic exception in _handle_datafiles. Database and Elastic are INCONSISTENT! '
      'Restore the DB from the backup as soon as possible!'), Exception)
])
@pytest.mark.django_db
def test_handle_files_exceptions(mocker, log_context, exc_msg, exception_type):
    """Test error exception handling."""
    mocker.patch(
        'tdpservice.search_indexes.management.commands.clean_and_reparse.Command._handle_datafiles',
        side_effect=exception_type('Files exception')
    )
    cmd = clean_and_reparse.Command()
    with pytest.raises(exception_type):
        cmd._handle_datafiles([], None, log_context)
        exception_msg = LogEntry.objects.latest('pk').change_message
        assert exception_msg == exc_msg

@pytest.mark.django_db
def test_timeout_calculation(log_context, dfs, cat4_edge_case_file, big_file, small_ssp_section1_datafile,
                             tribal_section_1_file):
    """Verify calculated timeout."""
    ids = parse_files(dfs, cat4_edge_case_file, big_file, small_ssp_section1_datafile, tribal_section_1_file)

    cmd = clean_and_reparse.Command()
    num_records = cmd._count_total_num_records(log_context)

    assert cmd._calculate_timeout(len(ids), num_records).seconds == 57

    assert cmd._calculate_timeout(len(ids), 50).seconds == 40

@pytest.mark.django_db
def test_reparse_dunce():
    """Test reparse no args."""
    cmd = clean_and_reparse.Command()
    assert None is cmd.handle()
    assert ReparseMeta.objects.count() == 0

@pytest.mark.django_db
def test_reparse_sequential(log_context):
    """Test reparse _assert_sequential_execution."""
    cmd = clean_and_reparse.Command()
    assert True is cmd._assert_sequential_execution(log_context)

    meta = ReparseMeta.objects.create(timeout_at=None)
    assert False is cmd._assert_sequential_execution(log_context)
    timeout_entry = LogEntry.objects.latest('pk')
    assert timeout_entry.change_message == ("The latest ReparseMeta model's (ID: 1) timeout_at field is None. Cannot "
                                            "safely execute reparse, please fix manually.")

    meta.timeout_at = timezone.now() + timedelta(seconds=100)
    meta.save()
    assert False is cmd._assert_sequential_execution(log_context)
    not_seq_entry = LogEntry.objects.latest('pk')
    assert not_seq_entry.change_message == ("A previous execution of the reparse command is RUNNING. "
                                            "Cannot execute in parallel, exiting.")

    meta.timeout_at = timezone.now()
    meta.save()
    assert True is cmd._assert_sequential_execution(log_context)
    timeout_entry = LogEntry.objects.latest('pk')
    assert timeout_entry.change_message == ("Previous reparse has exceeded the timeout. Allowing "
                                            "execution of the command.")

@pytest.mark.django_db()
def test_reparse_quarter_and_year(mocker, dfs, cat4_edge_case_file, big_file, small_ssp_section1_datafile,
                                  tribal_section_1_file):
    """Test reparse with year and quarter."""
    parse_files(dfs, cat4_edge_case_file, big_file, small_ssp_section1_datafile, tribal_section_1_file)
    cmd = clean_and_reparse.Command()

    mocker.patch(
        'tdpservice.scheduling.parser_task.parse',
        return_value=None
    )

    opts = {'fiscal_quarter': 'Q1', 'fiscal_year': 2021, 'testing': True}
    cmd.handle(**opts)

    latest = ReparseMeta.objects.select_for_update().latest("pk")
    assert latest.num_files_to_reparse == 1
    assert latest.num_records_deleted == 3073

@pytest.mark.django_db()
def test_reparse_quarter(mocker, dfs, cat4_edge_case_file, big_file, small_ssp_section1_datafile,
                         tribal_section_1_file):
    """Test reparse with quarter."""
    parse_files(dfs, cat4_edge_case_file, big_file, small_ssp_section1_datafile, tribal_section_1_file)
    cmd = clean_and_reparse.Command()

    mocker.patch(
        'tdpservice.scheduling.parser_task.parse',
        return_value=None
    )

    opts = {'fiscal_quarter': 'Q1', 'testing': True}
    cmd.handle(**opts)

    latest = ReparseMeta.objects.select_for_update().latest("pk")
    assert latest.num_files_to_reparse == 4
    assert latest.num_records_deleted == 3104

@pytest.mark.django_db()
def test_reparse_year(mocker, dfs, cat4_edge_case_file, big_file, small_ssp_section1_datafile,
                      tribal_section_1_file):
    """Test reparse year."""
    parse_files(dfs, cat4_edge_case_file, big_file, small_ssp_section1_datafile, tribal_section_1_file)
    cmd = clean_and_reparse.Command()

    mocker.patch(
        'tdpservice.scheduling.parser_task.parse',
        return_value=None
    )

    opts = {'fiscal_year': 2024, 'testing': True}
    cmd.handle(**opts)

    latest = ReparseMeta.objects.select_for_update().latest("pk")
    assert latest.num_files_to_reparse == 2
    assert latest.num_records_deleted == 27

@pytest.mark.django_db()
def test_reparse_all(mocker, dfs, cat4_edge_case_file, big_file, small_ssp_section1_datafile,
                     tribal_section_1_file):
    """Test reparse all."""
    parse_files(dfs, cat4_edge_case_file, big_file, small_ssp_section1_datafile, tribal_section_1_file)
    cmd = clean_and_reparse.Command()

    mocker.patch(
        'tdpservice.scheduling.parser_task.parse',
        return_value=None
    )

    opts = {'all': True, 'testing': True}
    cmd.handle(**opts)

    latest = ReparseMeta.objects.select_for_update().latest("pk")
    assert latest.num_files_to_reparse == 4
    assert latest.num_records_deleted == 3104

@pytest.mark.django_db()
def test_reparse_no_files(mocker):
    """Test reparse with no files in query."""
    cmd = clean_and_reparse.Command()

    mocker.patch(
        'tdpservice.scheduling.parser_task.parse',
        return_value=None
    )

    opts = {'fiscal_year': 2025, 'testing': True}
    res = cmd.handle(**opts)

    assert ReparseMeta.objects.count() == 0
    assert res is None
    assert LogEntry.objects.latest('pk').change_message == ("No files available for the selected Fiscal Year: 2025 and "
                                                            "Quarter: Q1-4. Nothing to do.")

@pytest.mark.django_db()
def test_mm_all_files_done():
    """Test meta model all files done."""
    meta_model = ReparseMeta.objects.create()
    assert ReparseMeta.assert_all_files_done(meta_model) is False

    meta_model.finished = True
    meta_model.files_completed = 1
    meta_model.num_files_to_reparse = 1
    assert ReparseMeta.assert_all_files_done(meta_model) is True

@pytest.mark.django_db()
def test_mm_increment_files_completed(big_file):
    """Test meta model increment files completed."""
    meta_model = ReparseMeta.objects.create(num_files_to_reparse=2, all=True)
    big_file.reparse_meta_models.add(meta_model)
    big_file.save()

    ReparseMeta.increment_files_completed(big_file.reparse_meta_models)
    meta_model = ReparseMeta.get_latest()
    assert meta_model.finished is False
    assert meta_model.files_completed == 1
    assert meta_model.files_failed == 0

    ReparseMeta.increment_files_completed(big_file.reparse_meta_models)
    meta_model = ReparseMeta.get_latest()
    assert meta_model.finished is True
    assert meta_model.files_completed == 2
    assert meta_model.files_failed == 0

    assert meta_model.success is True

    assert ReparseMeta.assert_all_files_done(meta_model) is True

@pytest.mark.django_db()
def test_mm_increment_files_failed(big_file):
    """Test meta model increment files failed."""
    meta_model = ReparseMeta.objects.create(num_files_to_reparse=2, all=True)
    big_file.reparse_meta_models.add(meta_model)
    big_file.save()

    ReparseMeta.increment_files_failed(big_file.reparse_meta_models)
    meta_model = ReparseMeta.get_latest()
    assert meta_model.finished is False
    assert meta_model.files_completed == 0
    assert meta_model.files_failed == 1

    ReparseMeta.increment_files_failed(big_file.reparse_meta_models)
    meta_model = ReparseMeta.get_latest()
    assert meta_model.finished is True
    assert meta_model.files_completed == 0
    assert meta_model.files_failed == 2

    assert meta_model.success is False

    assert ReparseMeta.assert_all_files_done(meta_model) is True

@pytest.mark.django_db()
def test_mm_increment_files_failed_and_passed(big_file):
    """Test meta model both increment failed and passed files."""
    meta_model = ReparseMeta.objects.create(num_files_to_reparse=2, all=True)
    big_file.reparse_meta_models.add(meta_model)
    big_file.save()

    ReparseMeta.increment_files_completed(big_file.reparse_meta_models)
    meta_model = ReparseMeta.get_latest()
    assert meta_model.finished is False
    assert meta_model.files_completed == 1
    assert meta_model.files_failed == 0

    ReparseMeta.increment_files_failed(big_file.reparse_meta_models)
    meta_model = ReparseMeta.get_latest()
    assert meta_model.finished is True
    assert meta_model.files_completed == 1
    assert meta_model.files_failed == 1

    assert meta_model.success is False

    assert ReparseMeta.assert_all_files_done(meta_model) is True

@pytest.mark.django_db()
def test_mm_increment_records_created(big_file):
    """Test meta model increment records created."""
    meta_model = ReparseMeta.objects.create(num_files_to_reparse=2, all=True)
    big_file.reparse_meta_models.add(meta_model)
    big_file.save()

    ReparseMeta.increment_records_created(big_file.reparse_meta_models, 500)
    meta_model = ReparseMeta.get_latest()
    assert meta_model.num_records_created == 500

    ReparseMeta.increment_records_created(big_file.reparse_meta_models, 888)
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
def test_mm_file_counts_match():
    """Test meta model file counts match."""
    meta_model = ReparseMeta.objects.create(num_files_to_reparse=2)
    assert ReparseMeta.file_counts_match(meta_model) is False

    meta_model.files_completed = 2
    assert ReparseMeta.file_counts_match(meta_model) is True

    meta_model.files_completed = 0
    meta_model.files_failed = 2
    assert ReparseMeta.file_counts_match(meta_model) is True

    meta_model.files_completed = 1
    meta_model.files_failed = 1
    assert ReparseMeta.file_counts_match(meta_model) is True
