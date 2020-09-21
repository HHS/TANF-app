"""Define API views for user class."""
import logging

from django.db.models import Prefetch
from rest_framework import generics
from rest_framework.permissions import AllowAny
from tdpservice.stts.models import Region, STT
from .serializers import RegionSerializer

logger = logging.getLogger(__name__)


class RegionAPIView(generics.ListAPIView):
    """Simple view to get all regions and STTs, without pagination."""

    pagination_class = None
    permission_classes = [AllowAny]
    queryset = Region.objects.prefetch_related(
        Prefetch("stts", queryset=STT.objects.select_related("state").order_by("name"))
    ).order_by("id")
    serializer_class = RegionSerializer
