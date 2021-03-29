""" Tests for client services which may be used system-wide. """
import pytest

from django.conf import settings

from tdpservice.clients import get_s3_client

LOCALSTACK_URL = 'http://localhost:4566'


@pytest.fixture
def patch_localstack_setting():
    settings.USE_LOCALSTACK = False


def test_s3_client_localstack_url():
    """ Tests that when USE_LOCALSTACK is True the generated S3 client points
        to the localstack URL instead of directly to AWS.
    """
    # NOTE: By default this is True in tests but confirm before proceeding
    assert settings.USE_LOCALSTACK is True

    s3_client = get_s3_client()

    assert s3_client is not None
    assert s3_client._endpoint.host == LOCALSTACK_URL


def test_s3_client_aws_url(patch_localstack_setting):
    """ Tests that when USE_LOCALSTACK is False the generated S3 client points
        to a production AWS environment and *not* the localstack URL.
    """
    # Confirm that the settings patch was applied properly
    assert settings.USE_LOCALSTACK is False

    s3_client = get_s3_client()

    assert s3_client is not None
    assert s3_client._endpoint.host != LOCALSTACK_URL
