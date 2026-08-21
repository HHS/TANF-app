"""API views for approved ETL pipelines."""

from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from tdpservice.etl.exceptions import ActivePipelineRunError, PipelineValidationError
from tdpservice.etl.models import ETLPipelineRun
from tdpservice.etl.permissions import ETLPermissions
from tdpservice.etl.runner import PipelineRunFactory
from tdpservice.etl.serializers import (
    ETLPipelineRunCreateSerializer,
    ETLPipelineRunSerializer,
    PipelineDefinitionSerializer,
)
from tdpservice.etl.tasks import enqueue_pipeline_run


class PipelineViewSet(viewsets.ViewSet):
    """Expose registered ETL pipeline definitions."""

    permission_classes = [ETLPermissions]

    def list(self, request):
        """List approved code-defined ETL pipelines."""
        serializer = PipelineDefinitionSerializer.from_registry(many=True)
        return Response(serializer.data)


class PipelineRunViewSet(viewsets.ModelViewSet):
    """Create and inspect ETL pipeline runs."""

    http_method_names = ["get", "post", "head", "options"]
    serializer_class = ETLPipelineRunSerializer
    permission_classes = [ETLPermissions]
    queryset = (
        ETLPipelineRun.objects.all()
        .select_related("triggered_by", "retry_of", "final_output")
        .prefetch_related("node_runs", "qa_results", "artifacts")
        .order_by("-created_at")
    )

    def create(self, request, *args, **kwargs):
        """Create and enqueue an approved pipeline run."""
        serializer = ETLPipelineRunCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            pipeline_run = PipelineRunFactory.for_pipeline_key(
                serializer.validated_data["pipeline_key"]
            ).create(
                parameters=serializer.validated_data["parameters"],
                trigger_source=ETLPipelineRun.TriggerSource.ADMIN,
                triggered_by=request.user,
            )
        except ActivePipelineRunError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_409_CONFLICT)
        except PipelineValidationError as exc:
            raise ValidationError(str(exc)) from exc

        enqueue_pipeline_run(pipeline_run)
        response_serializer = self.get_serializer(pipeline_run)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)

    @action(methods=["post"], detail=True)
    def retry(self, request, pk=None):
        """Retry a failed pipeline run with the same parameters."""
        failed_run = self.get_object()
        if failed_run.status != ETLPipelineRun.Status.FAILED:
            raise ValidationError("Only failed ETL runs can be retried.")

        try:
            pipeline_run = PipelineRunFactory.for_pipeline_key(
                failed_run.pipeline_key
            ).create(
                parameters=failed_run.parameters,
                trigger_source=ETLPipelineRun.TriggerSource.RETRY,
                triggered_by=request.user,
                retry_of=failed_run,
            )
        except ActivePipelineRunError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_409_CONFLICT)
        except PipelineValidationError as exc:
            raise ValidationError(str(exc)) from exc

        enqueue_pipeline_run(pipeline_run)
        response_serializer = self.get_serializer(pipeline_run)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)
