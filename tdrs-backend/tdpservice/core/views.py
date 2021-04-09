"""Define core, generic views of the app."""
import logging

from rest_framework.response import Response
from rest_framework.decorators import api_view

logger = logging.getLogger()


@api_view(['POST'])
def write_logs(request):
    """Pass request bodies to the system logger.

    Mainly used to log client-side alerts and errors.
    """
    logger.info(request.data)

    return Response('Success')
