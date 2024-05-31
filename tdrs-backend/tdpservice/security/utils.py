"""Utility classes and functions for security."""

from rest_framework import exceptions
from rest_framework.authentication import TokenAuthentication
from django.utils.translation import gettext_lazy as _
from datetime import datetime
import pytz
from datetime import timedelta
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

def token_is_valid(token):
    """Check if token is valid."""
    utc_now = datetime.now()
    utc_now = utc_now.replace(tzinfo=pytz.utc)
    if token.created < (utc_now - timedelta(hours=settings.TOKEN_EXPIRATION_HOURS)):
        logger.info("API auth Token expired")
        return False
    return token is not None

# have to use ExpTokenAuthentication in settings.py instead of TokenAuthentication
class ExpTokenAuthentication(TokenAuthentication):
    """Custom token authentication class that checks if token is expired."""

    # see https://github.com/encode/django-rest-framework/blob/master/rest_framework/authentication.py

    def authenticate_credentials(self, key):
        """Authenticate the credentials."""
        model = self.get_model()
        try:
            token = model.objects.select_related("user").get(key=key)
        except model.DoesNotExist:
            raise exceptions.AuthenticationFailed(_("Invalid token."))

        if not token.user.is_active:
            raise exceptions.AuthenticationFailed(_("User inactive or deleted."))

        if not token_is_valid(token):
            raise exceptions.AuthenticationFailed(_("Token expired."))

        return (token.user, token)
