"""Create a read-only user for the PLG database."""

from django.conf import settings
from django.db import connection

sql_tmpl = """
DO $$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = '{role}') THEN
        CREATE ROLE {role};
    END IF;
END
$$;
GRANT CONNECT ON DATABASE {db_name} TO {role};
GRANT USAGE ON SCHEMA public TO {role};
{select_stmt}
"""

SELECT_STATEMENT = "GRANT SELECT ON {tables} TO {role};"
ADMIN_SELECT_STATEMENT = "GRANT SELECT ON ALL TABLES IN SCHEMA public TO {role};"

SECTION_TYPES = ("ssp_m", "tanf_t", "tribal_tanf_t")
SECTION_NUMBERS = range(1, 8)

USER_VIEWS = [f"{section}{num}" for section in SECTION_TYPES for num in SECTION_NUMBERS]

ADMIN_VIEWS = [f"admin_{view}" for view in USER_VIEWS]

# The views appended below are custom view(s) that OFA admins have created that they want included. Prod only.
if hasattr(settings, "APP_NAME") and settings.APP_NAME == "tdp-backend-prod":
    ADMIN_VIEWS.append("latest_tanf_exiters_view_prod")


def run(*args):  # noqa: C901
    """Create a read-only user for the PLG database.

    Usage:
        ./manage.py runscript create_grafana_postgres_role --script-args <role> [switches|tables...]

    Switches:
        all          - Grant SELECT on ALL tables in the public schema (CANNOT be combined with any switches or tables)
        user_views   - Include all user-facing views (ssp_m1..m7, tanf_t1..t7, tribal_tanf_t1..t7)
        admin_views  - Include all admin views (admin_ssp_m1..m7, admin_tanf_t1..t7, admin_tribal_tanf_t1..t7)

    Any other arguments are treated as explicit table/view names.
    Switches and explicit tables can be combined.
    """
    if not args:
        print("Role and tables/switches must be provided.")
        return

    role = args[0]
    remaining = args[1:]

    if not role or not remaining:
        print("Role and tables/switches must be provided.")
        return

    db_name = settings.DATABASES["default"]["NAME"]

    if "all" in remaining and len(remaining) > 1:
        print('The "all" switch must not be used with any other switch or tables.')
        return

    if remaining == ("all",):
        select_stmt = ADMIN_SELECT_STATEMENT.format(role=role)
        sql = sql_tmpl.format(role=role, db_name=db_name, select_stmt=select_stmt)
    else:
        tables: list[str] = []
        for arg in remaining:
            if arg == "user_views":
                tables.extend(USER_VIEWS)
            elif arg == "admin_views":
                tables.extend(ADMIN_VIEWS)
            else:
                tables.append(arg)

        if not tables:
            print(
                "No tables resolved. Provide table names or use user_views / admin_views."
            )
            return

        tables_str = ",".join(tables)
        select_stmt = SELECT_STATEMENT.format(tables=tables_str, role=role)
        sql = sql_tmpl.format(
            role=role, tables=tables_str, db_name=db_name, select_stmt=select_stmt
        )

    with connection.cursor() as cursor:
        cursor.execute(sql)
    print(f"PostgreSQL role: {role} created successfully.")
