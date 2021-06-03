"""Tests for Reports Application."""
import uuid

import pytest
from rest_framework import status

from ..models import ReportFile


def multi_year_report_data(user, stt):
    """Return report data that encompasses multiple years."""
    return [{"original_filename": "report.txt",
             "quarter": "Q1",
             "user": user,
             "stt": stt,
             "year": 2020,
             "section": "Active Case Data", },
            {"original_filename": "report.txt",
             "quarter": "Q1",
             "user": user,
             "stt": stt,
             "year": 2021,
             "section": "Active Case Data", },
            {"original_filename": "report.txt",
             "quarter": "Q1",
             "user": user,
             "stt": stt,
             "year": 2022,
             "section": "Active Case Data", }]

@pytest.mark.django_db
def test_create_report_file_entry(api_client, ofa_admin):
    """Test ability to create report file metadata registry."""
    user = ofa_admin
    api_client.login(username=user.username, password="test_password")
    data = {
        "original_filename": "report.txt",
        "quarter": "Q1",
        "slug": str(uuid.uuid4()),
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
    """Test that a Data Prepper is allowed to add reports to their own STT."""
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
    """Test that Data preppers can't add reports to STTs other than their own."""
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
def test_reports_inactive_user_not_allowed(api_client, inactive_user):
    """Test that an inactive user can't add reports at all."""
    user = inactive_user
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
    assert response.status_code == status.HTTP_403_FORBIDDEN

@pytest.mark.django_db
def test_list_report_years(api_client, data_prepper):
    """Test list of years for which there exist a report as a data prepper."""
    user = data_prepper

    reports = multi_year_report_data(user, user.stt)

    ReportFile.create_new_version(reports[0])
    ReportFile.create_new_version(reports[1])
    ReportFile.create_new_version(reports[2])

    api_client.login(username=user.username, password="test_password")

    response = api_client.get("/v1/reports/years")

    assert response.status_code == status.HTTP_200_OK
    assert response.data == [
        2020,
        2021,
        2022
    ]

@pytest.mark.django_db
def test_list_ofa_admin_report_years(api_client, ofa_admin, stt):
    """Test list of years for which there exist a report as an OFA admin."""
    user = ofa_admin

    reports = multi_year_report_data(user, stt)

    ReportFile.create_new_version(reports[0])
    ReportFile.create_new_version(reports[1])
    ReportFile.create_new_version(reports[2])

    api_client.login(username=user.username, password="test_password")

    response = api_client.get(f"/v1/reports/years/{stt.id}")

    assert response.status_code == status.HTTP_200_OK
    assert response.data == [
        2020,
        2021,
        2022
    ]


@pytest.mark.django_db
def test_list_ofa_admin_report_years_positional_stt(api_client, ofa_admin, stt):
    """Test list year fail for OFA admin when no STT is provided."""
    user = ofa_admin

    data1, data2, data3 = multi_year_report_data(user, stt)

    ReportFile.create_new_version(data1)
    ReportFile.create_new_version(data2)
    ReportFile.create_new_version(data3)

    api_client.login(username=user.username, password="test_password")

    response = api_client.get("/v1/reports/years")

    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_list_ofa_admin_report_years_no_self_stt(api_client, ofa_admin_stt_user, stt):
    """Test OFA Admin with no stt assigned can view list of years."""
    user = ofa_admin_stt_user

    data1, data2, data3 = multi_year_report_data(user, stt)

    assert user.stt is None

    ReportFile.create_new_version(data1)
    ReportFile.create_new_version(data2)
    ReportFile.create_new_version(data3)

    api_client.login(username=user.username, password="test_password")

    response = api_client.get(f"/v1/reports/years/{stt.id}")

    assert response.status_code == status.HTTP_200_OK

    assert response.data == [
        2020,
        2021,
        2022
    ]


# @pytest.mark.django_db
# def test_
