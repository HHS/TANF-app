"""Define utility methods for users api."""

import logging
import os
import secrets
import time
from urllib.parse import quote_plus, urlencode

from django.core.exceptions import SuspiciousOperation

import jwt
import requests
from jwcrypto import jwk
from rest_framework import status
from rest_framework.response import Response

LOGGER = logging.getLogger(__name__)

"""
Stores the state and nonce generated on login in the the users session
:param request: current session between client and server
:param state: random string generated to verify API call to login.gov/authorize
:param nonce: random string generated to verify API call to login.gov/token
"""


def add_state_and_nonce_to_session(request, state, nonce):
    """Add state and nonce to session."""
    if "openid_authenticity_tracker" not in request.session or not isinstance(
        request.session["openid_authenticity_tracker"], dict
    ):
        request.session["openid_authenticity_tracker"] = {}

    limit = 1
    if len(request.session["openid_authenticity_tracker"]) >= limit:
        LOGGER.info(
            'User has more than {} "openid_authenticity_tracker" in his session, '
            "deleting the oldest one!".format(limit)
        )
        oldest_state = None
        oldest_added_on = time.time()
        for item_state, item in request.session["openid_authenticity_tracker"].items():
            if item["added_on"] < oldest_added_on:
                oldest_state = item_state
                oldest_added_on = item["added_on"]
        if oldest_state:
            del request.session["openid_authenticity_tracker"][oldest_state]

    request.session["openid_authenticity_tracker"][state] = {
        "nonce": nonce,
        "added_on": time.time(),
    }
    # Tell the session object explicitly that it has been modified by setting
    # the modified attribute on the session object:
    request.session.modified = True


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

:param self: parameter to permit django python to call a method within its own class
"""


def generate_client_assertion():
    """
    Generate client assertion parameters.

    :param JWT_KEY: private key expected by the login.gov application
    :param CLIENT_ID: Issuer as defined login.gov application
    """
    private_key = os.environ["JWT_KEY"]
    payload = {
        "iss": os.environ["CLIENT_ID"],
        "aud": os.environ["OIDC_OP_TOKEN_ENDPOINT"],
        "sub": os.environ["CLIENT_ID"],
        "jti": secrets.token_urlsafe(32)[:32],
        # set token experation to be 1 minute from current time
        "exp": int(round(time.time() * 1000)) + 60000,
    }
    encoded_jwt = jwt.encode(payload, key=private_key, algorithm="RS256")
    return encoded_jwt.decode("UTF-8")


"""
Generate a token to be passed to the login.gov/token endpoint

:param self: parameter to permit django python to call a method within its own class
:param code: value returned by a valid call to the login.gov/authorize endpoint
:return: query string parameters to call the login.gov/token endpoint
"""


def generate_token_endpoint_parameters(code):
    """Generate token parameters."""
    client_assertion = generate_client_assertion()
    params = {
        "client_assertion": client_assertion,
        "client_assertion_type": os.environ["CLIENT_ASSERTION_TYPE"],
        "code": code,
        "grant_type": "authorization_code",
    }
    encoded_params = urlencode(params, quote_via=quote_plus)
    return encoded_params


"""
Generate the public JWT key used to verify the token returned from login.gov/token
from the login.gov/certs endpoint

:param self: parameter to permit django python to call a method within its own class
"""


def generate_jwt_from_jwks():
    """Generate JWT."""
    certs_endpoint = os.environ["OIDC_OP_JWKS_ENDPOINT"]
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


def get_nonce_and_state(request):
    """Get the nonce and state values."""
    if "state_nonce_tracker" not in request.session:
        msg = "error: Could not find session store for nonce and state"
        raise SuspiciousOperation(msg)
    openid_authenticity_tracker = request.session.get("state_nonce_tracker", None)

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
        expires=None,
        path="/",
        domain=None,
        secure=True,
        httponly=True,
    )
    return response
