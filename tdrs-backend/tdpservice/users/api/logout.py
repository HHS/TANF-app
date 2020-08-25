"""Login.gov/logout is redirected to this endpoint end a django user session."""

from django.contrib.auth import logout

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView


# logout user
class LogoutUser(APIView):
    """Define method to log out user from Django."""

    def get(self, request, *args, **kwargs):
        """Destroy user session."""
        try:
            logout(request)
        # TODO: Not sure what exceptions can actually occur here or why.
        # Can we just remove this?
        except Exception:  # pragma: nocover
            return Response(
                {
                    "system": (
                        "User logged out of Login.gov/ "
                        "Django sessions terminated before local logout"
                    )
                },
                status=status.HTTP_200_OK,
            )
        return Response({"system": "User logged out"}, status=status.HTTP_200_OK)
