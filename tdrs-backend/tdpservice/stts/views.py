"""Define API views for user class."""
import logging

from django.db.models import Prefetch
from rest_framework import generics, mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from tdpservice.stts.models import Region, STT
from .serializers import RegionSerializer, STTSerializer

logger = logging.getLogger(__name__)


class RegionAPIView(generics.ListAPIView):
    """Simple view to get all regions and STTs, without pagination."""

    pagination_class = None
    permission_classes = [IsAuthenticated]
    queryset = Region.objects.prefetch_related(
        Prefetch("stts", queryset=STT.objects.select_related("state").order_by("name"))
    ).order_by("id")
    serializer_class = RegionSerializer


class STTApiAlphaView(generics.ListAPIView):
    """Simple view to get all STTs alphabetized."""

    pagination_class = None
    permission_classes = [IsAuthenticated]
    queryset = STT.objects.order_by("name")
    serializer_class = STTSerializer


class STTApiViewSet(mixins.ListModelMixin,
                    viewsets.GenericViewSet):
    """Simple view to get all STTs."""

    pagination_class = None
    permission_classes = [IsAuthenticated]
    queryset = STT.objects
    serializer_class = STTSerializer
    lookup_field = "name"

    @action(methods=["get"], detail=True)
    def num_sections(self, request, name=None):
        """Return number of sections an stt submits based on stt name."""
        try:
            stt = self.queryset.get(name=name)
            self.check_object_permissions(request, stt)
            divisor = int(stt.ssp) + 1
            return Response({"num_sections": len(stt.filenames) // divisor})
        except Exception:
            logger.exception(f"Caught exception trying to get STT with name {stt}.")
            return Response(status=status.HTTP_404_NOT_FOUND)
