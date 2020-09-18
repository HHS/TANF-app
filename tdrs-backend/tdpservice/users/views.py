"""Define API views for user class."""
import datetime
import logging
import time

from django.db.models import Prefetch

from rest_framework import generics, mixins, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from .models import Region, STT, User
from .permissions import IsUserOrReadOnly
from .serializers import (
    CreateUserSerializer,
    RegionSerializer,
    SetUserProfileSerializer,
    UserSerializer,
)

logger = logging.getLogger(__name__)


class RegionAPIView(generics.ListAPIView):
    """Simple view to get all regions and STTs, without pagination."""

    pagination_class = None
    permission_classes = [AllowAny]
    queryset = Region.objects.prefetch_related(
        Prefetch("stts", queryset=STT.objects.select_related("state").order_by("name"))
    ).order_by("id")
    serializer_class = RegionSerializer


class UserViewSet(
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    viewsets.GenericViewSet,
):
    """User accounts viewset."""

    queryset = User.objects.all()

    def get_permissions(self):
        """Get permissions for the viewset."""
        if self.action == "create":
            permission_classes = [AllowAny]
        else:
            permission_classes = [IsUserOrReadOnly]
        return [permission() for permission in permission_classes]

    def get_serializer_class(self):
        """Return the serializer class."""
        return {
            "create": CreateUserSerializer,
            "set_profile": SetUserProfileSerializer,
        }.get(self.action, UserSerializer)

    @action(methods=["POST"], detail=False)
    def set_profile(self, request, pk=None):
        """Set a user's profile data."""
        serializer = self.get_serializer(self.request.user, request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        datetime_time = datetime.datetime.fromtimestamp(time.time())
        logger.info(
            f"Profile update for user:  {self.request.user} on {datetime_time}(UTC)"
        )
        return Response(serializer.data)
