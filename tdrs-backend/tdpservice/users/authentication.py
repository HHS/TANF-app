"""Define custom authentication class."""

from django.contrib.auth import get_user_model

from rest_framework.authentication import BaseAuthentication
import logging
logger = logging.getLogger(__name__)

class CustomAuthentication(BaseAuthentication):
    """Define authentication and get user functions for custom authentication."""

    @staticmethod
    def authenticate(username=None, login_gov_uuid=None, hhs_id=None):
        """Authenticate user with the request and username."""
        User = get_user_model()
        logger.debug("CustomAuthentication::authenticate:hhs_id {}".format(hhs_id))
        logger.debug("CustomAuthentication::authenticate:login_gov_uuid {}".format(login_gov_uuid))
        logger.debug("CustomAuthentication::authenticate:username {}".format(username))
        try:
            if hhs_id:
                user = User.objects.get(username=username)
                # user already exists but hhs_id hasn't been filled in, update it
                if user.username == username and user.hhs_id is None:
                    user.hhs_id = hhs_id
                    user.save()
                # else email doesn't exist in postgres yet, but we have a new hhsid
                # below return triggers else clause in login.py::handler_user() and will create new user
                return User.objects.get(hhs_id=hhs_id)

            elif login_gov_uuid:
                return User.objects.get(login_gov_uuid=login_gov_uuid)
            else:
                return User.objects.get(username=username)
        except User.DoesNotExist:
            return None

    @staticmethod
    def get_user(user_id):
        """Get user by the user id."""
        User = get_user_model()
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
