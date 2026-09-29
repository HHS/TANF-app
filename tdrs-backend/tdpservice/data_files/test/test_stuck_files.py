"""Test stuck file notification queries and rendering."""

from datetime import timedelta

from django.conf import settings
from django.contrib.admin.models import LogEntry
from django.core import mail
from django.utils import timezone

import pytest

from tdpservice.data_files.enums import SubmissionState
from tdpservice.data_files.models import DataFile
from tdpservice.data_files.tasks import (
    get_current_fiscal_year,
    get_stale_lifecycle_files,
    get_stuck_files,
    mark_stale_files_stuck,
)
from tdpservice.email.helpers.data_file import send_stuck_file_email
from tdpservice.parsers.models import DataFileSummary
from tdpservice.parsers.test.factories import (
    DataFileSummaryFactory,
    ParsingFileFactory,
    ReparseMetaFactory,
)


def make_datafile(stt_user, stt, version, state=SubmissionState.UPLOADED, year=None):
    """Create a test data file with default params."""
    return ParsingFileFactory.create(
        quarter=DataFile.Quarter.Q1,
        section=DataFile.Section.ACTIVE_CASE_DATA,
        year=year or get_current_fiscal_year(),
        version=version,
        user=stt_user,
        stt=stt,
        state=state,
    )


def make_summary(datafile, status):
    """Create a test data file summary given a file and status."""
    return DataFileSummaryFactory.create(
        datafile=datafile,
        status=status,
    )


def set_created_at(datafile, created_at):
    """Set legacy creation and lifecycle timestamps for stale-query tests."""
    DataFile.objects.filter(pk=datafile.pk).update(
        created_at=created_at,
        state_changed_at=created_at,
    )


@pytest.fixture(autouse=True)
def production_stale_timeout(settings):
    """Keep day-based tests independent from any E2E process environment."""
    settings.STALE_PARSE_TIMEOUT_SECONDS = 24 * 60 * 60


def test_stale_file_checker_is_scheduled():
    """Register the stale checker with Celery beat."""
    schedule = settings.CELERY_BEAT_SCHEDULE["Mark Stale Data Files Stuck"]
    route = settings.CELERY_TASK_ROUTES[
        "tdpservice.data_files.tasks.mark_stale_files_stuck"
    ]

    assert schedule["task"] == "tdpservice.data_files.tasks.mark_stale_files_stuck"
    assert route["queue"] == settings.CELERY_LIFECYCLE_QUEUE


@pytest.mark.django_db
def test_stale_timeout_can_be_shortened_for_browser_testing(stt_user, stt, settings):
    """Honor the environment-specific timeout without changing production's day."""
    settings.STALE_PARSE_TIMEOUT_SECONDS = 60
    datafile = make_datafile(
        stt_user,
        stt,
        1,
        state=SubmissionState.PARSE_STARTED,
    )
    set_created_at(datafile, timezone.now() - timedelta(seconds=61))

    assert list(get_stale_lifecycle_files().values_list("pk", flat=True)) == [
        datafile.pk
    ]


@pytest.mark.django_db
def test_stale_timeout_can_be_supplied_by_task_caller(stt_user, stt):
    """Allow an accelerated task run without changing production settings."""
    datafile = make_datafile(
        stt_user,
        stt,
        1,
        state=SubmissionState.PARSE_STARTED,
    )
    set_created_at(datafile, timezone.now() - timedelta(seconds=61))

    marked_count = mark_stale_files_stuck(timeout_seconds=60)

    datafile.refresh_from_db()
    assert marked_count == 1
    assert datafile.state == SubmissionState.STUCK


@pytest.mark.django_db
def test_stuck_current_fiscal_year_file_is_included(stt_user, stt):
    """Finds current fiscal year files explicitly marked stuck."""
    datafile = make_datafile(
        stt_user,
        stt,
        1,
        state=SubmissionState.STUCK,
    )

    stuck_files = get_stuck_files()

    assert list(stuck_files.values_list("pk", flat=True)) == [datafile.pk]


@pytest.mark.django_db
@pytest.mark.parametrize("summary_status", [None, DataFileSummary.Status.PENDING])
def test_non_stuck_current_fy_missing_or_pending_summary_is_excluded(
    stt_user,
    stt,
    summary_status,
):
    """Ignore legacy summary conditions unless the lifecycle state is STUCK."""
    stuck_file = make_datafile(
        stt_user,
        stt,
        1,
        state=SubmissionState.STUCK,
    )
    non_stuck_file = make_datafile(
        stt_user,
        stt,
        2,
        state=SubmissionState.PARSE_STARTED,
    )
    if summary_status is not None:
        make_summary(non_stuck_file, summary_status)

    stuck_files = get_stuck_files()

    assert list(stuck_files.values_list("pk", flat=True)) == [stuck_file.pk]


@pytest.mark.django_db
@pytest.mark.parametrize(
    ("state", "is_stale_eligible"),
    [
        (SubmissionState.UPLOADED, True),
        (SubmissionState.VIRUS_SCAN_STARTED, True),
        (SubmissionState.VIRUS_SCAN_COMPLETED, True),
        (SubmissionState.REPARSE_REQUESTED, True),
        (SubmissionState.PARSE_STARTED, True),
        (SubmissionState.VIRUS_SCAN_FAILED, False),
        (SubmissionState.PARSE_FAILED, False),
        (SubmissionState.PARSED_WITH_ERRORS, False),
        (SubmissionState.PARSE_COMPLETED, False),
        (SubmissionState.STUCK, False),
        (SubmissionState.COMPLETED, False),
        (SubmissionState.CANCELED, False),
    ],
)
def test_stale_lifecycle_state_matrix(stt_user, stt, state, is_stale_eligible):
    """Evaluate every lifecycle state above and below the stale threshold."""
    now = timezone.now()
    old_file = make_datafile(stt_user, stt, 1, state=state)
    set_created_at(old_file, now - timedelta(days=1, minutes=1))
    recent_file = make_datafile(stt_user, stt, 2, state=state)
    set_created_at(recent_file, now - timedelta(hours=23))

    stale_file_ids = set(
        get_stale_lifecycle_files(now=now).values_list("pk", flat=True)
    )

    expected_ids = {old_file.pk} if is_stale_eligible else set()
    assert stale_file_ids == expected_ids
    assert recent_file.pk not in stale_file_ids


@pytest.mark.django_db
@pytest.mark.parametrize("summary_status", [None, DataFileSummary.Status.PENDING])
def test_stale_parse_is_ready_to_be_marked_stuck(
    stt_user,
    stt,
    summary_status,
):
    """Finds parses with missing or PENDING summaries after one day."""
    datafile = make_datafile(
        stt_user,
        stt,
        1,
        state=SubmissionState.PARSE_STARTED,
    )
    set_created_at(datafile, timezone.now() - timedelta(days=1, minutes=1))
    if summary_status is not None:
        make_summary(datafile, summary_status)

    stale_files = get_stale_lifecycle_files()

    assert list(stale_files.values_list("pk", flat=True)) == [datafile.pk]


@pytest.mark.django_db
@pytest.mark.parametrize("summary_status", [None, DataFileSummary.Status.PENDING])
def test_parse_less_than_a_day_old_is_not_stale(
    stt_user,
    stt,
    summary_status,
):
    """Ignores parses that have not reached the one-day threshold."""
    datafile = make_datafile(
        stt_user,
        stt,
        1,
        state=SubmissionState.PARSE_STARTED,
    )
    set_created_at(datafile, timezone.now() - timedelta(hours=23))
    if summary_status is not None:
        make_summary(datafile, summary_status)

    stale_files = get_stale_lifecycle_files()

    assert stale_files.count() == 0


@pytest.mark.django_db
def test_reparse_older_than_a_day_is_stale(stt_user, stt):
    """Apply the lifecycle timeout even before a reparse-specific deadline."""
    now = timezone.now()
    datafile = make_datafile(
        stt_user,
        stt,
        1,
        state=SubmissionState.PARSE_STARTED,
    )
    set_created_at(datafile, now - timedelta(days=30))
    make_summary(datafile, DataFileSummary.Status.PENDING)
    reparse = ReparseMetaFactory.create(timeout_at=now + timedelta(days=1))
    datafile.reparses.add(
        reparse,
        through_defaults={
            "finished": False,
            "success": False,
            "started_at": now - timedelta(days=1, minutes=1),
        },
    )
    DataFile.objects.filter(pk=datafile.pk).update(
        state_changed_at=now - timedelta(days=1, minutes=1)
    )

    stale_files = get_stale_lifecycle_files(now=now)

    assert list(stale_files.values_list("pk", flat=True)) == [datafile.pk]


@pytest.mark.django_db
def test_recent_reparse_of_old_file_is_not_stale(stt_user, stt):
    """Ignore an unfinished reparse before either detection deadline."""
    now = timezone.now()
    datafile = make_datafile(
        stt_user,
        stt,
        1,
        state=SubmissionState.PARSE_STARTED,
    )
    set_created_at(datafile, now - timedelta(days=30))
    make_summary(datafile, DataFileSummary.Status.PENDING)
    reparse = ReparseMetaFactory.create(timeout_at=now + timedelta(hours=1))
    datafile.reparses.add(
        reparse,
        through_defaults={
            "finished": False,
            "success": False,
            "started_at": now - timedelta(hours=23),
        },
    )
    DataFile.objects.filter(pk=datafile.pk).update(
        state_changed_at=now - timedelta(hours=23)
    )

    stale_files = get_stale_lifecycle_files(now=now)

    assert stale_files.count() == 0


@pytest.mark.django_db
def test_timed_out_unfinished_reparse_is_stale(stt_user, stt):
    """Honor ReparseMeta.timeout_at before the generic lifecycle timeout."""
    now = timezone.now()
    datafile = make_datafile(
        stt_user,
        stt,
        1,
        state=SubmissionState.PARSE_STARTED,
    )
    set_created_at(datafile, now - timedelta(hours=1))
    reparse = ReparseMetaFactory.create(timeout_at=now - timedelta(minutes=1))
    datafile.reparses.add(
        reparse,
        through_defaults={
            "finished": False,
            "success": False,
            "started_at": now - timedelta(hours=1),
        },
    )

    stale_files = get_stale_lifecycle_files(now=now)

    assert list(stale_files.values_list("pk", flat=True)) == [datafile.pk]


@pytest.mark.django_db
def test_timed_out_finished_reparse_is_not_stale(stt_user, stt):
    """Do not use a completed historical reparse to mark current work stale."""
    now = timezone.now()
    datafile = make_datafile(
        stt_user,
        stt,
        1,
        state=SubmissionState.PARSE_STARTED,
    )
    set_created_at(datafile, now - timedelta(hours=1))
    reparse = ReparseMetaFactory.create(timeout_at=now - timedelta(minutes=1))
    datafile.reparses.add(
        reparse,
        through_defaults={
            "finished": True,
            "success": False,
            "started_at": now - timedelta(hours=1),
            "finished_at": now - timedelta(minutes=30),
        },
    )

    stale_files = get_stale_lifecycle_files(now=now)

    assert stale_files.count() == 0


@pytest.mark.django_db
def test_old_file_with_completed_summary_is_not_stale(stt_user, stt):
    """Ignores files whose parsing completed before the stale check."""
    datafile = make_datafile(
        stt_user,
        stt,
        1,
        state=SubmissionState.PARSE_COMPLETED,
    )
    set_created_at(datafile, timezone.now() - timedelta(days=2))
    make_summary(datafile, DataFileSummary.Status.ACCEPTED)

    stale_files = get_stale_lifecycle_files()

    assert stale_files.count() == 0


@pytest.mark.django_db
def test_mark_stale_files_stuck_transitions_eligible_files(stt_user, stt):
    """Persist STUCK for stale parses and leave recent parses unchanged."""
    stale_file = make_datafile(
        stt_user,
        stt,
        1,
        state=SubmissionState.PARSE_STARTED,
    )
    set_created_at(stale_file, timezone.now() - timedelta(days=2))
    make_summary(stale_file, DataFileSummary.Status.PENDING)
    recent_file = make_datafile(
        stt_user,
        stt,
        2,
        state=SubmissionState.PARSE_STARTED,
    )
    set_created_at(recent_file, timezone.now() - timedelta(hours=23))
    make_summary(recent_file, DataFileSummary.Status.PENDING)

    marked_count = mark_stale_files_stuck()

    stale_file.refresh_from_db()
    recent_file.refresh_from_db()
    assert marked_count == 1
    assert stale_file.state == SubmissionState.STUCK
    assert recent_file.state == SubmissionState.PARSE_STARTED


@pytest.mark.django_db
def test_stuck_file_outside_current_fiscal_year_is_excluded(stt_user, stt):
    """Ignores stuck files outside the current fiscal year."""
    datafile = make_datafile(
        stt_user,
        stt,
        1,
        state=SubmissionState.STUCK,
        year=get_current_fiscal_year() - 1,
    )

    stuck_files = get_stuck_files()

    assert datafile.pk not in stuck_files.values_list("pk", flat=True)
    assert stuck_files.count() == 0


@pytest.mark.django_db
def test_stuck_file_email_rendering_includes_state(stt_user, stt):
    """Renders each stuck file's DataFile.state value."""
    datafile = make_datafile(
        stt_user,
        stt,
        1,
        state=SubmissionState.STUCK,
    )

    send_stuck_file_email([datafile], ["recipient@example.com"])

    assert len(mail.outbox) == 1
    html_body = mail.outbox[0].alternatives[0][0]
    assert ">State<" in html_body
    assert f">{SubmissionState.STUCK.value}<" in html_body


@pytest.mark.django_db
def test_send_stuck_file_email(mocker):
    """Test send_stuck_file_email logging."""
    mocker.patch("tdpservice.email.email.automated_email", return_value=True)

    send_stuck_file_email([], ["recipient"])
    entries = LogEntry.objects.all().order_by("pk")
    assert len(entries) == 4
    assert entries[0].change_message == (
        "Emailing stuck files to SysAdmins: ['recipient']"
    )
