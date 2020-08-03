import logging
import os
import requests
import sys
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.models import User

# consider adding throttling logic
class ValidateOIDCBearerToken(ObtainAuthToken):
 

    def post(self, request, *args, **kwargs):
        MAX_RETRIES = 0
        temp_token=request.data['temp_token']
   
        print('temp_token: ' + temp_token)
        attempt_num = 0
        # keep track of how many times we've retried
        '''Check the auth token against the userinfo endpoint to authenticate'''
        r = requests.get(os.environ['OIDC_OP_USER_ENDPOINT'],
                              headers={'Authorization': 'Bearer '+temp_token})
        if r.status_code == 200:
            data = r.json()
            
            # get user from database if they exist. if not, create a new one
            try:
                user = User.objects.get(email=data.email)
            except ObjectDoesNotExist:
                user = User.objects.create_user(data.email)
                user.set_unusable_password()
                user.save()
                
            session.user_id = user.pk
            
            return Response({
                    'user_id': user.pk,
                    'email': user.email
                }, status=status.HTTP_200_OK)
        else:
            return Response({"error": "Request failed"}, status=r.status_code)
 
    def get(self, request, *args, **kwargs):
        return Response({"error": "Method not allowed."}, status=status.HTTP_400_BAD_REQUEST)
