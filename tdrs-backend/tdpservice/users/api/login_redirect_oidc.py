"""Handle login requests."""

import logging
import requests
import secrets
import time
from urllib.parse import quote_plus, urlencode

from django.conf import settings
from django.http import HttpResponseRedirect
from django.views.generic.base import RedirectView

logger = logging.getLogger(__name__)


class LoginRedirectLoginDotGov(RedirectView):
    """Handle login workflow for login.gov clients."""

    permanent = False
    query_string = True
    pattern_name = "oidc-logindotgov"

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
        """Handle login workflow based on request origin."""
        # Create state and nonce to track requests
        state = secrets.token_hex(32)
        nonce = secrets.token_hex(32)

        """Get request and manage login information with login.gov."""
        auth_params = {
            "acr_values": settings.LOGIN_GOV_ACR_VALUES,
            "client_id": settings.LOGIN_GOV_CLIENT_ID,
            "nonce": nonce,
            "prompt": "select_account",
            "redirect_uri": settings.BASE_URL + "/login",
            "response_type": "code",
            "state": state,
        }

        # escape params dict into a url encoded query string
        encoded_params = urlencode(auth_params, quote_via=quote_plus)

        # build out full API GET call to authorize endpoint
        auth_endpoint = (
            settings.LOGIN_GOV_AUTHORIZATION_ENDPOINT + "?" + encoded_params
        )

        # login.gov expects unescaped '+' value for scope parameter
        auth_endpoint_with_scope = auth_endpoint + "&scope=openid+email"

        # update the user session so OIDC logout URL has token_hint
        request.session["state_nonce_tracker"] = {
            "nonce": nonce,
            "state": state,
            "added_on": time.time(),
        }

        return HttpResponseRedirect(auth_endpoint_with_scope)


class LoginRedirectAMS(RedirectView):
    """Handle login workflow for login.gov clients."""

    permanent = False
    query_string = True
    pattern_name = "oidc-ams"

    """
    Redirects user to AMS openid with the needed query parameter strings

    :param self: parameter to permit django python to call a method within its own class
    :param request: current session between client and server
    :param args: helper value in the event any additional unknown arguments
        need to be passed in
    :param kwargs: helper value in the event any additional unknown
        key value pairs need to be passed in
    """

    @staticmethod
    def get_ams_configuration():
        """Get and pass on the AMS configuration.

        Includes currently published URLs for authorization, token, etc.
        """
        r = requests.get(settings.AMS_CONFIGURATION_ENDPOINT)
        data = r.json()
        return data

    def get(self, request, *args, **kwargs):
        """Handle login workflow based on request origin."""
        # Create state and nonce to track requests
        state = secrets.token_hex(32)
        nonce = secrets.token_hex(32)

        """Get request and manage login information with AMS OpenID."""
        configuration = self.get_ams_configuration()

        auth_params = {
            "client_id": settings.AMS_CLIENT_ID,
            "nonce": nonce,
            "redirect_uri": settings.BASE_URL + "/oidc/ams",
            "response_type": "code",
            "state": state,
        }

        # escape params dict into a url encoded query string
        encoded_params = urlencode(auth_params, quote_via=quote_plus)

        # build out full API GET call to authorize endpoint
        auth_endpoint = (
            configuration["authorization_endpoint"] + "?" + encoded_params
        )

        auth_endpoint_with_scope = auth_endpoint + "&scope=openid+email"

        # update the user session so OIDC logout URL has token_hint
        request.session["state_nonce_tracker"] = {
            "nonce": nonce,
            "state": state,
            "added_on": time.time(),
            "ams": True
        }

        logger.info(encoded_params)

        return HttpResponseRedirect(auth_endpoint_with_scope)
