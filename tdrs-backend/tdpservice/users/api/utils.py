"""Define utility methods for users test_api."""

import binascii
import logging
import secrets
import time
import datetime
from base64 import b64decode
from urllib.parse import quote_plus, urlencode

from django.core.exceptions import SuspiciousOperation
from django.http import HttpResponseRedirect

import jwt
import requests
from jwcrypto import jwk
from rest_framework import status
from rest_framework.response import Response
from django.conf import settings

logger = logging.getLogger()
logger.setLevel(logging.INFO)
now = datetime.datetime.now()
timeout = now + datetime.timedelta(minutes=settings.SESSION_TIMEOUT)

"""
Validate the nonce and state returned by login.gov API calls match those
originated by the request

:param self: parameter to permit django python to call a method within its own class
:param decoded_nonce: nonce found from the decoded token returned by call
    to login.gov/token
:param state: state value returned by the call to login.gov/authorize
:param nonce_validator: the original nonce value created by login_redirect_oidc.py
:param state_validator: the original state value created by login_redirect_oidc.py
"""


def validate_nonce_and_state(decoded_nonce, state, nonce_validator, state_validator):
    """Validate nonce and state are correct values."""
    return decoded_nonce == nonce_validator and state == state_validator


"""
Generate the client_assertion parameter needed by the login.gov/token endpoint
"""


def generate_login_gov_client_assertion():
    """
    Generate client assertion parameters for login.gov.
    """
    private_key = settings.LOGIN_GOV_JWT_KEY

    # We allow the JWT_KEY to be passed in as base64 encoded or as the
    # raw PEM format to support docker-compose env_file where there are
    # issues with newlines in env vars
    # https://github.com/moby/moby/issues/12997
    try:
        private_key = b64decode(private_key).decode("utf-8")
    except (UnicodeDecodeError, binascii.Error):
        # If the private_key couldn't be Base64 decoded then just try it as
        # configured, in order to handle PEM format keys.
        pass

    payload = {
        "iss": settings.LOGIN_GOV_CLIENT_ID,
        "aud": settings.LOGIN_GOV_TOKEN_ENDPOINT,
        "sub": settings.LOGIN_GOV_CLIENT_ID,
        "jti": secrets.token_urlsafe(32)[:32],
        # set token expiration to be 1 minute from current time
        "exp": int(round(time.time() * 1000)) + 60000,
    }
    return jwt.encode(payload, key=private_key, algorithm="RS256")


"""
Generate the client_assertion parameter needed by the login.gov/token endpoint

"""


def generate_ams_client_assertion(ams_token_endpoint: str):
    """
    Generate client assertion parameters for AMS.
    :param ams_token_endpoint: The token auth endpoint returned in the ams configuration.
    """
    private_key = settings.AMS_CLIENT_SECRET

    # We allow the JWT_KEY to be passed in as base64 encoded or as the
    # raw PEM format to support docker-compose env_file where there are
    # issues with newlines in env vars
    # https://github.com/moby/moby/issues/12997
    try:
        private_key = b64decode(private_key).decode("utf-8")
    except (UnicodeDecodeError, binascii.Error):
        # If the private_key couldn't be Base64 decoded then just try it as
        # configured, in order to handle PEM format keys.
        pass

    payload = {
        "iss": settings.AMS_CLIENT_ID,
        "aud": ams_token_endpoint,
        "sub": settings.AMS_CLIENT_ID,
        "jti": secrets.token_urlsafe(32)[:32],
        # set token expiration to be 1 minute from current time
        "exp": int(round(time.time() * 1000)) + 60000,
    }
    return jwt.encode(payload, key=private_key, algorithm="RS256")


"""
Generate a token to be passed to the login.gov/token endpoint

:param self: parameter to permit django python to call a method within its own class
:param code: value returned by a valid call to the login.gov/authorize endpoint
:return: query string parameters to call the login.gov/token endpoint
"""


def generate_token_endpoint_parameters(code, options=None):
    """Generate token parameters."""
    params = {
        "code": code,
        "grant_type": "authorization_code",
        **options
    }
    encoded_params = urlencode(params, quote_via=quote_plus)
    return encoded_params


"""
Generate the public JWT key used to verify the token returned from login.gov/token
from the login.gov/certs endpoint

:param self: parameter to permit django python to call a method within its own class
"""


def generate_jwt_from_jwks(certs_endpoint):
    """Generate JWT."""
    certs_response = requests.get(certs_endpoint)
    public_cert = jwk.JWK(**certs_response.json().get("keys")[0])
    public_pem = public_cert.export_to_pem()
    return public_pem


"""
Get the original nonce and state from the user session

:param self: parameter to permit django python to call a method within its own class
:param request: retains current user session keeping track original the state
    and nonce
"""


def get_nonce_and_state(session):
    """Get the nonce and state values."""
    if "state_nonce_tracker" not in session:
        msg = "error: Could not find session store for nonce and state"
        raise SuspiciousOperation(msg)

    openid_authenticity_tracker = session.get("state_nonce_tracker", None)

    if "state" not in openid_authenticity_tracker:
        msg = "OIDC callback state was not found in session."
        raise SuspiciousOperation(msg)

    state = openid_authenticity_tracker.get("state", None)

    if "nonce" not in openid_authenticity_tracker:
        msg = "OIDC callback nonce was not found in session `state_nonce_tracker`."
        raise SuspiciousOperation(msg)

    nonce = openid_authenticity_tracker.get("nonce", None)
    validation_keys = {"state": state, "nonce": nonce}
    return validation_keys


"""
Returns a found users information along with an httpOnly cookie.

:param self: parameter to permit django python to call a method within its own class
:param user: current user associated with this session
:param status_message: Helper message to note how the user was found
:param id_token: encoded token returned by login.gov/token
"""


def response_internal(user, status_message, id_token):
    """Respond with an httpOnly cookie to secure the session with the client."""
    response = Response(
        {"user_id": user.pk, "email": user.username, "status": status_message},
        status=status.HTTP_200_OK,
    )
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


def response_redirect(self, id_token):
    """
    Redirects to web app with an httpOnly cookie.

    :param self: parameter to permit django python to call a method within its own class
    :param id_token: encoded token returned by login.gov/token
    """
    response = HttpResponseRedirect(settings.FRONTEND_BASE_URL + "/login")
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
