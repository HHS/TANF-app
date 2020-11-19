"""Serialize user data."""

from rest_framework import serializers
from tdpservice.core.models import GlobalPermission


from .models import User
from tdpservice.stts.serializers import STTUpdateSerializer

logger = logging.getLogger()
logger.setLevel(logging.INFO)
logger.addHandler(logging.StreamHandler())


class UserSerializer(serializers.ModelSerializer):
    """Define meta user serializer class."""

    class Meta:
        """Define meta user serializer attributes."""

        model = User
        fields = (
            "id",
            "username",
            "first_name",
            "last_name",
        )
        read_only_fields = ("username",)


class CreateUserSerializer(serializers.ModelSerializer):
    """Defined class to create the user serializer."""

    def create(self, validated_data):
        """Serialize the user object."""
        # call create_user on user object. Without this
        # the password will be stored in plain text.
        user = User.objects.create_user(**validated_data)
        return user

    class Meta:
        """Define meta user serializer attributes."""

        model = User
        fields = (
            "id",
            "username",
            "password",
            "first_name",
            "last_name",
            "email",
            "auth_token",
        )
        read_only_fields = ("auth_token",)
        extra_kwargs = {"password": {"write_only": True}}


class UserProfileSerializer(serializers.ModelSerializer):
    """Serializer used for setting a user's profile."""

    stt = STTUpdateSerializer(required=True)
    email = serializers.SerializerMethodField("get_email")

    class Meta:
        """Metadata."""

        model = User
        fields = ["first_name", "last_name", "stt", "email"]

        """Enforce first and last name to be in API call and not empty"""
        extra_kwargs = {
            "first_name": {"allow_blank": False, "required": True},
            "last_name": {"allow_blank": False, "required": True},
            "requested_roles": {"allow_empty": True, "required": False},
        }

    def update(self, instance, validated_data):
        """Update the user with the STT."""
        instance.stt_id = validated_data.pop("stt")["id"]
        return super().update(instance, validated_data)

    def get_email(self, obj):
        """Return the user's email address."""
        return obj.username


class PermissionSerializer(serializers.ModelSerializer):
    """Permission serializer."""

    content_type = serializers.CharField(
        required=False, allow_null=True, write_only=True
    )

    class Meta:
        """Metadata."""

        model = Permission
        fields = ["id", "codename", "name", "content_type"]
        extra_kwargs = {
            "content_type": {"allow_null": True},
        }

    def validate_content_type(self, value):
        """If no content type is set, use the one for global permissions."""
        if not value:
            content_type = ContentType.objects.get_for_model(GlobalPermission)
            return content_type

        return ContentType.objects.get_by_natural_key(*value.split("."))


class GroupSerializer(serializers.ModelSerializer):
    """Group (role) serializer."""

    class Meta:
        """Metadata."""

        model = Group
        fields = ["id", "name", "permissions"]
