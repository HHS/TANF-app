"""Handle logout requests."""
import datetime
import logging
import time

from rest_framework.response import Response
from rest_framework.views import APIView

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
            auth_params = {"authenticated": True, "user": {"email": user.username}}
            datetime_time = datetime.datetime.fromtimestamp(time.time())
            logger.info(
                f"Auth check PASS for user:  {user.username} on {datetime_time}(UTC)"
            )
            return Response(auth_params)
        else:
            datetime_time = datetime.datetime.fromtimestamp(time.time())
            logger.info(
                f"Auth check FAIL for user: {request.items()} on {datetime_time}(UTC)"
            )
            return Response({"authenticated": False})
