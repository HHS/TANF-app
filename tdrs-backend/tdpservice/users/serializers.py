"""Serialize user data."""

import logging
from rest_framework import serializers

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


class SetUserProfileSerializer(serializers.ModelSerializer):
    """Serializer used for setting a user's profile."""

    stt = STTUpdateSerializer(required=True)
    email = serializers.SerializerMethodField('get_email')

    class Meta:
        """Metadata."""

        model = User
        fields = ["first_name", "last_name", "stt", "email"]

        """Enforce first and last name to be in API call and not empty"""
        extra_kwargs = {
            "first_name": {"allow_blank": False, "required": True},
            "last_name": {"allow_blank": False, "required": True},
        }

    def update(self, instance, validated_data):
        """Update the user with the STT."""
        instance.stt_id = validated_data.pop("stt")["id"]
        return super().update(instance, validated_data)

    def get_email(self,obj):
        return obj.username

