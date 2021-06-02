"""Login.gov/authorize is redirected to this endpoint to start a django user session."""
import logging
import os

from django.contrib.auth import get_user_model, login
from django.core.exceptions import SuspiciousOperation
from django.http import HttpResponseRedirect
from django.utils import timezone

import jwt
import requests
from rest_framework import status
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.response import Response

from ..authentication import CustomAuthentication
from .utils import (
    get_nonce_and_state,
    generate_token_endpoint_parameters,
    generate_jwt_from_jwks,
    validate_nonce_and_state,
    response_redirect,
)

logger = logging.getLogger()
logger.setLevel(logging.INFO)


class InactiveUser(Exception):
    """Inactive User Error Handler."""

    pass


class TokenAuthorizationOIDC(ObtainAuthToken):
    """Define methods for handling login request from login.gov."""

    @staticmethod
    def decode_payload(id_token, options=None):
        """Decode the payload."""
        if not options:
            options = {'verify_nbf': False}

        cert_str = generate_jwt_from_jwks()

        # issuer: issuer of the response
        # subject : UUID - not useful for login.gov set options to ignore this
        try:
            decoded_payload = jwt.decode(
                id_token,
                key=cert_str,
                issuer=os.environ["OIDC_OP_ISSUER"],
                audience=os.environ["CLIENT_ID"],
                algorithms=["RS256"],
                subject=None,
                access_token=None,
                options=options,
            )
            return decoded_payload
        except jwt.ExpiredSignatureError:
            return {"error": "The token is expired."}

    def handle_user(self, request, id_token, decoded_payload):
        """Handle the incoming user."""
        # get user from database if they exist. if not, create a new one
        if "token" not in request.session:
            request.session["token"] = id_token

        # Authenticate users with the unique "subject" `sub` UUID from the payload.
        sub = decoded_payload["sub"]
        email = decoded_payload["email"]

        # First account for the initial superuser
        if (su_username := os.environ.get('DJANGO_SU_NAME')) and su_username == email:
            # If this is the initial login for the initial superuser,
            # we must authenticate with their username since we have yet to save the
            # user's `sub` UUID from the decoded payload, with which we will
            # authenticate later.
            initial_user = CustomAuthentication.authenticate(
                self, username=email
            )

            if initial_user.login_gov_uuid is None:
                # Save the `sub` to the superuser.
                initial_user.login_gov_uuid = sub
                initial_user.save()

                # Login with the new superuser.
                self.login_user(request, initial_user, "User Found")
                return initial_user

        # Authenticate with `sub` and not username, as user's can change their
        # corresponding emails externally.
        user = CustomAuthentication.authenticate(
            self, user_id=sub
        )

        if user and user.is_active:
            # User's are able to update their emails on login.gov
            # Update the User with the latest email from the decoded_payload.
            if user.username != email:
                user.email = email
                user.username = email
                user.save()

            self.login_user(request, user, "User Found")
        elif user and not user.is_active:
            raise InactiveUser(
                f'Login failed, user account is inactive: {user.username}'
            )
        else:
            User = get_user_model()
            user = User.objects.create_user(email, email=email, login_gov_uuid=sub)
            user.set_unusable_password()
            user.save()
            self.login_user(request, user, "User Created")

        return user

    def login_user(self, request, user, user_status):
        """Create a session for the associated user."""
        login(
            request,
            user,
            backend="tdpservice.users.authentication.CustomAuthentication",
        )
        logger.info("%s: %s on %s", user_status, user.username, timezone.now)

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
        nonce_and_state = get_nonce_and_state(request.session)
        nonce_validator = nonce_and_state.get("nonce", "not_nonce")
        state_validator = nonce_and_state.get("state", "not_state")

        # build out the query string parameters
        # and full URL path for OIDC token endpoint
        token_params = generate_token_endpoint_parameters(code)
        token_endpoint = os.environ["OIDC_OP_TOKEN_ENDPOINT"] + "?" + token_params
        token_response = requests.post(token_endpoint)

        if token_response.status_code != 200:
            return Response(
                {
                    "error": (
                        "Invalid Validation Code Or OpenID Connect Authenticator "
                        "Down!"
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        token_data = token_response.json()
        id_token = token_data.get("id_token")

        decoded_payload = self.decode_payload(id_token)
        if decoded_payload == {"error": "The token is expired."}:
            return Response(decoded_payload, status=status.HTTP_401_UNAUTHORIZED)

        decoded_nonce = decoded_payload["nonce"]

        if not validate_nonce_and_state(
            decoded_nonce, state, nonce_validator, state_validator
        ):
            msg = "Could not validate nonce and state"
            raise SuspiciousOperation(msg)

        if not decoded_payload["email_verified"]:
            return Response(
                {"error": "Unverified email!"}, status=status.HTTP_400_BAD_REQUEST
            )

        try:
            user = self.handle_user(request, id_token, decoded_payload)
            return response_redirect(user, id_token)

        except InactiveUser as e:
            logger.exception(e)
            return Response(
                {
                    "error": str(e)
                },
                status=status.HTTP_401_UNAUTHORIZED
            )

        except Exception as e:
            logger.exception(f"Error attempting to login/register user:  {e} at...")
            return Response(
                {
                    "error": (
                        "Email verified, but experienced internal issue "
                        "with login/registration."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
