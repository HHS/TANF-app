"""Handle authorization calls globally."""
import datetime

now = datetime.datetime.now()
timeout = now + datetime.timedelta(minutes=10)

class AuthUpdateMiddleware:
    """Update authorization cookie with new requests."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        """Update cookie."""
        response = self.get_response(request)
        user = getattr(request, "user", None)

        # if there is no user, the user is currently
        # in the authentication process so we can't
        # update the cookie yet
        if user:
            id_token = getattr(request, "id_token", None)
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
