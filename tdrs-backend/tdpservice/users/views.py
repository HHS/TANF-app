"""Define API views for user class."""

from rest_framework import mixins, viewsets
from rest_framework.permissions import AllowAny

from .models import User
from .permissions import IsUserOrReadOnly
from .serializers import CreateUserSerializer, UserSerializer


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
        if self.action == "create":
            return CreateUserSerializer
        return UserSerializer
