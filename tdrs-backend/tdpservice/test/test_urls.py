"""Test main routing works."""

from django.urls import reverse
from django.test import TestCase


class TestUrlResponses(TestCase):
    """Test url responses."""

    def test_oidc_auth(self):
        """Test login url redirects."""
        response = self.client.get(reverse('oidc-auth'))
        self.assertEqual(response.status_code, 302)
