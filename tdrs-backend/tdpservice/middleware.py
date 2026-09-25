"""Generic middleware for use across the TDP platform."""
import time

from django.conf import settings
from django.contrib.sessions.backends.base import UpdateError
from django.contrib.sessions.exceptions import SessionInterrupted
from django.contrib.sessions.middleware import (
    SessionMiddleware as DjangoSessionMiddleware,
)
from django.http import HttpResponseForbidden, JsonResponse
from django.utils.cache import add_never_cache_headers, patch_vary_headers
from django.utils.crypto import constant_time_compare
from django.utils.http import http_date

from prometheus_client import Counter

from tdpservice.request_attribution import (
    REQUEST_ATTRIBUTION_ATTRIBUTE,
    RequestAttribution,
)
from tdpservice.users.authorization import is_authorized_admin_user
from tdpservice.users.oidc import (
    ADMIN_OIDC_CLIENT,
    ADMIN_SESSION_SCOPE,
    STANDARD_SESSION_SCOPE,
)

ADMIN_AUTH_PREFIX = "/admin-auth/"
ADMIN_API_PREFIX = "/admin-api/"

API_REQUESTS_TOTAL = Counter(
    "tdp_api_requests_total",
    "Total Django API requests by backend-observed request source.",
    (
        "source",
        "auth_method",
        "client_id",
        "user_stt",
        "user_group",
        "method",
        "status_code",
        "view",
    ),
)


class RequestAttributionMetricsMiddleware(object):
    """Emit low-cardinality Prometheus metrics for API request attribution."""

    UNKNOWN_LABEL = "unknown"
    NONE_LABEL = "none"
    SKIPPED_PATH_PREFIXES = (
        "/admin/",
        "/prometheus/",
        "/redocs",
        "/swagger",
    )

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        """Record request attribution after the downstream response is known."""
        try:
            response = self.get_response(request)
        except Exception:
            self._record_request_attribution(request, 500)
            raise

        self._record_request_attribution(request, response.status_code)
        return response

    def _record_request_attribution(self, request, status_code):
        """Increment the request attribution counter for a completed request."""
        if not self._should_record_request(request):
            return

        user = getattr(request, "user", None)
        user_is_authenticated = bool(getattr(user, "is_authenticated", False))
        attribution = self._request_attribution(request, user_is_authenticated)
        status_code_label = str(status_code)

        resolver_match = getattr(request, "resolver_match", None)
        API_REQUESTS_TOTAL.labels(
            source=attribution.source,
            auth_method=attribution.auth_method,
            client_id=attribution.client_id,
            user_stt=attribution.user_stt,
            user_group=attribution.user_group,
            method=request.method.upper(),
            status_code=status_code_label,
            view=getattr(resolver_match, "view_name", None) or self.UNKNOWN_LABEL,
        ).inc()

    def _request_attribution(self, request, user_is_authenticated):
        """Return the attribution context for a request."""
        attribution = getattr(request, REQUEST_ATTRIBUTION_ATTRIBUTE, None)
        if attribution is not None:
            return attribution

        if self._authorization_header(request):
            return RequestAttribution(
                source="api_client",
                client_id=self.UNKNOWN_LABEL,
                auth_method="authorization_header",
            )

        if user_is_authenticated:
            return RequestAttribution(
                source="browser_session",
                auth_method="session",
            )

        return RequestAttribution()

    def _authorization_header(self, request):
        """Return the Authorization header value, if Django exposed one."""
        headers = getattr(request, "headers", None)
        if headers:
            authorization_header = headers.get("Authorization", "")
            if authorization_header:
                return authorization_header

        return (
            request.META.get("HTTP_AUTHORIZATION")
            or request.META.get("Authorization")
            or request.META.get("REDIRECT_HTTP_AUTHORIZATION")
            or ""
        )

    def _should_record_request(self, request):
        """Return whether the route should be included in API attribution metrics."""
        path = getattr(request, "path_info", None) or getattr(request, "path", "")
        if any(
            path == prefix.rstrip("/") or path.startswith(prefix)
            for prefix in self.SKIPPED_PATH_PREFIXES
        ):
            return False

        static_url = getattr(settings, "STATIC_URL", None)
        if static_url and path.startswith(static_url):
            return False

        media_url = getattr(settings, "MEDIA_URL", None)
        if media_url and path.startswith(media_url):
            return False

        return True


class NoCacheMiddleware(object):
    """Disable client caching with a Cache-Control header."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        """Add appropriate headers to the response before sending it out."""
        response = self.get_response(request)
        add_never_cache_headers(response)
        return response


class SessionMiddleware(DjangoSessionMiddleware):
    """Patch Django session handling for TDP cookie and CORS requirements."""

    def __init__(self, get_response):
        """Initialize the middleware with the configured session engine."""
        super().__init__(get_response)

    @staticmethod
    def _get_allowed_origin(request):
        """Return the request origin when it is allowed by CORS settings."""
        origin = request.headers.get("Origin")
        if not origin:
            return None

        if getattr(settings, "CORS_ORIGIN_ALLOW_ALL", False):
            return origin

        if origin in getattr(settings, "CORS_ALLOWED_ORIGINS", []):
            return origin

        return None

    @staticmethod
    def _path_matches_prefix(request, prefix):
        """Return whether the request path is at or under the prefix."""
        path = getattr(request, "path_info", request.path)

        return path == prefix.rstrip("/") or path.startswith(prefix)

    def _is_admin_auth_request(self, request):
        """Return whether this request belongs to admin auth."""
        return self._path_matches_prefix(request, ADMIN_AUTH_PREFIX)

    def _is_admin_api_request(self, request):
        """Return whether this request belongs to admin API proxying."""
        return self._path_matches_prefix(request, ADMIN_API_PREFIX)

    def _is_admin_oidc_callback_request(self, request):
        """Return whether a versionless OIDC callback belongs to admin auth."""
        path = getattr(request, "path_info", request.path)
        if path != "/oidc/callback/":
            return False

        state = request.GET.get("state")
        if not state:
            return False

        admin_session_key = request.COOKIES.get(settings.ADMIN_SESSION_COOKIE_NAME)
        if not admin_session_key:
            return False

        admin_session = self.SessionStore(admin_session_key)
        oidc_clients = admin_session.get("oidc_clients", {})

        return oidc_clients.get(state) == ADMIN_OIDC_CLIENT

    @staticmethod
    def _has_admin_proxy_token(request):
        """Return whether the request has the server-side admin proxy token."""
        expected_token = getattr(settings, "ADMIN_API_PROXY_TOKEN", "")
        request_token = request.headers.get("x-admin-proxy-token", "")

        return bool(
            expected_token and constant_time_compare(request_token, expected_token)
        )

    def _is_admin_session_request(self, request):
        """Return whether this request should use the admin session cookie."""
        return (
            self._is_admin_auth_request(request)
            or self._is_admin_oidc_callback_request(request)
            or (
                self._is_admin_api_request(request)
                and self._has_admin_proxy_token(request)
            )
        )

    def _get_session_cookie_name(self, request):
        """Return the session cookie name for this request."""
        if self._is_admin_session_request(request):
            return settings.ADMIN_SESSION_COOKIE_NAME
        return settings.SESSION_COOKIE_NAME

    def _get_expected_session_scope(self, request):
        """Return the signed session scope allowed for this request."""
        if self._is_admin_session_request(request):
            return ADMIN_SESSION_SCOPE
        return STANDARD_SESSION_SCOPE

    @staticmethod
    def _set_cors_allow_headers(response):
        """Set CORS allow headers from settings when not already provided."""
        if "Access-Control-Allow-Headers" in response:
            return

        response["Access-Control-Allow-Headers"] = ", ".join(
            getattr(settings, "CORS_ALLOW_HEADERS", [])
        )

    def process_request(self, request):
        """Load the request session from the request-scoped cookie name."""
        if self._is_admin_api_request(request) and not self._has_admin_proxy_token(
            request
        ):
            request._tdp_session_cookie_name = settings.SESSION_COOKIE_NAME
            return HttpResponseForbidden("Admin API proxy token is required.")

        cookie_name = self._get_session_cookie_name(request)
        request._tdp_session_cookie_name = cookie_name
        session_key = request.COOKIES.get(cookie_name)
        request.session = self.SessionStore(session_key)
        current_scope = request.session.get("session_scope")
        expected_scope = self._get_expected_session_scope(request)

        if current_scope != expected_scope and not (
            current_scope is None and expected_scope == STANDARD_SESSION_SCOPE
        ):
            request.session = self.SessionStore()

    def process_response(self, request, response):
        """Save the session and ensure cross-origin cookie headers are correct."""
        cookie_name = getattr(
            request,
            "_tdp_session_cookie_name",
            self._get_session_cookie_name(request),
        )

        try:
            accessed = request.session.accessed
            modified = request.session.modified
            empty = request.session.is_empty()
        except AttributeError:
            return self._augment_response_headers(request, response, cookie_name)

        if cookie_name in request.COOKIES and empty:
            response.delete_cookie(
                cookie_name,
                path=settings.SESSION_COOKIE_PATH,
                domain=settings.SESSION_COOKIE_DOMAIN,
                samesite=settings.SESSION_COOKIE_SAMESITE,
            )
            patch_vary_headers(response, ("Cookie",))
        else:
            need_vary_cookie = accessed
            if (modified or settings.SESSION_SAVE_EVERY_REQUEST) and not empty:
                if request.session.get_expire_at_browser_close():
                    max_age = None
                    expires = None
                else:
                    max_age = request.session.get_expiry_age()
                    expires_time = time.time() + max_age
                    expires = http_date(expires_time)

                if response.status_code < 500:
                    try:
                        request.session.save()
                    except UpdateError:
                        raise SessionInterrupted(
                            "The request's session was deleted before the request "
                            "completed. The user may have logged out in a "
                            "concurrent request, for example."
                        )

                    response.set_cookie(
                        cookie_name,
                        request.session.session_key,
                        max_age=max_age,
                        expires=expires,
                        domain=settings.SESSION_COOKIE_DOMAIN,
                        path=settings.SESSION_COOKIE_PATH,
                        secure=settings.SESSION_COOKIE_SECURE or None,
                        httponly=settings.SESSION_COOKIE_HTTPONLY or None,
                        samesite=settings.SESSION_COOKIE_SAMESITE,
                    )
                    need_vary_cookie = True
            if need_vary_cookie:
                patch_vary_headers(response, ("Cookie",))

        return self._augment_response_headers(request, response, cookie_name)

    def _augment_response_headers(self, request, response, cookie_name):
        """Add TDP-specific CORS and cookie attributes to the response."""
        allowed_origin = self._get_allowed_origin(request)
        if allowed_origin:
            response["Access-Control-Allow-Origin"] = allowed_origin
            patch_vary_headers(response, ("Origin",))
            self._set_cors_allow_headers(response)

        if cookie_name in response.cookies:
            response.cookies[cookie_name]["samesite"] = settings.SESSION_COOKIE_SAMESITE

        if settings.CSRF_COOKIE_NAME in response.cookies:
            response.cookies[settings.CSRF_COOKIE_NAME][
                "samesite"
            ] = settings.CSRF_COOKIE_SAMESITE
            if settings.CSRF_COOKIE_SECURE:
                response.cookies[settings.CSRF_COOKIE_NAME]["secure"] = True
        return response


class AdminAPIAuthorizationMiddleware:
    """Require Django admin authorization for admin API proxy requests."""

    def __init__(self, get_response):
        """Initialize the middleware."""
        self.get_response = get_response

    def __call__(self, request):
        """Reject admin API requests unless Django recognizes an admin user."""
        if SessionMiddleware._path_matches_prefix(request, ADMIN_API_PREFIX):
            if request.session.get("session_scope") != ADMIN_SESSION_SCOPE:
                return JsonResponse(
                    {
                        "authenticated": False,
                        "detail": "An admin-scoped session is required.",
                    },
                    status=401,
                )

            user = getattr(request, "user", None)

            if not getattr(user, "is_authenticated", False):
                return JsonResponse(
                    {
                        "authenticated": False,
                        "detail": "Admin authentication is required.",
                    },
                    status=401,
                )

            if not is_authorized_admin_user(user):
                return JsonResponse(
                    {
                        "authenticated": True,
                        "authorized": False,
                        "detail": "User is not authorized for the admin console.",
                    },
                    status=403,
                )

        return self.get_response(request)
