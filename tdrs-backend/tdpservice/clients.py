from boto3 import client
from django.conf import settings


def get_s3_client():
    """ Returns an S3 client that either goes to localstack or AWS depending
        on configuration. Intended to be used in place of a direct boto3 client.
    """
    region_name = settings.AWS_REGION_NAME

    # If localstack support is turned on we will return a client that redirects
    # all S3 requests to the localstack container
    if settings.USE_LOCALSTACK:
        # To get s3 signed URLs to work with localstack we must pass in
        # dummy credentials of `test` per the docs
        # https://github.com/localstack/localstack#setting-up-local-region-and-credentials-to-run-localstack  noqa
        localstack_creds_placeholder = 'test'

        # If localstack is in use then we must supply the endpoint URL
        # explicitly to prevent boto3 from auto-generating a live S3 URL
        localstack_endpoint_url = 'http://localhost:4566'

        return client(
            service_name='s3',
            aws_access_key_id=localstack_creds_placeholder,
            aws_secret_access_key=localstack_creds_placeholder,
            endpoint_url=localstack_endpoint_url,
            region_name=region_name
        )

    # Otherwise, use a live S3 with the credentials configured via env vars
    return client(
        service_name='s3',
        aws_access_key_id=settings.AWS_S3_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_S3_SECRET_ACCESS_KEY,
        region_name=region_name
    )
