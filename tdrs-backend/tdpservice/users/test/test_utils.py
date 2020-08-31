"""Test user utils."""

import pytest
import time
from ..api import utils
from django.test import TestCase
from django.core.exceptions import SuspiciousOperation
from rest_framework import status


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

    @pytest.mark.django_db
    def test_error_raised_when_state_not_in_session(self):
        """When state is not in session an exception should be raised."""
        nonce = "testnonce2"
        session = self.client.session
        session["state_nonce_tracker"] = {
            "nonce": nonce,
            "added_on": time.time(),
        }
        session.save()
        with pytest.raises(SuspiciousOperation):
            assert utils.get_nonce_and_state(session)

    @pytest.mark.django_db
    def test_error_raised_when_nonce_not_in_session(self):
        """When state is not in session an exception should be raised."""
        state = "teststate2"
        session = self.client.session
        session["state_nonce_tracker"] = {
            "state": state,
            "added_on": time.time(),
        }
        session.save()
        with pytest.raises(SuspiciousOperation):
            assert utils.get_nonce_and_state(session)

    @pytest.mark.django_db
    def test_response_redirect_redirects(self):
        """Response redirect redirects."""
        id_token = "dummy"
        response = utils.response_redirect(self, id_token)
        assert response.status_code == status.HTTP_302_FOUND
