import logging
import os
import requests
import sys
import json
import uuid
import jwt
import secrets
import time
from jwcrypto import jwk
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.parsers import JSONParser
from rest_framework import status
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
from django.conf import settings
from urllib.parse import urlencode, quote_plus
from ...auth_backend import CustomAuthentication
from django.contrib.auth import login


# consider adding throttling logic
class ValidateOIDCBearerToken(ObtainAuthToken):


    def post(self, request, *args, **kwargs):
        '''Handle decoding auth token and authenticate user'''
        token_params = self.generateTokenParameters(request.data['code'])

        token_endpoint = os.environ['OIDC_OP_TOKEN_ENDPOINT'] + '?' + token_params
        token_response = requests.post(token_endpoint)
    
        if token_response.status_code == 200:
            token_data = token_response.json()
            id_token =  token_data.get('id_token')
            cert_str = self.generateJWTFromJWKS()

            #issuer: issuer of the response
            #subject : UUID - not useful for login.gov set options to ignore this
            decoded_payload = jwt.decode(id_token,
                                          key=cert_str, 
                                          issuer='https://idp.int.identitysandbox.gov/',
                                          audience='urn:gov:gsa:openidconnect.profiles:sp:sso:hhs:tanf-proto-dev',
                                          algorithm='RS256',
                                          subject=None,
                                          access_token=None)
            print(decoded_payload)
            User = get_user_model()
                        # get user from database if they exist. if not, create a new one
            if decoded_payload["email_verified"] == True:
                try:
                    user = CustomAuthentication.authenticate(self, request, username=decoded_payload["email"])
                    login(request, user, backend="tdpservice.auth_backend.CustomAuthentication")
                    print('existing user logging in ' + user.username)
                    return Response({
                    'user_id': user.pk,
                    'email': user.username,
                    "status": "Existing User Found!"
                }, status=status.HTTP_200_OK)
                except User.DoesNotExist:
                    user = User.objects.create_user(decoded_payload["email"])
                    user.set_unusable_password()
                    user.save()
                    login(request, user, backend="tdpservice.auth_backend.CustomAuthentication")
                    print('new user created ' + user.username)
                    return Response({
                    'user_id': user.pk,
                    'email': user.username,
                    "status": "New User Created!"
                }, status=status.HTTP_200_OK)
            else:
                return Response({"error": "Unverified email!"}, status=status.HTTP_400_BAD_REQUEST)

        # else:
        return Response({"error": "Invalid Validation Code Or OpenID Connect Authenticator Down!"}, status=status.HTTP_400_BAD_REQUEST)


    def get(self, request, *args, **kwargs):
        return Response({"error": "Method not allowed."}, status=status.HTTP_400_BAD_REQUEST)


    def generateTokenParameters(self, code):
        clientAssertion = self.generateClientAssertion()
        #TODO: extract hard coded fields as environment variables
        params = {
            'client_assertion': clientAssertion,
            'client_assertion_type': 'urn:ietf:params:oauth:client-assertion-type:jwt-bearer',
            'code': code,
            "grant_type": 'authorization_code'
        }
        encoded_params = urlencode(params, quote_via=quote_plus)
        #print(encoded_params)
        return encoded_params

    
    def generateClientAssertion(self):
       privateKey = os.environ['JWT_KEY']
       #TODO: extract these as environment variables
       payload = {
            "iss": "urn:gov:gsa:openidconnect.profiles:sp:sso:hhs:tanf-proto-dev",
            "aud": "https://idp.int.identitysandbox.gov/api/openid_connect/token",
            "sub": "urn:gov:gsa:openidconnect.profiles:sp:sso:hhs:tanf-proto-dev",
            "jti": secrets.token_urlsafe(32)[:32],
            "exp": int(round(time.time() * 1000))+60000
        }
       encoded_jwt = jwt.encode(payload,key=privateKey,algorithm='RS256')
       return encoded_jwt.decode('UTF-8')

    def generateJWTFromJWKS(self):
       certs_endpoint = os.environ['OIDC_OP_JWKS_ENDPOINT']
       certs_response = requests.get(certs_endpoint)
       print(certs_response.json().get('keys')[0])

       public_cert=jwk.JWK(**certs_response.json().get('keys')[0])
       public_pem = public_cert.export_to_pem()
       return public_pem
