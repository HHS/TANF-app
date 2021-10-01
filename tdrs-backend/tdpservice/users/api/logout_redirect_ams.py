"""Handle logout requests for AMS OpenID."""

import secrets
from urllib.parse import quote_plus, urlencode

from django.conf import settings
from django.http import HttpResponseRedirect
from django.views.generic.base import RedirectView


class LogoutRedirectAMS(RedirectView):
    """Handle logout requests."""

    permanent = False
    query_string = True
    pattern_name = "ams-logout"

    """
    Redirects user to login.gov/logout with the needed query parameter strings

    """

    def get(self, request, *args, **kwargs):
        """Manage logout requests with AMS OpenID"""
        # generate a random secured hex string for the state parameter
        state = secrets.token_hex(32)

        token_hint = request.session.get("token", None)

        # if the token hint isn't found in the store,
        # default to the direct logout endpoint
        if token_hint is None:
            return HttpResponseRedirect(settings.BASE_URL + "/logout")

        # remove the token from the session store as it is no longer needed
        del request.session["token"]

        # params needed by the login.gov/logout endpoint
        logout_params = {
            "id_token_hint": token_hint,
            "post_logout_redirect_uri": settings.BASE_URL + "/logout",
            "state": state,
        }

        # escape params dict into a url encoded query string
        encoded_params = urlencode(logout_params, quote_via=quote_plus)

        # build out full API GET call to authorize endpoint
        logout_endpoint = settings.LOGIN_GOV_LOGOUT_ENDPOINT + "?" + encoded_params
        return HttpResponseRedirect(logout_endpoint)
