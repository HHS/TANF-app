"""Serialize user data."""

import logging
from django.contrib.auth.models import Group, Permission
from django.core.exceptions import ValidationError
from rest_framework import serializers

from tdpservice.stts.serializers import STTPrimaryKeyRelatedField, RegionPrimaryKeyRelatedField
from tdpservice.users.models import User


logger = logging.getLogger(__name__)


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
            "access_request",
            'access_requested',
            "account_approval_status"
        )
        read_only_fields = ("username", 'access_requested', "account_approval_status",)


class UserProfileSerializer(serializers.ModelSerializer):
    """Serializer used for retrieving/updating a user's profile."""

    email = serializers.CharField(read_only=True, source='username')
    roles = GroupSerializer(
        many=True,
        read_only=True,
        source='groups'
    )
    stt = STTPrimaryKeyRelatedField(required=False)
    region = RegionPrimaryKeyRelatedField(required=False)

    class Meta:
        """Metadata."""

        model = User
        fields = [
            'id',
            'first_name',
            'last_name',
            'email',
            'stt',
            'region',
            'roles',
            'access_request',
            'access_requested',
            'account_approval_status'
        ]
        read_only_fields = ('access_requested', "account_approval_status",)

        """Enforce first and last name to be in API call and not empty"""
        extra_kwargs = {
            'first_name': {'allow_blank': False, 'required': True},
            'last_name': {'allow_blank': False, 'required': True},
            'stt': {'allow_blank': True, 'required': False},
            'region': {'allow_blank': True, 'required': False},
        }

    def update(self, instance, validated_data):
        """Perform model validation before saving."""
        instance = super(UserProfileSerializer, self).update(instance, validated_data)

        try:
            instance.validate_location()
        except ValidationError as e:
            raise serializers.ValidationError(e.message)

        return instance
