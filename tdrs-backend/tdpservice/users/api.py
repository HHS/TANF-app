from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework import status
import sys
import logging

# consider adding throttling logic
class ValidateOIDCBearerToken(ObtainAuthToken):
 

    def post(self, request, *args, **kwargs):
        MAX_RETRIES = 0

        # include step to decrypt in tandem with UIs logic to encrypt token
        temp_token=request.data['temp_token']
        if temp_token is None:
            print('NO VALID AUTH TOKEN?!')
            return Response({"error": "Received a poor authentication token"}, status=status.HTTP_400_BAD_REQUEST)
    
        attempt_num = 0
        # keep track of how many times we've retried
        while attempt_num < MAX_RETRIES:
            '''Check the auth token against the userinfo endpoint to authenticate'''
            r = requests.post(os.environ['OIDC_OP_USER_ENDPOINT'],
                              headers={'Authorization': 'Bearer '+temp_token})

            if r.status_code == 200:
                data = r.json()
                return Response(data, status=status.HTTP_200_OK)
            else:
                attempt_num += 1
                return Response({"error": "Request failed"}, status=r.status_code)
        else:
            return Response({"error": "Method not allowed my good sir."}, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request, *args, **kwargs):
        return Response({"error": "Method not allowed."}, status=status.HTTP_400_BAD_REQUEST)
