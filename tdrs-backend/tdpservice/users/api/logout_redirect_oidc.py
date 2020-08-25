"""Handle logout requests."""

import os
import secrets
from urllib.parse import quote_plus, urlencode

from django.http import HttpResponseRedirect
from django.views.generic.base import RedirectView


class LogoutRedirectOIDC(RedirectView):
    """Handle logout requests."""

    permanent = False
    query_string = True
    pattern_name = "oidc-logout"

    """
    Redirects user to login.gov/logout with the needed query parameter strings

    :param self: parameter to permit django python to call a method within its own class
    :param request: contains a session keeping track of the value needed for
        the token_hint
    :param args: helper value in the event any additional unknown arguments need
        to be passed in
    :param kwargs: helper value in the event any additional unknown key value pairs
        need to be passed in
    """

    def get(self, request, *args, **kwargs):
        """Manage logout requests with login.gov."""
        # generate a random secured hex string for the state parameter
        state = secrets.token_hex(32)

        token_hint = request.session.get("token", None)

        # if the token hint isn't found in the store,
        # default to the direct logout endpoint
        if token_hint is None:
            return HttpResponseRedirect(os.environ["BASE_URL"] + "/logout")

        # remove the token from the session store as it is no longer needed
        del request.session["token"]

        # params needed by the login.gov/logout endpoint
        logout_params = {
            "id_token_hint": token_hint,
            "post_logout_redirect_uri": os.environ["BASE_URL"] + "/logout",
            "state": state,
        }

        # escape params dict into a url encoded query string
        encoded_params = urlencode(logout_params, quote_via=quote_plus)

        # build out full API GET call to authorize endpoint
        logout_endpoint = os.environ["OIDC_OP_LOGOUT_ENDPOINT"] + "?" + encoded_params
        return HttpResponseRedirect(logout_endpoint)
