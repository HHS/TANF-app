"""Log user in to Django from Login.gov."""

import jwt
import os
import requests
import secrets
import time
from ...auth_backend import CustomAuthentication
from jwcrypto import jwk
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import get_user_model
from django.contrib.auth import login
from django.core.exceptions import SuspiciousOperation
from urllib.parse import urlencode, quote_plus


# consider adding throttling logic
class TokenAuthorizationOIDC(ObtainAuthToken):
    """Define methods for handling login request from login.gov."""

    def get(self, request, *args, **kwargs):
        """Handle decoding auth token and authenticate user."""
        code = request.GET.get('code', None)
        state = request.GET.get('state', None)

        if code is None:
            return Response({'error': 'OIDC Code not found!'}, status=status.HTTP_400_BAD_REQUEST)
        if state is None:
            return Response({'error': 'OIDC State not found'}, status=status.HTTP_400_BAD_REQUEST)

        # get the validation keys to confirm generated nonce and state
        nonce_and_state = self.getNonceAndState(state, request)
        nonce_validator = nonce_and_state.get('nonce', 'not_nonce')
        state_validator = nonce_and_state.get('state', 'not_state')

        # build out the query string parameters and full URL path for OIDC token endpoint
        token_params = self.generateTokenEndpointParameters(code)
        token_endpoint = os.environ['OIDC_OP_TOKEN_ENDPOINT'] + '?' + token_params
        token_response = requests.post(token_endpoint)

        if token_response.status_code == 200:
            token_data = token_response.json()
            id_token = token_data.get('id_token')
            cert_str = self.generateJWTFromJWKS()

            # issuer: issuer of the response
            # subject : UUID - not useful for login.gov set options to ignore this
            decoded_payload = jwt.decode(id_token,
                                         key=cert_str,
                                         issuer=os.environ['OIDC_OP_ISSUER'],
                                         audience=os.environ['CLIENT_ID'],
                                         algorithm='RS256',
                                         subject=None,
                                         access_token=None,
                                         options={'verify_nbf': False}
                                         )

            decoded_nonce = decoded_payload['nonce']

            if self.validNonceAndState(decoded_nonce, state, nonce_validator, state_validator) is False:
                msg = ('Could not validate nonce and state')
                raise SuspiciousOperation(msg)

            if decoded_payload['email_verified'] is True:
                try:
                    # get user from database if they exist. if not, create a new one
                    if 'token' not in request.session:
                        request.session['token'] = id_token

                    user = CustomAuthentication.authenticate(self, request, username=decoded_payload['email'])
                    if user is not None:
                        login(request, user, backend='tdpservice.auth_backend.CustomAuthentication')

                        # update the user session so OIDC logout URL has the token_hint

                        return Response({
                            'user_id': user.pk,
                            'email': user.username,
                            'status': 'Existing User Found!'
                        }, status=status.HTTP_200_OK)
                    else:
                        User = get_user_model()
                        user = User.objects.create_user(decoded_payload['email'])
                        user.set_unusable_password()
                        user.save()
                        login(request, user, backend='tdpservice.auth_backend.CustomAuthentication')
                        return Response({
                            'user_id': user.pk,
                            'email': user.username,
                            'status': 'New User Created!'
                        }, status=status.HTTP_200_OK)

                except Exception:
                    return Response(
                        {'error': 'Email verfied, but experienced internal issue with login/registration.'},
                        status=status.HTTP_400_BAD_REQUEST)

            else:
                return Response({'error': 'Unverified email!'}, status=status.HTTP_400_BAD_REQUEST)

        # else:
        return Response({
            'error': 'Invalid Validation Code Or OpenID Connect Authenticator Down!'
        }, status=status.HTTP_400_BAD_REQUEST)

    def generateTokenEndpointParameters(self, code):
        """Generate token parameters."""
        clientAssertion = self.generateClientAssertion()
        params = {
            'client_assertion': clientAssertion,
            'client_assertion_type': os.environ['CLIENT_ASSERTION_TYPE'],
            'code': code,
            'grant_type': 'authorization_code'
        }
        encoded_params = urlencode(params, quote_via=quote_plus)
        return encoded_params

    def generateClientAssertion(self):
        """Generate client assertion."""
        private_key = os.environ['JWT_KEY']
        payload = {
            'iss': os.environ['CLIENT_ID'],
            'aud': os.environ['OIDC_OP_TOKEN_ENDPOINT'],
            'sub': os.environ['CLIENT_ID'],
            'jti': secrets.token_urlsafe(32)[:32],
            # set token experation to be 1 minute from current time
            'exp': int(round(time.time() * 1000)) + 60000
        }
        encoded_jwt = jwt.encode(payload, key=private_key, algorithm='RS256')
        return encoded_jwt.decode('UTF-8')

    def generateJWTFromJWKS(self):
        """Generate JWT."""
        certs_endpoint = os.environ['OIDC_OP_JWKS_ENDPOINT']
        certs_response = requests.get(certs_endpoint)
        public_cert = jwk.JWK(**certs_response.json().get('keys')[0])
        public_pem = public_cert.export_to_pem()
        return public_pem

    def validNonceAndState(self, decoded_nonce, state, nonce_validator, state_validator):
        """Validate nonce and state are correct values."""
        if decoded_nonce != nonce_validator:
            return False
        if state != state_validator:
            return False
        return True

    def getNonceAndState(self, state, request):
        """Get the nonce and state values."""
        if 'state_nonce_tracker' not in request.session:
            msg = ('error: Could not find session store for nonce and state')
            raise SuspiciousOperation(msg)
        openid_authenticity_tracker = request.session.get('state_nonce_tracker', None)
        if 'state' not in openid_authenticity_tracker:
            msg = 'OIDC callback state was not found in session .'
            raise SuspiciousOperation(msg)
        state = openid_authenticity_tracker.get('state', None)

        if 'nonce' not in openid_authenticity_tracker:
            msg = 'OIDC callback nonce was not found in session `state_nonce_tracker`.'
            raise SuspiciousOperation(msg)

        nonce = openid_authenticity_tracker.get('nonce', None)
        validation_keys = {'state': state, 'nonce': nonce}
        return validation_keys
