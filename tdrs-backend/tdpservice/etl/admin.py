"""Admin registrations for ETL models."""

from functools import partial
from urllib.parse import urlencode

from django import forms
from django.apps import apps
from django.contrib import admin, messages
from django.db import models, transaction
from django.shortcuts import redirect
from django.urls import NoReverseMatch, reverse
from django.utils.html import format_html

from tdpservice.core.utils import ReadOnlyAdminMixin
from tdpservice.etl.exceptions import ActivePipelineRunError, PipelineValidationError
from tdpservice.etl.models import (
    ETLArtifact,
    ETLNodeRun,
    ETLPipelineRun,
    ETLQAResult,
    StatisticalWeight,
    StatisticalWeightsCaseCount,
)
from tdpservice.etl.permissions import ETLPermissions
from tdpservice.etl.registry import get_pipeline_definition, list_pipeline_definitions
from tdpservice.etl.runner import PipelineRunFactory
from tdpservice.etl.tasks import enqueue_pipeline_run


class ETLPipelineRunAdminForm(forms.ModelForm):
    """Collect and validate inputs for an admin-triggered pipeline run."""

    pipeline_key = forms.ChoiceField(choices=())

    class Meta:
        """Limit creation to inputs owned by the pipeline definition."""

        model = ETLPipelineRun
        fields = ("pipeline_key", "parameters")

    def __init__(self, *args, **kwargs):
        """Populate choices from the approved pipeline registry."""
        super().__init__(*args, **kwargs)
        self.fields["pipeline_key"].choices = [
            (definition.key, definition.display_name)
            for definition in list_pipeline_definitions()
        ]

    def clean(self):
        """Validate and normalize parameters with the selected pipeline."""
        cleaned_data = super().clean()
        pipeline_key = cleaned_data.get("pipeline_key")
        parameters = cleaned_data.get("parameters")
        if not pipeline_key or parameters is None:
            return cleaned_data

        try:
            definition = get_pipeline_definition(pipeline_key)
            cleaned_data["parameters"] = definition.validate_parameters(parameters)
        except (KeyError, PipelineValidationError) as exc:
            raise forms.ValidationError(str(exc)) from exc

        return cleaned_data


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
    readonly_fields = (
        "pipeline_version",
        "status",
        "output_scope",
        "output_scope_key",
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
    )

    def has_add_permission(self, request):
        """Enable add permissions."""
        return ETLPermissions().has_action_permission(request, "create")

    def get_form(self, request, obj=None, change=False, **kwargs):
        """Use the pipeline input form when adding a run."""
        if obj is None:
            kwargs["form"] = ETLPipelineRunAdminForm
        return super().get_form(request, obj, change=change, **kwargs)

    def save_form(self, request, form, change):
        """Create new runs through the same factory used by the API."""
        if change:
            return super().save_form(request, form, change)

        super().save_form(request, form, change)
        pipeline_run = PipelineRunFactory.for_pipeline_key(
            form.cleaned_data["pipeline_key"]
        ).create(
            parameters=form.cleaned_data["parameters"],
            trigger_source=ETLPipelineRun.TriggerSource.ADMIN,
            triggered_by=request.user,
        )
        form.instance = pipeline_run
        return pipeline_run

    def save_model(self, request, obj, form, change):
        """Enqueue a newly created run after the admin transaction commits."""
        if change:
            super().save_model(request, obj, form, change)
            return

        transaction.on_commit(partial(enqueue_pipeline_run, obj))

    def add_view(self, request, form_url="", extra_context=None):
        """Report factory-level conflicts in the admin interface."""
        try:
            return super().add_view(request, form_url, extra_context)
        except (ActivePipelineRunError, PipelineValidationError) as exc:
            self.message_user(request, str(exc), level=messages.ERROR)
            return redirect(request.path)

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
