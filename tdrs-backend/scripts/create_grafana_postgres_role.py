"""Create a read-only user for the PLG database."""

import argparse

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
GRANT SELECT ON {tables} TO {role};
"""


def run(*args):  # noqa: C901
    """Create a read-only user for the PLG database."""
    # ./manage.py runscript create_grafana_postgres_role --script-args r1 t1 t2 t3...

    role = args[0]
    tables = args[1:]

    if not role or not tables:
        print("Role and tables must be provided.")
        return

    tables_str = ",".join(tables)

    db_name = settings.DATABASES["default"]["NAME"]

    sql = sql_tmpl.format(role=role, tables=tables_str, db_name=db_name)
    print(sql)

    with connection.cursor() as cursor:
        cursor.execute(sql)
    print(f"PostgreSQL role: {role} created successfully.")
