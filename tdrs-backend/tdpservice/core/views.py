"""Define core, generic views of the app."""
import logging

from django.contrib.admin.models import LogEntry, ADDITION
from django.contrib.contenttypes.models import ContentType
from django.views.generic.base import TemplateView
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from tdpservice.data_files.models import DataFile

logger = logging.getLogger()


class IndexView(TemplateView):
    """An empty template for the app root."""

    template_name = 'index.html'


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

    if 'files' in data:
        for file in data['files']:
            # Add the file name of each referenced DataFile.
            single_data_file_log = {
                **data,
                'file': DataFile.objects.get(pk=file).original_filename
            }
            # Remove the list of other files that were uploaded.
            single_data_file_log.pop('files', None)
            # Transform into newline-delimited string for the LogEntryDetails view.
            formatted = [
                f'{key}: {value}' for key, value in single_data_file_log.items()
            ]
            object_repr = '\n'.join(formatted)

            # @TODO: Fine tune the action flag to support CHANGE actions,
            # i.e. for newly uploaded DataFiles.

            LogEntry.objects.log_action(
                user_id=request.user.pk,
                content_type_id=ContentType.objects.get_for_model(DataFile).pk,
                object_id=file,
                object_repr=object_repr,
                action_flag=ADDITION,
                change_message=data['message'],
            )

    return Response('Success')
