"""Define API views for user class."""
import logging

from django.db.models import Prefetch
from rest_framework import generics
from rest_framework.permissions import AllowAny
from tdpservice.stts.models import Region, STT
from .serializers import RegionSerializer, STTSerializer

logger = logging.getLogger(__name__)


class RegionAPIView(generics.ListAPIView):
    """Simple view to get all regions and STTs, without pagination."""

    pagination_class = None
    permission_classes = [AllowAny]
    queryset = Region.objects.prefetch_related(
        Prefetch("stts", queryset=STT.objects.select_related("state").order_by("name"))
    ).order_by("id")
    serializer_class = RegionSerializer


class STTApiView(generics.ListAPIView):
    """Simple view to get all STTs alphabetized."""

    pagination_class = None
    permission_classes = [AllowAny]
    queryset = STT.objects.order_by("name")
    serializer_class = STTSerializer
