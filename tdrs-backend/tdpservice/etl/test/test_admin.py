"""Tests for ETL admin helpers."""

import json
import re
from decimal import Decimal
from html import unescape
from unittest.mock import patch

from django.contrib.admin.sites import AdminSite
from django.urls import reverse
from django.utils import timezone

import pytest

from tdpservice.data_files.models import Program
from tdpservice.etl.admin import ETLPipelineRunAdmin
from tdpservice.etl.models import ETLArtifact, ETLPipelineRun, StatisticalWeight
from tdpservice.etl.registry import get_pipeline_definition
from tdpservice.etl.runner import PipelineRunFactory


def _create_pipeline_run() -> ETLPipelineRun:
    return PipelineRunFactory.for_pipeline_key("statistical_weights").create(
        parameters={"fiscal_year": 2026, "program": Program.Code.TANF},
        trigger_source=ETLPipelineRun.TriggerSource.ADMIN,
    )


@pytest.mark.django_db
def test_pipeline_run_admin_add_creates_and_enqueues_pipeline_run(
    client,
    ofa_system_admin,
    django_capture_on_commit_callbacks,
):
    """Admin additions use the validated pipeline creation and launch flow."""
    assert client.login(username=ofa_system_admin.username, password="test_password")

    with (
        patch("tdpservice.etl.admin.enqueue_pipeline_run") as enqueue_pipeline_run,
        django_capture_on_commit_callbacks(execute=True),
    ):
        response = client.post(
            reverse("admin:etl_etlpipelinerun_add"),
            {
                "pipeline_key": "statistical_weights",
                "parameters": json.dumps(
                    {
                        "fiscal_year": "2026",
                        "program": Program.Code.TANF,
                    }
                ),
            },
        )

    assert response.status_code == 302
    pipeline_run = ETLPipelineRun.objects.get()
    assert pipeline_run.pipeline_version == "1"
    assert pipeline_run.status == ETLPipelineRun.Status.PENDING
    assert pipeline_run.parameters == {
        "fiscal_year": 2026,
        "program": Program.Code.TANF,
    }
    assert pipeline_run.output_scope == {
        "pipeline": "statistical_weights",
        "fiscal_year": 2026,
        "program": Program.Code.TANF,
        "section": "1",
    }
    assert pipeline_run.trigger_source == ETLPipelineRun.TriggerSource.ADMIN
    assert str(pipeline_run.triggered_by_id) == str(ofa_system_admin.id)
    assert list(pipeline_run.node_runs.values_list("node_key", flat=True)) == [
        node.key for node in get_pipeline_definition("statistical_weights").nodes
    ]
    enqueue_pipeline_run.assert_called_once_with(pipeline_run)


@pytest.mark.django_db
def test_pipeline_run_admin_add_rejects_invalid_parameters(client, ofa_system_admin):
    """Admin additions display pipeline parameter validation errors."""
    assert client.login(username=ofa_system_admin.username, password="test_password")

    response = client.post(
        reverse("admin:etl_etlpipelinerun_add"),
        {
            "pipeline_key": "statistical_weights",
            "parameters": json.dumps(
                {
                    "fiscal_year": 2026,
                    "program": "TANF",
                }
            ),
        },
    )

    assert response.status_code == 200
    assert "program must be one of" in response.content.decode()
    assert ETLPipelineRun.objects.count() == 0


@pytest.mark.django_db
def test_pipeline_run_admin_add_rejects_active_duplicate(client, ofa_system_admin):
    """Admin additions report an active run conflict without creating a duplicate."""
    pipeline_run = _create_pipeline_run()
    assert client.login(username=ofa_system_admin.username, password="test_password")

    response = client.post(
        reverse("admin:etl_etlpipelinerun_add"),
        {
            "pipeline_key": "statistical_weights",
            "parameters": json.dumps(pipeline_run.parameters),
        },
        follow=True,
    )

    assert response.status_code == 200
    assert f"Run {pipeline_run.id} is already active" in response.content.decode()
    assert ETLPipelineRun.objects.count() == 1


@pytest.mark.django_db
def test_pipeline_run_admin_final_output_link_filters_statistical_weights_table():
    """Table outputs link directly to the filtered output table."""
    pipeline_run = _create_pipeline_run()
    output = ETLArtifact.objects.create(
        pipeline_run=pipeline_run,
        key="statistical_weights",
        artifact_role=ETLArtifact.ArtifactRole.FINAL,
        artifact_kind=ETLArtifact.ArtifactKind.DATASET,
        storage_kind=ETLArtifact.StorageKind.POSTGRES_TABLE,
        reference=StatisticalWeight._meta.db_table,
        schema_key="statistical_weights",
        version=2,
        row_count=12,
        published=True,
        metadata=pipeline_run.output_scope,
    )
    pipeline_run.final_output = output
    pipeline_run.save(update_fields=["final_output", "updated_at"])
    pipeline_run_admin = ETLPipelineRunAdmin(ETLPipelineRun, AdminSite())

    link = str(pipeline_run_admin.final_output_link(pipeline_run))

    assert reverse("admin:etl_statisticalweight_changelist") in link
    assert "fiscal_year__exact=2026" in link
    assert f"program__exact={Program.Code.TANF}" in link
    assert "section__exact=1" in link
    assert "version__exact=2" in link
    assert "statistical_weights v2 (12 rows)" in link


@pytest.mark.django_db
def test_pipeline_run_admin_final_output_link_opens_filtered_admin_table(
    client, ofa_system_admin
):
    """The generated table link opens the admin changelist scoped to that output."""
    pipeline_run = _create_pipeline_run()
    output = ETLArtifact.objects.create(
        pipeline_run=pipeline_run,
        key="statistical_weights",
        artifact_role=ETLArtifact.ArtifactRole.FINAL,
        artifact_kind=ETLArtifact.ArtifactKind.DATASET,
        storage_kind=ETLArtifact.StorageKind.POSTGRES_TABLE,
        reference=StatisticalWeight._meta.db_table,
        schema_key="statistical_weights",
        version=2,
        row_count=1,
        published=True,
        metadata=pipeline_run.output_scope,
    )
    matching_weight = StatisticalWeight.objects.create(
        fiscal_year=2026,
        reporting_month=1,
        program=Program.Code.TANF,
        section="1",
        stt_code="55",
        stratum="01",
        version=2,
        case_count=1,
        cases=10,
        weight=Decimal("1.0000"),
        pipeline_run=pipeline_run,
        published_at=timezone.now(),
    )
    nonmatching_weight = StatisticalWeight.objects.create(
        fiscal_year=2026,
        reporting_month=1,
        program=Program.Code.TANF,
        section="1",
        stt_code="55",
        stratum="02",
        version=3,
        case_count=1,
        cases=10,
        weight=Decimal("1.0000"),
        pipeline_run=pipeline_run,
        published_at=timezone.now(),
    )
    pipeline_run.final_output = output
    pipeline_run.save(update_fields=["final_output", "updated_at"])
    pipeline_run_admin = ETLPipelineRunAdmin(ETLPipelineRun, AdminSite())
    link = str(pipeline_run_admin.final_output_link(pipeline_run))
    match = re.search("href='([^']+)'", link)
    assert match is not None
    assert client.login(username=ofa_system_admin.username, password="test_password")

    response = client.get(unescape(match.group(1)))

    assert response.status_code == 200
    assert list(response.context["cl"].queryset) == [matching_weight]
    assert nonmatching_weight not in response.context["cl"].queryset


@pytest.mark.django_db
def test_pipeline_run_admin_final_output_link_falls_back_to_output_change_page():
    """Non-table final artifacts link to the artifact admin record."""
    pipeline_run = _create_pipeline_run()
    output = ETLArtifact.objects.create(
        pipeline_run=pipeline_run,
        key="external_file",
        artifact_role=ETLArtifact.ArtifactRole.FINAL,
        artifact_kind=ETLArtifact.ArtifactKind.FILE,
        storage_kind=ETLArtifact.StorageKind.OBJECT,
        reference="s3://example/output.csv",
        schema_key="external_file",
        version=None,
        row_count=1,
        published=True,
    )
    pipeline_run.final_output = output
    pipeline_run.save(update_fields=["final_output", "updated_at"])
    pipeline_run_admin = ETLPipelineRunAdmin(ETLPipelineRun, AdminSite())

    link = str(pipeline_run_admin.final_output_link(pipeline_run))

    assert reverse("admin:etl_etlartifact_change", args=[output.id]) in link
    assert "external_file (1 rows)" in link


@pytest.mark.django_db
def test_pipeline_run_admin_final_output_link_handles_missing_output():
    """Runs without a final output show a blank admin value."""
    pipeline_run = _create_pipeline_run()
    pipeline_run_admin = ETLPipelineRunAdmin(ETLPipelineRun, AdminSite())

    assert pipeline_run_admin.final_output_link(pipeline_run) == "-"
