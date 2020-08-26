"""Login.gov/authorize is redirected to this endpoint to start a django user session."""
import datetime
import logging
import os
import time

from django.contrib.auth import get_user_model, login
from django.core.exceptions import SuspiciousOperation
from django.http import HttpResponseRedirect

import jwt
import requests
from rest_framework import status
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.response import Response

from ..authentication import CustomAuthentication
from . import utils

logger = logging.getLogger()
logger.setLevel(logging.INFO)
logger.addHandler(logging.StreamHandler())


class TokenAuthorizationOIDC(ObtainAuthToken):
    """Define methods for handling login request from login.gov."""

    def get(self, request, *args, **kwargs):
        """Handle decoding auth token and authenticate user."""
        code = request.GET.get("code", None)
        state = request.GET.get("state", None)

        if code is None:
            logger.info("Redirecting call to main page. No code provided.")
            return HttpResponseRedirect(os.environ["FRONTEND_BASE_URL"])

        if state is None:
            logger.info("Redirecting call to main page. No state provided.")
            return HttpResponseRedirect(os.environ["FRONTEND_BASE_URL"])

        # get the validation keys to confirm generated nonce and state
        nonce_and_state = utils.get_nonce_and_state(request)  # pragma: no cover
        nonce_validator = nonce_and_state.get("nonce", "not_nonce")  # pragma: no cover
        state_validator = nonce_and_state.get("state", "not_state")  # pragma: no cover

        # build out the query string parameters
        # and full URL path for OIDC token endpoint
        token_params = utils.generate_token_endpoint_parameters(code)  # pragma: no cover
        token_endpoint = os.environ["OIDC_OP_TOKEN_ENDPOINT"] + "?" + token_params  # pragma: no cover
        token_response = requests.post(token_endpoint)  # pragma: no cover

        if token_response.status_code != 200:  # pragma: no cover
            return Response(
                {
                    "error": (
                        "Invalid Validation Code Or OpenID Connect Authenticator "
                        "Down!"
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        token_data = token_response.json()  # pragma: no cover
        id_token = token_data.get("id_token")  # pragma: no cover
        cert_str = utils.generate_jwt_from_jwks()  # pragma: no cover

        # issuer: issuer of the response
        # subject : UUID - not useful for login.gov set options to ignore this
        decoded_payload = jwt.decode(
            id_token,
            key=cert_str,
            issuer=os.environ["OIDC_OP_ISSUER"],
            audience=os.environ["CLIENT_ID"],
            algorithm="RS256",
            subject=None,
            access_token=None,
            options={"verify_nbf": False},
        )  # pragma: no cover
        decoded_nonce = decoded_payload["nonce"]  # pragma: no cover

        if not utils.validate_nonce_and_state(
            decoded_nonce, state, nonce_validator, state_validator
        ):  # pragma: no cover
            msg = "Could not validate nonce and state"
            raise SuspiciousOperation(msg)

        if not decoded_payload["email_verified"]:  # pragma: no cover
            return Response(
                {"error": "Unverified email!"}, status=status.HTTP_400_BAD_REQUEST
            )

        try:  # pragma: no cover
            # get user from database if they exist. if not, create a new one
            if "token" not in request.session:
                request.session["token"] = id_token

            user = CustomAuthentication.authenticate(
                self, username=decoded_payload["email"]
            )
            if user is not None:
                login(
                    request,
                    user,
                    backend="tdpservice.users.authentication.CustomAuthentication",
                )
                datetime_time = datetime.datetime.fromtimestamp(time.time())
                logger.info(f"Found User:  {user.username} on {datetime_time}(UTC)")

                return utils.response_redirect(user, id_token)
            else:
                User = get_user_model()
                user = User.objects.create_user(decoded_payload["email"])
                user.set_unusable_password()
                user.save()

                login(
                    request,
                    user,
                    backend="tdpservice.users.authentication.CustomAuthentication",
                )

                datetime_time = datetime.datetime.fromtimestamp(time.time())
                logger.info(f"Created User:  {user.username} at {datetime_time}(UTC)")

                return utils.response_redirect(user, id_token)

        except Exception as e:
            logger.info(f"Error attempting to login/registeruser:  {e} at...")
            return Response(
                {
                    "error": (
                        "Email verfied, but experienced internal issue "
                        "with login/registration."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
