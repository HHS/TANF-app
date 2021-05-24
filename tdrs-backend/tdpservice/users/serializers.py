"""Serialize user data."""

import logging
from django.contrib.auth.models import Group, Permission
from rest_framework import serializers

from .models import User
from tdpservice.stts.serializers import STTUpdateSerializer

logger = logging.getLogger()
logger.setLevel(logging.INFO)


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


class GroupSerializer(serializers.ModelSerializer):
    """Group (role) serializer."""

    permissions = PermissionSerializer(many=True)

    class Meta:
        """Metadata."""

        model = Group
        fields = ["id", "name", "permissions"]


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


class UserProfileSerializer(serializers.ModelSerializer):
    """Serializer used for setting a user's profile."""

    stt = STTUpdateSerializer(required=True)
    email = serializers.SerializerMethodField("get_email")
    roles = GroupSerializer(
        many=True, required=False, allow_empty=True, source="groups"
    )

    class Meta:
        """Metadata."""

        model = User
        fields = ["id", "first_name", "last_name", "email", "stt", "roles"]

        """Enforce first and last name to be in API call and not empty"""
        extra_kwargs = {
            "first_name": {"allow_blank": False, "required": True},
            "last_name": {"allow_blank": False, "required": True},
        }

    def update(self, instance, validated_data):
        """Update the user with the STT."""
        instance.stt_id = validated_data.pop("stt")["id"]
        return super().update(instance, validated_data)

    def get_email(self, obj):
        """Return the user's email address."""
        return obj.username
