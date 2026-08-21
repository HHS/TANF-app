"""Helpers for run-scoped ETL artifact manifests."""

from django.db import models

from tdpservice.etl.models import ETLArtifact


def upsert_table_dataset_artifact(
    *,
    pipeline_run,
    key: str,
    model: type[models.Model],
    schema_key: str,
    row_count: int,
    artifact_role: str = ETLArtifact.ArtifactRole.INTERMEDIATE,
    schema_version: int = 1,
    version: int | None = None,
    published: bool = False,
    metadata: dict | None = None,
) -> ETLArtifact:
    """Create or update a Postgres table-backed dataset artifact."""
    artifact, _created = ETLArtifact.objects.update_or_create(
        pipeline_run=pipeline_run,
        key=key,
        defaults={
            "artifact_role": artifact_role,
            "artifact_kind": ETLArtifact.ArtifactKind.DATASET,
            "storage_kind": ETLArtifact.StorageKind.POSTGRES_TABLE,
            "reference": model._meta.db_table,
            "schema_key": schema_key,
            "schema_version": schema_version,
            "version": version,
            "row_count": row_count,
            "published": published,
            "metadata": metadata or {},
        },
    )
    return artifact
