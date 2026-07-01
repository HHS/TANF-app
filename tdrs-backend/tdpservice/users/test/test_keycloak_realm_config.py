"""Tests for environment-specific Keycloak realm configs."""

import json
from pathlib import Path

KEYCLOAK_DIR = Path(__file__).resolve().parents[3] / "keycloak"
CONFIGURE_IDPS_PATH = KEYCLOAK_DIR / "configure-idps.sh"
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


def get_client_scope(realm, scope_name):
    """Return the named client scope from the rendered realm."""
    return next(scope for scope in realm["clientScopes"] if scope["name"] == scope_name)


def get_identity_provider(realm, alias):
    """Return the named identity provider from the rendered realm."""
    return next(idp for idp in realm["identityProviders"] if idp["alias"] == alias)


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

    assert "https://test.tanfdata.acf.hhs.gov/*" in django_client["redirectUris"]
    assert "https://qasp.tanfdata.acf.hhs.gov/*" in django_client["redirectUris"]
    assert "https://a11y.tanfdata.acf.hhs.gov/*" in django_client["redirectUris"]
    assert "http://localhost:3000/*" in django_client["redirectUris"]
    assert "http://127.0.0.1:8989/*" in django_client["redirectUris"]
    assert grafana_client["attributes"]["post.logout.redirect.uris"] == (
        "https://grafana.tanfdata.acf.hhs.gov/*##http://localhost:9400/*"
    )


def test_staging_config_excludes_local_urls():
    """Staging config should allow only hosted staging frontends."""
    realm = load_realm_config("staging")
    django_client = get_client(realm, "tdp-django")

    assert django_client["redirectUris"] == [
        "https://staging.tanfdata.acf.hhs.gov/*",
        "https://develop.tanfdata.acf.hhs.gov/*",
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
        "https://grafana.tanfdata.acf.hhs.gov/login/generic_oauth"
    ]


def test_all_realm_configs_include_tdp_api_audience_scope():
    """Every realm should let tdp-cli tokens declare the Django API audience."""
    for env_name in ("local", "staging", "prod"):
        realm = load_realm_config(env_name)
        scope = get_client_scope(realm, "tdp-api-audience")
        mapper = scope["protocolMappers"][0]

        assert mapper["protocolMapper"] == "oidc-audience-mapper"
        assert mapper["config"]["included.client.audience"] == "tdp-django"
        assert mapper["config"]["access.token.claim"] == "true"
        assert mapper["config"]["id.token.claim"] == "false"


def test_all_realm_configs_attach_api_audience_only_to_tdp_cli():
    """The API audience scope should be defaulted for tdp-cli, not API/Grafana."""
    for env_name in ("local", "staging", "prod"):
        realm = load_realm_config(env_name)
        cli_client = get_client(realm, "tdp-cli")
        django_client = get_client(realm, "tdp-django")
        grafana_client = get_client(realm, "tdp-grafana")

        assert "tdp-api-audience" in cli_client["defaultClientScopes"]
        assert "tdp-api-audience" not in django_client["defaultClientScopes"]
        assert "tdp-api-audience" not in grafana_client["defaultClientScopes"]


def test_all_realm_configs_show_login_gov_on_login_page():
    """Manual CLI/Postman auth needs Login.gov visible on the login page."""
    for env_name in ("local", "staging", "prod"):
        realm = load_realm_config(env_name)
        login_gov_idp = get_identity_provider(realm, "login-gov")

        assert login_gov_idp.get("hideOnLogin") is not True


def test_configure_idps_applies_cli_audience_to_existing_realms():
    """Deploy-time config must update existing realms that skip JSON re-import."""
    script = CONFIGURE_IDPS_PATH.read_text()

    assert "configure_tdp_cli_api_audience()" in script
    assert "configure_tdp_cli_api_audience" in script.split("main()", maxsplit=1)[1]
    assert 'scope_name="tdp-api-audience"' in script
    assert "/client-scopes?name=${scope_name}" in script
    assert 'get_client_uuid "tdp-cli"' in script
    assert "default-client-scopes" in script


def test_configure_idps_shows_login_gov_for_existing_realms():
    """Deploy-time config must unhide Login.gov when realms skip re-import."""
    script = CONFIGURE_IDPS_PATH.read_text()

    assert "show_login_gov_on_login_page()" in script
    assert "show_login_gov_on_login_page" in script.split("main()", maxsplit=1)[1]
    assert ".hideOnLogin = false | del(.config.clientSecret)" in script
