"""Behavioral coverage for the bounded admin user API."""

import uuid

import pytest

from tdpservice.users.test.factories import UserFactory
from tdpservice.users.test.test_admin_form_api import (
    _admin_headers,
    _login_admin_api_session,
)

pytestmark = pytest.mark.django_db
URL = "/admin-api/v1/users/"


@pytest.fixture
def admin_reader(api_client, settings, admin_console_user):
    """Return a client with the actual admin middleware session and proxy token."""
    _login_admin_api_session(api_client, admin_console_user, settings)
    api_client.credentials(**_admin_headers(settings))
    return api_client


def test_bounded_pages_and_stable_order(admin_reader):
    """Page through tied names without loading or repeating all matching users."""
    users = UserFactory.create_batch(28, first_name="Pagination", last_name="Same")
    first = admin_reader.get(URL, {"search": "Pagination"})
    second = admin_reader.get(URL, {"search": "Pagination", "page": 2})
    assert first.status_code == second.status_code == 200
    assert first.data["count"] == 28
    assert len(first.data["results"]) == 25
    assert len(second.data["results"]) == 3
    ids = [u["id"] for u in first.data["results"] + second.data["results"]]
    assert ids == sorted(str(user.pk) for user in users)
    assert admin_reader.get(URL, {"page": 99999}).status_code == 404


def test_page_size_cap(admin_reader):
    """A direct API request cannot request an unbounded page."""
    UserFactory.create_batch(101, first_name="Bounded")
    response = admin_reader.get(URL, {"search": "Bounded", "page_size": 99999})
    assert response.status_code == 200
    assert response.data["count"] == 101
    assert len(response.data["results"]) == 100


def test_combined_filters_and_detail(admin_reader):
    """Search and filters narrow the database result and detail exposes safe fields."""
    user = UserFactory(
        first_name="FindMe", account_approval_status="Pending", is_active=False
    )
    UserFactory(first_name="FindMe", account_approval_status="Approved")
    response = admin_reader.get(
        URL, {"search": "findme", "status": "Pending", "active": "false"}
    )
    assert response.status_code == 200
    assert response.data["count"] == 1
    assert response.data["results"][0]["id"] == str(user.pk)
    detail = admin_reader.get(f"{URL}{user.pk}/")
    assert detail.status_code == 200
    assert detail.data["email"] == user.email
    assert detail.data["stt_name"] is None
    assert detail.data["roles"] == []
    assert not {"password", "hhs_id", "login_gov_uuid"}.intersection(detail.data)
    assert admin_reader.get(f"{URL}{uuid.uuid4()}/").status_code == 404
    assert admin_reader.get(f"{URL}invalid-id/").status_code == 404


@pytest.mark.parametrize(
    "query", [{"status": "invalid"}, {"active": "invalid"}, {"search": "a" * 151}]
)
def test_invalid_filters(admin_reader, query):
    """Invalid filters produce explicit validation errors."""
    assert admin_reader.get(URL, query).status_code == 400


def test_empty_and_summary(admin_reader):
    """Empty search stays distinguishable from failure; summary uses aggregate counts."""
    response = admin_reader.get(URL, {"search": "no-such-account-example"})
    assert response.data["count"] == 0
    assert response.data["results"] == []
    before = admin_reader.get(f"{URL}summary/").data
    UserFactory(account_approval_status="Access request")
    after = admin_reader.get(f"{URL}summary/").data
    assert after["total"] == before["total"] + 1
    assert after["access_requests"] == before["access_requests"] + 1
    assert after["approved"] == before["approved"]


@pytest.mark.parametrize("method", ["post", "put", "patch", "delete"])
def test_reads_do_not_allow_mutation(admin_reader, method, admin_console_user):
    """The new viewset exposes no mutation actions."""
    url = URL if method == "post" else f"{URL}{admin_console_user.pk}/"
    assert getattr(admin_reader, method)(url, {}, format="json").status_code == 405


@pytest.mark.parametrize("suffix", ["", "summary/"])
def test_anonymous_denied(api_client, settings, suffix):
    """The proxy token alone never authorizes user reads."""
    assert api_client.get(URL + suffix, **_admin_headers(settings)).status_code in (
        401,
        403,
    )


def test_non_admin_denied(api_client, settings, data_analyst):
    """An admin-scoped cookie does not grant a non-admin access."""
    _login_admin_api_session(api_client, data_analyst, settings)
    assert api_client.get(URL, **_admin_headers(settings)).status_code == 403


def test_standard_session_denied(api_client, settings, admin_console_user):
    """The standard portal cookie cannot authorize admin reads."""
    api_client.force_login(admin_console_user)
    assert api_client.get(URL, **_admin_headers(settings)).status_code in (401, 403)
