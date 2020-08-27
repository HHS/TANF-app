"""Test user utils."""

import pytest
import time
from ..api import utils
from django.test import TestCase


class TestUtilities(TestCase):
    """Test utility methods."""

    @pytest.mark.django_db
    def test_get_nonce_and_state(self):
        """Test method for getting the nonce and state."""
        state = "teststate2"
        nonce = "testnonce2"
        session = self.client.session
        session["state_nonce_tracker"] = {
            "nonce": nonce,
            "state": state,
            "added_on": time.time(),
        }
        session.save()
        sessionvals = utils.get_nonce_and_state(session)
        assert sessionvals["state"] == state
        assert sessionvals["nonce"] == nonce
