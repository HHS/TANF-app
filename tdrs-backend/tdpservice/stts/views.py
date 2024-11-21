"""Define API views for user class."""
import logging

from django.db.models import Prefetch
from rest_framework import generics, mixins, status, viewsets
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
                    mixins.RetrieveModelMixin,
                    viewsets.GenericViewSet):
    """Simple view to get all STTs."""

    pagination_class = None
    permission_classes = [IsAuthenticated]
    queryset = STT.objects
    serializer_class = STTSerializer

    def retrieve(self, request, pk=None):
        """Return a specific user."""
        try:
            stt = self.queryset.get(name=pk)
            self.check_object_permissions(request, stt)
            serializer = self.get_serializer_class()(stt)
            return Response(serializer.data)
        except Exception:
            logger.exception(f"Caught exception trying to get STT with name {pk}.")
            return Response(status=status.HTTP_404_NOT_FOUND)
