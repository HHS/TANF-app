"""Serialize stt data."""

from rest_framework import serializers

from tdpservice.stts.models import Region, STT


class STTSerializer(serializers.ModelSerializer):
    """STT serializer."""

    code = serializers.SerializerMethodField()

    class Meta:
        """Metadata."""

        model = STT
        fields = ["id", "type", "code", "name"]

    def get_code(self, obj):
        """Return the state code."""
        if obj.type == STT.EntityType.TRIBE:
            return obj.state.code
        return obj.code


class STTPrimaryKeyRelatedField(serializers.PrimaryKeyRelatedField):
    """Accept STT ID only for updates but return full STT in response."""

    queryset = STT.objects.all()

    def to_representation(self, value):
        """Return full STT object on outgoing serialization."""
        instance = self.queryset.get(pk=value.pk)
        return STTSerializer(instance).data


class RegionSerializer(serializers.ModelSerializer):
    """Region serializer."""

    stts = STTSerializer(many=True)

    class Meta:
        """Metadata."""

        model = Region
        fields = ["id", "stts"]
