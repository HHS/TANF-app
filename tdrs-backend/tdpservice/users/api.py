import logging
import os
import requests
import sys
import json
import uuid
import jwt
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
from django.conf import settings

# consider adding throttling logic
class ValidateOIDCBearerToken(ObtainAuthToken):
 

    def post(self, request, *args, **kwargs):
        '''Handle decoding auth token and authenticate user'''
        id_token = request.data['id_token']
        cert_str = settings.OIDC_RP_IDP_SIGN_KEY
        decoded_payload = jwt.decode(id_token, cert_str, algorithm='RS256')
        
        User = get_user_model()
        
        # get user from database if they exist. if not, create a new one
        if decoded_payload["email_verified"] == True:
            try:
                user = User.objects.get(username=decoded_payload["email"])
                print('existing user logging in ' + user.username)
            except User.DoesNotExist:
                user = User.objects.create_user(decoded_payload["email"])
                user.set_unusable_password()
                user.save()
                print('new user created ' + user.username)
        else:
            return Response({"error": "Unverified email"}, status=status.HTTP_400_BAD_REQUEST)
            
        request.session['user_id'] = str(user.pk)
        
        return Response({
                'user_id': user.pk,
                'email': user.username
            }, status=status.HTTP_200_OK)

 
    def get(self, request, *args, **kwargs):
        return Response({"error": "Method not allowed."}, status=status.HTTP_400_BAD_REQUEST)
