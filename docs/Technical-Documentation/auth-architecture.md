# TDP Authentication Architecture

## Overview

TDP uses **Keycloak** as a centralized OpenID Connect (OIDC) broker between the application and two upstream identity providers: **Login.gov** (grantee authentication) and **ACF AMS** (ACF staff authentication). Django remains the source of truth for user data — Keycloak handles authentication and token issuance, while Django pushes user/group state to Keycloak via the Admin REST API.

This replaces the previous architecture where Django hand-rolled two separate OIDC flows for Login.gov and AMS. The auth complexity now lives in Keycloak, and Django uses the `mozilla-django-oidc` library as a standard OIDC relying party.

## Authentication Flow

```
┌──────────┐   ┌──────────┐   ┌─────────┐   ┌────────┐   ┌───────────┐
│  Browser ├──►│  Nginx   ├──►│  Django ├──►│Keycloak├──►│ Login.gov │
│          │◄──┤ (frontend│◄──┤  /v2/   │◄──┤  OIDC  │   ├───────────┤
└──────────┘   │  proxy)  │   │  routes │   │ Broker ├──►│  ACF AMS  │
               └──────────┘   └─────────┘   └───┬────┘   └───────────┘
                                                │
                                          ┌─────┴──────┐
                                          │  Grafana   │
                                          │  (PLG SSO) │
                                          └────────────┘
```

### Login.gov Flow (Grantees)

1. User clicks "Sign in with LOGIN.GOV" on the TDP splash page
2. Frontend navigates to `{REACT_APP_AUTH_URL}/login/dotgov`
3. Django's `KeycloakLoginDotGovView` redirects to Keycloak with `kc_idp_hint=login-gov`
4. Keycloak skips its login page and redirects directly to Login.gov (sandbox or production)
5. User authenticates at Login.gov
6. Login.gov redirects back to Keycloak with an authorization code
7. Keycloak exchanges the code for tokens using `private_key_jwt` client authentication (RS256-signed JWT assertion)
8. Keycloak creates/links the user and issues its own tokens with TDP-specific claims
9. Keycloak redirects to Django's `mozilla-django-oidc` callback (`/v2/oidc/callback/`)
10. `KeycloakOIDCBackend` validates the token, looks up the user by `login_gov_uuid`, creates a Django session
11. Django redirects to the frontend with the session cookie set

### AMS Flow (ACF Staff)

Same as above, except:
- User clicks "Sign in with ACF AMS" which hits `/v2/login/ams`
- `KeycloakLoginAMSView` sets `kc_idp_hint=ams`
- AMS uses `client_secret_post` authentication (not `private_key_jwt`)
- User lookup is by `hhs_id` attribute

### ACF Email Domain Enforcement

Users with `@acf.hhs.gov` email addresses **must** authenticate via AMS, not Login.gov. This is enforced in `KeycloakOIDCBackend.verify_claims()` — if the email ends with `@acf.hhs.gov` and the `identity_provider` claim is `login-gov`, the authentication is rejected.

## System Architecture

### Environment Topology

One Keycloak instance per Cloud.gov space (3 total), matching the existing per-space infrastructure pattern:

```
tanf-dev (Dev Space)
├── tdp-backend-raft   + tdp-frontend-raft   + tdp-celery-raft
├── tdp-backend-qasp   + tdp-frontend-qasp   + tdp-celery-qasp
├── tdp-backend-a11y   + tdp-frontend-a11y   + tdp-celery-a11y
├── keycloak ← shared by all 3 dev pairs
└── Shared: tdp-db-dev, tdp-redis-dev, tdp-datafiles-dev

tanf-staging (Staging Space)
├── tdp-backend-develop + tdp-frontend-develop + tdp-celery-develop
├── tdp-backend-staging + tdp-frontend-staging + tdp-celery-staging
├── keycloak ← shared by both staging pairs
└── Shared: tdp-db-staging, tdp-redis-staging, tdp-datafiles-staging

tanf-prod (Production Space)
├── tdp-backend-prod + tdp-frontend-prod + tdp-celery-prod
├── keycloak ← prod pair + Grafana SSO
├── PLG Stack (Grafana, Prometheus, Loki, etc.)
└── Shared: tdp-db-prod, tdp-redis-prod, tdp-datafiles-prod
```

### Keycloak Container Architecture

Keycloak runs as a single Docker container with an embedded nginx reverse proxy. This design solves Keycloak 26's `X-Frame-Options: DENY` header issue on non-realm pages (which breaks the admin console's authentication iframe).

```
Cloud.gov:   gorouter → nginx ($PORT) → Keycloak (localhost:8081)
Local:       browser (localhost:8443) → nginx (:8080) → Keycloak (:8081)
```

The `entrypoint.sh` script:
1. Renders `nginx.conf` from template (substitutes `$PORT`)
2. Starts Keycloak on port 8081
3. Polls `/health/ready` until Keycloak is up (max 90 attempts, 2s each)
4. Starts nginx on `$PORT`
5. Monitors both processes — if either dies, kills the other and exits

Nginx strips `X-Frame-Options: DENY` from all Keycloak responses and replaces it with `SAMEORIGIN`.

### Routing

Keycloak is deployed with two routes:

| Route | Purpose | Used by |
|-------|---------|---------|
| `keycloak.apps.internal:8080` (internal) | Server-to-server API calls | Django backend, Celery, Grafana |
| `<hostname>.app.cloud.gov` (public) | Browser OIDC redirects, admin console | User browsers |

Django settings use:
- `KEYCLOAK_SERVER_URL` → internal route (token exchange, user sync, JWKS validation)
- `KEYCLOAK_BROWSER_URL` → public route (authorization endpoint, logout redirect)

### Network Policies

Each backend and celery app in a space needs a Cloud Foundry network policy to reach Keycloak on port 8080. Grafana (in tanf-prod) also needs a policy. These are created automatically by `deploy.sh`.

## Django Integration

### URL Routing

Auth endpoints live under `/v2/` (the legacy `/v1/` auth routes remain for backward compatibility during transition):

| Endpoint | View | Description |
|----------|------|-------------|
| `GET /v2/login/dotgov` | `KeycloakLoginDotGovView` | Redirects to Keycloak with `kc_idp_hint=login-gov` |
| `GET /v2/login/ams` | `KeycloakLoginAMSView` | Redirects to Keycloak with `kc_idp_hint=ams` |
| `GET /v2/oidc/callback/` | `mozilla-django-oidc` | Handles OIDC authorization code callback |
| `GET /v2/auth_check` | `AuthorizationCheck` | Returns current user authentication status |
| `GET /v2/logout/oidc` | `KeycloakLogoutView` | Clears Django session, redirects to Keycloak logout |

### OIDC Backend (`KeycloakOIDCBackend`)

Extends `mozilla-django-oidc`'s `OIDCAuthenticationBackend` with TDP-specific logic:

- **User lookup** (`filter_users_by_claims`): Looks up users by `hhs_id` (AMS) or `login_gov_uuid` (Login.gov), falling back to email
- **User creation** (`create_user`): Creates Django users with identity attributes from token claims
- **Claim verification** (`verify_claims`): Enforces ACF email domain check, blocks deactivated users, checks account approval status
- **Token handling** (`get_userinfo`): Uses ID token claims directly instead of calling the userinfo endpoint

### What `mozilla-django-oidc` handles

- OIDC authorization redirect with state/nonce generation
- Authorization code → token exchange
- ID token JWT signature verification against JWKS endpoint
- Session creation and renewal via `SessionRefresh` middleware
- CSRF protection during the OIDC flow

### Django-to-Keycloak User Sync

Django is the source of truth for user data. When user attributes or group memberships change in Django, they are pushed to Keycloak via the Admin REST API:

```
Django post_save signal → KeycloakSyncClient.sync_user()      → Updates KC attributes
Django m2m_changed signal → KeycloakSyncClient.sync_user_groups() → Updates KC groups
```

Controlled by `KEYCLOAK_SYNC_ENABLED` setting. Sync is idempotent — multiple backends in the same space can fire signals without conflicts.

**Group mapping:**

| Django Group | Keycloak Group |
|---|---|
| OFA Admin | ofa-admin |
| OFA System Admin | ofa-system-admin |
| Data Analyst | data-analyst |
| OFA Regional Staff | ofa-regional-staff |
| Developer | developer |
| ACF OCIO | acf-ocio |
| DIGIT Team | digit-team |

### Custom Token Claims

The `tdp-user-attributes` client scope maps these attributes into JWT tokens:

| Claim | Source | Description |
|-------|--------|-------------|
| `login_gov_uuid` | User attribute | Login.gov subject identifier |
| `hhs_id` | User attribute | AMS HHS ID |
| `stt_id` | User attribute | STT identifier |
| `account_approval_status` | User attribute | Approval status |
| `region_ids` | User attribute | Comma-separated region IDs |
| `groups` | Group membership | Keycloak group names |
| `identity_provider` | Session note | Which IdP authenticated the user |

## Keycloak Realm Configuration

### Clients

| Client | Type | Purpose |
|--------|------|---------|
| `tdp-django` | Confidential (service account) | Backend OIDC authentication + Admin API access |
| `tdp-grafana` | Confidential | Grafana SSO (AMS + local password auth only) |

### Identity Providers

| Alias | Provider | Client Auth Method | Usage |
|-------|----------|--------------------|-------|
| `login-gov` | Login.gov (OIDC) | `private_key_jwt` (RS256) | Grantee authentication |
| `ams` | ACF AMS (OIDC) | `client_secret_post` | ACF staff authentication |

### Authentication Flows

- **tdp-first-broker-login**: Auto-creates users on first login via an IdP, auto-links existing Keycloak users by email (no registration prompt — Django manages user creation)
- **tdp-auto-link-existing**: Sub-flow that detects and links existing Keycloak users by email

### Security Settings

- Brute force protection: 10 failure threshold, 15-minute lockout
- Access token lifespan: 5 minutes
- SSO session idle timeout: 30 minutes
- SSO session max lifespan: 12 hours

## Grafana SSO

Grafana authenticates via Keycloak OIDC using the `tdp-grafana` client, which is configured to only show the AMS identity provider (Login.gov is excluded).

### Access Control

Users **must** belong to one of three Keycloak groups to access Grafana. Users not in any of these groups are denied login entirely (`role_attribute_strict = true` with no fallback role).

| Keycloak Group | Grafana Org | Grafana Role | Auth Path |
|----------------|-------------|--------------|-----------|
| `ofa-system-admin` | Admin (ID 1) | Admin | PIV auth via AMS through Keycloak |
| `developer` | Admin (ID 1) | Admin | Local Keycloak username/password |
| `digit-team` | DIGIT (ID 3) | Editor | PIV auth via AMS through Keycloak |
| *(any other / none)* | — | **Login denied** | — |

**Login.gov users**: Cannot access Grafana (Login.gov IdP is not shown on the `tdp-grafana` client login page).

### Organization and Role Mapping

Grafana uses two complementary mechanisms from the `[auth.generic_oauth]` config:

**Role mapping** (JMESPath on `groups` claim — determines the role):
```
contains(groups[*], 'ofa-system-admin') && 'Admin'
  || contains(groups[*], 'developer') && 'Admin'
  || contains(groups[*], 'digit-team') && 'Editor'
```

**Org mapping** (maps Keycloak groups to Grafana orgs):
```ini
org_attribute_path = groups
org_mapping = ofa-system-admin:1:Admin developer:1:Admin digit-team:3:Editor
```

`auto_assign_org` is disabled — org assignment is handled entirely by `org_mapping`. If a user doesn't match any mapping rule and `role_attribute_strict = true`, login is denied.

Developer accounts for Grafana are local Keycloak accounts in the prod instance, manually created in the admin console and assigned to the `developer` group.

## Frontend Integration

The frontend uses `REACT_APP_AUTH_URL` for auth endpoints and `REACT_APP_BACKEND_URL` for all other API calls:

| File | Auth Endpoint |
|------|---------------|
| `SplashPage.jsx` | `{REACT_APP_AUTH_URL}/login/dotgov`, `{REACT_APP_AUTH_URL}/login/ams` |
| `signOut.js` | `{REACT_APP_AUTH_URL}/logout/oidc` |
| `IdleTimer.jsx` | `{REACT_APP_AUTH_URL}/logout/oidc` |
| `auth.js` | `{REACT_APP_AUTH_URL}/auth_check` |

`REACT_APP_AUTH_URL` defaults to `REACT_APP_BACKEND_URL` if not set.

## Per-Environment Configuration

| Setting | Dev | Staging | Production |
|---------|-----|---------|------------|
| Login.gov client ID | `tanf-proto-dev` | `tanf-proto-staging` | `tanf-prod` |
| Login.gov endpoints | `idp.int.identitysandbox.gov` | `idp.int.identitysandbox.gov` | `secure.login.gov` |
| AMS endpoint | `sso-stage.acf.hhs.gov` | `sso-stage.acf.hhs.gov` | Production AMS |
| Keycloak public route | `tdp-keycloak-dev.app.cloud.gov` | `tdp-keycloak-staging.acf.hhs.gov` | `tdp-keycloak-prod.acf.hhs.gov` |

The `realm-export.json` uses Keycloak's `${ENV_VAR}` syntax for environment-specific values (Login.gov client ID, endpoints, redirect URIs). These are injected as environment variables per space.

## Key Files

| Module | Path | Purpose |
|--------|------|---------|
| OIDC Backend | `tdrs-backend/tdpservice/users/oidc.py` | Custom authentication backend for mozilla-django-oidc |
| Sync Client | `tdrs-backend/tdpservice/users/keycloak_client.py` | Admin REST API client for user/group sync |
| Sync Signals | `tdrs-backend/tdpservice/users/keycloak_sync.py` | Django signal handlers for auto-sync |
| Login Views | `tdrs-backend/tdpservice/users/views.py` | Keycloak login/logout views with IdP hints |
| URL Routing | `tdrs-backend/tdpservice/urls.py` | `/v2/` auth route definitions |
| Realm Config | `tdrs-backend/keycloak/realm-export.json` | Complete Keycloak realm definition |
| IdP Config | `tdrs-backend/keycloak/configure-idps.sh` | Post-startup IdP configuration script |
| Keycloak Deploy | `tdrs-backend/keycloak/deploy.sh` | Cloud Foundry deployment script |
| Keycloak README | `tdrs-backend/keycloak/README.md` | Detailed integration reference |

## Related Documentation

- [Keycloak Operations Runbook](keycloak-operations.md) — restart procedures, secret rotation, troubleshooting, sync commands
- [Secret Key Rotation](secret-key-rotation-steps.md) — includes JWT key rotation procedures
- [OpenID Connect (legacy)](openid-connect.md) — documents the original Login.gov direct OIDC flow (pre-Keycloak)
