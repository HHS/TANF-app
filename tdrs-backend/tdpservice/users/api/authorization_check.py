"""Handle logout requests."""

from rest_framework.response import Response
from rest_framework.views import APIView


class AuthorizationCheck(APIView):
    """Handle logout requests."""

    query_string = False
    pattern_name = 'authorization-check'

    def get(self, request, *args, **kwargs):
        """Handle get request and authenticate user."""
        user = request.user
        if user.is_authenticated:
            auth_params = {
                'authenticated': True,
                'user': {'email': user.username}
            }
            return Response(auth_params)
        else:
            return Response({'authenticated': False})
