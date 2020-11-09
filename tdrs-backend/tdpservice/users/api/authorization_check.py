"""Handle logout requests."""
import logging

from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from django.middleware import csrf
from django.utils import timezone
from ..serializers import UserProfileSerializer

logger = logging.getLogger()
logger.setLevel(logging.INFO)


class AuthorizationCheck(APIView):
    """Handle logout requests."""

    query_string = False
    pattern_name = "authorization-check"
    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        """Handle get request and authenticate user."""
        user = request.user
        serializer = UserProfileSerializer(user)
        if user.is_authenticated:
            auth_params = {
                "authenticated": True,
                "user": serializer.data,
                "csrf": csrf.get_token(request),
            }
            logger.info(
                "Auth check PASS for user: %s on %s", user.username, timezone.now()
            )
            res = Response(auth_params)
            res['Access-Control-Allow-Headers'] = "X-CSRFToken"
            return res
        else:
            logger.info("Auth check FAIL for user on %s", timezone.now())
            return Response({"authenticated": False})
