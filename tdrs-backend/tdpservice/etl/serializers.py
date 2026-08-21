"""Serializers for ETL pipeline APIs."""

from rest_framework import serializers

from tdpservice.etl.exceptions import PipelineValidationError
from tdpservice.etl.models import ETLArtifact, ETLNodeRun, ETLPipelineRun, ETLQAResult
from tdpservice.etl.registry import get_pipeline_definition, list_pipeline_definitions


class PipelineDefinitionSerializer(serializers.Serializer):
    """Serialize a code-defined pipeline definition."""

    key = serializers.CharField()
    version = serializers.CharField()
    display_name = serializers.CharField()
    description = serializers.CharField()
    allowed_parameters = serializers.JSONField()
    schedule = serializers.JSONField(allow_null=True)
    nodes = serializers.JSONField()

    @classmethod
    def from_registry(cls, **kwargs):
        """Return a serializer over registered pipeline definitions."""
        definitions = [
            definition.serialize() for definition in list_pipeline_definitions()
        ]
        return cls(definitions, **kwargs)


class ETLNodeRunSerializer(serializers.ModelSerializer):
    """Serialize node run status."""

    class Meta:
        """Serializer metadata."""

        model = ETLNodeRun
        fields = [
            "id",
            "node_key",
            "status",
            "started_at",
            "finished_at",
            "input_row_count",
            "output_row_count",
            "error_message",
            "metadata",
        ]


class ETLQAResultSerializer(serializers.ModelSerializer):
    """Serialize persisted QA checks."""

    class Meta:
        """Serializer metadata."""

        model = ETLQAResult
        fields = [
            "id",
            "check_key",
            "status",
            "summary",
            "result_payload",
            "blocking",
            "created_at",
        ]


class ETLArtifactSerializer(serializers.ModelSerializer):
    """Serialize run-scoped artifact manifests."""

    class Meta:
        """Serializer metadata."""

        model = ETLArtifact
        fields = [
            "id",
            "key",
            "artifact_role",
            "artifact_kind",
            "storage_kind",
            "reference",
            "schema_key",
            "schema_version",
            "version",
            "row_count",
            "published",
            "metadata",
            "created_at",
        ]


class ETLPipelineRunSerializer(serializers.ModelSerializer):
    """Serialize pipeline run history with node, QA, and output status."""

    node_runs = ETLNodeRunSerializer(many=True, read_only=True)
    qa_results = ETLQAResultSerializer(many=True, read_only=True)
    artifacts = ETLArtifactSerializer(many=True, read_only=True)
    final_output = ETLArtifactSerializer(read_only=True)

    class Meta:
        """Serializer metadata."""

        model = ETLPipelineRun
        fields = [
            "id",
            "pipeline_key",
            "pipeline_version",
            "status",
            "parameters",
            "output_scope",
            "metadata",
            "trigger_source",
            "triggered_by",
            "retry_of",
            "final_output",
            "started_at",
            "finished_at",
            "error_message",
            "created_at",
            "updated_at",
            "node_runs",
            "qa_results",
            "artifacts",
        ]
        read_only_fields = fields


class ETLPipelineRunCreateSerializer(serializers.Serializer):
    """Validate admin-created pipeline run requests."""

    pipeline_key = serializers.CharField()
    parameters = serializers.JSONField(default=dict)

    def validate(self, attrs):
        """Validate the requested pipeline key and parameters."""
        try:
            definition = get_pipeline_definition(attrs["pipeline_key"])
        except KeyError as exc:
            raise serializers.ValidationError({"pipeline_key": str(exc)}) from exc

        try:
            attrs["parameters"] = definition.validate_parameters(
                attrs.get("parameters", {})
            )
        except PipelineValidationError as exc:
            raise serializers.ValidationError({"parameters": str(exc)}) from exc

        return attrs
