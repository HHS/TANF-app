"""Test the custom authorization class."""

import uuid
from django.test import TestCase
from django.forms.models import model_to_dict
from .factories import UserFactory
from ..authentication import CustomAuthentication


class TestCustomAuthentication(TestCase):
    """Test methods in custom authentication."""

    def setUp(self):
        """Get test user for tests."""
        user = UserFactory.build()
        user.set_password(user.password)
        user.save()
        self.user_data = model_to_dict(user)
        self.user_id = user.pk

    def test_authorization(self):
        """Test authorization method."""
        user = CustomAuthentication.authenticate(
            self, username=self.user_data["username"]
        )
        assert user.username == self.user_data["username"]

    def test_get_user(self):
        """Test get_user method."""
        user = CustomAuthentication.get_user(self, self.user_id)
        assert user.username == self.user_data["username"]

    def test_get_non_user(self):
        """Test that an invalid user does not return a user."""
        uuidOne = uuid.uuid1()
        nonuser = CustomAuthentication.get_user(self, uuidOne)
        assert nonuser is None
