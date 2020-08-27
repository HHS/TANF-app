"""Test user utils."""

import pytest
from ..api import utils
from django.test import TestCase
from django.test import Client


class TestUtilities(TestCase):
    """Test utility methods."""

    @pytest.mark.django_db
    def test_add_state_and_nonce_to_session(self):
        """Test method for adding state and nonce to the session."""
        state = "teststate"
        nonce = "testnonce"
        tracker = "openid_authenticity_tracker"
        request = Client.request
        utils.add_state_and_nonce_to_session(request, state, nonce)
        assert self.client.session[tracker][state].exists() is True
        assert self.client.session[tracker][state]["nonce"] == nonce

    @pytest.mark.django_db
    def test_get_nonce_and_state(self):
        """Test method for getting the nonce and state."""
        state = "teststate2"
        nonce = "testnonce2"
        request = Client.request
        utils.add_state_and_nonce_to_session(request, state, nonce)
        sessionvals = utils.get_nonce_and_state(request)
        assert sessionvals["state"] == state
        assert sessionvals["nonce"] == nonce
