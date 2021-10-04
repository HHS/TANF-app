"""Handle login requests for AMS OpenID"""

import secrets
import requests
import time
from urllib.parse import quote_plus, urlencode

from django.conf import settings
from django.http import HttpResponseRedirect
from django.views.generic.base import RedirectView


def get_ams_configuration():
    """Get and pass on the AMS configuration, which includes currently published URLs
    for authorization, token, etc..
    """
    r = requests.get(settings.AMS_CONFIGURATION_ENDPOINT)
    data = r.json()
    return data


class LoginRedirectAMS(RedirectView):
    """Handle login workflow with AMS OpenID."""

    permanent = False
    query_string = True
    pattern_name = "ams-auth"

    """
    Calls the AMS configuration endpoint to get additional relevant endpoints and info.
    
    Redirects user to the acs ams authorization endpoint with the needed query parameter strings

    :param self: parameter to permit django python to call a method within its own class
    :param request: current session between client and server
    :param args: helper value in the event any additional unknown arguments
        need to be passed in
    :param kwargs: helper value in the event any additional unknown
        key value pairs need to be passed in
    """

    def get(self, request, *args, **kwargs):
        """Get request and manage login information with AMS OpenID."""

        configuration = get_ams_configuration()

        state = secrets.token_hex(32)
        nonce = secrets.token_hex(32)

        auth_params = {
            "client_id": settings.AMS_CLIENT_ID,
            "nonce": nonce,
            "redirect_uri": settings.BASE_URL + "/login",
            "response_type": "code",
            "state ": state,
            "scope": "openid"
        }

        # escape params dict into a url encoded query string
        encoded_params = urlencode(auth_params, quote_via=quote_plus)

        # build out full API GET call to authorize endpoint
        auth_endpoint = (
            configuration.authorization_endpoint + "?" + encoded_params
        )

        # update the user session so OIDC logout URL has token_hint
        request.session["state_nonce_tracker"] = {
            "nonce": nonce,
            "state": state,
            "added_on": time.time(),
        }

        return HttpResponseRedirect(auth_endpoint)
