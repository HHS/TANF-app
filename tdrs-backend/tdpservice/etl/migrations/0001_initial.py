"""Initial ETL pipeline models and permissions."""

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion

from tdpservice.users.permissions import (
    add_permissions_q,
    change_permissions_q,
    create_perms,
    get_permission_ids_for_model,
    view_permissions_q,
)


ETL_MODELS = (
    "etlartifact",
    "etlnoderun",
    "etlpipelinerun",
    "etlqaresult",
    "statisticalweight",
    "statisticalweightscasecount",
)


def _permission_ids(filters):
    """Return ETL permission ids matching the supplied filters."""
    permission_ids = []
    for model_name in ETL_MODELS:
        permission_ids.extend(
            get_permission_ids_for_model("etl", model_name, filters=filters)
        )
    return permission_ids


def add_etl_group_permissions(apps, schema_editor):
    """Grant initial ETL permissions to approved operational groups."""
    ofa_system_admin = apps.get_model("auth", "Group").objects.get(
        name="OFA System Admin"
    )
    digit_team = apps.get_model("auth", "Group").objects.get(name="DIGIT Team")

    ofa_system_admin.permissions.add(
        *_permission_ids([view_permissions_q, add_permissions_q, change_permissions_q])
    )
    digit_team.permissions.add(*_permission_ids([view_permissions_q]))


def remove_etl_group_permissions(apps, schema_editor):
    """Remove initial ETL permissions from operational groups."""
    ofa_system_admin = apps.get_model("auth", "Group").objects.get(
        name="OFA System Admin"
    )
    digit_team = apps.get_model("auth", "Group").objects.get(name="DIGIT Team")

    ofa_system_admin.permissions.remove(
        *_permission_ids([view_permissions_q, add_permissions_q, change_permissions_q])
    )
    digit_team.permissions.remove(*_permission_ids([view_permissions_q]))


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("auth", "__latest__"),
        ("users", "0058_merge_20260318_2105"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="ETLPipelineRun",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("pipeline_key", models.CharField(max_length=128)),
                ("pipeline_version", models.CharField(max_length=32)),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("PENDING", "Pending"),
                            ("RUNNING", "Running"),
                            ("SUCCEEDED", "Succeeded"),
                            ("FAILED", "Failed"),
                            ("CANCELED", "Canceled"),
                        ],
                        default="PENDING",
                        max_length=16,
                    ),
                ),
                ("parameters", models.JSONField(default=dict)),
                ("output_scope", models.JSONField(default=dict)),
                (
                    "output_scope_key",
                    models.CharField(editable=False, max_length=64),
                ),
                ("metadata", models.JSONField(default=dict)),
                (
                    "trigger_source",
                    models.CharField(
                        choices=[
                            ("ADMIN", "Admin"),
                            ("SCHEDULED", "Scheduled"),
                            ("RETRY", "Retry"),
                        ],
                        max_length=16,
                    ),
                ),
                ("started_at", models.DateTimeField(blank=True, null=True)),
                ("finished_at", models.DateTimeField(blank=True, null=True)),
                ("error_message", models.TextField(blank=True, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "retry_of",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="retries",
                        to="etl.etlpipelinerun",
                    ),
                ),
                (
                    "triggered_by",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="etl_pipeline_runs",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "ordering": ["-created_at"],
                "indexes": [
                    models.Index(
                        fields=["pipeline_key", "status"],
                        name="etl_run_key_status_idx",
                    ),
                    models.Index(
                        fields=["pipeline_key", "output_scope_key"],
                        name="etl_run_scope_key_idx",
                    ),
                    models.Index(
                        fields=["created_at"],
                        name="etl_run_created_idx",
                    ),
                ],
                "constraints": [
                    models.UniqueConstraint(
                        condition=models.Q(status__in=("PENDING", "RUNNING")),
                        fields=("pipeline_key", "output_scope_key"),
                        name="unique_active_etl_run_scope",
                    )
                ],
            },
        ),
        migrations.CreateModel(
            name="ETLQAResult",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("check_key", models.CharField(max_length=128)),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("PASSED", "Passed"),
                            ("WARNING", "Warning"),
                            ("FAILED", "Failed"),
                        ],
                        max_length=16,
                    ),
                ),
                ("summary", models.TextField()),
                ("result_payload", models.JSONField(default=dict)),
                ("blocking", models.BooleanField(default=False)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "pipeline_run",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="qa_results",
                        to="etl.etlpipelinerun",
                    ),
                ),
            ],
            options={
                "ordering": ["pipeline_run_id", "id"],
                "indexes": [
                    models.Index(
                        fields=["check_key", "status"],
                        name="etl_qa_key_status_idx",
                    )
                ],
            },
        ),
        migrations.CreateModel(
            name="ETLNodeRun",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("node_key", models.CharField(max_length=128)),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("PENDING", "Pending"),
                            ("RUNNING", "Running"),
                            ("SUCCEEDED", "Succeeded"),
                            ("FAILED", "Failed"),
                        ],
                        default="PENDING",
                        max_length=16,
                    ),
                ),
                ("started_at", models.DateTimeField(blank=True, null=True)),
                ("finished_at", models.DateTimeField(blank=True, null=True)),
                ("input_row_count", models.PositiveIntegerField(blank=True, null=True)),
                (
                    "output_row_count",
                    models.PositiveIntegerField(blank=True, null=True),
                ),
                ("error_message", models.TextField(blank=True, null=True)),
                ("metadata", models.JSONField(default=dict)),
                (
                    "pipeline_run",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="node_runs",
                        to="etl.etlpipelinerun",
                    ),
                ),
            ],
            options={
                "ordering": ["pipeline_run_id", "id"],
                "indexes": [
                    models.Index(
                        fields=["node_key", "status"],
                        name="etl_node_key_status_idx",
                    )
                ],
            },
        ),
        migrations.CreateModel(
            name="ETLArtifact",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("key", models.CharField(max_length=128)),
                (
                    "artifact_role",
                    models.CharField(
                        choices=[
                            ("INTERMEDIATE", "Intermediate"),
                            ("FINAL", "Final"),
                        ],
                        default="INTERMEDIATE",
                        max_length=16,
                    ),
                ),
                (
                    "artifact_kind",
                    models.CharField(
                        choices=[
                            ("DATASET", "Dataset"),
                            ("FILE", "File"),
                            ("SCALAR", "Scalar"),
                        ],
                        max_length=16,
                    ),
                ),
                (
                    "storage_kind",
                    models.CharField(
                        choices=[
                            ("POSTGRES_TABLE", "Postgres Table"),
                            ("OBJECT", "Object"),
                            ("INLINE_JSON", "Inline Json"),
                        ],
                        max_length=32,
                    ),
                ),
                ("reference", models.CharField(max_length=255)),
                ("schema_key", models.CharField(max_length=128)),
                ("schema_version", models.PositiveIntegerField(default=1)),
                ("version", models.PositiveIntegerField(blank=True, null=True)),
                ("row_count", models.PositiveIntegerField(default=0)),
                ("published", models.BooleanField(default=False)),
                ("metadata", models.JSONField(default=dict)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "pipeline_run",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="artifacts",
                        to="etl.etlpipelinerun",
                    ),
                ),
            ],
            options={
                "ordering": ["pipeline_run_id", "id"],
                "indexes": [
                    models.Index(
                        fields=["key"],
                        name="etl_artifact_key_idx",
                    ),
                    models.Index(
                        fields=["key", "artifact_role"],
                        name="etl_artifact_key_role_idx",
                    ),
                    models.Index(
                        fields=["artifact_kind", "storage_kind"],
                        name="etl_artifact_kind_store_idx",
                    ),
                    models.Index(
                        fields=["artifact_role", "published"],
                        name="etl_artifact_role_pub_idx",
                    ),
                ],
            },
        ),
        migrations.AddField(
            model_name="etlpipelinerun",
            name="final_output",
            field=models.OneToOneField(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="final_pipeline_run",
                to="etl.etlartifact",
            ),
        ),
        migrations.CreateModel(
            name="StatisticalWeightsCaseCount",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "count_kind",
                    models.CharField(
                        choices=[
                            ("S1", "Active Family"),
                            ("S3", "Aggregate Case"),
                            ("S4", "Stratum Case"),
                        ],
                        max_length=2,
                    ),
                ),
                ("stt_code", models.CharField(max_length=3)),
                ("reporting_month", models.PositiveIntegerField()),
                ("stratum", models.CharField(blank=True, default="", max_length=2)),
                ("count", models.PositiveIntegerField()),
                (
                    "pipeline_run",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="statistical_weight_case_counts",
                        to="etl.etlpipelinerun",
                    ),
                ),
            ],
            options={
                "ordering": [
                    "pipeline_run_id",
                    "count_kind",
                    "stt_code",
                    "reporting_month",
                    "stratum",
                ],
                "indexes": [
                    models.Index(
                        fields=["pipeline_run", "count_kind", "reporting_month"],
                        name="sw_case_kind_month_idx",
                    ),
                    models.Index(
                        fields=[
                            "pipeline_run",
                            "count_kind",
                            "stt_code",
                            "reporting_month",
                        ],
                        name="sw_case_kind_pair_idx",
                    ),
                ],
            },
        ),
        migrations.CreateModel(
            name="StatisticalWeight",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("fiscal_year", models.PositiveIntegerField()),
                ("reporting_month", models.PositiveIntegerField()),
                (
                    "program",
                    models.CharField(
                        choices=[
                            ("TAN", "Tanf"),
                            ("SSP", "Ssp"),
                            ("TRIBAL", "Tribal"),
                            ("FRA", "Fra"),
                        ],
                        max_length=16,
                    ),
                ),
                ("section", models.CharField(max_length=16)),
                ("stt_code", models.CharField(max_length=3)),
                ("stratum", models.CharField(max_length=2)),
                ("version", models.PositiveIntegerField()),
                ("case_count", models.PositiveIntegerField()),
                ("cases", models.PositiveIntegerField()),
                ("weight", models.DecimalField(decimal_places=4, max_digits=12)),
                ("published_at", models.DateTimeField()),
                ("retention_expires_at", models.DateTimeField(blank=True, null=True)),
                (
                    "pipeline_run",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="statistical_weights",
                        to="etl.etlpipelinerun",
                    ),
                ),
            ],
            options={
                "indexes": [
                    models.Index(
                        fields=["fiscal_year", "program", "section", "version"],
                        name="etl_weight_scope_ver_idx",
                    ),
                    models.Index(
                        fields=["retention_expires_at"],
                        name="etl_weight_retention_idx",
                    ),
                ],
            },
        ),
        migrations.AddConstraint(
            model_name="etlartifact",
            constraint=models.UniqueConstraint(
                fields=("pipeline_run", "key"),
                name="unique_etl_artifact_per_run",
            ),
        ),
        migrations.AddConstraint(
            model_name="etlnoderun",
            constraint=models.UniqueConstraint(
                fields=("pipeline_run", "node_key"),
                name="unique_etl_node_run_per_pipeline_run",
            ),
        ),
        migrations.AddConstraint(
            model_name="statisticalweight",
            constraint=models.UniqueConstraint(
                fields=(
                    "fiscal_year",
                    "reporting_month",
                    "program",
                    "section",
                    "stt_code",
                    "stratum",
                    "version",
                ),
                name="unique_statistical_weight_version",
            ),
        ),
        migrations.AddConstraint(
            model_name="statisticalweightscasecount",
            constraint=models.UniqueConstraint(
                fields=(
                    "pipeline_run",
                    "count_kind",
                    "stt_code",
                    "reporting_month",
                    "stratum",
                ),
                name="unique_sw_case_count",
            ),
        ),
        migrations.RunPython(create_perms, reverse_code=migrations.RunPython.noop),
        migrations.RunPython(
            add_etl_group_permissions,
            reverse_code=remove_etl_group_permissions,
        ),
    ]
