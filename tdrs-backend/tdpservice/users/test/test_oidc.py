"""Tests for KeycloakOIDCBackend authentication backend."""

import logging
from unittest.mock import MagicMock, patch

from django.test import RequestFactory, TestCase, override_settings

import pytest

from tdpservice.users.models import AccountApprovalStatusChoices
from tdpservice.users.oidc import KeycloakOIDCBackend
from tdpservice.users.test.factories import UserFactory

logger = logging.getLogger(__name__)


@pytest.fixture
def backend():
    """Return a KeycloakOIDCBackend instance."""
    return KeycloakOIDCBackend()


@pytest.fixture
def request_factory():
    """Return a Django RequestFactory."""
    return RequestFactory()


@pytest.mark.django_db
class TestFilterUsersByClaims:
    """Tests for KeycloakOIDCBackend.filter_users_by_claims."""

    def test_filter_by_hhs_id(self, backend):
        user = UserFactory(hhs_id="ABC123456789")
        claims = {"hhs_id": "ABC123456789", "email": "other@test.com"}
        result = backend.filter_users_by_claims(claims)
        assert len(result) == 1
        assert result[0].id == user.id

    def test_filter_by_login_gov_uuid(self, backend):
        user = UserFactory(hhs_id=None)
        claims = {"login_gov_uuid": str(user.login_gov_uuid), "email": "other@test.com"}
        result = backend.filter_users_by_claims(claims)
        assert len(result) == 1
        assert result[0].id == user.id

    def test_filter_by_email_fallback(self, backend):
        user = UserFactory(login_gov_uuid=None, hhs_id=None)
        claims = {"email": user.email}
        result = backend.filter_users_by_claims(claims)
        assert len(result) == 1
        assert result[0].id == user.id

    def test_filter_returns_empty_for_unknown_user(self, backend):
        claims = {"email": "nonexistent@test.com"}
        result = backend.filter_users_by_claims(claims)
        assert result == []

    def test_hhs_id_takes_priority_over_login_gov_uuid(self, backend):
        """When both hhs_id and login_gov_uuid are in claims, hhs_id is checked first."""
        user_ams = UserFactory(hhs_id="AMS123456789", login_gov_uuid=None)
        user_logingov = UserFactory(hhs_id=None)

        claims = {
            "hhs_id": "AMS123456789",
            "login_gov_uuid": str(user_logingov.login_gov_uuid),
            "email": "someone@test.com",
        }
        result = backend.filter_users_by_claims(claims)
        assert len(result) == 1
        assert result[0].id == user_ams.id

    def test_hhs_id_falls_back_to_email_when_no_match(self, backend):
        """When hhs_id doesn't match, falls back to email lookup."""
        user = UserFactory(hhs_id="DIFFERENT123", login_gov_uuid=None)
        claims = {"hhs_id": "NOMATCH999999", "email": user.email}
        result = backend.filter_users_by_claims(claims)
        assert len(result) == 1
        assert result[0].id == user.id


@pytest.mark.django_db
class TestCreateUser:
    """Tests for KeycloakOIDCBackend.create_user."""

    def test_create_user_with_login_gov_uuid(self, backend):
        claims = {
            "email": "newuser@test.com",
            "login_gov_uuid": "550e8400-e29b-41d4-a716-446655440000",
        }
        user = backend.create_user(claims)
        assert user is not None
        assert user.username == "newuser@test.com"
        assert user.email == "newuser@test.com"
        assert str(user.login_gov_uuid) == "550e8400-e29b-41d4-a716-446655440000"
        assert not user.has_usable_password()

    def test_create_user_with_hhs_id(self, backend):
        claims = {"email": "acfuser@acf.hhs.gov", "hhs_id": "HHS123456789"}
        user = backend.create_user(claims)
        assert user is not None
        assert user.hhs_id == "HHS123456789"

    def test_create_user_without_email_returns_none(self, backend):
        claims = {"login_gov_uuid": "some-uuid"}
        user = backend.create_user(claims)
        assert user is None


@pytest.mark.django_db
class TestUpdateUser:
    """Tests for KeycloakOIDCBackend.update_user."""

    def test_update_user_sets_hhs_id(self, backend):
        user = UserFactory(hhs_id=None)
        claims = {"hhs_id": "NEWHHS123456"}
        updated = backend.update_user(user, claims)
        assert updated.hhs_id == "NEWHHS123456"

    def test_update_user_no_change_when_same(self, backend):
        user = UserFactory(hhs_id="EXISTING1234")
        claims = {"hhs_id": "EXISTING1234"}
        updated = backend.update_user(user, claims)
        assert updated.hhs_id == "EXISTING1234"


@pytest.mark.django_db
class TestVerifyClaims:
    """Tests for KeycloakOIDCBackend.verify_claims."""

    def test_rejects_missing_email(self, backend):
        claims = {"login_gov_uuid": "some-uuid"}
        assert backend.verify_claims(claims) is False

    def test_rejects_acf_user_via_login_gov(self, backend):
        """ACF staff (@acf.hhs.gov) must not authenticate via Login.gov."""
        UserFactory(
            username="staff@acf.hhs.gov",
            email="staff@acf.hhs.gov",
            account_approval_status=AccountApprovalStatusChoices.APPROVED,
        )
        claims = {
            "email": "staff@acf.hhs.gov",
            "identity_provider": "login-gov",
        }
        assert backend.verify_claims(claims) is False

    def test_allows_acf_user_via_ams(self, backend):
        """ACF staff authenticating via AMS should be allowed."""
        UserFactory(
            username="staff@acf.hhs.gov",
            email="staff@acf.hhs.gov",
            account_approval_status=AccountApprovalStatusChoices.APPROVED,
        )
        claims = {
            "email": "staff@acf.hhs.gov",
            "identity_provider": "ams",
        }
        assert backend.verify_claims(claims) is True

    def test_allows_non_acf_user_via_login_gov(self, backend):
        """Non-ACF users should be able to use Login.gov."""
        claims = {
            "email": "grantee@example.com",
            "identity_provider": "login-gov",
        }
        assert backend.verify_claims(claims) is True

    def test_rejects_deactivated_user(self, backend):
        user = UserFactory(
            account_approval_status=AccountApprovalStatusChoices.DEACTIVATED,
        )
        claims = {
            "email": user.email,
            "login_gov_uuid": str(user.login_gov_uuid),
        }
        assert backend.verify_claims(claims) is False

    def test_rejects_inactive_user(self, backend):
        user = UserFactory(is_active=False)
        claims = {
            "email": user.email,
            "login_gov_uuid": str(user.login_gov_uuid),
        }
        assert backend.verify_claims(claims) is False

    def test_allows_approved_active_user(self, backend):
        user = UserFactory(
            account_approval_status=AccountApprovalStatusChoices.APPROVED,
            is_active=True,
        )
        claims = {
            "email": user.email,
            "login_gov_uuid": str(user.login_gov_uuid),
        }
        assert backend.verify_claims(claims) is True

    def test_allows_new_user_not_yet_in_system(self, backend):
        """New users not yet in the system should pass verify_claims."""
        claims = {
            "email": "brandnew@test.com",
            "identity_provider": "login-gov",
        }
        assert backend.verify_claims(claims) is True
