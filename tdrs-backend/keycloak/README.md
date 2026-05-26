# Keycloak Integration

Keycloak acts as a centralized **OpenID Connect (OIDC) broker** between the TDP application and multiple identity providers (Login.gov and AMS).

```
User -> Frontend -> Django /v2/ -> Keycloak -> Identity Provider (Login.gov / AMS)
                                      |
                                      v
                              Django OIDC callback -> session cookie -> Frontend
```

## Directory Contents

| File | Purpose |
|---|---|
| `Dockerfile` | Keycloak 26.0 image with `jq` and `curl` for IdP configuration |
| `realm-export.json` | Complete "tdp" realm configuration (clients, groups, IdP mappers) |
| `configure-idps.sh` | Post-startup script that configures Login.gov signing key and ACR values |
| `deploy.sh` | Cloud Foundry deployment script for cloud.gov |
| `manifest.yml` | Cloud.gov manifest template |

## Local Setup

### Prerequisites

- Docker and Docker Compose
- The backend `docker-compose.yml` defines three Keycloak-related services:
  - **keycloak-pg** — PostgreSQL 15.7 database for Keycloak (port 5434)
  - **keycloak** — Keycloak 26.0 server (ports 8443 browser / 8080 internal / 9001 management)
  - **keycloak-configure** — Runs `configure-idps.sh` after Keycloak starts

### Starting Keycloak

```bash
cd tdrs-backend
docker compose up keycloak
```

The `keycloak-configure` container will automatically run after Keycloak is healthy, configuring the Login.gov signing key and ACR values.

### Accessing the Admin Console

- URL: http://localhost:8443/admin
- Username: `admin`
- Password: `admin`

### Verifying the Setup

1. Keycloak health check: http://localhost:9001/health/ready
2. Realm discovery: http://localhost:8443/realms/tdp/.well-known/openid-configuration

## Environment Variables

### Backend (`tdrs-backend/.env`)

#### Keycloak Core

| Variable | Default | Description |
|---|---|---|
| `KEYCLOAK_SYNC_ENABLED` | `false` | Enable Django-to-Keycloak user sync on save/group change |
| `KEYCLOAK_SERVER_URL` | `http://keycloak:8080` | Internal (server-to-server) Keycloak URL |
| `KEYCLOAK_BROWSER_URL` | `http://localhost:8443` | Browser-facing Keycloak URL (used for auth/logout redirects) |
| `KEYCLOAK_REALM` | `tdp` | Keycloak realm name |
| `KEYCLOAK_ADMIN_CLIENT_ID` | `tdp-django` | Client ID for admin API access |
| `KEYCLOAK_ADMIN_CLIENT_SECRET` | `tdp-django-local-secret` | Client secret for admin API access |
| `KEYCLOAK_DJANGO_CLIENT_ID` | `tdp-django` | Client ID for OIDC authentication |
| `KEYCLOAK_DJANGO_CLIENT_SECRET` | `tdp-django-local-secret` | Client secret for OIDC authentication |

#### OIDC (mozilla-django-oidc)

These are derived from the Keycloak variables above in `settings/common.py`:

| Variable | Value |
|---|---|
| `OIDC_RP_CLIENT_ID` | Same as `KEYCLOAK_DJANGO_CLIENT_ID` |
| `OIDC_RP_CLIENT_SECRET` | Same as `KEYCLOAK_DJANGO_CLIENT_SECRET` |
| `OIDC_RP_SIGN_ALGO` | `RS256` |
| `OIDC_RP_SCOPES` | `openid email` |
| `OIDC_OP_AUTHORIZATION_ENDPOINT` | `{KEYCLOAK_BROWSER_URL}/realms/tdp/protocol/openid-connect/auth` |
| `OIDC_OP_TOKEN_ENDPOINT` | `{KEYCLOAK_SERVER_URL}/realms/tdp/protocol/openid-connect/token` |
| `OIDC_OP_USER_ENDPOINT` | `{KEYCLOAK_SERVER_URL}/realms/tdp/protocol/openid-connect/userinfo` |
| `OIDC_OP_JWKS_ENDPOINT` | `{KEYCLOAK_SERVER_URL}/realms/tdp/protocol/openid-connect/certs` |
| `OIDC_OP_LOGOUT_ENDPOINT` | `{KEYCLOAK_BROWSER_URL}/realms/tdp/protocol/openid-connect/logout` |

Note: `OIDC_OP_AUTHORIZATION_ENDPOINT` and `OIDC_OP_LOGOUT_ENDPOINT` use `KEYCLOAK_BROWSER_URL` because the browser redirects to these. The token/userinfo/JWKS endpoints use `KEYCLOAK_SERVER_URL` because they are server-to-server calls.

#### Identity Provider Configuration

| Variable | Default | Description |
|---|---|---|
| `LOGIN_GOV_CLIENT_ID` | `urn:gov:gsa:openidconnect.profiles:sp:sso:hhs:tanf-proto-dev` | Login.gov OIDC client ID |
| `LOGIN_GOV_AUTH_URL` | `https://idp.int.identitysandbox.gov/openid_connect/authorize` | Login.gov authorization endpoint |
| `LOGIN_GOV_TOKEN_URL` | `https://idp.int.identitysandbox.gov/api/openid_connect/token` | Login.gov token endpoint |
| `LOGIN_GOV_JWKS_URL` | `https://idp.int.identitysandbox.gov/api/openid_connect/certs` | Login.gov JWKS endpoint |
| `LOGIN_GOV_LOGOUT_URL` | `https://idp.int.identitysandbox.gov/openid_connect/logout` | Login.gov logout endpoint |
| `LOGIN_GOV_ISSUER` | `https://idp.int.identitysandbox.gov/` | Login.gov issuer |
| `LOGIN_GOV_ACR_VALUES` | `http://idmanagement.gov/ns/assurance/ial/1` | Identity assurance level |
| `JWT_KEY` | — | Login.gov private RSA key (PEM or base64-encoded) |
| `AMS_CLIENT_ID` | — | AMS OIDC client ID |
| `AMS_CLIENT_SECRET` | — | AMS OIDC client secret |
| `AMS_AUTH_URL` | `https://sso-stage.acf.hhs.gov/auth/realms/ACF-SSO/protocol/openid-connect/auth` | AMS authorization endpoint |
| `AMS_TOKEN_URL` | `https://sso-stage.acf.hhs.gov/auth/realms/ACF-SSO/protocol/openid-connect/token` | AMS token endpoint |

### Frontend (`tdrs-frontend/.env.development`)

| Variable | Value | Description |
|---|---|---|
| `REACT_APP_AUTH_URL` | `http://localhost:3000/` | Points to Django versionless auth routes (Keycloak OIDC) |
| `REACT_APP_BACKEND_URL` | `http://localhost:3000/v1` | Fallback; used for non-auth API calls |

### Keycloak Container

| Variable | Default | Description |
|---|---|---|
| `KEYCLOAK_ADMIN` | `admin` | Admin console username |
| `KEYCLOAK_ADMIN_PASSWORD` | `admin` | Admin console password |
| `KC_TDP_DJANGO_CLIENT_SECRET` | — | Realm variable for tdp-django client secret |
| `KC_TDP_GRAFANA_CLIENT_SECRET` | — | Realm variable for tdp-grafana client secret |

## Realm Configuration

### Clients

| Client | Type | Purpose |
|---|---|---|
| `tdp-django` | Confidential (service account) | Backend OIDC authentication and admin API access |
| `tdp-grafana` | Confidential | Grafana SSO integration |

### Groups

Groups are synced from Django using the mapping in `keycloak_client.py`:

| Django Group | Keycloak Group |
|---|---|
| OFA Admin | ofa-admin |
| OFA System Admin | ofa-system-admin |
| Data Analyst | data-analyst |
| OFA Regional Staff | ofa-regional-staff |
| Developer | developer |
| ACF OCIO | acf-ocio |
| DIGIT Team | digit-team |

### Custom User Attributes

The `tdp-user-attributes` client scope includes these custom attributes, synced from Django:

- `login_gov_uuid` — Login.gov subject identifier
- `hhs_id` — AMS HHS ID
- `stt_id` — STT identifier
- `account_approval_status` — Approval status
- `region_ids` — Comma-separated region IDs
- `groups` — Keycloak group memberships
- `identity_provider` — Which IdP authenticated the user

### Identity Providers

| Alias | Provider | Purpose |
|---|---|---|
| `login-gov` | Login.gov (OIDC) | Grantee authentication |
| `ams` | ACF AMS (OIDC) | ACF staff authentication |

### Authentication Flows

- **tdp-first-broker-login** — Auto-creates users on first login, auto-links existing users by email
- **tdp-auto-link-existing** — Detects and links existing Keycloak users by email

## Django Integration

### Key Modules

| Module | Purpose |
|---|---|
| `users/oidc.py` | `KeycloakOIDCBackend` — custom OIDC authentication backend |
| `users/keycloak_client.py` | `KeycloakSyncClient` — admin API client for syncing user data |
| `users/keycloak_sync.py` | Django signal handlers for automatic sync on user save/group change |
| `users/views.py` | OIDC login/logout views with IdP hint routing |

### API Endpoints (v2)

| Endpoint | View | Description |
|---|---|---|
| `GET /v2/login/dotgov` | `KeycloakLoginDotGovView` | Redirects to Keycloak with `kc_idp_hint=login-gov` |
| `GET /v2/login/ams` | `KeycloakLoginAMSView` | Redirects to Keycloak with `kc_idp_hint=ams` |
| `GET /v2/oidc/callback/` | mozilla-django-oidc | Handles authorization code callback |
| `GET /v2/auth_check` | `AuthorizationCheck` | Returns current user authentication status |
| `GET /v2/logout/oidc` | `KeycloakLogoutView` | Clears session and redirects to Keycloak logout |

### User Sync

When `KEYCLOAK_SYNC_ENABLED=true`:

- **On user save** — syncs attributes (login_gov_uuid, hhs_id, stt_id, etc.) to Keycloak
- **On group change** — syncs Django group memberships to Keycloak groups
- **Bulk sync** — `python manage.py sync_users_to_keycloak`

Sync only works if the Keycloak user already exists (i.e., user has logged in via Keycloak at least once).

### Security Rules

- `@acf.hhs.gov` email users **must** use AMS, not Login.gov (enforced in `verify_claims()`)
- Deactivated users are rejected at login
- OIDC tokens stored in httpOnly session cookies

## Deployment (cloud.gov)

### Deploy Keycloak

```bash
cd keycloak
./deploy.sh -e <environment> -d <rds_service_name> -p <public_hostname> -i <docker_image>
# Example: ./deploy.sh -e dev -d tdp-keycloak-db-dev -p tdp-keycloak-dev -i ghcr.io/hhs/tdp-keycloak:latest
```

This will:
1. Push the Keycloak Docker image to Cloud Foundry
2. Bind the RDS service for the database
3. Map the internal route `keycloak.apps.internal:8080` (for server-to-server backend/celery calls)
4. Map the public route `<public_hostname>.app.cloud.gov` (for browser redirects and admin console)
5. Set `KC_HOSTNAME` so Keycloak generates correct redirect URIs matching the public route
6. Set up network policies so backend and celery can reach Keycloak

### Routing Architecture

Keycloak is deployed with two routes:

- **Internal** (`keycloak.apps.internal:8080`) — used by the Django backend and Celery for server-to-server API calls (token exchange, user sync, JWKS). Configured via `KEYCLOAK_SERVER_URL`.
- **Public** (`<hostname>.app.cloud.gov`) — used by the browser for OIDC redirects and the admin console. Configured via `KEYCLOAK_BROWSER_URL`.

Set `KEYCLOAK_BROWSER_URL` in the backend's environment to match the public route (e.g., `https://tdp-keycloak-dev.app.cloud.gov`).

### Required cloud.gov Environment Variables

Set these via `cf set-env` or a user-provided service:

- `KEYCLOAK_ADMIN` / `KEYCLOAK_ADMIN_PASSWORD`
- `KC_TDP_DJANGO_CLIENT_SECRET`
- `KC_TDP_GRAFANA_CLIENT_SECRET`
- `LOGIN_GOV_JWT_KEY`
- `LOGIN_GOV_ACR_VALUES`
- `AMS_CLIENT_ID` / `AMS_CLIENT_SECRET`

### Network Policies

The deploy script creates network policies allowing the backend (`tdp-backend-<space>`) and celery (`tdp-backend-<space>-celery`) apps to communicate with Keycloak on port 8080.

## Troubleshooting

**Keycloak won't start**
- Check `keycloak-pg` is running: `docker compose ps keycloak-pg`
- Verify `JWT_KEY` is set and in correct format (PEM or base64-encoded)

**Login redirects fail**
- Verify `KEYCLOAK_BROWSER_URL` matches what the browser can reach (e.g., `http://localhost:8443`)
- Check IdP is enabled in realm admin console
- Verify redirect URIs in the client configuration match the application URLs

**Keycloak sync errors**
- Ensure `KEYCLOAK_SYNC_ENABLED=true` in backend env
- User must exist in Keycloak first (login at least once)
- Verify `tdp-django` client has `realm-management` roles (view-users, manage-users, query-users)

**`NoReverseMatch` errors on v2 endpoints**
- Check `OIDC_EXEMPT_URLS` entries start with `/` (e.g., `"/v1/"` not `"v1/"`)

## Dependencies

| Package | Version | Purpose |
|---|---|---|
| `python-keycloak` | 4.6.2 | Keycloak Admin REST API client |
| `mozilla-django-oidc` | 4.0.1 | Django OIDC authentication backend |
