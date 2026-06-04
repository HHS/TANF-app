# Keycloak Context

This context covers the Keycloak initiative under `tdrs-backend/keycloak/`.

## Boundaries

- Keycloak acts as the OpenID Connect broker between TDP and external identity providers, currently Login.gov and AMS.
- Keycloak container, deployment scripts, realm exports, IdP configuration, nginx proxy config, and cloud.gov manifest assets live here.
- Django remains the source of truth for TDP user information. Keycloak should receive synced user attributes and group memberships from Django; do not treat Keycloak as authoritative for application user state.
- Authentication and identity changes usually cross `tdrs-backend/`, `tdrs-backend/keycloak/`, and `tdrs-frontend/`.
- Treat user access, roles, identity-provider behavior, client secrets, signing keys, and realm exports as security-sensitive.

## Important Paths

- `README.md`: setup, environment variables, realm configuration, Django integration, deployment, and troubleshooting overview.
- `keycloak-operations.md`: operational runbook for deployment, health checks, troubleshooting, Grafana SSO, and sync failures.
- `realm-configs/`: checked-in realm exports for local/dev, staging, and production.
- `select-realm-config.sh`: selects the environment-specific realm export before Keycloak starts.
- `configure-idps.sh`: applies runtime-sensitive IdP configuration such as Login.gov signing key and ACR values.
- `deploy.sh`: cloud.gov deployment script; sets routes, network policies, and post-start IdP configuration.
- `entrypoint.sh`: starts Keycloak on an internal port and nginx on the Cloud Foundry `$PORT`.
- `nginx.conf`: reverse proxy in front of Keycloak, including headers needed for the admin console.

## Runtime Model

- Browser login starts from the frontend, routes through Django `/v2/` auth endpoints, redirects to Keycloak, then to the upstream IdP.
- Keycloak brokers external IdPs; Django handles the OIDC callback and creates the application session cookie.
- `KEYCLOAK_BROWSER_URL` is browser-facing and is used for authorization and logout redirects.
- `KEYCLOAK_SERVER_URL` is server-to-server and is used by Django for token exchange, userinfo, JWKS, admin API calls, and user sync.
- Local Docker defines `keycloak-pg`, `keycloak`, and `keycloak-configure` services in `tdrs-backend/docker-compose.yml`.
- In cloud.gov, Keycloak has a public route for browser/admin access and an internal route for backend/celery server-to-server traffic.

## Django Integration

- `tdpservice.users.oidc.KeycloakOIDCBackend` is the custom mozilla-django-oidc backend.
- `tdpservice.users.keycloak_client.KeycloakSyncClient` syncs Django user state into Keycloak through the Admin REST API.
- `tdpservice.users.keycloak_sync` registers Django signal handlers for user saves and group membership changes.
- `tdpservice.users.tasks.reconcile_keycloak_users` periodically reconciles active Django users into Keycloak via Celery Beat.
- `tdpservice.users.management.commands.sync_users_to_keycloak` performs a manual bulk sync.
- `settings/common.py` defines the Keycloak and mozilla-django-oidc settings, including the canary `KEYCLOAK_AUTH_PERCENTAGE`.

## User Sync Rules

- Django is authoritative for application users, user attributes, approval status, STT/region assignment, and Django group membership.
- Sync is enabled by `KEYCLOAK_SYNC_ENABLED`.
- On `User` save, Django syncs user attributes such as `login_gov_uuid`, `hhs_id`, `stt_id`, `account_approval_status`, and `region_ids` to Keycloak.
- On Django group membership changes, Django syncs mapped Keycloak group memberships.
- Bulk sync only syncs active Django users.
- Sync finds Keycloak users by exact email. If the user has not logged in through Keycloak yet and does not exist in Keycloak, sync is skipped.
- The sync client sets absolute state, not deltas; group sync removes current Keycloak groups before adding groups that match current Django state.

## Group Mapping

The Django-to-Keycloak group mapping lives in `tdpservice.users.keycloak_client.DJANGO_TO_KC_GROUP`.

| Django Group | Keycloak Group |
| --- | --- |
| OFA Admin | ofa-admin |
| OFA System Admin | ofa-system-admin |
| Data Analyst | data-analyst |
| OFA Regional Staff | ofa-regional-staff |
| Developer | developer |
| ACF OCIO | acf-ocio |
| DIGIT Team | digit-team |

## Authentication Rules

- Users are looked up by IdP-specific claims first: `hhs_id` for AMS and `login_gov_uuid` for Login.gov, then by normalized email.
- `@acf.hhs.gov` users must authenticate through AMS, not Login.gov.
- Inactive and deactivated users are rejected during login.
- Keycloak includes required claims in the ID token through protocol mappers, so `KeycloakOIDCBackend.get_userinfo` uses the ID token payload directly.

## Test Strategy

- Keycloak OIDC backend tests live in `tdrs-backend/tdpservice/users/test/test_oidc.py`.
- Keycloak sync tests live in `tdrs-backend/tdpservice/users/test/test_keycloak_sync.py`.
- Run backend tests through the backend pytest workflow; focus the test path when changing only Keycloak integration code.

## Read With

- Root `CONTEXT.md`
- `CONTEXT-MAP.md`
- `tdrs-backend/CONTEXT.md`
- Keycloak README and operations docs in this directory
- Relevant authentication docs under `docs/Technical-Documentation/`
- `tdrs-backend/tdpservice/users/oidc.py`
- `tdrs-backend/tdpservice/users/keycloak_client.py`
- `tdrs-backend/tdpservice/users/keycloak_sync.py`
- `tdrs-backend/tdpservice/users/tasks.py`
- `tdrs-backend/docker-compose.yml`
