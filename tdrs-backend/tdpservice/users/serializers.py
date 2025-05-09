"""Serialize user data."""

import logging
from django.contrib.auth.models import Group, Permission
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers, utils

from tdpservice.stts.serializers import STTPrimaryKeyRelatedField, RegionPrimaryKeyRelatedField
from tdpservice.users.models import User, UserChangeRequest, ChangeRequestAuditLog


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


class UserProfileChangeRequestSerializer(UserProfileSerializer):
    """Serializer for user profile updates that creates change requests instead of direct updates."""

    # Add a field to indicate whether to create change requests or update directly
    create_change_requests = serializers.BooleanField(default=True, write_only=True)

    # Add fields to track pending change requests
    has_pending_first_name_change = serializers.SerializerMethodField()
    has_pending_last_name_change = serializers.SerializerMethodField()
    has_pending_stt_change = serializers.SerializerMethodField()
    has_pending_regions_change = serializers.SerializerMethodField()

    class Meta(UserProfileSerializer.Meta):
        """Metadata."""
        # Add the new fields to the existing fields list
        fields = UserProfileSerializer.Meta.fields + [
            'create_change_requests',
            'has_pending_first_name_change',
            'has_pending_last_name_change',
            'has_pending_stt_change',
            'has_pending_regions_change',
        ]

    def get_has_pending_first_name_change(self, obj):
        """Check if there's a pending change request for first_name."""
        return obj.has_pending_change_for_field('first_name')

    def get_has_pending_last_name_change(self, obj):
        """Check if there's a pending change request for last_name."""
        return obj.has_pending_change_for_field('last_name')

    def get_has_pending_stt_change(self, obj):
        """Check if there's a pending change request for stt."""
        return obj.has_pending_change_for_field('stt')

    def get_has_pending_regions_change(self, obj):
        """Check if there's a pending change request for regions."""
        return obj.has_pending_change_for_field('regions')

    def update(self, instance, validated_data):
        """Handle updates by either creating change requests or updating directly."""
        # Extract and remove the create_change_requests flag
        create_change_requests = validated_data.pop('create_change_requests', True)

        # If not creating change requests, use the parent update method
        print(f"\n\nCreating change requests: {create_change_requests}\n\n")
        if not create_change_requests:
            # Only admins can bypass change requests
            user = self.context['request'].user
            if not (user.is_an_admin or user.is_ofa_sys_admin):
                raise serializers.ValidationError({
                    'create_change_requests': _('Only administrators can update user profiles directly.')
                })
            return super().update(instance, validated_data)

        # Otherwise, create change requests for each field
        change_requests = []

        # Process simple fields
        print("Processing first name and last name")
        for field_name in ['first_name', 'last_name']:
            if field_name in validated_data:
                # Check if the value is actually changing
                new_value = validated_data[field_name]
                current_value = getattr(instance, field_name)

                if new_value != current_value:
                    # Create a change request
                    change_request = instance.request_change(
                        field_name=field_name,
                        requested_value=new_value,
                        requested_by=self.context['request'].user
                    )
                    change_requests.append(change_request)

        # Process STT field
        print("Processing stt")
        if 'stt' in validated_data:
            new_stt = validated_data['stt']
            current_stt = instance.stt

            # Compare IDs for foreign keys
            new_stt_id = new_stt.id if new_stt else None
            current_stt_id = current_stt.id if current_stt else None

            if new_stt_id != current_stt_id:
                change_request = instance.request_change(
                    field_name='stt',
                    requested_value=new_stt_id,
                    requested_by=self.context['request'].user
                )
                change_requests.append(change_request)

        # Process regions field (many-to-many)
        print("processing regions")
        if 'regions' in validated_data:
            new_regions = validated_data['regions']
            current_regions = set(instance.regions.all().values_list('id', flat=True))
            new_region_ids = set(region.id for region in new_regions)

            if current_regions != new_region_ids:
                # Store as a list of IDs
                change_request = instance.request_change(
                    field_name='regions',
                    requested_value=list(new_region_ids),
                    requested_by=self.context['request'].user
                )
                change_requests.append(change_request)

        # Return the instance without changes
        return instance


class UserChangeRequestSerializer(serializers.ModelSerializer):
    """Serializer for user change requests."""

    class Meta:
        """Meta class for serializer configuration."""

        model = UserChangeRequest
        fields = [
            'id', 'user', 'field_name', 'current_value',
            'requested_value', 'status', 'requested_at'
        ]
        read_only_fields = ['status', 'requested_at']

    def create(self, validated_data):
        """Create a new change request with current value automatically set."""
        user = validated_data['user']
        field_name = validated_data['field_name']

        # Get the current value from the user object
        try:
            current_value = str(getattr(user, field_name, ''))
        except (AttributeError, TypeError):
            current_value = ''

        # Set the current value and requested_by
        validated_data['current_value'] = current_value
        validated_data['requested_by'] = self.context['request'].user

        # Create the change request
        change_request = super().create(validated_data)

        # Create audit log entry
        ChangeRequestAuditLog.objects.create(
            change_request=change_request,
            action='created',
            performed_by=self.context['request'].user,
            details={
                'field': field_name,
                'requested_value': validated_data['requested_value']
            }
        )

        return change_request

    def validate(self, data):
        """Validate that the field exists and is editable."""
        field_name = data.get('field_name')
        user = data.get('user')

        # Check if the field exists on the User model
        if not hasattr(User, field_name):
            raise serializers.ValidationError({
                'field_name': _('This field does not exist on the User model.')
            })

        # Check if the field is in the list of allowed fields for change requests
        allowed_fields = [
            'first_name', 'last_name', 'email',
            'stt', 'regions'
        ]
        if field_name not in allowed_fields:
            raise serializers.ValidationError({
                'field_name': _('This field cannot be changed through a change request.')
            })

        # Ensure the requested value is different from the current value
        current_value = str(getattr(user, field_name, ''))
        requested_value = data.get('requested_value', '')
        if current_value == requested_value:
            raise serializers.ValidationError({
                'requested_value': _('The requested value is the same as the current value.')
            })

        return data


class AdminChangeRequestSerializer(serializers.ModelSerializer):
    """Serializer for admin management of change requests."""

    user_email = serializers.EmailField(source='user.email', read_only=True)
    user_username = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        """Meta class for serializer configuration."""

        model = UserChangeRequest
        fields = [
            'id', 'user', 'user_email', 'user_username', 'field_name',
            'current_value', 'requested_value', 'status', 'requested_at',
            'reviewed_at', 'reviewed_by', 'notes'
        ]
        read_only_fields = [
            'user', 'field_name', 'current_value',
            'requested_value', 'requested_at'
        ]

    def validate_status(self, value):
        """Validate status transitions."""
        instance = getattr(self, 'instance', None)
        if instance and instance.status != 'pending' and value != instance.status:
            raise serializers.ValidationError(
                _('Cannot change status of a request that has already been processed.')
            )
        return value

    def update(self, instance, validated_data):
        """Update the change request and apply changes if approved."""
        status = validated_data.get('status')
        notes = validated_data.get('notes')
        user = self.context['request'].user

        # If status is changing to approved or rejected, handle appropriately
        if status and instance.status == 'pending':
            if status == 'approved':
                instance.approve(user, notes)
            elif status == 'rejected':
                instance.reject(user, notes)
            return instance

        # Otherwise, just update the fields normally
        return super().update(instance, validated_data)


class ChangeRequestAuditLogSerializer(serializers.ModelSerializer):
    """Serializer for change request audit logs."""

    class Meta:
        """Meta class for serializer configuration."""

        model = ChangeRequestAuditLog
        fields = ['id', 'change_request', 'action', 'performed_by', 'timestamp', 'details']
        read_only_fields = fields
