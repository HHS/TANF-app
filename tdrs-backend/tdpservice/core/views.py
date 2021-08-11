"""Define core, generic views of the app."""
import logging

from django.contrib.admin.models import LogEntry, ADDITION
from django.contrib.contenttypes.models import ContentType
from django.views.generic.base import TemplateView
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes

from ..users.permissions import IsUser
from ..users.models import User
from ..reports.models import ReportFile

logger = logging.getLogger()

class IndexView(TemplateView):
    """An empty template for the app root."""

    template_name = 'index.html'

@api_view(['POST'])
@permission_classes([IsUser])
def write_logs(request):
    """Pass request bodies to the system logger.

    Mainly used to log client-side alerts and errors.
    """
    data = request.data
    logger.info(f"[{data['timestamp']}]: "
                f"[{data['type']}] "
                f"{data['message']} "
                f"for {request.user}")

    if 'files' in data:
        for file in data['files']:
            # Add the file name of each referenced ReportFile.
            single_report_log = {
                **data,
                'file': ReportFile.objects.get(pk=file).original_filename
            }
            # Remove the list of other files that were uploaded.
            single_report_log.pop('files', None)
            # Transform into newline-delimited string for the LogEntryDetails view.
            formatted = [f'{key}: {value}' for key, value in single_report_log.items()]
            object_repr = '\n'.join(formatted)

            # @TODO: Fine tune the action flag to support CHANGE actions,
            # i.e. for newly uploaded Reports.

            LogEntry.objects.log_action(
                user_id=User.objects.get(username=data['user']).pk,
                content_type_id=ContentType.objects.get_for_model(ReportFile).pk,
                object_id=file,
                object_repr=object_repr,
                action_flag=ADDITION,
                change_message=data['message'],
            )

    return Response('Success')
