"""Login.gov/authorize is redirected to this endpoint to start a django user session."""
import logging

from django.conf import settings
from django.contrib.auth import get_user_model, login
from django.core.exceptions import SuspiciousOperation
from django.http import HttpResponseRedirect
from django.utils import timezone

import jwt
import requests
from rest_framework import status
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.response import Response

from .login_redirect_oidc import LoginRedirectOIDC
from ..authentication import CustomAuthentication
from .utils import (
    get_nonce_and_state,
    generate_token_endpoint_parameters,
    generate_jwt_from_jwks,
    validate_nonce_and_state,
    response_redirect, generate_client_assertion,
)

logger = logging.getLogger()
logger.setLevel(logging.INFO)


class InactiveUser(Exception):
    """Inactive User Error Handler."""

    pass


class TokenAuthorizationOIDC(ObtainAuthToken):
    """Define methods for handling login request from login.gov."""

    def get(self, request, *args, **kwargs):
        """Handle decoding auth token and authenticate user."""
        code = request.GET.get("code", None)
        state = request.GET.get("state", None)

        if code is None:
            logger.info("Redirecting call to main page. No code provided.")
            return HttpResponseRedirect(settings.FRONTEND_BASE_URL)

        if state is None:
            logger.info("Redirecting call to main page. No state provided.")
            return HttpResponseRedirect(settings.FRONTEND_BASE_URL)

        token_response = self.get_token_response(request, code)

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

        decoded_payload = self.validate_and_decode_payload(request, id_token, state)

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

    def get_token_response(self, request, code):
        # Get request origin to handle login appropriately
        origin = request.headers['Origin']
        if 'login.gov' in origin:
            return self.handle_login_gov_token(request, code)
        else:
            return self.handle_ams_token(request, code)

    def handle_login_gov_token(self, code):
        # build out the query string parameters
        # and full URL path for OIDC token endpoint
        options = {
            "client_assertion": generate_client_assertion(),
            "client_assertion_type": settings.LOGIN_GOV_CLIENT_ASSERTION_TYPE
        }
        token_params = generate_token_endpoint_parameters(code, options)
        token_endpoint = settings.LOGIN_GOV_TOKEN_ENDPOINT + "?" + token_params
        return requests.post(token_endpoint)

    def handle_ams_token(self, code):
        ams_configuration = LoginRedirectOIDC.get_ams_configuration()
        token_params = generate_token_endpoint_parameters(code)
        token_endpoint = ams_configuration["token_endpoint"] + "?" + token_params
        # TODO Add params with code in utils?
        return requests.post(token_endpoint)

    def validate_and_decode_payload(self, request, id_token, state):
        decoded_payload = self.decode_payload(request, id_token)

        if decoded_payload == {"error": "The token is expired."}:
            return Response(decoded_payload, status=status.HTTP_401_UNAUTHORIZED)

        # get the validation keys to confirm generated nonce and state
        nonce_and_state = get_nonce_and_state(request.session)
        nonce_validator = nonce_and_state.get("nonce", "not_nonce")
        state_validator = nonce_and_state.get("state", "not_state")

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

        return decoded_payload

    def decode_payload(self, request, id_token, options=None):
        """Decode the payload."""
        origin = request.headers['Origin']
        if 'login.gov' in origin:
            return self.decode_payload_login_gov(id_token, options)
        else:
            return self.decode_payload_ams(id_token, options)

    @staticmethod
    def decode_payload_login_gov(id_token, options=None):
        """Decode the payload with keys for login.gov."""
        if not options:
            options = {'verify_nbf': False}

        certs_endpoint = settings.LOGIN_GOV_JWKS_ENDPOINT
        cert_str = generate_jwt_from_jwks(certs_endpoint)

        # issuer: issuer of the response
        # subject : UUID - not useful for login.gov set options to ignore this
        try:
            decoded_payload = jwt.decode(
                id_token,
                key=cert_str,
                issuer=settings.LOGIN_GOV_ISSUER,
                audience=settings.LOGIN_GOV_CLIENT_ID,
                algorithms=["RS256"],
                subject=None,
                access_token=None,
                options=options,
            )
            return decoded_payload
        except jwt.ExpiredSignatureError:
            return {"error": "The token is expired."}

    def decode_payload_ams(self, id_token, options=None):
        """Decode the payload with keys for AMS."""
        if not options:
            options = {'verify_nbf': False}

        ams_configuration = LoginRedirectOIDC.get_ams_configuration()
        certs_endpoint = ams_configuration["jwks_uri"]
        cert_str = generate_jwt_from_jwks(certs_endpoint)

        # issuer: issuer of the response
        try:
            decoded_payload = jwt.decode(
                id_token,
                key=cert_str,
                issuer=ams_configuration["issuer"],
                audience=settings.AMS_CLIENT_ID,
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
        if email == settings.DJANGO_SUPERUSER_NAME:
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

            if user.deactivated:
                self.login_user(request, user, "Inactive User Found")
            else:
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
