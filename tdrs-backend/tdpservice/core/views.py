"""Define core, generic views of the app."""

import logging

from django.conf import settings
from django.contrib.admin.models import ADDITION, LogEntry
from django.contrib.contenttypes.models import ContentType
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page

from rest_framework import generics
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from tdpservice.core.models import FeatureFlag
from tdpservice.core.serializers import FeatureFlagSerializer
from tdpservice.data_files.models import DataFile

logger = logging.getLogger()


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def write_logs(request):
    """Pass request bodies to the system logger.

    Mainly used to log client-side alerts and errors.
    """
    data = request.data
    logger.info(
        f"[{data['timestamp']}]: "
        f"[{data['type']}] "
        f"{data['message']} "
        f"for {request.user}"
    )

    if "files" in data:
        for file in data["files"]:
            # Add the file name of each referenced DataFile.
            single_data_file_log = {
                **data,
                "file": DataFile.objects.get(pk=file).original_filename,
            }
            # Remove the list of other files that were uploaded.
            single_data_file_log.pop("files", None)
            # Transform into newline-delimited string for the LogEntryDetails view.
            formatted = [
                f"{key}: {value}" for key, value in single_data_file_log.items()
            ]
            object_repr = "\n".join(formatted)

            # @TODO: Fine tune the action flag to support CHANGE actions,
            # i.e. for newly uploaded DataFiles.

            LogEntry.objects.log_action(
                user_id=request.user.pk,
                content_type_id=ContentType.objects.get_for_model(DataFile).pk,
                object_id=file,
                object_repr=object_repr,
                action_flag=ADDITION,
                change_message=data["message"],
            )

    return Response("Success")


class FeatureFlagView(generics.ListAPIView):
    """Simple view to get all STTs alphabetized."""

    pagination_class = None
    permission_classes = []  # [IsAuthenticated]
    queryset = FeatureFlag.objects.all()
    serializer_class = FeatureFlagSerializer

    @method_decorator(
        [
            cache_page(
                settings.DEFAULT_CACHE_TIMEOUT,
                cache="feature-flags",
                key_prefix="list",
            ),
        ]
    )
    def list(self, request):
        """Get the feature flag list from the cache if available, else fetch the queryset."""
        return super().list(request)
