"""Test main routing works."""

from django.urls import reverse


def test_create(self):
    """Test login url responds."""
    response = self.client.get(reverse('login'))
    self.assertEqual(response.status_code, 200)
