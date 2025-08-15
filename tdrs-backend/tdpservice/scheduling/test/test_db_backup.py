"""Test cases for db_backup.py functions."""

import os

from django.contrib.admin.models import LogEntry

import pytest

from tdpservice.scheduling.management import db_backup


@pytest.mark.django_db
def test_backup_database(system_user):
    """Test backup functionality."""
    file_name = "/tmp/test_backup.pg"
    ret = db_backup.backup_database(
        file_name,
        "",
        "postgres://tdpuser:something_secure@postgres:5432/tdrs_test",
        system_user,
    )

    assert ret is True
    assert os.path.getsize(file_name) > 0
    os.remove(file_name)
    assert os.path.exists(file_name) is False


@pytest.mark.django_db
def test_backup_database_fail_on_backup(system_user):
    """Test backup fails on psql non-zero return code."""
    with pytest.raises(Exception) as e:
        file_name = "/tmp/test_backup.pg"
        db_backup.backup_database(
            file_name,
            "asdfasdfassfd",
            "postgres://tdpuser:something_secure@postgres:5432/tdrs_test",
            system_user,
        )

    assert str(e.value) == "pg_dump command failed with a non zero exit code."
    assert os.path.exists(file_name) is False


@pytest.mark.django_db
def test_backup_database_fail_on_general_exception():
    """Test backup succeeds but raises exception on string user for log entry."""
    with pytest.raises(Exception) as e:
        file_name = "/tmp/test_backup.pg"
        db_backup.backup_database(
            file_name,
            "",
            "postgres://tdpuser:something_secure@postgres:5432/tdrs_test",
            "system_user",
        )

    assert str(e.value) == "'str' object has no attribute 'pk'"
    assert os.path.exists(file_name) is True
    os.remove(file_name)
    assert os.path.exists(file_name) is False


@pytest.mark.django_db
def test_get_database_credentials():
    """Test get credentials."""
    creds = db_backup.get_database_credentials(
        "postgres://tdpuser:something_secure@postgres:5432/tdrs_test"
    )
    assert creds == ["tdpuser", "something_secure", "postgres", "5432", "tdrs_test"]


@pytest.mark.django_db
def test_main_backup(mocker, system_user):
    """Test call the main function."""
    mocker.patch(
        "tdpservice.scheduling.management.db_backup.upload_file", return_value=True
    )
    sys_vals = {
        "DATABASE_URI": "postgres://tdpuser:something_secure@postgres:5432",
        "DATABASE_DB_NAME": "tdrs_test",
        "POSTGRES_CLIENT_DIR": "",
        "S3_BUCKET": "",
        "S3_REGION": "",
    }

    db_backup.main(
        ["-b", "-f", "/tmp/test_backup.pg"],
        sys_values=sys_vals,
        system_user=system_user,
    )
    assert (
        LogEntry.objects.get(change_message="Begining database backup.").pk is not None
    )
    assert (
        LogEntry.objects.get(change_message="Finished database backup.").pk is not None
    )
