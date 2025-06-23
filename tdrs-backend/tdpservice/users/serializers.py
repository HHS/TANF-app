"""Serialize user data."""

import logging
from django.contrib.auth.models import Group, Permission
from django.core.exceptions import ValidationError
from django.utils import timezone
from rest_framework import serializers, utils

from tdpservice.stts.serializers import STTPrimaryKeyRelatedField, RegionPrimaryKeyRelatedField
from tdpservice.users.models import User, Feedback


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
            "account_approval_status",
            'groups',
            'is_superuser',
            'is_staff',
            'stt',
            'regions',
            'login_gov_uuid',
            'hhs_id',
            'last_login',
            'date_joined',
            'access_requested_date',
        )
        read_only_fields = (
            'id',
            'username',
            'access_request',
            'account_approval_status',
            'groups',
            'login_gov_uuid',
            'is_staff',
            'is_superuser',
            'hhs_id',
            'last_login',
            'date_joined',
            'access_requested_date',
        )


class UserProfileSerializer(serializers.ModelSerializer):
    """Serializer used for retrieving/updating a user's profile."""

    email = serializers.CharField(read_only=True, source='username')
    roles = GroupSerializer(
        many=True,
        read_only=True,
        source='groups'
    )
    stt = STTPrimaryKeyRelatedField(required=False)
    regions = RegionPrimaryKeyRelatedField(many=True, required=False)

    class Meta:
        """Metadata."""

        model = User
        fields = [
            'id',
            'first_name',
            'last_name',
            'email',
            'stt',
            'regions',
            'login_gov_uuid',
            'hhs_id',
            'roles',
            'groups',
            'is_superuser',
            'is_staff',
            'last_login',
            'date_joined',
            'access_request',
            'access_requested_date',
            'account_approval_status',
            'feature_flags',
        ]
        read_only_fields = (
            'id',
            'email',
            'login_gov_uuid',
            'hhs_id',
            'groups',
            'roles',
            'is_staff',
            'is_superuser',
            'last_login',
            'date_joined',
            'access_request',
            'access_requested_date',
            'account_approval_status',
            'feature_flags',
        )

        """Enforce first and last name to be in API call and not empty"""
        extra_kwargs = {
            'first_name': {'allow_blank': False, 'required': True},
            'last_name': {'allow_blank': False, 'required': True},
            'stt': {'allow_blank': True, 'required': False},
            'regions': {'allow_blank': True, 'required': False},
        }

    def update(self, instance, validated_data):
        """Perform model validation before saving."""
        ###############################################################################################################
        # This code block is pulled directly from rest_framework.serializers.ModelSerializer::update.
        # The only modification is to the line 1033 in rest_framework.serializers.ModelSerializer::update.
        # The User model M2M fields are passed as a kwargs to `save()` so that the email context can access the
        # fields.
        serializers.raise_errors_on_nested_writes('update', self, validated_data)
        info = utils.model_meta.get_field_info(instance)
        # Simply set each attribute on the instance, and then save it.
        # Note that unlike `.create()` we don't need to treat many-to-many
        # relationships as being a special case. During updates we already
        # have an instance pk for the relationships to be associated with.
        m2m_fields = []
        for attr, value in validated_data.items():
            if attr in info.relations and info.relations[attr].to_many:
                m2m_fields.append((attr, value))
            else:
                setattr(instance, attr, value)

        # We changed this line
        instance.save(regions=validated_data.get('regions', []))

        # Note that many-to-many fields are set after updating instance.
        # Setting m2m fields triggers signals which could potentially change
        # updated instance and we do not want it to collide with .update()
        for attr, value in m2m_fields:
            field = getattr(instance, attr)
            field.set(value)
        ###############################################################################################################

        try:
            instance.validate_location()
        except ValidationError as e:
            raise serializers.ValidationError(e.message)

        return instance


class FeedbackSerializer(serializers.ModelSerializer):
    """Serializer for user feedback."""

    class Meta:
        """Serializer metadata."""

        model = Feedback
        fields = (
            'id',
            'user',
            'rating',
            'feedback',
        )
        read_only_fields = (
            'id',
            'acked',
            'reviewed_at',
            'reviewed_by',
        )

    def create(self, validated_data):
        """Create a new feedback instance."""
        return Feedback.objects.create(**validated_data, created_at=timezone.now())
