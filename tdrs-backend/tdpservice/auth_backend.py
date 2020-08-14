from django.contrib.auth import get_user_model

# requires to define two functions authenticate and get_user

class CustomAuthentication:

    def authenticate(self, request, username=None):
        User = get_user_model()
        try:
            user = User.objects.get(username=username)
            return user
        except User.DoesNotExist:
            return None

    def get_user(self, user_id):
        User = get_user_model()
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
