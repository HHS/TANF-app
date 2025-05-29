"""Create a read-only user for the PLG database."""

from django.db import connection
from django.conf import settings

def run(*args):
    """Create a read-only user for the PLG database."""
    # ./manage.py runscript create_readonly_grafana_user --script-args "test" "test2"
    GRAFANA_PASSWORD = args[0]
    GRAFANA_USER = args[1]
    DB_NAME = settings.DATABASES['default']['NAME']
    print("Creating Grafana user...")
    if not GRAFANA_PASSWORD or not GRAFANA_USER:
        print("Grafana user and password must be provided.")
        return

    with open("init.sql", "r") as file:
        print("Reading init.sql file...")
        while True:
            sql_query = file.readline()
            if not sql_query:
                break
            if "$GRAFANA_USER" in sql_query:
                sql_query = sql_query.replace("$GRAFANA_USER", GRAFANA_USER)
            if "$GRAFANA_PASSWORD" in sql_query:
                sql_query = sql_query.replace("$GRAFANA_PASSWORD", GRAFANA_PASSWORD)
            if "$DB_NAME" in sql_query:
                sql_query = sql_query.replace("$DB_NAME", DB_NAME)
            print("Creating Readonly Grafana user...")
            print(f"--Executing SQL query: {sql_query.strip()}")
            try:
                with connection.cursor() as cursor:
                    cursor.execute(sql_query)
            except Exception as e:
                if "already exists" in str(e):
                    pass
                else:
                    print(f"An error occurred: {e}")
                    print("An unexpected error occurred.")
                continue
        return
    print("Grafana readonly user created successfully.")
