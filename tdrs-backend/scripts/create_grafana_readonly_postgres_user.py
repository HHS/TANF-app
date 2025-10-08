"""Create a read-only user for the default database."""

from django.db import connection

sql_tmpl = """
DO $$
BEGIN
   IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = '{username}' AND rolcanlogin = true) THEN
      CREATE USER {username} WITH PASSWORD '{password}';
   END IF;
END
$$;
GRANT {role} TO {username};
"""


def run(*args):  # noqa: C901
    """Create a read-only user for the default database."""
    # ./manage.py runscript create_readonly_grafana_user --script-args "user1" "password1" "role1" "user2" "password" "role2"...

    if len(args) % 3 != 0:
        print(
            "Expects args in groups of 3. E.g. 'user1' 'password1' 'role1' 'user2' 'password2' 'role2'..."
        )
        return

    with connection.cursor() as cursor:
        for i in range(0, len(args), 3):
            username = args[i]
            password = args[i + 1]
            role = args[i + 2]

            if len(password) < 20:
                print(
                    f"\nSupplied password for user: {username} is not long enough. Must be at least 20 characters. Skipping creation of user.\n"
                )
            else:
                sql = sql_tmpl.format(username=username, password=password, role=role)
                cursor.execute(sql)
                print(f"Successfully created user: {username} with role: {role}.")
