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
| `Dockerfile` | Keycloak 26.5 image with nginx proxying and the config-cli jar copied from `adorsys/keycloak-config-cli` |
| `realm-configs/` | Full realm exports for `dev-local`, `staging`, and `prod` |
| `normalize-login-gov-key.sh` | Decodes the base64 Login.gov private key and runs `keycloak-config-cli` |
| `deploy.sh` | Cloud Foundry deployment script for cloud.gov |
| `manifest.yml` | Cloud.gov manifest template |

## Local Setup

### Prerequisites

- Docker and Docker Compose
- The backend `docker-compose.yml` defines two Keycloak-related services:
  - **keycloak-pg** — PostgreSQL 15.7 database for Keycloak (port 5434)
  - **keycloak** — Keycloak 26.5 server (ports 8443 browser / 8080 internal / 9001 management) that runs config-cli during startup

Local Docker starts Keycloak first, then the Keycloak entrypoint imports `realm-export.dev-local.json` with config-cli after Keycloak is healthy. Cloud.gov uses the same startup import path.

### Starting Keycloak

```bash
cd tdrs-backend
docker compose up keycloak
```

The Keycloak entrypoint automatically imports the local realm export after Keycloak is healthy. It decodes `JWT_KEY` into the Login.gov signing key, applies Login.gov `acr_values`, configures AMS, and updates the browser flow used by `kc_idp_hint`.

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
| `KEYCLOAK_TDP_ADMIN_CLIENT_ID` | `tdp-admin` | Client ID for the standalone admin console OIDC flow |
| `KEYCLOAK_TDP_ADMIN_CLIENT_SECRET` | `tdp-admin-local-secret` | Client secret for the standalone admin console OIDC flow |
| `ADMIN_FRONTEND_BASE_URL` | `http://localhost:3001` | Browser-facing admin console URL used for admin login/logout redirects |
| `ADMIN_SESSION_COOKIE_NAME` | `admin_sessionid` | Django session cookie name used only by the admin frontend flow |
| `ADMIN_API_PROXY_TOKEN` | empty | Shared server-side token required for admin frontend proxy requests to `/admin-api/*` |

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
| `JWT_KEY` | — | Base64-encoded Login.gov private RSA PEM; compose passes this to `LOGIN_GOV_JWT_KEY` for config-cli |
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
| `KC_TDP_ADMIN_CLIENT_SECRET` | — | Realm variable for tdp-admin client secret |
| `KC_TDP_GRAFANA_CLIENT_SECRET` | empty | Realm variable for tdp-grafana client secret; optional and may be blank |
| `LOGIN_GOV_JWT_KEY` | — | Base64-encoded Login.gov private RSA PEM used by `normalize-login-gov-key.sh` |

## Realm Configuration

### Clients

| Client | Type | Purpose |
|---|---|---|
| `tdp-django` | Confidential (service account) | Backend OIDC authentication and admin API access |
| `tdp-admin` | Confidential | Standalone admin console browser authentication |
| `tdp-grafana` | Confidential | Grafana SSO integration |
| `tdp-cli` | **Public** (no secret, PKCE + Device Authorization Grant) | External API clients - Postman, CLI tools, CI/CD, security auditors |

Realm configurations are stored as full exports in `realm-configs/`:

- `realm-export.dev-local.json` is shared by `local` and `dev` and includes both hosted dev frontend URLs and localhost/`127.0.0.1`.
- `realm-export.staging.json` allows the hosted staging frontends and the admin client's Django-hosted `/admin-auth/*` callbacks.
- `realm-export.prod.json` allows the production frontend and the admin client's Django-hosted `/admin-auth/*` callback.

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
| `GET /v2/logout/oidc` | `KeycloakLogoutView` | Clears the standard Django session and returns to the TDP frontend |

### Admin Console Endpoints

| Endpoint | View | Description |
|---|---|---|
| `GET /admin-auth/login/dotgov` | `AdminKeycloakLoginDotGovView` | Redirects admin users to Keycloak with the `tdp-admin` client and `kc_idp_hint=login-gov` |
| `GET /admin-auth/login/ams` | `AdminKeycloakLoginAMSView` | Redirects admin users to Keycloak with the `tdp-admin` client and `kc_idp_hint=ams` |
| `GET /admin-auth/oidc/callback/` | mozilla-django-oidc | Handles admin authorization code callback with the admin-scoped Django session |
| `GET /admin-auth/auth_check` | `AdminAuthorizationCheck` | Validates the Django session and OFA System Admin authorization before admin rendering |
| `GET /admin-auth/logout/oidc` | `AdminKeycloakLogoutView` | Clears the admin-scoped Django session and returns to the admin frontend |
| `/admin-api/v1/*` | v1 API routes | Admin frontend proxy path; requires the server-side `X-Admin-Proxy-Token` header matching `ADMIN_API_PROXY_TOKEN`, an admin-scoped Django session, and OFA System Admin authorization |

The standard and admin cookies contain explicit signed `standard` and `admin`
session scopes. Django rejects a session whose signed scope does not match the
auth or API route, even if the cookie value is copied under the other cookie
name.

App sign-out deliberately does not call Keycloak's RP-initiated logout
endpoint. Keycloak maintains one realm SSO user session with child sessions for
`tdp-django`, `tdp-admin`, and other clients; RP-initiated logout terminates the
shared SSO session and can continue to Login.gov or AMS. A separate global
sign-out flow is required if the product needs "sign out everywhere" behavior.

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

### Request attribution metrics

Django also emits the Prometheus counter `tdp_api_requests_total` through the existing `/prometheus/metrics` scrape path. The metric is intended for low-cardinality API source attribution in Grafana.

Direct tools such as Postman and curl are identified by verified bearer-auth context or the presence of an `Authorization` header. Verified bearer tokens expose the real Keycloak `azp` client id such as `tdp-cli` and use `auth_method="bearer"`. Invalid bearer tokens and other Authorization schemes remain API-client attempts with `client_id="unknown"` and `auth_method="authorization_header"`. Authenticated requests without verified bearer context or an Authorization header are tracked separately as `browser_session`, because the backend can observe the authenticated Django session but cannot prove a specific OAuth client id. Unauthenticated requests without an Authorization header remain `source="unknown"` and `auth_method="none"`. Frontend-provided service headers are not used for attribution because they are request-supplied and spoofable.

Labels:

| Label | Meaning |
|---|---|
| `source` | `api_client`, `browser_session`, or `unknown` |
| `auth_method` | `bearer` for verified bearer context, `session` for authenticated browser sessions, `authorization_header` for unverified Authorization attempts, or `none` |
| `client_id` | A verified Keycloak `azp` value such as `tdp-cli`, `unknown` when an Authorization header was present but no client id was verified, or `none` |
| `user_stt` | Authenticated user's assigned STT name such as `Alabama`; `none` for authenticated users without an STT; `unknown` when no authenticated user is available |
| `user_group` | Authenticated user's group such as `OFA System Admin` or `Data Analyst`; `none` for authenticated users without a group; `unknown` when no authenticated user is available |
| `method` | HTTP method |
| `status_code` | HTTP response status code |
| `view` | Django `resolver_match.view_name`; raw paths and user identifiers are not included |

Examples:

```promql
100 * (
  (sum(increase(tdp_api_requests_total{source="api_client",auth_method="bearer"}[$__range])) or vector(0))
  / clamp_min((sum(increase(tdp_api_requests_total{auth_method=~"bearer|session"}[$__range])) or vector(0)), 1)
)
```

```promql
sum(increase(tdp_api_requests_total{source="api_client",auth_method="bearer"}[$__range]))
  by (client_id, auth_method, user_group, user_stt, method, view, status_code)
```

```promql
sum(increase(tdp_api_requests_total{source="api_client",status_code=~"4.."}[$__range]))
  by (client_id, auth_method, user_group, user_stt, method, view, status_code)
```

Use the 4XX query for failed API-client traffic. Expired or invalid bearer tokens appear as `auth_method="authorization_header"` and `client_id="unknown"` because the backend observed an API-client attempt but did not verify the token or client id. Verified bearer clients that fail authorization, including STT-scoping issues, keep `auth_method="bearer"` and include the authenticated user's low-cardinality STT/group labels.


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
./deploy.sh -e <environment> -d <rds_service_name> -p <public_hostname> -i <docker_image> -u <docker_username>
# Example: ./deploy.sh -e dev -d tdp-keycloak-db-dev -p tdp-keycloak-dev -i ghcr.io/hhs/tdp-keycloak:latest -u myuser
```

This will:
1. Push the Keycloak Docker image to Cloud Foundry
2. Bind the RDS service for the database
3. Map the internal route `keycloak.apps.internal:8080` (for server-to-server backend/celery calls)
4. Map the public route `<public_hostname>.app.cloud.gov` (for browser redirects and admin console)
5. Set `KC_HOSTNAME`, `DEPLOY_ENV`, and config-cli substitution variables
6. Set up network policies so backend and celery can reach Keycloak
7. Start Keycloak with `KEYCLOAK_CONFIG_IMPORT_ON_STARTUP=true`, causing the entrypoint to run `/opt/keycloak/normalize-login-gov-key.sh` after Keycloak is healthy. This decodes the Login.gov key and invokes `keycloak-config-cli` against the selected realm export before nginx starts.

Cloud deployment does **not** use Keycloak's native `--import-realm`. The app starts Keycloak first, then the entrypoint runs config-cli against the local Keycloak port through the Admin API. This is what allows checked-in realm JSON to contain `$(env:...)`, `$(urlEncoder:...)`, and the decoded Login.gov signing key.

### Routing Architecture

Keycloak is deployed with two routes:

- **Internal** (`keycloak.apps.internal:8080`) — used by the Django backend and Celery for server-to-server API calls (token exchange, user sync, JWKS). Configured via `KEYCLOAK_SERVER_URL`.
- **Public** (`<hostname>.app.cloud.gov`) — used by the browser for OIDC redirects and the admin console. Configured via `KEYCLOAK_BROWSER_URL`.

Set `KEYCLOAK_BROWSER_URL` in the backend's environment to match the public route (e.g., `https://tdp-keycloak-dev.app.cloud.gov`).

For the checked-in realm exports:

- `local` and `dev` both use `realm-export.dev-local.json`, which allows `raft`, `qasp`, and `a11y` hosted frontends, admin `/admin-auth/*` callbacks on those hosts, plus localhost/`127.0.0.1`.
- `staging` uses `realm-export.staging.json`, which allows `develop` and `staging` hosted frontends plus admin `/admin-auth/*` callbacks on those hosts.
- `prod` uses `realm-export.prod.json`, which allows `https://tanfdata.acf.hhs.gov` plus the admin `/admin-auth/*` callback on that host.

### Required cloud.gov Environment Variables

Set these via `cf set-env` or a user-provided service:

- `KEYCLOAK_ADMIN` / `KEYCLOAK_ADMIN_PASSWORD`
- `KC_TDP_DJANGO_CLIENT_SECRET`
- `KC_TDP_ADMIN_CLIENT_SECRET`
- `LOGIN_GOV_JWT_KEY`
- `AMS_CLIENT_ID` / `AMS_CLIENT_SECRET`
- `ADMIN_API_PROXY_TOKEN`

Optional Keycloak config values:

- `KC_TDP_GRAFANA_CLIENT_SECRET` (defaults to an empty string for config-cli substitution)
- `LOGIN_GOV_ACR_VALUES`
- `LOGIN_GOV_CLIENT_ID`, `LOGIN_GOV_AUTH_URL`, `LOGIN_GOV_TOKEN_URL`, `LOGIN_GOV_JWKS_URL`, `LOGIN_GOV_LOGOUT_URL`, `LOGIN_GOV_ISSUER`
- `AMS_AUTH_URL`, `AMS_TOKEN_URL`, `AMS_JWKS_URL`, `AMS_LOGOUT_URL`, `AMS_USERINFO_URL`, `AMS_ISSUER`
- `KC_CLI_REDIRECT_URI`, `KC_CLI_WEB_ORIGIN`

### Network Policies

The deploy script creates network policies allowing the backend (`tdp-backend-<space>`) and celery (`tdp-backend-<space>-celery`) apps to communicate with Keycloak on port 8080.

### Rerun Config Import

The cloud.gov config import runs from `entrypoint.sh` during Keycloak startup when `KEYCLOAK_CONFIG_IMPORT_ON_STARTUP=true`. To rerun it after changing only a Keycloak app env var, restage or restart the Keycloak app:

```bash
cf restage keycloak-staging
cf logs keycloak-staging --recent
```

Use the app name for the target environment:

| Environment | App |
|---|---|
| Dev | `keycloak-dev` |
| Staging | `keycloak-staging` |
| Prod | `keycloak` |

Checked-in realm JSON is packaged into the Keycloak container image. To apply realm JSON changes in cloud.gov, rebuild the Keycloak container, push it to the container registry, then redeploy Keycloak with that image so startup config import runs against the new realm export.

## Secret Rotation

Detailed steps live in [keycloak-operations.md](keycloak-operations.md#secret-rotation). The short version is:

- Rotate `KC_TDP_DJANGO_CLIENT_SECRET`, `KC_TDP_ADMIN_CLIENT_SECRET`, `KC_TDP_GRAFANA_CLIENT_SECRET`, `LOGIN_GOV_JWT_KEY`, or AMS credentials in the Keycloak app environment.
- Restage Keycloak so the entrypoint reruns config-cli with the new env and updates the realm.
- Update and restage downstream apps that use the same secret, such as backend/celery for `tdp-django` and `tdp-admin`, or Grafana for `tdp-grafana`.

`LOGIN_GOV_JWT_KEY` must be a base64-encoded PEM private key in cloud.gov. `KC_TDP_GRAFANA_CLIENT_SECRET` is optional and defaults to an empty string so config-cli can resolve the realm placeholder when Grafana SSO is not deployed.

## Recovery

Detailed steps live in [keycloak-operations.md](keycloak-operations.md#restart-and-recovery) and [keycloak-operations.md](keycloak-operations.md#backup-and-restore).

- If Keycloak is unhealthy, check `cf logs keycloak --recent`, verify the bound RDS service, and restart or redeploy.
- If realm changes are missing, check startup logs for the `Running Keycloak config import...` and `Keycloak config import complete.` messages. Restage after fixing env issues; rebuild, push, and redeploy after fixing realm JSON.
- After RDS restore or a new Keycloak instance, redeploy or restage Keycloak so startup config import runs, then run `./manage.py sync_users_to_keycloak` from a backend app to reconcile Django user state.

## Troubleshooting

**Keycloak won't start**
- Check `keycloak-pg` is running: `docker compose ps keycloak-pg`
- Verify `JWT_KEY` / `LOGIN_GOV_JWT_KEY` is set to a base64-encoded PEM private key before config import runs

**Login redirects fail**
- Verify `KEYCLOAK_BROWSER_URL` matches what the browser can reach (e.g., `http://localhost:8443`)
- Check IdP is enabled in realm admin console
- Verify redirect URIs in the client configuration match the application URLs

**Config-cli startup import fails**
- `Failed to decode private key`: `LOGIN_GOV_JWT_KEY` did not decode to a PEM private key with a `BEGIN ... PRIVATE KEY` header.
- `Cannot resolve variable 'env:...'`: the referenced env var was not present in the Keycloak app environment. Optional values must still be injected as empty strings when the realm JSON references them.
- `awk: command not found` or `JAVA_OPTS: unbound variable`: rebuild and redeploy the Keycloak image with the current `normalize-login-gov-key.sh`.
- Check startup logs with `cf logs keycloak --recent`, then restage after fixing the app env or image.

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
