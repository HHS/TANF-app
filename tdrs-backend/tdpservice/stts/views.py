"""Define API views for user class."""
import logging

from django.db.models import Prefetch
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
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


class STTApiView(generics.ListAPIView):
    """Simple view to get all STTs."""

    pagination_class = None
    permission_classes = [IsAuthenticated]
    queryset = STT.objects
    serializer_class = STTSerializer
