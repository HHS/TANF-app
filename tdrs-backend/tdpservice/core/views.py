"""Define core, generic views of the app."""
import logging

from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes

logger = logging.getLogger()


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def write_logs(request):
    """Pass request bodies to the system logger.

    Mainly used to log client-side alerts and errors.
    """
    data = request.data
    logger.info(f"[{data['timestamp']}]: "
                f"[{data['type']}] "
                f"{data['message']} "
                f"for {request.user}")

    return Response('Success')
