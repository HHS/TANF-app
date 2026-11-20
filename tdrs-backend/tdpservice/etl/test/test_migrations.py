"""Migration tests for the ETL app."""

import importlib
from decimal import Decimal

from django.apps import apps
from django.utils import timezone

import pytest

from tdpservice.data_files.models import Program
from tdpservice.etl.models import ETLPipelineRun, StatisticalWeight
from tdpservice.etl.runner import PipelineRunFactory


@pytest.mark.django_db
def test_statistical_weight_choices_migration_rejects_unknown_program():
    """Unknown persisted program values fail before choices are applied."""
    pipeline_run = PipelineRunFactory.for_pipeline_key("statistical_weights").create(
        parameters={"fiscal_year": 2026, "program": Program.Code.TANF},
        trigger_source=ETLPipelineRun.TriggerSource.ADMIN,
    )
    StatisticalWeight.objects.create(
        fiscal_year=2026,
        reporting_month=1,
        program="UNKNOWN",
        section="1",
        stt_code="55",
        stratum="01",
        version=1,
        case_count=1,
        cases=1,
        weight=Decimal("1.0000"),
        pipeline_run=pipeline_run,
        published_at=timezone.now(),
    )
    migration = importlib.import_module(
        "tdpservice.etl.migrations.0004_add_statisticalweight_program_choices"
    )

    with pytest.raises(RuntimeError, match="UNKNOWN"):
        migration.validate_statistical_weight_programs(apps, None)
