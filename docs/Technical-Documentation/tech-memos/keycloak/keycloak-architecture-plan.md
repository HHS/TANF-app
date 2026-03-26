# High-Level Architecture Plan: Keycloak Integration

## 1. Purpose

This document is the formal architecture plan for integrating Keycloak as the centralized OIDC authentication broker for the TANF Data Portal. It covers production integration concerns, migration strategy, security posture, risks, and open decisions.

---

## 2. Architecture Summary

### What Keycloak Does

Keycloak acts as an **OIDC broker** — it sits between the TDP application and the upstream identity providers (Login.gov and AMS), handling all authentication protocol complexity. The TDP Django backend becomes a standard OIDC relying party using the `mozilla-django-oidc` library.

```
┌──────────┐   ┌──────────┐   ┌─────────┐   ┌────────┐   ┌───────────┐
│  Browser ├──►│  Nginx   ├──►│  Django ├──►│Keycloak├──►│ Login.gov │
│          │◄──┤ (frontend│◄──┤   auth  │◄──┤  OIDC  │   ├───────────┤
└──────────┘   │  proxy)  │   │  routes │   │ Broker ├──►│  ACF AMS  │
               └──────────┘   └─────────┘   └───┬────┘   └───────────┘
                                                │
                                          ┌─────┴──────┐
                                          │  Grafana   │
                                          │  (PLG SSO) │
                                          └────────────┘
```

### What Keycloak Does NOT Do

- **Keycloak is not the source of truth for user data.** Django/RDS owns user records, groups, approval status, and STT assignments. Keycloak mirrors this data via a one-way sync (Django → Keycloak) for inclusion in JWT tokens.
- **Keycloak does not replace Django sessions.** Django continues to manage its own sessions via `SessionRefresh` middleware. Keycloak issues tokens during the OIDC flow; Django validates them and creates a Django session. The browser holds a Django session cookie, not a Keycloak token.
- **Keycloak does not manage user registration or approval.** The existing Django admin workflow for user approval, group assignment, and deactivation is unchanged.

### Major Subsystems

| Subsystem | Technology | Purpose |
|-----------|------------|---------|
| OIDC Brokering | Keycloak 26 + nginx reverse proxy | Centralizes Login.gov and AMS authentication behind a single OIDC interface |
| Identity Providers | Login.gov (`private_key_jwt`), AMS (`client_secret_post`) | Upstream authentication — Keycloak brokers to both |
| Django OIDC RP | `mozilla-django-oidc` + `KeycloakOIDCBackend` | Replaces hand-rolled OIDC flow with a standard library + custom user lookup/validation |
| User Sync | `KeycloakSyncClient` + Django signals | Pushes user attributes and group memberships from Django to Keycloak on every save |
| Realm Configuration | `realm-export.json` + `configure-idps.sh` | Declarative realm definition with post-startup script for sensitive material (signing keys) |
| PLG SSO | `tdp-grafana` Keycloak client | Grafana authenticates via Keycloak OIDC (AMS + local password only) |
| Deployment | `deploy.sh` + `manifest.yml` + Terraform (RDS) | Cloud Foundry deployment with rolling strategy, network policies, and IdP configuration |

---

## 3. Infrastructure

### Environment Topology

One Keycloak instance per Cloud.gov space (3 total), consistent with the existing per-space infrastructure pattern where each space shares one RDS, one Redis, and one S3 bucket:

| Space | App Pairs | Keycloak Serves |
|-------|-----------|-----------------|
| `tanf-dev` | raft, qasp, a11y | All 3 dev backend/frontend pairs |
| `tanf-staging` | develop, staging | Both staging backend/frontend pairs |
| `tanf-prod` | prod | Prod backend/frontend pair **+ the PLG observability stack (Grafana, Prometheus, Loki, Tempo, Mimir, AlertManager)** |

The **production Keycloak instance** has a dual role: it authenticates TDP application users (Login.gov and AMS) **and** manages SSO for the PLG observability stack. Grafana, which monitors all environments, authenticates its users through the prod Keycloak instance using the `tdp-grafana` OIDC client. This means the prod Keycloak is a dependency for both TDP user authentication and operational monitoring access.

### Container Architecture

Keycloak runs as a single Docker container with an embedded nginx reverse proxy. Nginx is required because Keycloak 26 sets `X-Frame-Options: DENY` on non-realm pages, which cannot be overridden via Keycloak configuration and breaks the admin console's authentication iframe.

```
Cloud.gov:   gorouter → nginx ($PORT) → Keycloak (localhost:8081)
Local:       browser (localhost:8443) → nginx (:8080) → Keycloak (:8081)
```

The `entrypoint.sh` process manager starts Keycloak, waits for health, starts nginx, then monitors both — if either dies, the container exits.

### Routing

Each Keycloak instance is deployed with two Cloud Foundry routes:

| Route Type | Route | Used By |
|------------|-------|---------|
| Internal | `keycloak.apps.internal:8080` | Django backend, Celery, Grafana (token exchange, user sync, JWKS) |
| Public | `<hostname>.app.cloud.gov` | User browsers (OIDC redirects, admin console) |

Django settings split these: `KEYCLOAK_SERVER_URL` (internal, server-to-server) and `KEYCLOAK_BROWSER_URL` (public, browser-facing).

### Network Policies

Cloud Foundry network policies are required for every app that needs to reach Keycloak over the internal route. The `deploy.sh` script creates these automatically per space:

- **Dev**: 6 policies (3 backends + 3 celery workers)
- **Staging**: 4 policies (2 backends + 2 celery workers)
- **Prod**: 3 policies (1 backend + 1 celery worker + Grafana)

### Database

Each Keycloak instance uses a dedicated Cloud.gov RDS PostgreSQL instance (separate from the TDP application database):

| Space | RDS Service | Purpose |
|-------|-------------|---------|
| `tanf-dev` | `tdp-keycloak-db-dev` | Keycloak realm data, users, sessions |
| `tanf-staging` | `tdp-keycloak-db-staging` | Same |
| `tanf-prod` | `tdp-keycloak-db-prod` | Same |

These are provisioned via Terraform and bound to the Keycloak app via the Cloud Foundry manifest.

---

## 4. Authentication Flows

### TDP Application Authentication

Two identity provider paths, both brokered through Keycloak:

**Login.gov (grantees):** Browser → `/login/dotgov` → Django checks canary flag → if Keycloak: redirects to Keycloak with `kc_idp_hint=login-gov` → Keycloak redirects to Login.gov → user authenticates → Login.gov returns code to Keycloak → Keycloak exchanges code using `private_key_jwt` (RS256-signed JWT assertion) → Keycloak issues its own token with TDP claims → Django `mozilla-django-oidc` callback validates token → `KeycloakOIDCBackend` looks up user by `login_gov_uuid` → Django session created. If legacy: the existing direct Login.gov OIDC flow is used.

**AMS (ACF staff):** Same flow, except `kc_idp_hint=ams`, AMS uses `client_secret_post` authentication, and user lookup is by `hhs_id`.

**Key enforcement:** Users with `@acf.hhs.gov` emails **must** use AMS. This is enforced in `KeycloakOIDCBackend.verify_claims()`.

### PLG / Grafana Authentication

The **production Keycloak instance** manages authentication for the PLG observability stack. Grafana uses the `tdp-grafana` Keycloak client. Login.gov is hidden from the Keycloak login page via `hideOnLogin: true` on the Login.gov IdP — this is safe because the TDP frontend bypasses the login page entirely using `kc_idp_hint=login-gov`. Grafana's `auth_url` includes `?prompt=login` to force re-authentication, ensuring that an existing Keycloak SSO session (e.g., from a prior Login.gov login) does not automatically grant Grafana access. The result is that Grafana's login page shows only the AMS identity provider button and the Keycloak local password form.

Users **must** belong to one of three Keycloak groups to access Grafana. Users not in any recognized group are denied login entirely (`role_attribute_strict = true` with no fallback role).

| Keycloak Group | Auth Path | Grafana Org | Grafana Role |
|----------------|-----------|-------------|--------------|
| `ofa-system-admin` | PIV auth via AMS through Keycloak | Admin (ID 1) | Admin |
| `developer` | Local Keycloak username/password | Admin (ID 1) | Admin |
| `digit-team` | PIV auth via AMS through Keycloak | DIGIT (ID 3) | Editor |
| *(any other / none)* | — | — | **Login denied** |
| Login.gov users | Cannot access (Login.gov hidden via `hideOnLogin`, SSO blocked by `prompt=login`) | — | N/A |

Grafana has two orgs: **Admin** (ID 1) for system administrators and developers, and **DIGIT** (ID 3) for the DIGIT operations team. Org assignment is controlled by `org_mapping` in Grafana's `[auth.generic_oauth]` config, which maps Keycloak group names to specific Grafana org IDs and roles. `auto_assign_org` is disabled so that org placement is handled entirely by the mapping — users not matching any rule are denied.

Developer accounts for Grafana are **local Keycloak accounts** in the prod instance — manually created in the admin console and assigned to the `developer` group. This is a practical exception to the "Django is source of truth" rule: these accounts avoid requiring developers to exist in the prod Django database.

Grafana currently runs behind the frontend nginx proxy at a subpath. Grafana **will be** moved to a public URL at `grafana.app.cloud.gov`, which will require updating the `tdp-grafana` client's redirect URIs, web origins, and post-logout redirect URI in the Keycloak realm configuration, as well as Grafana's `auth_url` and `signout_redirect_url` in `custom.ini`.

Role mapping uses a JMESPath expression on the `groups` token claim (no fallback — unrecognized users denied):
```
contains(groups[*], 'ofa-system-admin') && 'Admin'
  || contains(groups[*], 'developer') && 'Admin'
  || contains(groups[*], 'digit-team') && 'Editor'
```

Org mapping (in `custom.ini`):
```ini
org_attribute_path = groups
org_mapping = ofa-system-admin:1:Admin developer:1:Admin digit-team:3:Editor
```

---

## 5. Django Backend Integration

### OIDC Relying Party

The Django backend uses `mozilla-django-oidc` as a standard OIDC relying party library. This replaces ~500 lines of hand-rolled OIDC code (redirect generation, state/nonce management, token exchange, JWT validation) with library configuration plus a small authentication backend subclass.

**What the library handles:** Authorization redirect with state/nonce, code → token exchange, JWT signature verification via JWKS, session creation/renewal via `SessionRefresh` middleware, CSRF protection.

**What `KeycloakOIDCBackend` customizes:** User lookup by `login_gov_uuid`/`hhs_id` (not just email), ACF email domain enforcement, account deactivation/approval checks, `kc_idp_hint` passthrough to skip the Keycloak login page.

### User Sync Architecture

Django remains the authoritative source for user data. Changes are pushed to Keycloak in real time via Django signals:

| Trigger | Signal | Action |
|---------|--------|--------|
| User save | `post_save` on `User` | Sync attributes: `login_gov_uuid`, `hhs_id`, `stt_id`, `account_approval_status`, `region_ids` |
| Group change | `m2m_changed` on `User.groups.through` | Remove all KC groups, re-add current Django groups |

Controlled by `KEYCLOAK_SYNC_ENABLED`. Sync is idempotent and only operates on users that already exist in Keycloak (have logged in at least once). A bulk sync management command (`sync_users_to_keycloak`) and Celery beat task (every 6 hours) handle reconciliation.

In spaces with multiple backend pairs (dev has 3), all backends fire sync signals to the same Keycloak — this is safe because syncs set current state, not deltas.

### Auth Endpoints

The existing auth endpoints are extended to support both the legacy and Keycloak flows. The canary feature flag (`KEYCLOAK_AUTH_PERCENTAGE`) determines which flow handles each request — no separate URL paths are needed:

| Endpoint | Purpose |
|----------|---------|
| `GET /login/dotgov` | Redirect to Login.gov (legacy or via Keycloak, based on canary flag) |
| `GET /login/ams` | Redirect to AMS (legacy or via Keycloak, based on canary flag) |
| `GET /oidc/callback/` | OIDC authorization code callback (delegates to correct flow based on session marker) |
| `GET /auth_check` | Current user authentication status |
| `GET /logout/oidc` | Session termination (+ Keycloak logout if session was Keycloak-originated) |

---

## 6. Frontend Integration

The React frontend continues to use `REACT_APP_BACKEND_URL` for all API calls, including the 4 auth touchpoints. No frontend changes or separate auth URL configuration are required — the canary routing is handled entirely server-side:

| File | Endpoint |
|------|----------|
| `SplashPage.jsx` | `{REACT_APP_BACKEND_URL}/login/dotgov`, `/login/ams` |
| `signOut.js` | `{REACT_APP_BACKEND_URL}/logout/oidc` |
| `IdleTimer.jsx` | `{REACT_APP_BACKEND_URL}/logout/oidc` |
| `auth.js` | `{REACT_APP_BACKEND_URL}/auth_check` |

The frontend is unaware of which auth flow (legacy or Keycloak) is handling a given request. This eliminates the need for frontend redeployment during the migration — the rollout is controlled entirely via the backend `KEYCLOAK_AUTH_PERCENTAGE` environment variable.

---

## 7. Realm Configuration

### Approach

The Keycloak realm is defined declaratively in `realm-export.json` and imported on startup with `--import-realm`. Environment-specific values (Login.gov client ID, IdP endpoints, redirect URIs) use Keycloak's `${ENV_VAR}` substitution syntax, injected per space via Cloud Foundry environment variables.

Sensitive configuration that cannot be expressed in the realm export (Login.gov RSA private key, ACR values) and idempotent runtime fixes (IdP visibility, security headers) are applied post-startup by `configure-idps.sh`, which runs as a Cloud Foundry task after deployment.

### Clients

| Client | Type | Service Account | Purpose |
|--------|------|-----------------|---------|
| `tdp-django` | Confidential | Yes (`realm-management` roles) | Backend OIDC auth + Admin REST API access for user sync |
| `tdp-grafana` | Confidential | No | Grafana SSO (AMS + local password; Login.gov hidden via `hideOnLogin`) |

### Identity Provider Configuration

| IdP | Alias | Auth Method | Signing Key | First Login Flow |
|-----|-------|-------------|-------------|------------------|
| Login.gov | `login-gov` | `private_key_jwt` | RSA key uploaded via `configure-idps.sh` | `tdp-first-broker-login` (auto-create/auto-link by email) |
| AMS | `ams` | `client_secret_post` | N/A | `tdp-first-broker-login` (auto-create/auto-link by email) |

### Custom Token Claims

The `tdp-user-attributes` client scope includes protocol mappers for: `login_gov_uuid`, `hhs_id`, `stt_id`, `account_approval_status`, `region_ids`, `groups` (group membership), and `identity_provider` (session note). These claims are consumed by Django (for user identification) and Grafana (for role mapping).

---

## 8. Migration Strategy: Canary Cutover

### Approach

Both the legacy auth flow (direct Login.gov/AMS) and the Keycloak-brokered flow are deployed simultaneously behind the same endpoints. A server-side feature flag (`KEYCLOAK_AUTH_PERCENTAGE`) controls what percentage of new login requests are routed through Keycloak. This avoids versioned URL paths entirely — the frontend always hits the same auth endpoints, and the backend decides which flow to use.

### How It Works

The Django auth views (`/login/dotgov`, `/login/ams`) inspect the canary flag on each new login request:

1. Generate a random value per request
2. If the value falls within the canary percentage → route through Keycloak (via `mozilla-django-oidc`)
3. Otherwise → route through the legacy direct OIDC flow
4. A cookie or session attribute records which flow was used, so the callback handler knows how to process the response

Both flows return to the same callback URL. The callback inspects the session marker to delegate to the correct token exchange logic.

```
KEYCLOAK_AUTH_PERCENTAGE=0    → 100% legacy (default, no behavior change)
KEYCLOAK_AUTH_PERCENTAGE=10   → 10% Keycloak, 90% legacy
KEYCLOAK_AUTH_PERCENTAGE=50   → 50/50 split
KEYCLOAK_AUTH_PERCENTAGE=100  → 100% Keycloak (full cutover)
```

### Canary Rollout (Per Environment)

| Phase | `KEYCLOAK_AUTH_PERCENTAGE` | Action |
|-------|---------------------------|--------|
| 1. Deploy | `0` | Deploy backend with both flows wired up. No user impact — all traffic uses legacy. |
| 2. Smoke test | `0` (manual override) | Team members test Keycloak flow explicitly via an internal query parameter or admin toggle. |
| 3. Canary | `10` | 10% of new logins route through Keycloak. Monitor error rates, login latency, user reports. |
| 4. Expand | `50` | Increase to 50% after canary period shows no issues (minimum 48 hours per phase). |
| 5. Full cutover | `100` | All logins through Keycloak. Legacy flow still deployed but unused. |
| 6. Bake period | `100` | Run at 100% for at least 2 weeks before removing legacy code. |

**Rollback at any phase:** Set `KEYCLOAK_AUTH_PERCENTAGE=0` via `cf set-env` + `cf restage`. Takes effect on next login attempt. No frontend redeployment required. Existing sessions (both legacy and Keycloak-originated) are unaffected.

### Implementation Notes

- The percentage check happens only at login initiation — once a user is in a flow, they complete it regardless of flag changes
- The canary flag is a Django setting backed by an environment variable, changeable via `cf set-env` without a code deploy (Could also be managed by our FeatureFlag model)
- Logging should tag each login event with `auth_flow=legacy` or `auth_flow=keycloak` for monitoring the split. These are structured log fields (via Python's `logger.info("Login initiated", extra={"auth_flow": "keycloak"})`) that flow into Loki via Cloud Foundry's log stream. Grafana dashboards can then query by `auth_flow` label to compare error rates, latency, and success rates between the two flows during the canary period.
- The canary is per-request, not per-user — the same user may hit different flows on different logins (this is acceptable since both flows produce identical Django sessions)

### Legacy Code Removal

After running at `KEYCLOAK_AUTH_PERCENTAGE=100` in production for at least 2 weeks with no issues:

- Remove the canary routing logic and the `KEYCLOAK_AUTH_PERCENTAGE` flag
- Delete `users/api/login.py`, `login_redirect_oidc.py`, custom OIDC utility functions
- Remove `LOGIN_GOV_*` and `AMS_*` direct-integration settings from Django
- Remove `PlgAuthorizationCheck` and the nginx `auth_request` pattern for Grafana (replaced by Keycloak SSO)

---

## 9. Deployment and Configuration Management

### Deployment Flow

```
Build Docker image → Push to registry → deploy.sh → cf push (rolling)
  → Map internal + public routes → Create network policies
  → Run configure-idps.sh as CF task
```

A deploy script (`tdrs-backend/keycloak/deploy.sh`) handles the full lifecycle: manifest templating via `yq`, Docker image push, route mapping, network policy creation, and post-startup IdP configuration.

### Environment Variables

Keycloak configuration is driven by environment variables at three levels:

1. **Keycloak container env vars** — injected by the deploy script into the CF manifest (admin credentials, client secrets, Login.gov key, IdP endpoints)
2. **Realm `${ENV_VAR}` substitution** — Keycloak's native env var syntax in `realm-export.json` for per-environment values
3. **Django backend env vars** — `KEYCLOAK_SERVER_URL`, `KEYCLOAK_BROWSER_URL`, client credentials, `KEYCLOAK_SYNC_ENABLED`

All secrets are stored in Cloud Foundry environment variables or user-provided services. No secrets are committed to code.

### Configuration Lifecycle

| Change Type | Method |
|-------------|--------|
| Realm structure (new client, new group, flow change) | Update `realm-export.json`, rebuild image, deploy |
| Signing keys, ACR values, IdP visibility, security headers | Re-run `configure-idps.sh` as a CF task |
| One-off realm setting (token lifespan, etc.) | Admin console UI, then back-port to `realm-export.json` |
| Secret rotation | `cf set-env` + `cf restage` (see operations runbook) |

---

## 10. Security Considerations

### Credential Isolation

| Secret | Stored In | Accessed By |
|--------|-----------|-------------|
| Login.gov RSA private key | Keycloak CF env var (`LOGIN_GOV_JWT_KEY`) | Keycloak only (for `private_key_jwt` assertions + token signing) |
| AMS client secret | Keycloak CF env var (`AMS_CLIENT_SECRET`) | Keycloak only |
| `tdp-django` client secret | Keycloak + Django CF env vars | Keycloak (realm config) + Django (OIDC RP + Admin API) |
| `tdp-grafana` client secret | Keycloak + Grafana CF env vars | Keycloak (realm config) + Grafana (OAuth) |
| Keycloak admin credentials | Keycloak CF env var | `configure-idps.sh` task only |

Critically, the Login.gov RSA private key — previously stored in every Django backend instance — is now isolated to the Keycloak container. Django never sees it.

### Token and Session Security

| Setting | Value | Rationale |
|---------|-------|-----------|
| Access token lifespan | 5 minutes | Short-lived to limit exposure |
| SSO session idle timeout | 30 minutes | Matches existing TDP session policy |
| SSO session max lifespan | 12 hours | Absolute session limit |
| Token signing algorithm | RS256 | Industry standard, verifiable via JWKS |
| Brute force protection | 10 failures / 15-minute lockout | Prevents credential stuffing |

### Access Controls

- **Keycloak admin console** is accessible via the public route but protected by admin credentials. Consider restricting access via Cloud.gov route service or IP allowlist for production.
- **Keycloak Admin REST API** is accessible over the internal route only. The `tdp-django` service account has scoped roles: `view-users`, `manage-users`, `query-users`, `view-realm`, `query-groups`.
- **ACF email domain enforcement** — `@acf.hhs.gov` users who attempt Login.gov authentication are rejected. This is enforced in `KeycloakOIDCBackend.verify_claims()`.
- **Account approval** — deactivated or unapproved users are rejected at the Django OIDC backend level, regardless of valid Keycloak tokens.

### CSRF and Session Protections

- `mozilla-django-oidc` handles CSRF protection during the OIDC flow (state parameter validation)
- Django session cookies remain `httpOnly` and `Secure`
- `SessionRefresh` middleware handles token renewal without user interaction
- CSP headers are updated to allow the Keycloak domain

### Compliance

Keycloak runs on Cloud.gov infrastructure and falls within the existing Cloud.gov FedRAMP ATO boundary. No additional ATO activities are required for Keycloak itself. The Login.gov and AMS identity provider integrations maintain their existing compliance posture — Keycloak brokers the same OIDC flows with the same assurance levels.

---

## 11. Disaster Recovery

### Failure Modes

| Failure | Impact | Recovery |
|---------|--------|----------|
| Keycloak container crash | New logins fail; existing Django sessions continue working | Auto-restart via CF health check, or manual `cf restart keycloak` |
| Keycloak database loss | All Keycloak state lost (users, sessions, runtime config) | Restore from RDS backup, run `configure-idps.sh`, run bulk user sync |
| Keycloak completely lost | Same as database loss | Full redeploy via `deploy.sh` (realm import + IdP config + bulk sync) |
| Keycloak database corruption | Unpredictable auth behavior | Restore from RDS backup |

### Backup Strategy

- **Automatic**: Cloud.gov RDS instances have daily automated backups with configurable retention
- **On-demand**: `pg_dump` via `cf create-service-key` for ad-hoc backups
- **Realm export**: `kc.sh export` from within the container captures realm config (not user credentials/sessions)

### Recovery Procedure

Cloud.gov administratrors are available during normal business hours to restore daily backups.

Key point: Django sessions are independent of Keycloak. A Keycloak outage blocks new logins but does not terminate existing user sessions.

---

## 12. Monitoring

### Health Checks

| Check | Endpoint | Frequency |
|-------|----------|-----------|
| Readiness | `/health/ready` | CF health check (continuous) |
| Liveness | `/health/live` | CF health check (continuous) |
| OIDC discovery | `/realms/tdp/.well-known/openid-configuration` | On-demand verification |

### Prometheus Metrics

Keycloak exposes a `/metrics` endpoint when `KC_METRICS_ENABLED=true` is set. Prometheus scrapes this endpoint to collect native Keycloak metrics, which are then available in Grafana for dashboards and alerting.

**Setup requirements:**
- Set `KC_METRICS_ENABLED=true` in the Keycloak container environment
- Add a Prometheus scrape target for `keycloak.apps.internal:8080/metrics` (internal route — no public exposure needed)
- Create a Cloud Foundry network policy allowing Prometheus → Keycloak on the internal route

**Key metrics for auth flow monitoring:**

| Metric | What It Tells You |
|--------|-------------------|
| `keycloak_login_attempts_total` | Total login attempts by IdP, client, and outcome (success/failure) |
| `keycloak_failed_login_attempts_total` | Failed logins — spike indicates IdP issues or brute force |
| `keycloak_code_to_token_requests_total` | Token exchange attempts — failures indicate callback/token issues |
| `keycloak_refresh_tokens_total` | Token refresh activity |
| `keycloak_registrations_total` | New user registrations (first broker logins) |
| `keycloak_request_duration_seconds` | Request latency histograms — track login flow performance |
| `jvm_memory_used_bytes` | JVM heap usage — early warning for memory pressure |
| `jvm_gc_pause_seconds` | GC pauses — correlates with latency spikes |

**Canary monitoring:** During the canary rollout, the Keycloak metrics cover the Keycloak-brokered flow natively. For comparing against the legacy flow, the Django-side structured logging (`auth_flow=legacy` or `auth_flow=keycloak` tags in Loki) provides the other half of the picture. Once at `KEYCLOAK_AUTH_PERCENTAGE=100`, the Prometheus metrics become the single source of truth for auth observability.

### Additional Observability

- **Keycloak logs**: `cf logs keycloak` — includes authentication events, errors, startup diagnostics
- **Login events**: Keycloak admin console → Events tab (LOGIN, LOGOUT, LOGIN_ERROR, etc.)
- **Sync health**: Django/Celery logs for `KeycloakSyncClient` errors; Celery beat runs `reconcile_keycloak_users` every 6 hours
- **Resource usage**: `cf app keycloak` for memory/disk/CPU

### Alerting

| Alert | Condition | Severity |
|-------|-----------|----------|
| Auth failure spike | `rate(keycloak_failed_login_attempts_total[5m])` exceeds baseline by 3x | Warning |
| Token exchange failures | `rate(keycloak_code_to_token_requests_total{error!=""}[5m]) > 0` sustained for 5 min | Critical |
| Login latency degradation | `keycloak_request_duration_seconds` p95 > 5s for 10 min | Warning |
| High memory usage | `jvm_memory_used_bytes / jvm_memory_max_bytes > 0.85` for 10 min | Warning |
| Container restarts | CF event stream restart count > 2 in 30 min | Critical |
| Sync failures | Celery `KeycloakSyncClient` error rate > 0 sustained for 1 hour | Warning |

---

## 13. Keycloak Upgrade Strategy

Keycloak is pinned at version 26.0 in the Dockerfile (`quay.io/keycloak/keycloak:26.0`). Upgrades should follow this process:

1. Review the [Keycloak release notes](https://www.keycloak.org/docs/latest/release_notes/) for breaking changes
2. Update the `FROM` image tag in the Dockerfile
3. Test locally with `docker compose up --build keycloak` — verify admin console, Login.gov flow, AMS flow, Grafana SSO
4. Verify `realm-export.json` compatibility (Keycloak occasionally changes export format)
5. Deploy to dev space first, validate all auth flows
6. Roll through staging → production with validation at each stage

Keycloak stores its schema version in the database and runs automatic migrations on startup. Rolling back a Keycloak version after a database migration is not straightforward — take an RDS snapshot before upgrading production.

---

## 14. Risks and Dependencies

### External Dependencies

| Dependency | Risk | Mitigation |
|------------|------|------------|
| Login.gov sandbox/production | Outage blocks Login.gov authentication | Users see Login.gov error; AMS path unaffected. No TDP-side mitigation possible. |
| AMS (ACF SSO) | Outage blocks AMS authentication | Users see AMS error; Login.gov path unaffected. No TDP-side mitigation possible. |
| Cloud.gov RDS | Keycloak database unavailable | CF health check restarts Keycloak. If RDS is down, new logins fail but existing sessions work. |
| `mozilla-django-oidc` library | Breaking changes or vulnerabilities | Pinned at 4.0.1; update deliberately with testing |
| `python-keycloak` library | Breaking changes or API incompatibility | Pinned at 4.6.2; update deliberately with testing |

### Operational Risks

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Keycloak becomes single point of failure for all auth | Medium | High — new logins blocked | Existing Django sessions survive Keycloak outage. CF auto-restarts crashed containers. Scale to 2+ instances for availability. |
| Prod Keycloak outage blocks both TDP auth AND Grafana/PLG access | Low | High — lose monitoring access during incident | Grafana `[auth.basic]` can be re-enabled as emergency fallback. Document the procedure. |
| Secret rotation window causes auth failures | Medium | Medium — brief disruption | Coordinate Keycloak + backend restages. Document procedure in operations runbook. |
| `realm-export.json` import doesn't overwrite | Medium | Low — stale config | Use Admin REST API or console for updates. Back-port all changes to `realm-export.json`. |
| Login.gov JWT key rotation requires ~2 week lead time | Known | Medium — blocks rotation | Plan rotations proactively. Sandbox keys can be rotated immediately. |

### Open Questions

| Question | Status | Owner |
|----------|--------|-------|
| Should Keycloak admin console access be IP-restricted in production? | Open | ACF Tech |
| What is the Login.gov IAL2 (identity proofing) strategy if required in the future? | Open — Keycloak supports configurable ACR values per IdP, so IAL2 can be enabled by changing `LOGIN_GOV_ACR_VALUES` | Product |
| What is the Grafana public URL domain and timeline for the move from the current subpath? | Planned — Grafana will be moved to `grafana.app.cloud.gov`. Requires updating `tdp-grafana` client redirect URIs, web origins, and post-logout URI in realm config + Grafana `custom.ini` auth URLs. | Ops |

---

## 15. Production Readiness Checklist

- [ ] Keycloak deployed to all three spaces (dev, staging, prod)
- [ ] Login.gov sandbox flow validated end-to-end (dev + staging)
- [ ] Login.gov production flow validated (prod)
- [ ] AMS flow validated end-to-end (all environments)
- [ ] Django user sync verified (signal-based + bulk reconciliation)
- [ ] Grafana SSO via prod Keycloak verified (AMS login + developer password login)
- [ ] Login.gov users confirmed blocked from Grafana access
- [ ] Network policies created for all app pairs per space
- [ ] All secrets stored in CF environment variables (no secrets in code)
- [ ] Token lifespans and session timeouts match security policy
- [ ] Brute force protection enabled and tested
- [ ] ACF email domain enforcement tested (@acf.hhs.gov blocked from Login.gov)
- [ ] Backup/restore procedure tested (RDS backup → restore → configure-idps → bulk sync)
- [ ] `KC_METRICS_ENABLED=true` set and Prometheus scraping Keycloak `/metrics` endpoint
- [ ] Grafana dashboards configured for Keycloak auth metrics and JVM health
- [ ] Alerting rules deployed for auth failure spikes, token exchange errors, and memory pressure
- [ ] Monitoring in place (health checks, log review, sync health)
- [ ] Canary cutover tested per environment (0% → 10% → 50% → 100%) with rollback verification
- [ ] CSP headers updated to allow Keycloak domain
- [ ] Keycloak admin console accessible and functional
- [ ] `deploy.sh` tested with fresh deploy and redeployment
- [ ] Secret rotation procedures tested for all credential types

---
