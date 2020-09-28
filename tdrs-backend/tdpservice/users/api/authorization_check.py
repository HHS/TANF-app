"""Handle logout requests."""
import logging

from rest_framework.response import Response
from rest_framework.views import APIView
from django.utils import timezone

logger = logging.getLogger()
logger.setLevel(logging.INFO)


class AuthorizationCheck(APIView):
    """Handle logout requests."""

    query_string = False
    pattern_name = "authorization-check"

    def get(self, request, *args, **kwargs):
        """Handle get request and authenticate user."""
        user = request.user
        if user.is_authenticated:
            auth_params = {
                "authenticated": True,
                "user": {
                    "email": user.username,
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                },
            }
            logger.info(
                "Auth check PASS for user: %s on %s", user.username, timezone.now()
            )
            return Response(auth_params)
        else:
            logger.info("Auth check FAIL for user on %s", timezone.now())
            return Response({"authenticated": False})
