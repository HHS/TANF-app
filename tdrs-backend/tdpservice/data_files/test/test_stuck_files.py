"""Test the get_stuck_files function."""


import pytest
from datetime import timedelta
from django.utils import timezone
from django.contrib.admin.models import LogEntry
from tdpservice.data_files.models import DataFile
from tdpservice.email.helpers.data_file import send_stuck_file_email
from tdpservice.parsers.models import DataFileSummary
from tdpservice.data_files.tasks import get_stuck_files
from tdpservice.parsers.test.factories import ParsingFileFactory, DataFileSummaryFactory, ReparseMetaFactory


def _time_ago(hours=0, minutes=0, seconds=0):
    return timezone.now() - timedelta(hours=hours, minutes=minutes, seconds=seconds)


def make_datafile(stt_user, stt, version):
    """Create a test data file with default params."""
    datafile = ParsingFileFactory.create(
        quarter=DataFile.Quarter.Q1, section=DataFile.Section.ACTIVE_CASE_DATA,
        year=2023, version=version, user=stt_user, stt=stt
    )
    return datafile


def make_summary(datafile, status):
    """Create a test data file summary given a file and status."""
    return DataFileSummaryFactory.create(
        datafile=datafile,
        status=status,
    )


def make_reparse_meta():
    """Create a test reparse meta model."""
    return ReparseMetaFactory.create(
        timeout_at=_time_ago(hours=1)
    )


@pytest.mark.django_db
def test_find_pending_submissions__none_stuck(stt_user, stt):
    """Finds no stuck files."""
    # an accepted standard submission, more than an hour old
    df1 = make_datafile(stt_user, stt, 1)
    df1.created_at = _time_ago(hours=2)
    df1.save()
    make_summary(df1, DataFileSummary.Status.ACCEPTED)

    # an accepted reparse submission, past the timeout
    df2 = make_datafile(stt_user, stt, 2)
    df2.created_at = _time_ago(hours=1)
    df2.save()
    make_summary(df2, DataFileSummary.Status.ACCEPTED)
    rpm = make_reparse_meta()
    df2.reparses.add(rpm, through_defaults={'finished': True, 'success': True})

    # a pending standard submission, less than an hour old
    df3 = make_datafile(stt_user, stt, 3)
    df3.created_at = _time_ago(minutes=40)
    df3.save()
    make_summary(df3, DataFileSummary.Status.PENDING)

    stuck_files = get_stuck_files()
    assert stuck_files.count() == 0


@pytest.mark.django_db
def test_find_pending_submissions__non_reparse_stuck(stt_user, stt):
    """Finds standard upload/submission stuck in Pending."""
    # a pending standard submission, more than an hour old
    df1 = make_datafile(stt_user, stt, 1)
    df1.created_at = _time_ago(hours=2)
    df1.save()
    make_summary(df1, DataFileSummary.Status.PENDING)

    # an accepted reparse submission, past the timeout
    df2 = make_datafile(stt_user, stt, 2)
    df2.created_at = _time_ago(hours=1)
    df2.save()
    make_summary(df2, DataFileSummary.Status.ACCEPTED)
    rpm = make_reparse_meta()
    df2.reparses.add(rpm, through_defaults={'finished': True, 'success': True})

    stuck_files = get_stuck_files()
    assert stuck_files.count() == 1
    assert stuck_files.first().pk == df1.pk


@pytest.mark.django_db
def test_find_pending_submissions__non_reparse_stuck__no_dfs(stt_user, stt):
    """Finds standard upload/submission stuck in Pending."""
    # a standard submission with no summary
    df1 = make_datafile(stt_user, stt, 1)
    df1.created_at = _time_ago(hours=2)
    df1.save()

    # an accepted reparse submission, past the timeout
    df2 = make_datafile(stt_user, stt, 2)
    df2.created_at = _time_ago(hours=1)
    df2.save()
    make_summary(df2, DataFileSummary.Status.ACCEPTED)
    rpm = make_reparse_meta()
    df2.reparses.add(rpm, through_defaults={'finished': True, 'success': True})

    stuck_files = get_stuck_files()
    assert stuck_files.count() == 1
    assert stuck_files.first().pk == df1.pk


@pytest.mark.django_db
def test_find_pending_submissions__reparse_stuck(stt_user, stt):
    """Finds a reparse submission stuck in pending, past the timeout."""
    # an accepted standard submission, more than an hour old
    df1 = make_datafile(stt_user, stt, 1)
    df1.created_at = _time_ago(hours=2)
    df1.save()
    make_summary(df1, DataFileSummary.Status.ACCEPTED)

    # a pending reparse submission, past the timeout
    df2 = make_datafile(stt_user, stt, 2)
    df2.created_at = _time_ago(hours=1)
    df2.save()
    make_summary(df2, DataFileSummary.Status.PENDING)
    rpm = make_reparse_meta()
    df2.reparses.add(rpm, through_defaults={'finished': False, 'success': False})

    stuck_files = get_stuck_files()
    assert stuck_files.count() == 1
    assert stuck_files.first().pk == df2.pk


@pytest.mark.django_db
def test_find_pending_submissions__reparse_stuck__no_dfs(stt_user, stt):
    """Finds a reparse submission stuck in pending, past the timeout."""
    # an accepted standard submission, more than an hour old
    df1 = make_datafile(stt_user, stt, 1)
    df1.created_at = _time_ago(hours=2)
    df1.save()
    make_summary(df1, DataFileSummary.Status.ACCEPTED)

    # a reparse submission with no summary, past the timeout
    df2 = make_datafile(stt_user, stt, 2)
    df2.created_at = _time_ago(hours=1)
    df2.save()
    rpm = make_reparse_meta()
    df2.reparses.add(rpm, through_defaults={'finished': False, 'success': False})

    stuck_files = get_stuck_files()
    assert stuck_files.count() == 1
    assert stuck_files.first().pk == df2.pk


@pytest.mark.django_db
def test_find_pending_submissions__reparse_and_non_reparse_stuck(stt_user, stt):
    """Finds stuck submissions, both reparse and standard parse."""
    # a pending standard submission, more than an hour old
    df1 = make_datafile(stt_user, stt, 1)
    df1.created_at = _time_ago(hours=2)
    df1.save()
    make_summary(df1, DataFileSummary.Status.PENDING)

    # a pending reparse submission, past the timeout
    df2 = make_datafile(stt_user, stt, 2)
    df2.created_at = _time_ago(hours=1)
    df2.save()
    make_summary(df2, DataFileSummary.Status.PENDING)
    rpm = make_reparse_meta()
    df2.reparses.add(rpm, through_defaults={'finished': False, 'success': False})

    stuck_files = get_stuck_files()
    assert stuck_files.count() == 2
    for f in stuck_files:
        assert f.pk in (df1.pk, df2.pk)


@pytest.mark.django_db
def test_find_pending_submissions__reparse_and_non_reparse_stuck_no_dfs(stt_user, stt):
    """Finds stuck submissions, both reparse and standard parse."""
    # a pending standard submission, more than an hour old
    df1 = make_datafile(stt_user, stt, 1)
    df1.created_at = _time_ago(hours=2)
    df1.save()

    # a pending reparse submission, past the timeout
    df2 = make_datafile(stt_user, stt, 2)
    df2.created_at = _time_ago(hours=1)
    df2.save()
    rpm = make_reparse_meta()
    df2.reparses.add(rpm, through_defaults={'finished': False, 'success': False})

    stuck_files = get_stuck_files()
    assert stuck_files.count() == 2
    for f in stuck_files:
        assert f.pk in (df1.pk, df2.pk)


@pytest.mark.django_db
def test_find_pending_submissions__old_reparse_stuck__new_not_stuck(stt_user, stt):
    """Finds no stuck files, as the new parse is successful."""
    # a pending standard submission, more than an hour old
    df1 = make_datafile(stt_user, stt, 1)
    df1.created_at = _time_ago(hours=2)
    df1.save()
    dfs1 = make_summary(df1, DataFileSummary.Status.PENDING)

    # reparse fails the first time
    rpm1 = make_reparse_meta()
    df1.reparses.add(rpm1, through_defaults={'finished': False, 'success': False})

    stuck_files = get_stuck_files()
    assert stuck_files.count() == 1

    # reparse again, succeeds this time
    dfs1.delete()  # reparse deletes the original dfs and creates the new one
    make_summary(df1, DataFileSummary.Status.ACCEPTED)

    rpm2 = make_reparse_meta()
    df1.reparses.add(rpm2, through_defaults={'finished': True, 'success': True})

    stuck_files = get_stuck_files()
    assert stuck_files.count() == 0


@pytest.mark.django_db
def test_find_pending_submissions__new_reparse_stuck__old_not_stuck(stt_user, stt):
    """Finds files stuck from the new reparse, even though the old one was successful."""
    # file rejected on first upload
    df1 = make_datafile(stt_user, stt, 1)
    df1.created_at = _time_ago(hours=2)
    df1.save()
    dfs1 = make_summary(df1, DataFileSummary.Status.REJECTED)

    # reparse succeeds
    rpm1 = make_reparse_meta()
    df1.reparses.add(rpm1, through_defaults={'finished': True, 'success': True})

    # reparse again, fails this time
    dfs1.delete()  # reparse deletes the original dfs and creates the new one
    DataFileSummary.objects.create(
        datafile=df1,
        status=DataFileSummary.Status.PENDING,
    )

    rpm2 = make_reparse_meta()
    df1.reparses.add(rpm2, through_defaults={'finished': False, 'success': False})

    stuck_files = get_stuck_files()
    assert stuck_files.count() == 1
    assert stuck_files.first().pk == df1.pk

@pytest.mark.django_db
def test_send_stuck_file_email(mocker):
    """Test send_stuck_file_email."""
    mocker.patch(
        'tdpservice.email.email.automated_email',
        return_value=True
    )

    send_stuck_file_email([], ["recipient"])
    entries = LogEntry.objects.all().order_by('pk')
    assert len(entries) == 4
    assert entries[0].change_message == ("Emailing stuck files to SysAdmins: ['recipient']")
