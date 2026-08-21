"""Admin registrations for ETL models."""

from urllib.parse import urlencode

from django.apps import apps
from django.contrib import admin
from django.db import models
from django.urls import NoReverseMatch, reverse
from django.utils.html import format_html

from tdpservice.core.utils import ReadOnlyAdminMixin
from tdpservice.etl.models import (
    ETLArtifact,
    ETLNodeRun,
    ETLPipelineRun,
    ETLQAResult,
    StatisticalWeight,
    StatisticalWeightsCaseCount,
)


@admin.register(ETLPipelineRun)
class ETLPipelineRunAdmin(ReadOnlyAdminMixin, admin.ModelAdmin):
    """Admin view for pipeline runs."""

    list_display = (
        "id",
        "pipeline_key",
        "pipeline_version",
        "status",
        "trigger_source",
        "triggered_by",
        "final_output_link",
        "created_at",
        "started_at",
        "finished_at",
    )
    list_filter = ("pipeline_key", "status", "trigger_source")
    search_fields = ("pipeline_key", "error_message")
    readonly_fields = ("final_output_link", "created_at", "updated_at")

    @admin.display(description="Final output")
    def final_output_link(self, obj: ETLPipelineRun) -> str:
        """Return an admin link to the run's final output."""
        output = obj.final_output
        if output is None:
            return "-"

        return format_html(
            "<a href='{url}'>{label}</a>",
            url=self._final_output_url(obj, output),
            label=self._final_output_label(output),
        )

    def _final_output_url(
        self,
        pipeline_run: ETLPipelineRun,
        output: ETLArtifact,
    ) -> str:
        if output.storage_kind == ETLArtifact.StorageKind.POSTGRES_TABLE:
            table_url = self._table_output_url(pipeline_run, output)
            if table_url:
                return table_url

        return reverse("admin:etl_etlartifact_change", args=[output.id])

    def _table_output_url(
        self,
        pipeline_run: ETLPipelineRun,
        output: ETLArtifact,
    ) -> str | None:
        model = self._model_for_db_table(output.reference)
        if model is None:
            return None

        try:
            changelist_url = reverse(
                f"admin:{model._meta.app_label}_{model._meta.model_name}_changelist"
            )
        except NoReverseMatch:
            return None

        query_string = urlencode(self._table_output_filter(model, pipeline_run, output))
        if query_string:
            return f"{changelist_url}?{query_string}"
        return changelist_url

    def _table_output_filter(
        self,
        model: type[models.Model],
        pipeline_run: ETLPipelineRun,
        output: ETLArtifact,
    ) -> dict[str, object]:
        scope = {**pipeline_run.output_scope, **(output.metadata or {})}
        field_names = {
            field.name for field in model._meta.fields if hasattr(field, "attname")
        }
        filters = {
            f"{key}__exact": value
            for key, value in scope.items()
            if key in field_names and value not in (None, "")
        }
        if "version" in field_names and output.version is not None:
            filters["version__exact"] = output.version
        return filters

    def _model_for_db_table(self, db_table: str) -> type[models.Model] | None:
        for model in apps.get_models():
            if model._meta.db_table == db_table:
                return model
        return None

    def _final_output_label(self, output: ETLArtifact) -> str:
        version = f" v{output.version}" if output.version else ""
        return f"{output.key}{version} ({output.row_count} rows)"


@admin.register(ETLNodeRun)
class ETLNodeRunAdmin(ReadOnlyAdminMixin, admin.ModelAdmin):
    """Admin view for node runs."""

    list_display = (
        "id",
        "pipeline_run",
        "node_key",
        "status",
        "input_row_count",
        "output_row_count",
    )
    list_filter = ("node_key", "status")
    search_fields = ("node_key", "error_message")


@admin.register(ETLQAResult)
class ETLQAResultAdmin(ReadOnlyAdminMixin, admin.ModelAdmin):
    """Admin view for QA results."""

    list_display = ("id", "pipeline_run", "check_key", "status", "blocking")
    list_filter = ("check_key", "status", "blocking")
    search_fields = ("check_key", "summary")


@admin.register(ETLArtifact)
class ETLArtifactAdmin(ReadOnlyAdminMixin, admin.ModelAdmin):
    """Admin view for run-scoped ETL artifacts."""

    list_display = (
        "id",
        "pipeline_run",
        "key",
        "artifact_role",
        "artifact_kind",
        "storage_kind",
        "version",
        "row_count",
        "published",
        "created_at",
    )
    list_filter = (
        "key",
        "artifact_role",
        "artifact_kind",
        "storage_kind",
        "schema_key",
        "published",
    )
    search_fields = ("key", "reference", "schema_key")


@admin.register(StatisticalWeightsCaseCount)
class StatisticalWeightsCaseCountAdmin(ReadOnlyAdminMixin, admin.ModelAdmin):
    """Admin view for statistical weights aggregate count rows."""

    list_display = (
        "id",
        "pipeline_run",
        "count_kind",
        "stt_code",
        "reporting_month",
        "stratum",
        "count",
    )
    list_filter = ("count_kind", "reporting_month", "stt_code", "stratum")
    search_fields = ("stt_code", "stratum")


@admin.register(StatisticalWeight)
class StatisticalWeightAdmin(ReadOnlyAdminMixin, admin.ModelAdmin):
    """Admin view for statistical weights."""

    list_display = (
        "id",
        "fiscal_year",
        "reporting_month",
        "program",
        "section",
        "stt_code",
        "stratum",
        "version",
        "weight",
        "retention_expires_at",
    )
    list_filter = ("fiscal_year", "program", "section", "version")
    search_fields = ("stt_code", "stratum")
