"""Test user utils."""

import pytest
from ..api import utils

@pytest.fixture(scope="session", autouse=True)
def test_add_state_and_nonce_to_session(request):
    """Test method for adding state and nonce to the session."""
    state = "teststate"
    nonce = "testnonce"
    utils.add_state_and_nonce_to_session(request, state, nonce)
    assert request.session["openid_authenticity_tracker"][state].exists() is True
    assert request.session["openid_authenticity_tracker"][state]["nonce"] == nonce

@pytest.fixture(scope="session", autouse=True)
def test_get_nonce_and_state(request):
    """Test method for getting the nonce and state."""
    state = "teststate2"
    nonce = "testnonce2"
    utils.add_state_and_nonce_to_session(request, state, nonce)
    sessionvals = utils.get_nonce_and_state(request)
    assert sessionvals["state"] == state
    assert sessionvals["nonce"] == nonce
