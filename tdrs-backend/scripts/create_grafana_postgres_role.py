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

select_statement = "GRANT SELECT ON {tables} TO {role};"
admin_select_statement = "GRANT SELECT ON ALL TABLES IN SCHEMA public TO {role};"


def run(*args):  # noqa: C901
    """Create a read-only user for the PLG database."""
    # ./manage.py runscript create_grafana_postgres_role --script-args r1 t1 t2 t3...

    role = args[0]
    tables = args[1:]

    if not role or not tables:
        print("Role and tables must be provided.")
        return

    db_name = settings.DATABASES["default"]["NAME"]
    if args[1] == "all":
        select_stmt = admin_select_statement.format(role=role)
        sql = sql_tmpl.format(role=role, db_name=db_name, select_stmt=select_stmt)
    else:
        tables_str = ",".join(tables)

        # Remove stt_section_to_type_mapping from the list of tables if we are not in prod.
        if (
            "prod" not in settings.APP_NAME
            and "stt_section_to_type_mapping," in tables_str
        ):
            tables_str = tables_str.replace("stt_section_to_type_mapping,", "")
        select_stmt = select_statement.format(tables=tables_str, role=role)
        sql = sql_tmpl.format(
            role=role, tables=tables_str, db_name=db_name, select_stmt=select_stmt
        )

    with connection.cursor() as cursor:
        cursor.execute(sql)
    print(f"PostgreSQL role: {role} created successfully.")
