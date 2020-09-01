"""Validation Check to esnure beaer token is valid."""
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.response import Response
from rest_framework import status


# consider adding throttling logic
class ValidateOIDCBearerToken(ObtainAuthToken):
    """Return error message on authentication failures."""

    def get(self, request, *args, **kwargs):
        """Ensure returned message is wrapped in a 400 error."""
        return Response(
            {"error": "Method not allowed."}, status=status.HTTP_400_BAD_REQUEST
        )
