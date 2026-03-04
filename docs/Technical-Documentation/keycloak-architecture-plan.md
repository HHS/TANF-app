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
│          │◄──┤ (frontend│◄──┤  /v2/   │◄──┤  OIDC  │   ├───────────┤
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

**Login.gov (grantees):** Browser → `/v2/login/dotgov` → Django redirects to Keycloak with `kc_idp_hint=login-gov` → Keycloak redirects to Login.gov → user authenticates → Login.gov returns code to Keycloak → Keycloak exchanges code using `private_key_jwt` (RS256-signed JWT assertion) → Keycloak issues its own token with TDP claims → Django `mozilla-django-oidc` callback validates token → `KeycloakOIDCBackend` looks up user by `login_gov_uuid` → Django session created

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

### v2 API Endpoints

Auth endpoints live under `/v2/`, coexisting with legacy `/v1/` routes during transition:

| Endpoint | Purpose |
|----------|---------|
| `GET /v2/login/dotgov` | Redirect to Keycloak → Login.gov |
| `GET /v2/login/ams` | Redirect to Keycloak → AMS |
| `GET /v2/oidc/callback/` | OIDC authorization code callback |
| `GET /v2/auth_check` | Current user authentication status |
| `GET /v2/logout/oidc` | Session termination + Keycloak logout |

---

## 6. Frontend Integration

The React frontend uses a dedicated `REACT_APP_AUTH_URL` environment variable for the 4 auth touchpoints. All other API calls continue using `REACT_APP_BACKEND_URL`:

| File | Endpoint |
|------|----------|
| `SplashPage.jsx` | `{REACT_APP_AUTH_URL}/login/dotgov`, `/login/ams` |
| `signOut.js` | `{REACT_APP_AUTH_URL}/logout/oidc` |
| `IdleTimer.jsx` | `{REACT_APP_AUTH_URL}/logout/oidc` |
| `auth.js` | `{REACT_APP_AUTH_URL}/auth_check` |

`REACT_APP_AUTH_URL` defaults to `REACT_APP_BACKEND_URL` if not set, making the transition zero-risk: deploy the backend with `/v2/` routes, then flip `REACT_APP_AUTH_URL` per environment to activate the Keycloak flow.

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

## 8. Migration Strategy: v1 → v2

### Parallel Running

The `/v1/` (direct Login.gov/AMS) and `/v2/` (Keycloak-brokered) auth routes coexist. The frontend controls which path is active via `REACT_APP_AUTH_URL`:

| Phase | `REACT_APP_AUTH_URL` | Auth Path |
|-------|---------------------|-----------|
| Pre-cutover | `{domain}/v1` (default) | Direct Login.gov/AMS (legacy) |
| Cutover | `{domain}/v2` | Keycloak-brokered |
| Rollback | `{domain}/v1` | Direct Login.gov/AMS (legacy) |

### Cutover Process (Per Environment)

1. Deploy backend with `/v2/` routes active (no user impact — `/v1/` still works)
2. Set `REACT_APP_AUTH_URL` to the `/v2` URL in `deploy-frontend.sh`
3. Redeploy frontend — auth now flows through Keycloak
4. Monitor for issues
5. **Rollback:** Set `REACT_APP_AUTH_URL` back to `/v1`, redeploy frontend

### v1 Deprecation

After the Keycloak-brokered flow (v2) is stable in production for at least 2 weeks, the legacy v1 auth code will be removed:

- Delete `users/api/login.py`, `login_redirect_oidc.py`, custom OIDC utility functions
- Remove `/v1/` auth URL patterns (non-auth `/v1/` API routes remain)
- Remove `LOGIN_GOV_*` and `AMS_*` direct-integration settings from Django
- Remove `jwcrypto` dependency (if no longer needed)
- Consolidate `REACT_APP_AUTH_URL` back into `REACT_APP_BACKEND_URL`
- Remove `PlgAuthorizationCheck` and the nginx `auth_request` pattern for Grafana (replaced by Keycloak SSO)

This is a point of no return — a tagged release of the pre-cleanup codebase should be created before executing.

---

## 9. Deployment and Configuration Management

### Deployment Flow

```
Build Docker image → Push to registry → deploy.sh → cf push (rolling)
  → Map internal + public routes → Create network policies
  → Run configure-idps.sh as CF task
```

The deploy script (`tdrs-backend/keycloak/deploy.sh`) handles the full lifecycle: manifest templating via `yq`, Docker image push, route mapping, network policy creation, and post-startup IdP configuration.

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

See the [Keycloak Operations Runbook — Backup and Restore](../../tdrs-backend/keycloak/keycloak-operations.md#backup-and-restore) for step-by-step procedures.

Key point: Django sessions are independent of Keycloak. A Keycloak outage blocks new logins but does not terminate existing user sessions.

---

## 12. Monitoring

### Health Checks

| Check | Endpoint | Frequency |
|-------|----------|-----------|
| Readiness | `/health/ready` | CF health check (continuous) |
| Liveness | `/health/live` | CF health check (continuous) |
| OIDC discovery | `/realms/tdp/.well-known/openid-configuration` | On-demand verification |

### Observability

- **Keycloak logs**: `cf logs keycloak` — includes authentication events, errors, startup diagnostics
- **Login events**: Keycloak admin console → Events tab (LOGIN, LOGOUT, LOGIN_ERROR, etc.)
- **Sync health**: Django/Celery logs for `KeycloakSyncClient` errors; Celery beat runs `reconcile_keycloak_users` every 6 hours
- **Resource usage**: `cf app keycloak` for memory/disk/CPU

### Alerting Considerations

- Monitor Keycloak container restarts (CF event stream)
- Alert on sustained authentication failures (Keycloak events or Django error logs)
- Monitor Keycloak memory usage — default 768M allocation may need tuning under load
- Monitor sync failure rates in Celery worker logs

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
| Should Keycloak admin console access be IP-restricted in production? | Open | Ops/Security |
| What is the Login.gov IAL2 (identity proofing) strategy if required in the future? | Open — Keycloak supports configurable ACR values per IdP, so IAL2 can be enabled by changing `LOGIN_GOV_ACR_VALUES` | Product |
| Should Keycloak metrics be scraped by Prometheus for PLG dashboards? | Open — Keycloak exposes metrics at `/metrics` when `KC_METRICS_ENABLED=true` | Ops |
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
- [ ] Operations runbook reviewed by ops team
- [ ] Monitoring in place (health checks, log review, sync health)
- [ ] v1 → v2 cutover tested per environment with rollback verification
- [ ] CSP headers updated to allow Keycloak domain
- [ ] Keycloak admin console accessible and functional
- [ ] `deploy.sh` tested with fresh deploy and redeployment
- [ ] Secret rotation procedures tested for all credential types

---
