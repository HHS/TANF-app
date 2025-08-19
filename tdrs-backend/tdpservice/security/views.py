"""Views for the security app."""

import json
import logging

from django.conf import settings
from django.contrib.auth.decorators import user_passes_test

import jwt
import requests
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView

from tdpservice.security.event_handler import SecurityEventHandler
from tdpservice.security.utils import token_is_valid
from tdpservice.users.models import AccountApprovalStatusChoices, User

logger = logging.getLogger(__name__)


def can_get_new_token(user):
    """Check if user can get a new token."""
    return (
        user.is_authenticated
        and user.is_ofa_sys_admin
        and user.account_approval_status == AccountApprovalStatusChoices.APPROVED
    )


@user_passes_test(can_get_new_token, login_url="/login/")
@api_view(["GET"])
def generate_new_token(request):
    """Generate new token for the API user."""
    if request.method == "GET":
        user = User.objects.get(username=request.user)
        token, created = Token.objects.get_or_create(user=user)
        if token_is_valid(token):
            return Response(str(token))
        else:
            token.delete()
            token = Token.objects.create(user=user)
            return Response(str(token))


class SecurityEventTokenView(APIView):
    """Endpoint to receive Security Event Tokens (SETs) from Login.gov."""

    authentication_classes = []
    permission_classes = []

    def _validate_content_type(self, request):
        """Validate content type."""
        if request.content_type != "application/secevent+jwt":
            logger.error(f"Invalid content type: {request.content_type}")
            raise ValidationError("Invalid content type")

    def _validate_key_id(self, key_id):
        """Validate key ID."""
        if not key_id:
            logger.error("No 'kid' found in JWT header")
            raise ValidationError("No 'kid' found in JWT header")

    def _get_public_key(self, certs, key_id):
        """Validate and return public key."""
        public_key = None
        for key in certs.get("keys", []):
            if key.get("kid") == key_id:
                public_key = jwt.algorithms.RSAAlgorithm.from_jwk(json.dumps(key))
                break

        if not public_key:
            logger.error(f"No public key found for kid: {key_id}")
            raise ValidationError("No public key found for kid")

    def post(self, request, *args, **kwargs):
        """Process incoming Security Event Token from Login.gov."""
        try:
            # Validate the content type
            self._validate_content_type(request)

            # Get the JWT from the request body
            jwt_token = request.body.decode("utf-8").strip()

            # Fetch Login.gov's public key from the certificates endpoint
            well_known_config = requests.get(
                settings.LOGIN_GOV_WELL_KNOWN_CONFIG
            ).json()
            certs_response = requests.get(well_known_config["jwks_uri"])
            certs = certs_response.json()

            # Find the key that matches the kid in the JWT header
            header = jwt.get_unverified_header(jwt_token)
            key_id = header.get("kid")

            self._validate_key_id(key_id)

            public_key = self._get_public_key(certs, key_id)

            # Decode and verify the JWT
            decoded_jwt = jwt.decode(
                jwt_token,
                public_key,
                algorithms=["RS256"],
                audience=settings.LOGIN_GOV_SET_AUDIENCE,
                options={
                    "verify_signature": False,
                    "verify_exp": True,
                },
            )

            # Process the event
            events = decoded_jwt.get("events", {})
            if not events:
                logger.error("No events found in JWT")
                raise ValidationError("No events found in JWT")

            # Process each event in the JWT
            logger.info(f"Processing security events: {events}")
            for event_type, event_data in events.items():
                SecurityEventHandler.handle_event(event_type, event_data, decoded_jwt)
            logger.info("Successfully processed security events.")

            return Response(status=status.HTTP_200_OK)

        except jwt.InvalidTokenError as e:
            logger.error(f"Invalid token: {e}")
            raise ValidationError("Invalid token")
        except ValidationError as e:
            raise e
        except Exception:
            logger.exception(
                "An unknown exception occurred when trying to handle a SET request."
            )
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)
