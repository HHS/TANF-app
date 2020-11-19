"""Handle authorization calls globally."""
import datetime
from django.conf import settings


class AuthUpdateMiddleware:
    """Update authorization cookie with new requests."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        """Update cookie."""
        response = self.get_response(request)
        now = datetime.datetime.now()
        timeout = now + datetime.timedelta(minutes=settings.SESSION_TIMEOUT)

        # if there is no user, the user is currently
        # in the authentication process so we can't
        # update the cookie yet
        if request.user.is_authenticated:
            id_token = request.COOKIES.get("id_token")
            response.set_cookie(
                "id_token",
                value=id_token,
                max_age=None,
                expires=timeout,
                path="/",
                domain=None,
                secure=True,
                httponly=True,
            )

        return response
