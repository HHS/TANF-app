"""Check the existing reporting-role boundary for automatically restored views."""

from pathlib import Path

from django.db import connection

import pytest

from scripts import apply_grafana_views, create_grafana_postgres_role

pytestmark = pytest.mark.django_db


def can_select(role: str, view: str) -> bool:
    """Include inherited and PUBLIC access in privilege checks."""
    with connection.cursor() as cursor:
        cursor.execute("SELECT has_table_privilege(%s, %s, 'SELECT')", [role, view])
        return cursor.fetchone()[0]


@pytest.mark.parametrize("app_name", ["tdp-backend-prod", "tdp-backend-develop"])
def test_restored_views_preserve_environment_role_access(
    grafana_view_files: Path, settings, app_name: str
) -> None:
    """Aggregate grants do not expose raw exiters to the ordinary reporting role."""
    settings.APP_NAME = app_name
    metadata = ("mr_record_counts_by_tableview", "stt_section_to_type_mapping")
    ordinary = "grafana_pipeline_read_test"
    sensitive = "grafana_pipeline_sensitive_test"
    admin = "grafana_pipeline_admin_test"
    production = app_name == "tdp-backend-prod"

    for _ in range(2):
        apply_grafana_views.run()
        create_grafana_postgres_role.run(
            ordinary, "user_views", *(metadata if production else ())
        )
        create_grafana_postgres_role.run(sensitive, *metadata, "user_views", "admin_views")
        create_grafana_postgres_role.run(admin, "all")
        assert not can_select(ordinary, "latest_tanf_exiters_view_prod")
        assert can_select(sensitive, "latest_tanf_exiters_view_prod") == production
        assert can_select(admin, "latest_tanf_exiters_view_prod")
        for view in metadata:
            assert can_select(ordinary, view) == production
            assert can_select(sensitive, view)
            assert can_select(admin, view)
        with connection.cursor() as cursor:
            cursor.execute(f"SET LOCAL ROLE {sensitive}")
            try:
                for view in metadata:
                    cursor.execute(f'SELECT * FROM public."{view}" LIMIT 0')
            finally:
                cursor.execute("RESET ROLE")
