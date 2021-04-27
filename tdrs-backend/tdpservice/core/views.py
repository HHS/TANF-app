"""Define core, generic views of the app."""
import logging

from django.contrib.admin.models import LogEntry, CHANGE
from django.contrib.contenttypes.models import ContentType
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes

from ..reports.models import ReportFile

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

    if data['files']:
        for file in data['files']:
            LogEntry.objects.log_action(
                user_id=data['user'],
                content_type_id=ContentType.objects.get_for_model(ReportFile).pk,
                object_id=file,
                object_repr=str(data),
                action_flag=CHANGE,
                change_message=data['message'],
            )

    return Response('Success')
