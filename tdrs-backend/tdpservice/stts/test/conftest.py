"""stts fixtures."""

from django.core.management import call_command

import pytest


@pytest.fixture
def stts():
    """Populate STTs."""
    call_command("populate_stts")
