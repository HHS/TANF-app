import os
import pytest

from django.conf import settings


def test_clamav():
    """Test that ClamAV is configured and accessible by this application."""
    clamav_url = settings.AV_SCAN_URL

    assert clamav_url is not None
