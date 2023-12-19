"""Define custom authentication class."""

from django.contrib.auth import get_user_model

from rest_framework.authentication import BaseAuthentication
from rest_framework.request import Request
import logging
import os
logger = logging.getLogger(__name__)

class CustomAuthentication(BaseAuthentication):
    """Define authentication and get user functions for custom authentication."""

    @staticmethod
    def authenticate(request=None, login_gov_uuid=None, hhs_id=None):
        """ HACK
        This method currently needs to support two unrelated workflows.
        References:
          tdpservice/users/api/login.py:TokenAuthorizationOIDC.handleUser
          https://www.django-rest-framework.org/api-guide/authentication
        """
        if type(request) == Request:
            username = request.data.get('username')
            logging.debug(f"CustomAuthentication::authenticate: {request} {request.data} "
                          f"login_gov_id={login_gov_uuid} hhs_id={hhs_id}")
        else:
            username = request
            logging.debug(f"CustomAuthentication::authenticate: {username} "
                          f"login_gov_id={login_gov_uuid} hhs_id={hhs_id}")
        User = get_user_model()
        try:
            if hhs_id:
                try:
                    user_obj = User.objects.get(hhs_id=hhs_id)
                except User.DoesNotExist:
                    # If below line also fails with User.DNE, will bubble up and return None
                    user = User.objects.filter(username=username)
                    user.update(hhs_id=hhs_id)
                    logging.debug("Updated user {} with hhs_id {}.".format(username, hhs_id))
                    user_obj = User.objects.get(hhs_id=hhs_id)

            elif login_gov_uuid:
                user_obj = User.objects.get(login_gov_uuid=login_gov_uuid)
            else:
                user_obj = User.objects.get(username=username)
        except User.DoesNotExist:
            user_obj = None
        logging.debug(f"CustomAuthentication::authenticate found user: {user_obj}")
        if type(request) == Request:
            return (user_obj, None) if user_obj else None
        return user_obj

    @staticmethod
    def get_user(user_id):
        """Get user by the user id."""
        User = get_user_model()
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
