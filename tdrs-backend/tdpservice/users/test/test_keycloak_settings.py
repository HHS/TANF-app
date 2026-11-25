"""Verify client-specific Keycloak configuration in local and hosted deployments."""

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

BACKEND_DIR = Path(__file__).resolve().parents[3]
CLIENT_ENV = {
    "KC_TDP_DJANGO_REALM": "django-realm",
    "KC_TDP_DJANGO_CLIENT_ID": "django-client",
    "KC_TDP_DJANGO_CLIENT_SECRET": "django-test-secret",
    "KC_TDP_ADMIN_REALM": "react-admin-realm",
    "KC_TDP_ADMIN_CLIENT_ID": "react-admin-client",
    "KC_TDP_ADMIN_CLIENT_SECRET": "react-admin-test-secret",
}
SETTINGS_SCRIPT = """
import json
import configurations

configurations.setup()

from django.conf import settings
from unittest.mock import patch
from tdpservice.users.keycloak_client import KeycloakSyncClient
from tdpservice.users.oidc import KeycloakOIDCBackend

backend = KeycloakOIDCBackend()
backend._use_admin_oidc_settings()
admin_login = [backend.OIDC_RP_CLIENT_ID, backend.OIDC_RP_CLIENT_SECRET]
backend._use_standard_oidc_settings()
django_login = [backend.OIDC_RP_CLIENT_ID, backend.OIDC_RP_CLIENT_SECRET]
with patch('tdpservice.users.keycloak_client.KeycloakOpenIDConnection') as connection:
    KeycloakSyncClient.get_sync_client()
    sync = [call.kwargs for call in connection.call_args_list]

print(json.dumps({
    'django_login': django_login,
    'admin_login': admin_login,
    'oidc': [settings.OIDC_RP_CLIENT_ID, settings.OIDC_RP_CLIENT_SECRET],
    'django_api_audience': settings.KEYCLOAK_API_AUDIENCE,
    'django_token_url': settings.OIDC_OP_TOKEN_ENDPOINT,
    'admin_token_url': settings.KC_TDP_ADMIN_TOKEN_ENDPOINT,
    'sync': sync,
}))
"""


def load_keycloak_settings(
    configuration: str,
    service_credentials: dict[str, str] | None = None,
    client_environment: dict[str, str] | None = None,
) -> dict:
    """Load real Django settings in an isolated process with test credentials."""
    env = {
        name: value
        for name, value in os.environ.items()
        if not name.startswith(("KEYCLOAK_", "KC_", "VCAP_"))
    }
    env.update(CLIENT_ENV if client_environment is None else client_environment)
    env.update(
        DJANGO_SETTINGS_MODULE=f"tdpservice.settings.{configuration}",
        DJANGO_CONFIGURATION="Local" if configuration == "local" else "CloudGov",
        DJANGO_SECRET_KEY="test-settings-secret",
        DJANGO_SU_NAME="test@example.com",
        JWT_KEY="test-jwt-key",
        KEYCLOAK_SERVER_URL="https://keycloak.internal",
        KEYCLOAK_BROWSER_URL="https://auth.example.gov",
        KEYCLOAK_SYNC_ENABLED="no",
        OTEL_ENABLED="no",
    )
    if configuration == "cloudgov":
        s3_credentials = {
            "access_key_id": "test-key",
            "secret_access_key": "test-secret",
            "bucket": "test-bucket",
            "endpoint": "s3.example.gov",
            "region": "us-gov-west-1",
        }
        services = {
            "aws-rds": [
                {
                    "instance_name": "tdp-db-dev",
                    "credentials": {
                        "db_name": "test",
                        "username": "test",
                        "password": "test",
                        "host": "localhost",
                        "port": "5432",
                    },
                }
            ],
            "s3": [
                {
                    "instance_name": f"tdp-{name}-dev",
                    "credentials": s3_credentials,
                }
                for name in ("datafiles", "staticfiles")
            ],
            "user-provided": [
                {
                    "instance_name": "tdp-keycloak-dev",
                    "credentials": service_credentials or {},
                }
            ],
        }
        env["VCAP_SERVICES"] = json.dumps(services)
        env["VCAP_APPLICATION"] = json.dumps(
            {"name": "tdp-backend-test", "space_name": "tanf-dev"}
        )

    result = subprocess.run(
        [sys.executable, "-c", SETTINGS_SCRIPT],
        cwd=BACKEND_DIR,
        env=env,
        capture_output=True,
        text=True,
        check=True,
        timeout=30,
    )
    return json.loads(result.stdout)


@pytest.mark.parametrize("configuration", ["local", "cloudgov"])
def test_client_environment_configures_login_and_sync(configuration: str) -> None:
    """Login and sync use each client's shared secret and its own realm."""
    configured = load_keycloak_settings(configuration)

    assert configured["django_login"] == ["django-client", "django-test-secret"]
    assert configured["oidc"] == configured["django_login"]
    assert configured["django_api_audience"] == "django-client"
    assert configured["admin_login"] == [
        "react-admin-client",
        "react-admin-test-secret",
    ]
    assert configured["django_token_url"] == (
        "https://keycloak.internal/realms/django-realm/protocol/openid-connect/token"
    )
    assert configured["admin_token_url"] == (
        "https://keycloak.internal/realms/react-admin-realm/protocol/openid-connect/token"
    )
    assert configured["sync"] == [
        {
            "server_url": "https://keycloak.internal",
            "realm_name": "django-realm",
            "client_id": "django-client",
            "client_secret_key": "django-test-secret",
            "verify": True,
        },
        {
            "server_url": "https://keycloak.internal",
            "realm_name": "react-admin-realm",
            "client_id": "react-admin-client",
            "client_secret_key": "react-admin-test-secret",
            "verify": True,
        },
    ]


def test_bound_service_credentials_override_client_environment() -> None:
    """Cloud.gov service credentials apply consistently to login and user sync."""
    configured = load_keycloak_settings(
        "cloudgov",
        {
            "django_client_id": "bound-django-client",
            "django_client_secret": "bound-django-secret",
            "tdp_admin_realm": "bound-admin",
            "tdp_admin_client_id": "bound-admin-client",
            "tdp_admin_client_secret": "bound-admin-secret",
        },
    )

    assert configured["django_login"] == ["bound-django-client", "bound-django-secret"]
    assert configured["oidc"] == configured["django_login"]
    assert configured["django_api_audience"] == "bound-django-client"
    assert configured["admin_login"] == ["bound-admin-client", "bound-admin-secret"]
    assert [client["realm_name"] for client in configured["sync"]] == [
        "django-realm",
        "bound-admin",
    ]
    assert [client["client_secret_key"] for client in configured["sync"]] == [
        "bound-django-secret",
        "bound-admin-secret",
    ]


def test_cloudgov_does_not_use_local_secret_defaults() -> None:
    """Missing hosted secrets must not silently use local development credentials."""
    configured = load_keycloak_settings("cloudgov", client_environment={})

    assert configured["django_login"] == ["tdp-django", ""]
    assert configured["admin_login"] == ["tdp-admin", ""]
    assert [client["client_secret_key"] for client in configured["sync"]] == ["", ""]
