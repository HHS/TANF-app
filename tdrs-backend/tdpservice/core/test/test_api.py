"""Core API tests."""
import uuid

import pytest
from django.contrib.admin.models import LogEntry
from django.contrib.contenttypes.models import ContentType
from rest_framework import status

from tdpservice.data_files.models import DataFile


@pytest.mark.django_db
def test_write_logs(api_client, ofa_admin):
    """Test endpoint consumption of arbitrary JSON to be logged."""
    user = ofa_admin
    api_client.login(username=user.username, password="test_password")
    data = {
        "original_filename": "data_file.txt",
        "quarter": "Q1",
        "slug": uuid.uuid4(),
        "user": user.id,
        "stt": user.stt.id,
        "year": 2020,
        "section": "Active Case Data",
        "timestamp": "2021-04-26T18:32:43.330Z",
        "type": "error",
        "message": "Something strange happened",
    }
    response = api_client.post("/v1/logs/", data)
    assert response.status_code == status.HTTP_200_OK
    assert response.data == 'Success'


@pytest.mark.django_db
def test_log_output(api_client, ofa_admin, caplog):
    """Test endpoint's writing of logs to the output."""
    user = ofa_admin
    api_client.login(username=user.username, password="test_password")
    data = {
        "original_filename": "data_file.txt",
        "quarter": "Q1",
        "slug": uuid.uuid4(),
        "user": user.id,
        "stt": user.stt.id,
        "year": 2020,
        "section": "Active Case Data",
        "timestamp": "2021-04-26T18:32:43.330Z",
        "type": "alert",
        "message": "User submitted 1 file(s)",
    }

    api_client.post("/v1/logs/", data)

    assert "User submitted 1 file(s)" in caplog.text


@pytest.mark.django_db
def test_log_entry_creation(api_client, data_file_instance):
    """Test endpoint's creation of LogEntry objects."""
    api_client.login(username=data_file_instance.user.username, password="test_password")
    data = {
        "original_filename": data_file_instance.original_filename,
        "quarter": data_file_instance.quarter,
        "slug": data_file_instance.slug,
        "user": data_file_instance.user.username,
        "stt": data_file_instance.stt.id,
        "year": data_file_instance.year,
        "section": data_file_instance.section,
        "timestamp": "2021-04-26T18:32:43.330Z",
        "type": "alert",
        "message": "User submitted file(s)",
        "files": [data_file_instance.pk]
    }

    api_client.post("/v1/logs/", data)

    assert LogEntry.objects.filter(
        content_type_id=ContentType.objects.get_for_model(DataFile).pk,
        object_id=data_file_instance.pk
    ).exists()
