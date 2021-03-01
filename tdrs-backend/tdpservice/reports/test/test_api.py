"""Tests for Reports Application."""
import uuid

import pytest
from rest_framework import status

from ..models import ReportFile


# Create your tests here.
@pytest.mark.django_db
def test_create_report_file_entry(api_client, ofa_admin):
    """Test report file metadata registry."""
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
    }
    response = api_client.post("/v1/reports/", data)
    assert response.status_code == status.HTTP_201_CREATED
    assert response.data["slug"] == str(data["slug"])

    assert ReportFile.objects.filter(
        slug=data["slug"],
        year=data["year"],
        section=data["section"],
        version=1,
        user=user,
    ).exists()


@pytest.mark.django_db
def test_report_file_version_increment(api_client, ofa_admin):
    """Test that report file version numbers incremented."""
    user = ofa_admin
    api_client.login(username=user.username, password="test_password")
    data1 = {
        "original_filename": "report.txt",
        "quarter": "Q1",
        "slug": str(uuid.uuid4()),
        "user": user.id,
        "stt": user.stt.id,
        "year": 2020,
        "section": "Active Case Data",
    }
    data2 = {
        "original_filename": "report.txt",
        "quarter": "Q1",
        "slug": data1["slug"],
        "user": user.id,
        "stt": user.stt.id,
        "year": 2020,
        "section": "Active Case Data",
    }

    response1 = api_client.post("/v1/reports/", data1)
    response2 = api_client.post("/v1/reports/", data2)

    assert response1.status_code == status.HTTP_201_CREATED
    assert response1.data["slug"] == data1["slug"]

    assert response2.status_code == status.HTTP_201_CREATED
    assert response2.data["slug"] == data2["slug"]

    assert ReportFile.objects.filter(
        slug=data1["slug"],
        year=data1["year"],
        section=data1["section"],
        version=1,
        user=user,
    ).exists()

    assert ReportFile.objects.filter(
        slug=data1["slug"],
        year=data1["year"],
        section=data1["section"],
        version=2,
        user=user,
    ).exists()


@pytest.mark.django_db
def test_reports_data_prepper_permission(api_client, data_prepper):
    """Test report file metadata registry."""
    user = data_prepper
    api_client.login(username=user.username, password="test_password")
    data = {
        "original_filename": "report.txt",
        "quarter": "Q1",
        "slug": uuid.uuid4(),
        "user": user.id,
        "stt": int(user.stt.id),
        "year": 2020,
        "section": "Active Case Data",
    }

    response = api_client.post("/v1/reports/", data)
    assert response.status_code == status.HTTP_201_CREATED


@pytest.mark.django_db
def test_reports_data_prepper_not_allowed(api_client, data_prepper):
    """Test report file metadata registry."""
    user = data_prepper
    api_client.login(username=user.username, password="test_password")
    data = {
        "original_filename": "report.txt",
        "quarter": "Q1",
        "slug": uuid.uuid4(),
        "user": user.id,
        "stt": int(user.stt.id) + 1,
        "year": 2020,
        "section": "Active Case Data",
    }

    response = api_client.post("/v1/reports/", data)
    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_individual_report_file_retrieval(api_client, data_prepper):
    """Test retrieval of individual reports via GetReport."""
    user = data_prepper
    api_client.login(username=user.username, password="test_password")

    data = {
        "original_filename": "report.txt",
        "quarter": "Q1",
        "slug": str(uuid.uuid4()),
        "user": user,
        "stt": user.stt,
        "year": 2020,
        "section": "Active Case Data",
    }

    ReportFile.create_new_version(data)
    assert ReportFile.objects.filter(**data).exists()
    response = api_client.get("/v1/reports/2020/Q1/active_case_data")

    assert data["slug"] == response.data["slug"]

@pytest.mark.django_db
def test_list_report_years(api_client, data_prepper):
    """Test list of years for which there exist a report."""
    user = data_prepper

    data1 = {
        "original_filename": "report.txt",
        "quarter": "Q1",
        "slug": str(uuid.uuid4()),
        "user": user,
        "stt": user.stt,
        "year": 2020,
        "section": "Active Case Data",
    }

    data2 = {
        "original_filename": "report.txt",
        "quarter": "Q1",
        "slug": str(uuid.uuid4()),
        "user": user,
        "stt": user.stt,
        "year": 2021,
        "section": "Active Case Data",
    }

    data3 = {
        "original_filename": "report.txt",
        "quarter": "Q1",
        "slug": str(uuid.uuid4()),
        "user": user,
        "stt": user.stt,
        "year": 2022,
        "section": "Active Case Data",
    }
    ReportFile.create_new_version(data1)
    ReportFile.create_new_version(data2)
    ReportFile.create_new_version(data3)
    api_client.login(username=user.username, password="test_password")

    response = api_client.get(f"/v1/reports/years/{str(user.stt.id)}")

    assert response.status_code == status.HTTP_200_OK
    assert response.data == [
        2020,
        2021,
        2022
    ]
