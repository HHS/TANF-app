"""Core API tests."""
import uuid

import pytest
from django.contrib.admin.models import LogEntry
from django.contrib.contenttypes.models import ContentType
from rest_framework import status

from tdpservice.reports.models import ReportFile


@pytest.mark.django_db
def test_write_logs(api_client, ofa_admin):
    """Test endpoint consumption of arbitrary JSON to be logged."""
    user = ofa_admin
    api_client.login(username=user.username, password="test_password")
    data = {
        "original_filename": "report.txt",
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
        "original_filename": "report.txt",
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
def test_log_entry_creation(api_client, report):
    """Test endpoint's creation of LogEntry objects."""
    api_client.login(username=report.user.username, password="test_password")
    data = {
        "original_filename": report.original_filename,
        "quarter": report.quarter,
        "slug": report.slug,
        "user": report.user.username,
        "stt": report.stt.id,
        "year": report.year,
        "section": report.section,
        "timestamp": "2021-04-26T18:32:43.330Z",
        "type": "alert",
        "message": "User submitted file(s)",
        "files": [report.pk]
    }

    api_client.post("/v1/logs/", data)

    assert LogEntry.objects.filter(
        content_type_id=ContentType.objects.get_for_model(ReportFile).pk,
        object_id=report.pk
    ).exists()
