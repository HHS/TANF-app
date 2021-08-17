"""Login.gov/logout is redirected to this endpoint end a django user session."""

from django.conf import settings
from django.contrib.auth import logout
from django.http import HttpResponseRedirect

from rest_framework.views import APIView


# logout user
class LogoutUser(APIView):
    """Define method to log out user from Django."""

    def get(self, request, *args, **kwargs):
        """Destroy user session."""
        logout(request)
        response = HttpResponseRedirect(settings.FRONTEND_BASE_URL + "/login")
        response.delete_cookie("id_token")
        return response
