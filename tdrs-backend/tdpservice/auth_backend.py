"""Define custom authentication class."""

from django.contrib.auth import get_user_model

# requires to define two functions authenticate and get_user


class CustomAuthentication:
    """Define authentication and get user functions for custom authentication."""

    def authenticate(self, request, username=None):
        """Authenticate user with the request and username."""
        User = get_user_model()
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
