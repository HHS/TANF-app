"""Handle login requests."""

import os
import secrets
import time
from urllib.parse import quote_plus, urlencode

from django.http import HttpResponseRedirect
from django.views.generic.base import RedirectView


class LoginRedirectOIDC(RedirectView):
    """Handle login workflow with login.gov."""

    permanent = False
    query_string = True
    pattern_name = "oidc-auth"

    """
    Redirects user to login.gov/authorize with the needed query parameter strings

    :param self: parameter to permit django python to call a method within its own class
    :param request: current session between client and server
    :param args: helper value in the event any additional unknown arguments
        need to be passed in
    :param kwargs: helper value in the event any additional unknown
        key value pairs need to be passed in
    """

    def get(self, request, *args, **kwargs):
        """Get request and manage login information with login.gov."""
        state = secrets.token_hex(32)
        nonce = secrets.token_hex(32)
        auth_params = {
            "acr_values": os.environ["ACR_VALUES"],
            "client_id": os.environ["CLIENT_ID"],
            "nonce": nonce,
            "prompt": "select_account",
            "redirect_uri": os.environ["BASE_URL"] + "/login",
            "response_type": "code",
            "state": state,
        }
        # login.gov expects unescaped '+' value for scope parameter
        auth_scope = "&scope=openid+email"

        # escape params dict into a url encoded query string
        encoded_params = urlencode(auth_params, quote_via=quote_plus)

        # build out full API GET call to authorize endpoint
        auth_endpoint = (
            os.environ["OIDC_OP_AUTHORIZATION_ENDPOINT"] + "?" + encoded_params
        )
        auth_endpoint_scope = auth_endpoint + "&" + auth_scope

        # update the user session so OIDC logout URL has token_hint
        request.session["state_nonce_tracker"] = {
            "nonce": nonce,
            "state": state,
            "added_on": time.time(),
        }

        return HttpResponseRedirect(auth_endpoint_scope)
