"""Core API tests."""
import uuid

import pytest
from rest_framework import status


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
        "file_version": "0.0.1",
    }
    response = api_client.post("/v1/logs/", data)
    assert response.status_code == status.HTTP_200_OK
    assert response.data == 'Success'
