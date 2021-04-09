import logging

from rest_framework.response import Response
from rest_framework.decorators import api_view

logger = logging.getLogger()

@api_view(['POST'])
def write_logs(request):
    logger.info(request.data)

    return Response('Success')
