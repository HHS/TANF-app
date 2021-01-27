"""Globally available pytest fixtures."""
import pytest
from rest_framework.test import APIClient

from tdpservice.users.test.factories import UserFactory
from tdpservice.stts.test.factories import STTFactory, RegionFactory
from tdpservice.reports.test.factoriesw import ReportFileFactory

@pytest.fixture(scope="function")
def api_client():
    """Return an API client for testing."""
    return APIClient()


@pytest.fixture
def user():
    """Return a basic, non-admin user."""
    return UserFactory.create()


@pytest.fixture
def stt():
    """Return an STT."""
    return STTFactory.create()


@pytest.fixture
def region():
    """Return a region."""
    return RegionFactory.create()

@pytest.fixture
def report():
    """Return a report file."""
    return ReportFileFactory.create()
