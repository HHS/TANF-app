"""Test the authorization check."""

import pytest
from django.urls import reverse
from django.test import TestCase
from rest_framework import status

class TestAuth(TestCase):
    """Test authorization artifacts."""

    @pytest.mark.django_db
    def test_auth_check_endpoint_with_no_user(self):
        """Test auth check method with no user."""
        response = self.client.get(reverse("authorization-check"))
        assert response.status_code == status.HTTP_403_FORBIDDEN
