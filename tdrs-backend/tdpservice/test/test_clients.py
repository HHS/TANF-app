"""Tests for client services which may be used system-wide."""
import pytest

from django.conf import settings

from tdpservice.clients import get_s3_client

LOCALSTACK_URL = 'http://localhost:4566'


@pytest.fixture
def patch_no_localstack_setting():
    """Patches Django settings to turn off localstack setting."""
    settings.USE_LOCALSTACK = False


def test_s3_client_localstack_url():
    """Test global S3 client points to localstack when USE_LOCALSTACK is True.

    NOTE: USE_LOCALSTACK is True by default in test environments.
    """
    assert settings.USE_LOCALSTACK is True

    s3_client = get_s3_client()

    assert s3_client is not None
    assert s3_client._endpoint.host == LOCALSTACK_URL


def test_s3_client_aws_url(patch_no_localstack_setting):
    """Test global S3 client points to AWS when USE_LOCALSTACK is False.

    NOTE: Temporarily disables USE_LOCALSTACK setting for this test.
    """
    # Confirm that the settings patch was applied properly
    assert settings.USE_LOCALSTACK is False

    s3_client = get_s3_client()

    assert s3_client is not None
    assert s3_client._endpoint.host != LOCALSTACK_URL
