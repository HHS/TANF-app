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
| `realm-configs/` | Full realm exports for `dev-local`, `staging`, and `prod` |
| `select-realm-config.sh` | Copies the correct checked-in realm export into Keycloak's import path based on `DEPLOY_ENV` |
| `configure-idps.sh` | Post-startup script for runtime-sensitive IdP settings like signing keys and ACR values |
| `deploy.sh` | Cloud Foundry deployment script for cloud.gov |
| `manifest.yml` | Cloud.gov manifest template |

## Local Setup

### Prerequisites

- Docker and Docker Compose
- The backend `docker-compose.yml` defines three Keycloak-related services:
  - **keycloak-pg** — PostgreSQL 15.7 database for Keycloak (port 5434)
  - **keycloak** — Keycloak 26.0 server (ports 8443 browser / 8080 internal / 9001 management)
  - **keycloak-configure** — Runs `configure-idps.sh` after Keycloak starts

Local Docker uses `DEPLOY_ENV=local`, which selects the shared `dev-local` realm export before Keycloak starts.

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
| `LOGIN_GOV_CLIENT_ID` | `urn:gov:gsa:openidconnect.profiles:sp:sso:hhs:tanf-proto-{space}` | Login.gov OIDC client ID |
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
| `tdp-cli` | **Public** (no secret, PKCE + Device Authorization Grant) | External API clients - Postman, CLI tools, CI/CD, security auditors |

Realm configurations are stored as full exports in `realm-configs/`:

- `realm-export.dev-local.json` is shared by `local` and `dev` and includes both hosted dev frontend URLs and localhost/`127.0.0.1`.
- `realm-export.staging.json` allows only the hosted staging frontends.
- `realm-export.prod.json` allows only the production frontend.

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

## External API Clients

External tools (Postman, CLI, CI/CD, auditors) authenticate against the Django API using Keycloak-issued JWT bearer tokens. Tokens are obtained via standard OAuth2 grants against the **public** `tdp-cli` Keycloak client (no client secret to distribute).

Django validates incoming bearer tokens with `KeycloakBearerTokenAuthentication` (registered in DRF's `DEFAULT_AUTHENTICATION_CLASSES`), which verifies the JWT signature against `OIDC_OP_JWKS_ENDPOINT`, requires the `tdp-cli` client (`azp`) and Django API audience (`aud`), and resolves the user via the same claim-based logic used by browser logins. Authorization (permissions, STT scoping, approval status) is identical to a browser session.

### Postman (Authorization Code + PKCE)

In a Postman request → **Authorization** tab → Type **OAuth 2.0** → **Configure New Token**:

| Field | Value |
|---|---|
| Grant Type | **Authorization Code (With PKCE)** |
| Callback URL | `https://oauth.pstmn.io/v1/callback` |
| Auth URL | `${KEYCLOAK_BROWSER_URL}/realms/tdp/protocol/openid-connect/auth` |
| Access Token URL | `${KEYCLOAK_BROWSER_URL}/realms/tdp/protocol/openid-connect/token` |
| Client ID | `tdp-cli` |
| Client Secret | *(leave empty)* |
| Code Challenge Method | **SHA-256** |
| Scope | `openid email profile tdp-user-attributes` |
| Client Authentication | **Send client credentials in body** |

Click **Get New Access Token** → authenticate via Login.gov / AMS in the popup → token returned. Use it on requests as:

```
Authorization: Bearer <access_token>
```

### CLI (Device Authorization Grant)

For headless CLI tools (no browser on the host), use the device flow. Standard OAuth2 libraries support this out of the box (same grant `gh auth login`, `aws sso login`, and `gcloud auth login` use).

**1. Initiate device authorization**

```bash
curl -X POST "${KEYCLOAK_BROWSER_URL}/realms/tdp/protocol/openid-connect/auth/device" \
  -d "client_id=tdp-cli" \
  -d "scope=openid email profile tdp-user-attributes"
```

Response includes `device_code`, `user_code`, `verification_uri_complete`, `interval`, and `expires_in`.

**2. Display the verification URL** to the user (e.g. print `verification_uri_complete`). They open it in any browser, authenticate via Login.gov or AMS, and approve the device.

**3. Poll the token endpoint** every `interval` seconds until the user completes the flow:

```bash
curl -X POST "${KEYCLOAK_BROWSER_URL}/realms/tdp/protocol/openid-connect/token" \
  -d "grant_type=urn:ietf:params:oauth:grant-type:device_code" \
  -d "device_code=<from step 1>" \
  -d "client_id=tdp-cli"
```

While the user hasn't approved yet, you'll get `400 authorization_pending` (keep polling). When they approve, you get the access token.

### Calling the Django API

```bash
curl -H "Authorization: Bearer ${ACCESS_TOKEN}" \
  http://localhost:8080/v1/users/
```

Same authorization rules as a browser session:
  - the user behind the token must be approved, active, and respect ACF email / Login.gov mismatch rules.

### Audit logging

Every bearer-token-authenticated request emits a structured log line:

```
INFO Bearer token auth client=tdp-cli user=<email> path=/v1/users/
```

The `client_id` is the token's `azp` claim (which Keycloak client minted the token). The `tdp-api-audience` default client scope adds the Django API audience (`tdp-django`) to `tdp-cli` access tokens so Django can reject tokens intended for other clients. In Cloud.gov these flow into Loki and are queryable in Grafana.

### Rate limiting

`KeycloakClientRateThrottle` rate-limits per Keycloak client_id (the `azp` claim) — not per user. Default: `300/min`, configurable via the `KEYCLOAK_CLIENT_RATE` env var (DRF rate string, e.g. `60/min`, `1000/hour`). Browser sessions and other auth paths are unaffected. Counters live in the dedicated Redis-backed `throttle` cache (DB 3) so they're shared across web workers.

### Local testing

The `tdp-cli` client is in `realm-export.json`, so it's imported on first Keycloak start. To pick up realm changes locally after editing the file, the Keycloak image must be rebuilt and the keycloak-pg volume cleared:

```bash
task backend-down
docker volume rm tdrs-backend_keycloak_pg_data
docker compose build --no-cache keycloak
task backend-up
```

For testing without going through the full Login.gov / AMS broker flow, you can manually create a Keycloak user with a password (Keycloak admin → Users → Add user → Credentials → Set password, *Temporary OFF*) whose email matches an existing approved Django user
  - bearer auth's claim resolution falls back to email lookup, so the request resolves to the real Django user with all its STT scoping.

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
5. Set `KC_HOSTNAME` and `DEPLOY_ENV` so the correct checked-in realm export is selected inside the container
6. Set up network policies so backend and celery can reach Keycloak
7. Run `configure-idps.sh` to configure runtime-sensitive IdP settings after startup

### Routing Architecture

Keycloak is deployed with two routes:

- **Internal** (`keycloak.apps.internal:8080`) — used by the Django backend and Celery for server-to-server API calls (token exchange, user sync, JWKS). Configured via `KEYCLOAK_SERVER_URL`.
- **Public** (`<hostname>.app.cloud.gov`) — used by the browser for OIDC redirects and the admin console. Configured via `KEYCLOAK_BROWSER_URL`.

Set `KEYCLOAK_BROWSER_URL` in the backend's environment to match the public route (e.g., `https://tdp-keycloak-dev.app.cloud.gov`).

For the checked-in realm exports:

- `local` and `dev` both use `realm-export.dev-local.json`, which allows `raft`, `qasp`, and `a11y` hosted frontends plus localhost/`127.0.0.1`.
- `staging` uses `realm-export.staging.json`, which allows only `develop` and `staging` hosted frontends.
- `prod` uses `realm-export.prod.json`, which allows only `https://tanfdata.acf.hhs.gov`.

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
