"""Test cases for reparse functions."""

import pytest
from tdpservice.parsers import util, parse
from tdpservice.parsers.test.factories import DataFileSummaryFactory
from tdpservice.search_indexes.management.commands import clean_and_reparse
from tdpservice.search_indexes.models.reparse_meta import ReparseMeta
from tdpservice.users.models import User

from django.contrib.admin.models import LogEntry, ADDITION
from django.utils import timezone

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
def test_reparse_backup(log_context, dfs, cat4_edge_case_file, big_file, small_ssp_section1_datafile,
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
def test_delete_associated_models(log_context, dfs, cat4_edge_case_file, big_file, small_ssp_section1_datafile,
                                  tribal_section_1_file):
    """Verify all records and models are deleted."""
    ids = parse_files(dfs, cat4_edge_case_file, big_file, small_ssp_section1_datafile, tribal_section_1_file)

    cmd = clean_and_reparse.Command()
    assert 3104 == cmd._count_total_num_records(log_context)

    class Fake:
        pass
    fake_meta = Fake()
    cmd._delete_associated_models(fake_meta, ids, True, log_context)

    assert cmd._count_total_num_records(log_context) == 0

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

################################
# The function below doesn't work. This is because the command kicks off the parser task which tries to query the DB for
# the file to parse. But Pytest segregates the DB changes to the test (even when transactions are disbled) which leads
# the parser task to fail because it cannot query the DataFile model. I couldn't find a way around this issue.
################################

# @pytest.mark.django_db(transaction=False)
# def test_reparse_all(log_context, dfs, cat4_edge_case_file, big_file, small_ssp_section1_datafile,
#                              tribal_section_1_file):
#     """Test reparse no args."""
#     ids = parse_files(dfs, cat4_edge_case_file, big_file, small_ssp_section1_datafile, tribal_section_1_file)
#     cmd = clean_and_reparse.Command()
#     print(f"\n\nPKS: {ids}\n\n")

#     opts = {'all': True, 'test': True}
#     cmd.handle(**opts)
#     done = False
#     timeout = 0
#     while (not done or timeout == 30):
#         timeout += 1
#         time.sleep(1)
#         latest = ReparseMeta.objects.latest('pk')
#         done = latest.finished

#     latest = ReparseMeta.objects.select_for_update().latest("pk")
#     assert latest.success == True
#     assert latest.num_files_to_reparse == len(ids)
#     assert latest.files_completed == len(ids)
#     assert latest.files_failed == 0
#     assert latest.num_records_deleted == latest.num_records_created
#     assert latest.total_num_records_initial == latest.total_num_records_post
