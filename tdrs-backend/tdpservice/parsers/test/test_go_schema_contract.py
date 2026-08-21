"""Contract tests for Django search index models and Go parser schemas."""

from pathlib import Path

import pytest
import yaml

from tdpservice.search_indexes.models import fra, ssp, tanf, tribal

GO_SCHEMA_DIR = (
    Path(__file__).resolve().parents[4]
    / "tdrs-services"
    / "parser"
    / "config"
    / "schemas"
)
STORAGE_FIELDS = {"id", "datafile", "line_number"}

ACTIVE_SCHEMA_MODELS = (
    ("tanf/t1", tanf.TANF_T1),
    ("tanf/t2", tanf.TANF_T2),
    ("tanf/t3", tanf.TANF_T3),
    ("tanf/t4", tanf.TANF_T4),
    ("tanf/t5", tanf.TANF_T5),
    ("tanf/t6", tanf.TANF_T6),
    ("tanf/t7", tanf.TANF_T7),
    ("ssp/m1", ssp.SSP_M1),
    ("ssp/m2", ssp.SSP_M2),
    ("ssp/m3", ssp.SSP_M3),
    ("ssp/m4", ssp.SSP_M4),
    ("ssp/m5", ssp.SSP_M5),
    ("ssp/m6", ssp.SSP_M6),
    ("ssp/m7", ssp.SSP_M7),
    ("tribal_tanf/t1", tribal.Tribal_TANF_T1),
    ("tribal_tanf/t2", tribal.Tribal_TANF_T2),
    ("tribal_tanf/t3", tribal.Tribal_TANF_T3),
    ("tribal_tanf/t4", tribal.Tribal_TANF_T4),
    ("tribal_tanf/t5", tribal.Tribal_TANF_T5),
    ("tribal_tanf/t6", tribal.Tribal_TANF_T6),
    ("tribal_tanf/t7", tribal.Tribal_TANF_T7),
    ("fra/te1", fra.TANF_Exiter1),
)


def django_model_fields(model: type) -> set[str]:
    """Return persisted model field names that Go schemas must declare."""
    return {
        field.name
        for field in model._meta.get_fields()
        if getattr(field, "concrete", False) and field.name not in STORAGE_FIELDS
    }


def go_schema_fields(schema_path: str) -> set[str]:
    """Return field names declared by a Go parser YAML schema."""
    schema_file = GO_SCHEMA_DIR / f"{schema_path}.yaml"
    schema = yaml.safe_load(schema_file.read_text())

    fields = {field["name"] for field in schema.get("shared") or []}
    for segment in schema.get("segments") or []:
        fields.update(field["name"] for field in segment.get("fields") or [])
    return fields


@pytest.mark.parametrize(("schema_path", "model"), ACTIVE_SCHEMA_MODELS)
def test_go_schema_fields_match_active_django_model(schema_path: str, model: type):
    """Go YAML persisted fields must exactly match active Django model fields."""
    assert go_schema_fields(schema_path) == django_model_fields(model)
