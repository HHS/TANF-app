
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.response import Response
from rest_framework import status


# consider adding throttling logic
class ValidateOIDCBearerToken(ObtainAuthToken):

    def get(self, request, *args, **kwargs):
        return Response({"error": "Method not allowed."}, status=status.HTTP_400_BAD_REQUEST)
