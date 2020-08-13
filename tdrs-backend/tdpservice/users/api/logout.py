import jwt
import secrets
from rest_framework.response import Response
from rest_framework.parsers import JSONParser
from rest_framework import status
from rest_framework.views import APIView
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
from django.contrib.auth import logout


# logout user
class LogoutUser(APIView):


    def get(self, request, *args, **kwargs):
        """Destroy user session"""
        logout(request)
        return Response({
            "system": "User logged out"
        }, status=status.HTTP_200_OK)
