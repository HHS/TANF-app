"""Tests for environment-specific Keycloak realm configs."""

import json
from pathlib import Path

KEYCLOAK_DIR = Path(__file__).resolve().parents[3] / "keycloak"
REALM_CONFIGS_DIR = KEYCLOAK_DIR / "realm-configs"
REALM_CONFIG_PATHS = {
    "local": REALM_CONFIGS_DIR / "realm-export.dev-local.json",
    "dev": REALM_CONFIGS_DIR / "realm-export.dev-local.json",
    "staging": REALM_CONFIGS_DIR / "realm-export.staging.json",
    "prod": REALM_CONFIGS_DIR / "realm-export.prod.json",
}


def load_json(path):
    """Load a JSON file from disk."""
    return json.loads(path.read_text())


def get_client(realm, client_id):
    """Return the named client from the rendered realm."""
    return next(
        client for client in realm["clients"] if client["clientId"] == client_id
    )


def load_realm_config(env_name):
    """Load the selected full realm config for an environment."""
    return load_json(REALM_CONFIG_PATHS[env_name])


def test_local_and_dev_share_the_same_realm_config():
    """Local and dev should both load the combined dev/local realm export."""
    assert REALM_CONFIG_PATHS["local"] == REALM_CONFIG_PATHS["dev"]


def test_dev_local_config_includes_hosted_and_local_urls():
    """The shared dev/local config should allow both Cloud.gov dev and local workflows."""
    realm = load_realm_config("local")
    django_client = get_client(realm, "tdp-django")
    grafana_client = get_client(realm, "tdp-grafana")

    assert "https://tdp-frontend-raft.app.cloud.gov/*" in django_client["redirectUris"]
    assert "https://tdp-frontend-qasp.app.cloud.gov/*" in django_client["redirectUris"]
    assert "https://tdp-frontend-a11y.app.cloud.gov/*" in django_client["redirectUris"]
    assert "http://localhost:3000/*" in django_client["redirectUris"]
    assert "http://127.0.0.1:8989/*" in django_client["redirectUris"]
    assert grafana_client["attributes"]["post.logout.redirect.uris"] == (
        "https://grafana.app.cloud.gov/*##http://localhost:9400/*"
    )


def test_staging_config_excludes_local_urls():
    """Staging config should allow only hosted staging frontends."""
    realm = load_realm_config("staging")
    django_client = get_client(realm, "tdp-django")

    assert django_client["redirectUris"] == [
        "https://tdp-frontend-staging.acf.hhs.gov/*",
        "https://tdp-frontend-develop.acf.hhs.gov/*",
    ]
    assert all("localhost" not in uri for uri in django_client["redirectUris"])
    assert all("127.0.0.1" not in uri for uri in django_client["redirectUris"])


def test_prod_config_excludes_local_urls():
    """Prod config should allow only the production frontend."""
    realm = load_realm_config("prod")
    django_client = get_client(realm, "tdp-django")
    grafana_client = get_client(realm, "tdp-grafana")

    assert django_client["redirectUris"] == ["https://tanfdata.acf.hhs.gov/*"]
    assert django_client["webOrigins"] == ["https://tanfdata.acf.hhs.gov"]
    assert grafana_client["redirectUris"] == [
        "https://grafana.app.cloud.gov/login/generic_oauth"
    ]
