"""Module for testing the user model."""

from django.test import TestCase
from django.forms.models import model_to_dict
from tdpservice.users.models import User
from .factories import UserFactory


class TestUserModel(TestCase):
    """Test the user model."""

    def setUp(self):
        """Get test user for tests."""
        user = UserFactory.build(username="test@example.com")
        user.set_password(user.password)
        user.save()
        self.user_data = model_to_dict(user)
        self.user_id = user.pk

    def test_user_creation(self):
        """Test user creation."""
        user = User(self.user_data)
        assert isinstance(user, User)

    def test_string_representation(self):
        """Test __str__ method."""
        user = User(self.user_data)
        assert str(user) is user.username
