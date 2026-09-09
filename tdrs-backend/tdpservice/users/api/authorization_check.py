"""Check if user is authorized."""

import logging

from django.contrib.auth import logout
from django.http import HttpResponse
from django.middleware import csrf
from django.utils import timezone

from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from ..authorization import is_authorized_admin_user
from ..oidc import ADMIN_SESSION_SCOPE, STANDARD_SESSION_SCOPE
from ..serializers import UserProfileSerializer

logger = logging.getLogger(__name__)


class AuthorizationCheck(APIView):
    """Check if user is authorized."""

    query_string = False
    pattern_name = "authorization-check"
    permission_classes = [AllowAny]
    session_scope = STANDARD_SESSION_SCOPE
    allow_unscoped_session = True

    def has_valid_session_scope(self, request):
        """Return whether this endpoint can use the current signed session."""
        current_scope = request.session.get("session_scope")
        is_admin_api_request = (
            current_scope == ADMIN_SESSION_SCOPE
            and request.resolver_match
            and request.resolver_match.namespace == "admin-api"
        )
        return is_admin_api_request or current_scope == self.session_scope or (
            self.allow_unscoped_session and current_scope is None
        )

    def get(self, request, *args, **kwargs):
        """Handle get request and verify user is authorized."""
        logger.debug(
            f"{self.__class__.__name__}: {request} {request.user} {args} {kwargs}"
        )

        if not self.has_valid_session_scope(request):
            logger.warning(
                "Rejected %s session on %s",
                request.session.get("session_scope"),
                self.pattern_name,
            )
            return Response({"authenticated": False})

        user = request.user
        serializer = UserProfileSerializer(user, context={"request": request})

        if user.is_authenticated:
            # Check if the user is deactivated in our system before passing auth params.
            if user.is_deactivated:
                logout(request)
                response = Response({"authenticated": False, "inactive": True})
                response.delete_cookie("id_token")
                logger.info("Auth check FAIL for INACTIVE user on %s", timezone.now())
                return response

            auth_params = {
                "authenticated": True,
                "user": serializer.data,
                "csrf": csrf.get_token(request),
            }
            logger.info(
                "Auth check PASS for user: %s on %s", user.username, timezone.now()
            )
            res = Response(auth_params)
            res["Access-Control-Allow-Headers"] = "X-CSRFToken, Cookie, Set-Cookie"
            return res
        else:
            logger.info("Auth check FAIL for user on %s", timezone.now())
            return Response({"authenticated": False})


class AdminAuthorizationCheck(AuthorizationCheck):
    """Check if the current Django session is authorized for the admin console."""

    pattern_name = "admin-authorization-check"
    session_scope = ADMIN_SESSION_SCOPE
    allow_unscoped_session = False

    def get(self, request, *args, **kwargs):
        """Return authenticated and admin authorization state for the session."""
        response = super().get(request, *args, **kwargs)

        if not response.data.get("authenticated"):
            return response

        user = request.user
        is_admin = is_authorized_admin_user(user)

        response.data["authorized"] = is_admin
        response.data["csrf"] = csrf.get_token(request)

        if not is_admin:
            response.status_code = 403
            response.data["detail"] = "User is not authorized for the admin console."

        return response


class PlgAuthorizationCheck(APIView):
    """Check if user is authorized to view Grafana."""

    query_string = False
    pattern_name = "plg-authorization-check"
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        """Handle get request and verify user is authorized to access plg apps."""
        user = request.user

        user_in_valid_group = (
            user.is_ofa_sys_admin or user.is_developer or user.is_digit_team
        )

        if user_in_valid_group:
            return HttpResponse(status=200)
        else:
            logger.warning(
                f"User: {user} has incorrect authentication credentials. Not allowing access to Grafana."
            )
            return HttpResponse(status=401)
