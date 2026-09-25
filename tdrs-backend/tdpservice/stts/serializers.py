"""Serialize stt data."""

from rest_framework import serializers

from tdpservice.data_files.models import Program, Section
from tdpservice.stts.models import STT, Region, SttProgramParticipation


class ProgramSerializer(serializers.ModelSerializer):
    """Program serializer."""

    class Meta:
        """Metadata."""

        model = Program
        fields = ["id", "slug", "name"]


class SectionSerializer(serializers.ModelSerializer):
    """Section serializer."""

    program = ProgramSerializer()

    class Meta:
        """Metadata."""

        model = Section
        fields = ["id", "program", "name"]


class SttProgramParticipationSerializer(serializers.ModelSerializer):
    """STT program participation serializer."""

    program = ProgramSerializer()
    sections = SectionSerializer(many=True)

    class Meta:
        """Metadata."""

        model = SttProgramParticipation
        fields = ["id", "program", "status", "sections"]


class STTSerializer(serializers.ModelSerializer):
    """STT serializer."""

    postal_code = serializers.SerializerMethodField()
    program_participations = SttProgramParticipationSerializer(many=True)

    class Meta:
        """Metadata."""

        model = STT
        fields = [
            "id",
            "type",
            "postal_code",
            "name",
            "region",
            "filenames",
            "stt_code",
            "ssp",
            "program_participations",
            "num_sections",
        ]

    def get_postal_code(self, obj):
        """Return the state postal_code."""
        if obj.type == STT.EntityType.TRIBE:
            return obj.state.postal_code
        return obj.postal_code


class STTPrimaryKeyRelatedField(serializers.PrimaryKeyRelatedField):
    """Accept STT ID only for updates but return full STT in response."""

    queryset = STT.objects.select_related("state").prefetch_related(
        "program_participations__program",
        "program_participations__sections__program",
    )

    def to_representation(self, value):
        """Return full STT object on outgoing serialization."""
        instance = self.queryset.get(pk=value.pk)
        return STTSerializer(instance).data


class RegionPrimaryKeyRelatedField(serializers.PrimaryKeyRelatedField):
    """Accept Region ID only for updates but return full Region in response."""

    queryset = Region.objects.prefetch_related(
        "stts__state",
        "stts__program_participations__program",
        "stts__program_participations__sections__program",
    )

    def to_representation(self, value):
        """Return full Region object on outgoing serialization."""
        instance = self.queryset.get(pk=value.pk)
        return RegionSerializer(instance).data


class RegionSerializer(serializers.ModelSerializer):
    """Region serializer."""

    stts = STTSerializer(many=True)

    class Meta:
        """Metadata."""

        model = Region
        fields = ["id", "stts"]
