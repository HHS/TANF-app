"""Tests for project middleware."""

from types import SimpleNamespace

from django.http import HttpResponse
from django.test import RequestFactory
from django.urls import reverse

from tdpservice.middleware import AdminAPIAuthorizationMiddleware, SessionMiddleware
from tdpservice.users.models import AccountApprovalStatusChoices


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
        response["Access-Control-Allow-Origin"]
        == "https://admin.tanfdata.acf.hhs.gov"
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
        is_ofa_sys_admin=True,
        is_active=True,
        account_approval_status=AccountApprovalStatusChoices.PENDING,
    )

    response = _admin_api_response_for_user(user)

    assert response.status_code == 403


def test_admin_api_authorization_middleware_rejects_inactive_admin_user():
    """Admin API middleware should require active admin users."""
    user = SimpleNamespace(
        is_authenticated=True,
        is_ofa_sys_admin=True,
        is_active=False,
        account_approval_status=AccountApprovalStatusChoices.APPROVED,
    )

    response = _admin_api_response_for_user(user)

    assert response.status_code == 403
