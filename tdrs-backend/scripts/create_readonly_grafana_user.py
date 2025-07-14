"""Create a read-only user for the PLG database."""

from django.db import connection
from django.conf import settings


def run(*args):  # noqa: C901
    """Create a read-only user for the PLG database."""
    # ./manage.py runscript create_readonly_grafana_user --script-args "test" "test2"
    GRAFANA_USER = args[0]
    GRAFANA_PASSWORD = args[1]
    if not GRAFANA_PASSWORD or not GRAFANA_USER:
        print("Grafana user and password must be provided.")
        return

    OFA_ADMIN_USER = args[2] if len(args) > 4 else None
    OFA_ADMIN_PASSWORD = args[3] if len(args) > 5 else None

    OFA_DIGIT_TEAM_USER = args[4] if len(args) > 6 else None
    OFA_DIGIT_TEAM_PASSWORD = args[5] if len(args) > 7 else None

    print("Creating Grafana user...")

    DB_NAME = settings.DATABASES["default"]["NAME"]
    print("Creating Grafana user...")

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
            if "$OFA_DB_USER" in sql_query and OFA_ADMIN_USER:
                sql_query = sql_query.replace("$OFA_DB_USER", OFA_ADMIN_USER)
            elif "$OFA_DB_USER" in sql_query and not OFA_ADMIN_USER:
                continue
            if "$OFA_DB_PASSWORD" in sql_query and OFA_ADMIN_PASSWORD:
                sql_query = sql_query.replace("$OFA_DB_PASSWORD", OFA_ADMIN_PASSWORD)
            elif "$OFA_DB_PASSWORD" in sql_query and not OFA_ADMIN_PASSWORD:
                continue
            if "$DIGIT_READONLY_USER" in sql_query and OFA_DIGIT_TEAM_USER:
                sql_query = sql_query.replace(
                    "$DIGIT_READONLY_USER", OFA_DIGIT_TEAM_USER
                )
            elif "$DIGIT_READONLY_USER" in sql_query and not OFA_DIGIT_TEAM_USER:
                continue
            if "$DIGIT_READONLY_PASSWORD" in sql_query and OFA_DIGIT_TEAM_PASSWORD:
                sql_query = sql_query.replace(
                    "$DIGIT_READONLY_PASSWORD", OFA_DIGIT_TEAM_PASSWORD
                )
            elif (
                "$DIGIT_READONLY_PASSWORD" in sql_query and not OFA_DIGIT_TEAM_PASSWORD
            ):
                continue
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

        # CREATE DIGIT TEAM USER
        TANF_SEARCH_INDEX = "tanf_"
        TANF_SEARCH_TRIBAL = "tribal_tanf_"
        TANF_SEARCH_SSP = "ssp_"
        TANF_SEARCH_FRA = "fra_"
        TANF_DIGIT_TEAM_VIEWS = [
            TANF_SEARCH_INDEX,
            TANF_SEARCH_TRIBAL,
            TANF_SEARCH_SSP,
            TANF_SEARCH_FRA,
        ]

        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM information_schema.views")
            views = cursor.fetchall()

        for view in views:
            view_name = view[2]
            print(f"Checking view: {view_name}")
            if any(
                [
                    TANF_DIGIT_TEAM_VIEW in view_name
                    for TANF_DIGIT_TEAM_VIEW in TANF_DIGIT_TEAM_VIEWS
                ]
            ):
                try:
                    print(f"Granting SELECT on {view_name} to {OFA_DIGIT_TEAM_USER}...")
                    with connection.cursor() as cursor:
                        cursor.execute(
                            f"GRANT SELECT ON {view_name} TO {OFA_DIGIT_TEAM_USER};"
                        )
                except Exception as e:
                    print(
                        f"An error occurred while granting SELECT on {view_name}: {e}"
                    )

        return
    print("Grafana readonly user created successfully.")
