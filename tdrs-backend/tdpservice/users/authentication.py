"""Define custom authentication class."""

from django.contrib.auth import get_user_model

from rest_framework.authentication import BaseAuthentication


class CustomAuthentication(BaseAuthentication):
    """Define authentication and get user functions for custom authentication."""

    def authenticate(self, username=None, user_id=None):
        """Authenticate user with the request and username."""
        User = get_user_model()

        if user_id:
            try:
                return User.objects.get(login_gov_uuid=user_id)
            except User.DoesNotExist:
                return None

        try:
            user = User.objects.get(username=username)
            return user
        except User.DoesNotExist:
            return None

    def get_user(self, user_id):
        """Get user by the user id."""
        User = get_user_model()
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
