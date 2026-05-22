"""Fixtures for live Go parser integration tests."""

import pytest


@pytest.fixture(scope="session")
def django_db_setup():
    """Use the live Docker database instead of creating an isolated test DB."""
    pass
