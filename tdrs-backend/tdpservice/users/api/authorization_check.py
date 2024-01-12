"""Check if user is authorized."""

import logging
from django.contrib.auth import logout
from django.middleware import csrf
from django.utils import timezone
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from ..serializers import UserProfileSerializer
from django.http import HttpResponse, HttpResponseRedirect
from django.conf import settings
import urllib

logger = logging.getLogger(__name__)


class AuthorizationCheck(APIView):
    """Check if user is authorized."""

    query_string = False
    pattern_name = "authorization-check"
    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        """Handle get request and verify user is authorized."""
        user = request.user
        serializer = UserProfileSerializer(user)

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

class KibanaAuthorizationCheck(APIView):
    """Check if user is authorized to view Kibana."""

    query_string = False
    pattern_name = "kibana-authorization-check"
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        """Handle get request and verify user is authorized to access kibana."""
        logger.debug("INSIDE KibanaAuthorizationCheck.")
        user = request.user

        user_in_valid_group = user.is_ofa_sys_admin or user.is_ofa_admin

        logger.debug(f"\nIS OFA SYS AD: {user.is_ofa_sys_admin}, IS OFA AD: {user.is_ofa_admin}, " +
                     f"HHS ID: {user.hhs_id}\n")

        if (user.hhs_id is not None and user_in_valid_group) or settings.BYPASS_KIBANA_AUTH:
            logger.debug("\nSUCCESSFULLY AUTHENTICATED USER. RETURNING 200 CODE FOR AUTH ENDPOINT.\n\n")
            return HttpResponse(status=200)
        else:
            logger.debug("\nUSER AUTHENTICATION CREDENTIALS INCORRECT. RETURNING 401 CODE FOR AUTH ENDPOINT\n\n")
            return HttpResponse(status=401)
