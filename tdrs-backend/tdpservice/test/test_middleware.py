"""Tests for project middleware."""

from types import SimpleNamespace

from django.http import HttpResponse
from django.test import RequestFactory
from django.urls import reverse

import pytest

from tdpservice import middleware
from tdpservice.middleware import AdminAPIAuthorizationMiddleware, SessionMiddleware
from tdpservice.request_attribution import RequestAttribution
from tdpservice.users.models import AccountApprovalStatusChoices
from tdpservice.users.oidc import ADMIN_OIDC_CLIENT


class CounterSpy:
    """Capture Prometheus counter label calls without using the global registry."""

    def __init__(self):
        self.calls = []

    def labels(self, **labels):
        """Store the labels used for an increment."""
        self.calls.append({"labels": labels, "increments": 0})
        return self

    def inc(self):
        """Record that the counter was incremented."""
        self.calls[-1]["increments"] += 1


class GroupSpy:
    """Minimal groups manager for middleware identity label tests."""

    def __init__(self, group_names):
        self.group_names = group_names

    def values_list(self, *_args, **_kwargs):
        """Return group names like Django's values_list(..., flat=True)."""
        return self.group_names


class UserRelationTrap:
    """Authenticated user double that fails if relation labels are accessed."""

    is_authenticated = True

    @property
    def stt(self):
        """Fail if middleware tries to read the STT relation."""
        raise AssertionError("stt relation should not be touched")

    @property
    def groups(self):
        """Fail if middleware tries to read the groups relation."""
        raise AssertionError("groups relation should not be touched")


@pytest.fixture
def counter_spy(monkeypatch):
    """Patch the request attribution counter with a local spy."""
    spy = CounterSpy()
    monkeypatch.setattr(middleware, "API_REQUESTS_TOTAL", spy)
    return spy


@pytest.fixture
def request_factory():
    """Return a Django request factory."""
    return RequestFactory()


def _tracked_request(request_factory, path="/v1/users/", method="get", **headers):
    """Build a request with a resolved safe view name."""
    request = getattr(request_factory, method)(path, **headers)
    request.resolver_match = SimpleNamespace(view_name="user-list")
    return request


def _call_middleware(request, status_code=200):
    """Run the attribution middleware around a successful response."""
    attribution_middleware = middleware.RequestAttributionMetricsMiddleware(
        lambda _request: HttpResponse(status=status_code)
    )
    return attribution_middleware(request)


def _last_labels(counter_spy):
    """Return labels from the most recent counter increment."""
    assert len(counter_spy.calls) == 1
    assert counter_spy.calls[0]["increments"] == 1
    return counter_spy.calls[0]["labels"]


def _expected_labels(**overrides):
    """Return the default expected metric labels with selected overrides."""
    labels = {
        "source": "unknown",
        "auth_method": "none",
        "client_id": "none",
        "user_stt": "unknown",
        "user_group": "unknown",
        "method": "GET",
        "status_code": "200",
        "view": "user-list",
    }
    labels.update(overrides)
    return labels


def _set_bearer_attribution(request, client_id="tdp-cli"):
    """Attach verified bearer attribution like the DRF authenticator does."""
    request.tdp_attribution = RequestAttribution(
        source="api_client",
        client_id=client_id,
        auth_method="bearer",
    )


def test_request_attribution_uses_verified_bearer_identity_labels(
    counter_spy, request_factory
):
    """Bearer auth labels come from verified attribution, not user ORM relations."""
    request = _tracked_request(
        request_factory,
        HTTP_AUTHORIZATION="Bearer signed-token",
    )
    request.user = UserRelationTrap()
    request.tdp_attribution = RequestAttribution(
        source="api_client",
        client_id="tdp-cli",
        auth_method="bearer",
        user_stt="1",
        user_group="Data Analyst",
    )

    _call_middleware(request)

    assert _last_labels(counter_spy) == _expected_labels(
        source="api_client",
        auth_method="bearer",
        client_id="tdp-cli",
        user_stt="1",
        user_group="Data Analyst",
    )


def test_request_attribution_records_frontend_header(counter_spy, request_factory):
    """Frontend service headers do not identify unauthenticated request source."""
    request = _tracked_request(
        request_factory,
        HTTP_X_SERVICE_NAME="tdp-frontend",
    )

    _call_middleware(request, status_code=204)

    assert _last_labels(counter_spy) == _expected_labels(status_code="204")


def test_request_attribution_records_session_over_frontend_header(
    counter_spy, request_factory
):
    """Authenticated sessions are the browser-session signal, not headers."""
    request = _tracked_request(
        request_factory,
        HTTP_X_SERVICE_NAME="tdp-frontend",
    )
    request.user = SimpleNamespace(is_authenticated=True)
    request.COOKIES["id_token"] = "cookie-token"

    _call_middleware(request)

    assert _last_labels(counter_spy) == _expected_labels(
        source="browser_session",
        auth_method="session",
    )


def test_request_attribution_records_verified_bearer_client(
    counter_spy, request_factory
):
    """Verified bearer context wins over the spoofable frontend header."""
    request = _tracked_request(
        request_factory,
        HTTP_AUTHORIZATION="Bearer signed-token",
        HTTP_X_SERVICE_NAME="tdp-frontend",
    )
    _set_bearer_attribution(request)

    _call_middleware(request)

    assert _last_labels(counter_spy) == _expected_labels(
        source="api_client",
        auth_method="bearer",
        client_id="tdp-cli",
    )


def test_request_attribution_records_verified_bearer_context_without_header(
    counter_spy, request_factory
):
    """Verified bearer auth context is enough to identify the API client."""
    request = _tracked_request(request_factory)
    _set_bearer_attribution(request)
    request.user = SimpleNamespace(is_authenticated=True)

    _call_middleware(request)

    assert _last_labels(counter_spy) == _expected_labels(
        source="api_client",
        auth_method="bearer",
        client_id="tdp-cli",
    )


def test_request_attribution_keeps_verified_bearer_on_error_response(
    counter_spy, request_factory
):
    """A verified bearer client remains attributed even when the view rejects it."""
    request = _tracked_request(
        request_factory,
        HTTP_AUTHORIZATION="Bearer signed-token",
    )
    _set_bearer_attribution(request)

    _call_middleware(request, status_code=401)

    assert _last_labels(counter_spy) == _expected_labels(
        source="api_client",
        auth_method="bearer",
        client_id="tdp-cli",
        status_code="401",
    )


def test_request_attribution_records_authorization_meta_fallback(
    counter_spy, request_factory
):
    """Authorization fallback keys still identify API-client attempts."""
    request = _tracked_request(request_factory)
    request.META.pop("HTTP_AUTHORIZATION", None)
    request.META["Authorization"] = "Bearer signed-token"

    _call_middleware(request, status_code=401)

    assert _last_labels(counter_spy) == _expected_labels(
        source="api_client",
        auth_method="authorization_header",
        client_id="unknown",
        status_code="401",
    )


def test_request_attribution_records_bearer_client_over_session(
    counter_spy, request_factory
):
    """Authorization headers identify API clients even when cookies are present."""
    request = _tracked_request(
        request_factory,
        HTTP_AUTHORIZATION="Bearer signed-token",
        HTTP_COOKIE="id_token=abc123",
    )
    _set_bearer_attribution(request)
    request.user = SimpleNamespace(is_authenticated=True)

    _call_middleware(request)

    assert _last_labels(counter_spy) == _expected_labels(
        source="api_client",
        auth_method="bearer",
        client_id="tdp-cli",
    )


def test_request_attribution_records_unknown_bearer_client(
    counter_spy, request_factory
):
    """Bearer attempts without verified client context stay direct but unknown."""
    request = _tracked_request(
        request_factory,
        HTTP_AUTHORIZATION="Bearer invalid-token",
    )

    _call_middleware(request, status_code=401)

    assert _last_labels(counter_spy) == _expected_labels(
        source="api_client",
        auth_method="authorization_header",
        client_id="unknown",
        status_code="401",
    )


def test_request_attribution_does_not_verify_expired_bearer_token(
    counter_spy, request_factory
):
    """Legacy client id attributes do not prove bearer attribution."""
    request = _tracked_request(
        request_factory,
        HTTP_AUTHORIZATION="Bearer expired-token",
    )
    request._keycloak_client_id = "tdp-cli"

    _call_middleware(request, status_code=401)

    assert _last_labels(counter_spy) == _expected_labels(
        source="api_client",
        auth_method="authorization_header",
        client_id="unknown",
        status_code="401",
    )


def test_request_attribution_records_missing_source(counter_spy, request_factory):
    """Requests without auth, frontend, or bearer attribution stay unknown."""
    request = _tracked_request(request_factory)

    _call_middleware(request, status_code=403)

    assert _last_labels(counter_spy) == _expected_labels(
        status_code="403",
    )


def test_request_attribution_ignores_unrecognized_service_header(
    counter_spy, request_factory
):
    """Unexpected service-name values do not identify request source."""
    request = _tracked_request(
        request_factory,
        HTTP_X_SERVICE_NAME="postman",
    )

    _call_middleware(request)

    assert _last_labels(counter_spy) == _expected_labels()


def test_request_attribution_records_non_bearer_authorization(
    counter_spy, request_factory
):
    """Non-Bearer Authorization headers are categorized without storing them."""
    request = _tracked_request(
        request_factory,
        HTTP_AUTHORIZATION="Token abc123",
    )

    _call_middleware(request, status_code=403)

    assert _last_labels(counter_spy) == _expected_labels(
        source="api_client",
        auth_method="authorization_header",
        client_id="unknown",
        status_code="403",
    )


def test_request_attribution_records_authenticated_session(
    counter_spy, request_factory
):
    """Authenticated requests without Authorization are browser-session traffic."""
    request = _tracked_request(request_factory)
    request.user = SimpleNamespace(is_authenticated=True)

    _call_middleware(request)

    assert _last_labels(counter_spy) == _expected_labels(
        source="browser_session",
        auth_method="session",
    )


def test_request_attribution_records_authenticated_user_identity(
    counter_spy, request_factory
):
    """Authenticated sessions do not derive labels from user ORM relations."""
    request = _tracked_request(request_factory)
    request.user = SimpleNamespace(
        is_authenticated=True,
        stt_id=1,
        stt=SimpleNamespace(name="Alabama"),
        groups=GroupSpy(["Data Analyst"]),
    )

    _call_middleware(request)

    assert _last_labels(counter_spy) == _expected_labels(
        source="browser_session",
        auth_method="session",
    )


def test_request_attribution_records_admin_group_without_stt(
    counter_spy, request_factory
):
    """Admin session labels stay unknown unless attribution supplies them."""
    request = _tracked_request(request_factory)
    request.user = SimpleNamespace(
        is_authenticated=True,
        stt_id=None,
        stt=None,
        groups=GroupSpy(["OFA System Admin"]),
    )

    _call_middleware(request)

    assert _last_labels(counter_spy) == _expected_labels(
        source="browser_session",
        auth_method="session",
    )


def test_request_attribution_records_first_group(counter_spy, request_factory):
    """User groups are not read directly for request attribution labels."""
    request = _tracked_request(request_factory)
    request.user = SimpleNamespace(
        is_authenticated=True,
        stt_id=1,
        stt=SimpleNamespace(name="Alabama"),
        groups=GroupSpy(["OFA System Admin", "Data Analyst"]),
    )

    _call_middleware(request)

    assert _last_labels(counter_spy) == _expected_labels(
        source="browser_session",
        auth_method="session",
    )


def test_request_attribution_records_auth_cookie(counter_spy, request_factory):
    """Auth cookies without verified authentication do not identify source."""
    request = _tracked_request(request_factory, HTTP_COOKIE="id_token=abc123")
    request.user = SimpleNamespace(is_authenticated=False)

    _call_middleware(request, status_code=401)

    assert _last_labels(counter_spy) == _expected_labels(status_code="401")


def test_request_attribution_records_cors_preflight(counter_spy, request_factory):
    """CORS preflight requests without auth are left unknown."""
    request = _tracked_request(request_factory, method="options")

    _call_middleware(request)

    assert _last_labels(counter_spy) == _expected_labels(method="OPTIONS")


def test_request_attribution_skips_prometheus_scrape_path(counter_spy, request_factory):
    """Prometheus scrape traffic is not included in API source metrics."""
    request = _tracked_request(request_factory, path="/prometheus/metrics")

    _call_middleware(request)

    assert counter_spy.calls == []


def test_request_attribution_skips_admin_path(counter_spy, request_factory):
    """Django admin traffic is not included in API source metrics."""
    request = _tracked_request(request_factory, path="/admin/users/user/")

    _call_middleware(request)

    assert counter_spy.calls == []


def _response_with_origin(origin, settings):
    settings.CORS_ORIGIN_ALLOW_ALL = False
    settings.CORS_ALLOWED_ORIGINS = [
        "https://tanfdata.acf.hhs.gov",
        "https://admin.tanfdata.acf.hhs.gov",
    ]
    request = RequestFactory().get("/", HTTP_ORIGIN=origin)
    middleware = SessionMiddleware(lambda request: HttpResponse())

    return middleware.process_response(request, HttpResponse())


def _session_cookie(middleware, data):
    session = middleware.SessionStore()
    session.update(data)
    session.save()
    return session.session_key


def test_session_middleware_allows_configured_frontend_origin(settings):
    """The primary frontend origin should be echoed from CORS settings."""
    response = _response_with_origin("https://tanfdata.acf.hhs.gov", settings)

    assert response["Access-Control-Allow-Origin"] == "https://tanfdata.acf.hhs.gov"
    assert response["Vary"] == "Origin"


def test_session_middleware_uses_configured_cors_allow_headers(settings):
    """CORS allow headers should come from settings, including service headers."""
    settings.CORS_ALLOW_HEADERS = ["content-type", "x-service-name"]

    response = _response_with_origin("https://tanfdata.acf.hhs.gov", settings)

    assert response["Access-Control-Allow-Headers"] == "content-type, x-service-name"


def test_session_middleware_preserves_existing_cors_allow_headers(settings):
    """Do not overwrite headers already set by django-cors-headers."""
    settings.CORS_ORIGIN_ALLOW_ALL = False
    settings.CORS_ALLOWED_ORIGINS = ["https://tanfdata.acf.hhs.gov"]
    request = RequestFactory().get("/", HTTP_ORIGIN="https://tanfdata.acf.hhs.gov")
    response = HttpResponse()
    response["Access-Control-Allow-Headers"] = "from-cors-middleware"
    middleware = SessionMiddleware(lambda request: HttpResponse())

    response = middleware.process_response(request, response)

    assert response["Access-Control-Allow-Headers"] == "from-cors-middleware"


def test_session_middleware_allows_configured_admin_origin(settings):
    """The admin frontend origin should be echoed from CORS settings."""
    response = _response_with_origin("https://admin.tanfdata.acf.hhs.gov", settings)

    assert (
        response["Access-Control-Allow-Origin"] == "https://admin.tanfdata.acf.hhs.gov"
    )
    assert response["Vary"] == "Origin"


def test_session_middleware_does_not_allow_unconfigured_origin(settings):
    """Unexpected origins should not receive the allow-origin header."""
    response = _response_with_origin("https://unexpected.example", settings)

    assert "Access-Control-Allow-Origin" not in response


def test_admin_api_routes_do_not_override_standard_route_names():
    """The admin API mount should not change existing v1 route reversals."""
    assert reverse("feature-flag-list") == "/v1/feature-flags/"
    assert reverse("admin-api:feature-flag-list") == "/admin-api/v1/feature-flags/"


def test_session_middleware_uses_standard_cookie_by_default(settings):
    """Standard frontend requests should use the default Django session cookie."""
    middleware = SessionMiddleware(lambda request: HttpResponse())
    standard_cookie = _session_cookie(
        middleware, {"scope": "standard", "session_scope": "standard"}
    )
    admin_cookie = _session_cookie(
        middleware, {"scope": "admin", "session_scope": "admin"}
    )
    request = RequestFactory().get(
        "/v1/auth_check",
        HTTP_COOKIE=(
            f"{settings.SESSION_COOKIE_NAME}={standard_cookie}; "
            f"{settings.ADMIN_SESSION_COOKIE_NAME}={admin_cookie}"
        ),
    )

    middleware.process_request(request)

    assert request._tdp_session_cookie_name == settings.SESSION_COOKIE_NAME
    assert request.session["scope"] == "standard"


def test_session_middleware_uses_admin_cookie_for_admin_auth(settings):
    """Admin auth routes should use the admin session cookie."""
    middleware = SessionMiddleware(lambda request: HttpResponse())
    standard_cookie = _session_cookie(
        middleware, {"scope": "standard", "session_scope": "standard"}
    )
    admin_cookie = _session_cookie(
        middleware, {"scope": "admin", "session_scope": "admin"}
    )
    request = RequestFactory().get(
        "/admin-auth/auth_check",
        HTTP_COOKIE=(
            f"{settings.SESSION_COOKIE_NAME}={standard_cookie}; "
            f"{settings.ADMIN_SESSION_COOKIE_NAME}={admin_cookie}"
        ),
    )

    middleware.process_request(request)

    assert request._tdp_session_cookie_name == settings.ADMIN_SESSION_COOKIE_NAME
    assert request.session["scope"] == "admin"


def test_session_middleware_uses_admin_cookie_for_admin_oidc_callback(settings):
    """Versionless callbacks with admin OIDC state should use the admin session."""
    middleware = SessionMiddleware(lambda request: HttpResponse())
    standard_cookie = _session_cookie(
        middleware, {"scope": "standard", "session_scope": "standard"}
    )
    admin_cookie = _session_cookie(
        middleware,
        {
            "scope": "admin",
            "session_scope": "admin",
            "oidc_clients": {"admin-state": ADMIN_OIDC_CLIENT},
        },
    )
    request = RequestFactory().get(
        "/oidc/callback/",
        {"state": "admin-state"},
        HTTP_COOKIE=(
            f"{settings.SESSION_COOKIE_NAME}={standard_cookie}; "
            f"{settings.ADMIN_SESSION_COOKIE_NAME}={admin_cookie}"
        ),
    )

    middleware.process_request(request)

    assert request._tdp_session_cookie_name == settings.ADMIN_SESSION_COOKIE_NAME
    assert request.session["scope"] == "admin"


def test_session_middleware_ignores_service_header_for_standard_api(settings):
    """Client-controlled headers should not switch /v1 to the admin session."""
    middleware = SessionMiddleware(lambda request: HttpResponse())
    standard_cookie = _session_cookie(
        middleware, {"scope": "standard", "session_scope": "standard"}
    )
    admin_cookie = _session_cookie(
        middleware, {"scope": "admin", "session_scope": "admin"}
    )
    request = RequestFactory().get(
        "/v1/users/profile/",
        HTTP_X_SERVICE_NAME="tdp-admin",
        HTTP_COOKIE=(
            f"{settings.SESSION_COOKIE_NAME}={standard_cookie}; "
            f"{settings.ADMIN_SESSION_COOKIE_NAME}={admin_cookie}"
        ),
    )

    middleware.process_request(request)

    assert request._tdp_session_cookie_name == settings.SESSION_COOKIE_NAME
    assert request.session["scope"] == "standard"


def test_session_middleware_uses_admin_cookie_for_admin_api(settings):
    """Admin API routes should use the admin session cookie."""
    settings.ADMIN_API_PROXY_TOKEN = "server-only-token"
    middleware = SessionMiddleware(lambda request: HttpResponse())
    standard_cookie = _session_cookie(
        middleware, {"scope": "standard", "session_scope": "standard"}
    )
    admin_cookie = _session_cookie(
        middleware, {"scope": "admin", "session_scope": "admin"}
    )
    request = RequestFactory().get(
        "/admin-api/v1/users/profile/",
        HTTP_X_ADMIN_PROXY_TOKEN="server-only-token",
        HTTP_COOKIE=(
            f"{settings.SESSION_COOKIE_NAME}={standard_cookie}; "
            f"{settings.ADMIN_SESSION_COOKIE_NAME}={admin_cookie}"
        ),
    )

    middleware.process_request(request)

    assert request._tdp_session_cookie_name == settings.ADMIN_SESSION_COOKIE_NAME
    assert request.session["scope"] == "admin"


def test_session_middleware_rejects_admin_scope_on_standard_api(settings):
    """Admin signed sessions cannot authenticate standard API routes."""
    middleware = SessionMiddleware(lambda request: HttpResponse())
    admin_cookie = _session_cookie(
        middleware, {"scope": "admin", "session_scope": "admin"}
    )
    request = RequestFactory().get(
        "/v1/users/profile/",
        HTTP_COOKIE=f"{settings.SESSION_COOKIE_NAME}={admin_cookie}",
    )

    middleware.process_request(request)

    assert request.session.is_empty()


def test_session_middleware_rejects_standard_scope_on_admin_auth(settings):
    """Standard signed sessions cannot authenticate admin auth routes."""
    middleware = SessionMiddleware(lambda request: HttpResponse())
    standard_cookie = _session_cookie(
        middleware, {"scope": "standard", "session_scope": "standard"}
    )
    request = RequestFactory().get(
        "/admin-auth/auth_check",
        HTTP_COOKIE=f"{settings.ADMIN_SESSION_COOKIE_NAME}={standard_cookie}",
    )

    middleware.process_request(request)

    assert request.session.is_empty()


def test_session_middleware_rejects_admin_api_without_proxy_token(settings):
    """Direct admin API requests should fail before loading the admin session."""
    settings.ADMIN_API_PROXY_TOKEN = "server-only-token"
    middleware = SessionMiddleware(lambda request: HttpResponse())
    admin_cookie = _session_cookie(middleware, {"scope": "admin"})
    request = RequestFactory().get(
        "/admin-api/v1/users/profile/",
        HTTP_COOKIE=f"{settings.ADMIN_SESSION_COOKIE_NAME}={admin_cookie}",
    )

    response = middleware.process_request(request)

    assert response.status_code == 403
    assert request._tdp_session_cookie_name == settings.SESSION_COOKIE_NAME


def test_session_middleware_sets_admin_cookie_for_admin_auth(settings):
    """Modified admin auth sessions should be saved to the admin cookie."""
    middleware = SessionMiddleware(lambda request: HttpResponse())
    request = RequestFactory().get("/admin-auth/auth_check")
    middleware.process_request(request)
    request.session["scope"] = "admin"
    request.session["session_scope"] = "admin"

    response = middleware.process_response(request, HttpResponse())

    assert settings.ADMIN_SESSION_COOKIE_NAME in response.cookies
    assert settings.SESSION_COOKIE_NAME not in response.cookies


def test_session_middleware_varies_on_cookie_when_session_is_saved(settings):
    """Saved session responses must vary on Cookie to keep cached views safe."""
    middleware = SessionMiddleware(lambda request: HttpResponse())
    request = RequestFactory().get("/v1/feature-flags/")
    middleware.process_request(request)
    request.session["scope"] = "standard"

    response = middleware.process_response(request, HttpResponse())

    assert settings.SESSION_COOKIE_NAME in response.cookies
    assert "Cookie" in response["Vary"]


def test_login_dotgov_session_cookie_is_host_only(settings):
    """Login.gov session cookies should not be scoped to the parent domain."""
    settings.SESSION_COOKIE_DOMAIN = None
    settings.SESSION_COOKIE_SECURE = True
    settings.SESSION_COOKIE_HTTPONLY = True
    settings.SESSION_COOKIE_SAMESITE = "None"
    middleware = SessionMiddleware(lambda request: HttpResponse())
    request = RequestFactory().get("/login/dotgov")
    middleware.process_request(request)
    request.session["session_scope"] = "standard"

    response = middleware.process_response(request, HttpResponse())
    session_cookie = response.cookies[settings.SESSION_COOKIE_NAME]

    assert session_cookie["domain"] == ""
    assert session_cookie["secure"]
    assert session_cookie["httponly"]
    assert session_cookie["samesite"] == "None"


def _admin_api_response_for_user(user):
    middleware = AdminAPIAuthorizationMiddleware(lambda request: HttpResponse())
    request = RequestFactory().get("/admin-api/v1/users/profile/")
    request.session = {"session_scope": "admin"}
    request.user = user

    return middleware(request)


def test_admin_api_authorization_middleware_rejects_standard_session():
    """The trusted proxy path still requires an explicitly admin-scoped session."""
    middleware = AdminAPIAuthorizationMiddleware(lambda request: HttpResponse())
    request = RequestFactory().get("/admin-api/v1/users/profile/")
    request.session = {"session_scope": "standard"}
    request.user = SimpleNamespace(is_authenticated=True)

    response = middleware(request)

    assert response.status_code == 401


def test_admin_api_authorization_middleware_rejects_unapproved_admin_user():
    """Admin API middleware should require approved admin users."""
    user = SimpleNamespace(
        is_authenticated=True,
        is_staff=True,
        is_superuser=True,
        is_active=True,
        account_approval_status=AccountApprovalStatusChoices.PENDING,
    )

    response = _admin_api_response_for_user(user)

    assert response.status_code == 403


def test_admin_api_authorization_middleware_rejects_inactive_admin_user():
    """Admin API middleware should require active admin users."""
    user = SimpleNamespace(
        is_authenticated=True,
        is_staff=True,
        is_superuser=True,
        is_active=False,
        account_approval_status=AccountApprovalStatusChoices.APPROVED,
    )

    response = _admin_api_response_for_user(user)

    assert response.status_code == 403


def test_admin_api_authorization_middleware_allows_django_superuser():
    """Admin API middleware should not depend on the user's assigned role."""
    user = SimpleNamespace(
        is_authenticated=True,
        is_staff=True,
        is_superuser=True,
        is_active=True,
        account_approval_status=AccountApprovalStatusChoices.APPROVED,
    )

    response = _admin_api_response_for_user(user)

    assert response.status_code == 200
