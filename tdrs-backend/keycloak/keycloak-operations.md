# Keycloak Operations Runbook

Operational procedures for managing the TDP Keycloak deployment across Cloud.gov environments.

For architectural context, see [Authentication Architecture](auth-architecture.md). For local development setup and integration details, see [tdrs-backend/keycloak/README.md](../../tdrs-backend/keycloak/README.md).

## Table of Contents

- [Deployment](#deployment)
- [Restart and Recovery](#restart-and-recovery)
- [Secret Rotation](#secret-rotation)
- [Realm Configuration Updates](#realm-configuration-updates)
- [User Sync Operations](#user-sync-operations)
- [Adding New Clients](#adding-new-clients)
- [Managing Developer Grafana Accounts](#managing-developer-grafana-accounts)
- [Backup and Restore](#backup-and-restore)
- [Monitoring and Health Checks](#monitoring-and-health-checks)
- [Troubleshooting](#troubleshooting)

---

## Deployment

### Prerequisites

- Authenticated to Cloud.gov (`cf login`) and targeting the correct space
- Docker image built and pushed to the container registry
- `yq` installed locally (the deploy script uses it to inject env vars into the manifest)
- Required environment variables set in your shell (see below)

### Deploy Script

```bash
cd tdrs-backend/keycloak
./deploy.sh -e <environment> -d <rds_service> -p <public_hostname> -i <docker_image> -u <docker_username>
```

**Parameters:**

| Flag | Description | Example |
|------|-------------|---------|
| `-d` | Cloud Foundry RDS service name | `tdp-keycloak-db-dev` |
| `-p` | Public hostname (creates `<hostname>.app.cloud.gov`) | `tdp-keycloak-dev` |
| `-i` | Docker image URI | `ghcr.io/hhs/tdp-keycloak:latest` |
| `-u` | Docker registry username | `myuser` |

**Required environment variables:**

| Variable | Description |
|----------|-------------|
| `KEYCLOAK_ADMIN` | Admin console username |
| `KEYCLOAK_ADMIN_PASSWORD` | Admin console password |
| `KC_TDP_DJANGO_CLIENT_SECRET` | `tdp-django` client secret |
| `LOGIN_GOV_JWT_KEY` | Login.gov RSA private key (PEM or base64) |
| `CF_DOCKER_PASSWORD` | Docker registry password/token |

**Optional environment variables:**

| Variable | Description |
|----------|-------------|
| `KC_TDP_GRAFANA_CLIENT_SECRET` | `tdp-grafana` client secret |
| `KC_GRAFANA_REDIRECT_URI` | Grafana OAuth redirect URI |
| `KC_GRAFANA_WEB_ORIGIN` | Grafana web origin |
| `KC_GRAFANA_POST_LOGOUT_URI` | Grafana post-logout redirect URI |
| `LOGIN_GOV_ACR_VALUES` | Login.gov identity assurance level |

### What the Deploy Script Does

1. Copies `manifest.yml` → `manifest.tmp.yml` and injects environment-specific values via `yq`
2. Pushes the Docker image to Cloud Foundry with rolling strategy
3. Maps the **internal** route: `keycloak-<ENV>.apps.internal:8080` (server-to-server)
4. Maps the **public** route: `<hostname>.app.cloud.gov` (browser redirects, admin console)
5. Creates network policies so backend and celery apps can reach Keycloak on port 8080
6. Runs the `configure-idps.sh` script as a CF task to configure Login.gov signing key, ACR values, master realm security headers, and Grafana client IdP restriction

### Per-Space Deployment Examples

```bash
# Dev
./deploy.sh -e dev -d tdp-keycloak-db-dev -p tdp-keycloak-dev -i ghcr.io/hhs/tdp-keycloak:latest -u myuser

# Staging
./deploy.sh -e staging -d tdp-keycloak-db-staging -p tdp-keycloak-staging -i ghcr.io/hhs/tdp-keycloak:latest -u myuser

# Production
./deploy.sh -e prod -d tdp-keycloak-db-prod -p tdp-keycloak-prod -i ghcr.io/hhs/tdp-keycloak:latest -u myuser
```

---

## Restart and Recovery

### Restart Keycloak

```bash
cf target -o hhs-acf-ofa -s <space>
cf restart keycloak
```

This performs a full restart. Keycloak takes approximately 60-90 seconds to become healthy (the entrypoint script polls `/health/ready` up to 90 times at 2-second intervals before starting the nginx proxy).

**Impact:** Active sessions are preserved in the database. Users with active Django sessions are unaffected. Users mid-authentication (in the OIDC redirect flow) will need to re-initiate login.

### Rolling Restart (Zero Downtime)

If the app has multiple instances:

```bash
cf restart keycloak --strategy rolling
```

### Recover from Crash

If Keycloak exits unexpectedly (either the Keycloak or nginx process within the container):

1. Check recent logs:
   ```bash
   cf logs keycloak --recent
   ```

2. Look for common causes:
   - **Memory exhaustion**: Check `cf app keycloak` for memory usage. Default is 768M.
   - **Database connection failure**: The RDS instance may be down or credentials may have changed.
   - **Startup timeout**: Keycloak may not reach healthy state within the 90-attempt window.

3. If the issue is transient, restart:
   ```bash
   cf restart keycloak
   ```

4. If restarting doesn't help, redeploy:
   ```bash
   cd tdrs-backend/keycloak
   ./deploy.sh -e <environment> -d <rds_service> -p <hostname> -i <image> -u <username>
   ```

### Scale Keycloak

```bash
# Increase memory (if experiencing OOM)
cf scale keycloak -m 1G
```

---

## Secret Rotation

### Rotate the Keycloak Admin Password

1. Set the new password in your shell:
   ```bash
   export KEYCLOAK_ADMIN_PASSWORD="new-secure-password"
   ```

2. Update the Cloud Foundry environment:
   ```bash
   cf set-env keycloak KEYCLOAK_ADMIN_PASSWORD "$KEYCLOAK_ADMIN_PASSWORD"
   ```

3. Restage the app:
   ```bash
   cf restage keycloak
   ```

Note: The admin password is only used during Keycloak startup for initial admin user creation and by `configure-idps.sh`. Existing admin sessions use Keycloak-managed credentials in the database.

### Rotate the `tdp-django` Client Secret

This secret is used by both the Django OIDC flow and the Admin REST API sync layer.

1. Generate a new secret (e.g., `openssl rand -hex 32`)

2. Update the Keycloak app:
   ```bash
   cf set-env keycloak KC_TDP_DJANGO_CLIENT_SECRET "<new-secret>"
   cf restage keycloak
   ```

3. Update **every** backend and celery app in the space:
   ```bash
   # Example for dev space
   for app in tdp-backend-raft tdp-backend-qasp tdp-backend-a11y \
              tdp-celery-raft tdp-celery-qasp tdp-celery-a11y; do
       cf set-env $app KEYCLOAK_ADMIN_CLIENT_SECRET "<new-secret>"
       cf set-env $app KEYCLOAK_DJANGO_CLIENT_SECRET "<new-secret>"
   done
   ```

4. Restage all affected apps:
   ```bash
   for app in tdp-backend-raft tdp-backend-qasp tdp-backend-a11y \
              tdp-celery-raft tdp-celery-qasp tdp-celery-a11y; do
       cf restage $app
   done
   ```

**Impact:** During the window between restaging Keycloak and restaging the backends, auth and sync will fail. Coordinate to minimize this window.

### Rotate the `tdp-grafana` Client Secret

1. Generate a new secret

2. Update the Keycloak app:
   ```bash
   cf set-env keycloak KC_TDP_GRAFANA_CLIENT_SECRET "<new-secret>"
   cf restage keycloak
   ```

3. Update the Grafana app:
   ```bash
   cf set-env grafana GF_AUTH_GENERIC_OAUTH_CLIENT_SECRET "<new-secret>"
   cf restage grafana
   ```

### Rotate the Login.gov JWT Key

The Login.gov private key (`LOGIN_GOV_JWT_KEY`) is used for `private_key_jwt` authentication and Keycloak token signing. See [Secret Key Rotation](secret-key-rotation-steps.md) for key generation procedures.

1. Generate a new RSA key pair (see linked doc)

2. Upload the new public key to Login.gov (sandbox or production dashboard)

3. Update Keycloak with the new private key:
   ```bash
   cf set-env keycloak LOGIN_GOV_JWT_KEY "<base64-encoded-private-key>"
   cf restage keycloak
   ```

4. Re-run the IdP configuration task to update the signing key component:
   ```bash
   cf run-task keycloak \
       --command "export SKIP_KEYCLOAK_WAIT=true KEYCLOAK_URL=http://keycloak-<ENV>.apps.internal:8080 KEYCLOAK_MANAGEMENT_URL=http://keycloak-<ENV>.apps.internal:9000 && /opt/keycloak/configure-idps.sh" \
       --name "configure-idps"
   ```

5. Monitor the task:
   ```bash
   cf tasks keycloak
   cf logs keycloak --recent
   ```

**Impact:** Login.gov production key changes require a change request to Login.gov support (~2 weeks). Sandbox keys can be updated immediately.

### Rotate AMS Client Credentials

AMS credentials are managed by ACF OCIO Ops. Submit a service request (see [Secret Key Rotation](secret-key-rotation-steps.md) for the process).

After receiving new credentials:

```bash
cf set-env keycloak AMS_CLIENT_ID "<new-client-id>"
cf set-env keycloak AMS_CLIENT_SECRET "<new-secret>"
cf restage keycloak
```

---

## Realm Configuration Updates

### Updating the Realm Export

The realm is defined in `tdrs-backend/keycloak/realm-export.json`. Changes to clients, groups, IdP mappers, authentication flows, or token settings should be made in this file.

1. Make changes to `realm-export.json`
2. Test locally:
   ```bash
   cd tdrs-backend
   docker compose down keycloak keycloak-pg
   docker compose up --build keycloak
   ```
3. Verify changes in the admin console at http://localhost:8443/admin
4. Rebuild and push the Docker image
5. Deploy with `deploy.sh`

**Important:** Keycloak imports the realm on startup with `--import-realm`. This does **not** overwrite existing realm data — it only creates missing resources. To force updates, you need to either:
- Delete the realm first in the admin console (destructive, loses all user data)
- Use the Admin REST API to update specific resources
- Modify realm settings via the admin console manually

### Modifying Realm Settings via Admin Console

For one-off changes that don't warrant a full redeployment:

1. Access the admin console at `https://<hostname>.app.cloud.gov/admin`
2. Log in with admin credentials
3. Select the `tdp` realm
4. Make changes through the UI

**Remember to back-port changes to `realm-export.json`** so they persist across redeployments.

### Running the IdP Configuration Script

The `configure-idps.sh` script handles post-startup configuration that can't be expressed in `realm-export.json` (signing keys, ACR values, client IdP restrictions):

```bash
cf run-task keycloak \
    --command "export SKIP_KEYCLOAK_WAIT=true KEYCLOAK_URL=http://keycloak-<ENV>.apps.internal:8080 KEYCLOAK_MANAGEMENT_URL=http://keycloak-<ENV>.apps.internal:9000 && /opt/keycloak/configure-idps.sh" \
    --name "configure-idps"
```

The script is idempotent — safe to run multiple times.

### Updating Token Lifespans

Current settings in `realm-export.json`:

| Setting | Value |
|---------|-------|
| Access token lifespan | 300 seconds (5 minutes) |
| SSO session idle timeout | 1800 seconds (30 minutes) |
| SSO session max lifespan | 43200 seconds (12 hours) |

To change, update either:
- `realm-export.json` and redeploy, **or**
- Admin console → Realm settings → Sessions/Tokens tabs

---

## User Sync Operations

### How Sync Works

Django is the source of truth. When `KEYCLOAK_SYNC_ENABLED=true`:

- **On user save** (`post_save` signal): Syncs user attributes (login_gov_uuid, hhs_id, stt_id, account_approval_status, region_ids) to the matching Keycloak user
- **On group change** (`m2m_changed` signal): Syncs Django group memberships to Keycloak groups

Sync only operates on users that already exist in Keycloak (i.e., users who have logged in via Keycloak at least once). Users who haven't logged in yet are skipped.

### Bulk Sync All Users

Run the management command from within the backend app:

```bash
# Cloud.gov
cf ssh tdp-backend-<name>
/tmp/lifecycle/shell
cd /home/vcap/app
./manage.py sync_users_to_keycloak

# Local
docker compose exec web python manage.py sync_users_to_keycloak
```

Output: `Sync complete: N synced, N skipped (not in Keycloak), N failed`

Use bulk sync:
- After initial Keycloak deployment (once users have started logging in)
- After restoring a Keycloak database backup
- As a periodic reconciliation (also runs via Celery beat)
- When Django group definitions or user attributes have been modified in bulk

### Disabling Sync

Set `KEYCLOAK_SYNC_ENABLED=false` on the backend/celery apps:

```bash
cf set-env tdp-backend-<name> KEYCLOAK_SYNC_ENABLED false
cf restage tdp-backend-<name>
```

When disabled, all signal handlers become no-ops. No sync calls are made to Keycloak.

### Multi-Backend Sync

In spaces with multiple backend pairs (e.g., dev has raft, qasp, a11y), all backends share the same RDS and fire sync signals to the same Keycloak instance. This is safe — syncs are idempotent (they set current state, not deltas). Redundant calls from multiple backends result in extra API calls but no conflicts or data corruption.

---

## Adding New Clients

To add a new application that authenticates via Keycloak:

1. **Define the client in `realm-export.json`:**
   ```json
   {
     "clientId": "my-new-app",
     "enabled": true,
     "protocol": "openid-connect",
     "publicClient": false,
     "secret": "${MY_NEW_APP_CLIENT_SECRET}",
     "redirectUris": ["https://my-app.example.com/*"],
     "webOrigins": ["https://my-app.example.com"],
     "defaultClientScopes": ["openid", "email", "profile", "tdp-user-attributes"]
   }
   ```

2. **Add the secret env var to `deploy.sh`** in the `OPTIONAL_ENV_VARS` array

3. **Test locally** by adding the client secret to `docker-compose.yml` Keycloak environment

4. **Deploy** with the new secret set:
   ```bash
   export MY_NEW_APP_CLIENT_SECRET="$(openssl rand -hex 32)"
   ./deploy.sh ...
   ```

5. **If the new app needs a network policy:**
   ```bash
   cf add-network-policy my-new-app keycloak --protocol tcp --port 8080
   ```

6. **If the client should only allow specific IdPs** (like `tdp-grafana` only allows AMS), add the restriction in `configure-idps.sh` following the `configure_grafana_client_idps` pattern.

---

## Managing Developer Grafana Accounts

Developer accounts for Grafana are **local Keycloak accounts** in the prod Keycloak instance. These are a practical exception to the "Django is source of truth" rule — they avoid requiring developers to exist in the prod Django database.

### Create a Developer Account

1. Access the prod Keycloak admin console: `https://<prod-hostname>.app.cloud.gov/admin`
2. Select the `tdp` realm
3. Go to **Users** → **Add user**
4. Fill in:
   - **Username**: developer's email or identifier
   - **Email**: developer's email
   - **Email verified**: On
5. Click **Create**
6. Go to the **Credentials** tab → **Set password**
   - Set a temporary password
   - Toggle **Temporary** to On (forces password change on first login)
7. Go to the **Groups** tab → **Join Group** → select `developer`

The developer can now log into Grafana at the Keycloak login page using username/password. The `developer` group maps to Grafana `Admin` role.

### Remove a Developer Account

1. Access the prod Keycloak admin console
2. Select the `tdp` realm → **Users**
3. Search for the user
4. Click the user → **Delete** (or disable by toggling **Enabled** off)

### List Current Developer Accounts

In the admin console: **Groups** → click `developer` → view members.

---

## Backup and Restore

### Database Backup

Keycloak's state (users, sessions, realm config applied at runtime) lives in the bound RDS instance. Cloud.gov RDS instances have automatic daily backups with a retention period.

To create an on-demand backup, review the process in `tdrs-backend/db-upgrade/cloud-foundry-db-upgrade.md`.

### Realm Export (Configuration Only)

Export the current realm configuration from a running instance:

```bash
cf ssh keycloak
/tmp/lifecycle/shell
/opt/keycloak/bin/kc.sh export --dir /tmp/export --realm tdp
cat /tmp/export/tdp-realm.json
```

Note: This exports realm configuration but **not** user credentials or sessions.

### Restore from Backup

1. Restore the RDS instance from a Cloud.gov backup (contact Cloud.gov support)
2. Restart Keycloak:
   ```bash
   cf restart keycloak
   ```
3. Run the IdP configuration task (signing keys are stored in the database, not the Docker image):
   ```bash
   cf run-task keycloak \
       --command "export SKIP_KEYCLOAK_WAIT=true KEYCLOAK_URL=http://keycloak-<ENV>.apps.internal:8080 KEYCLOAK_MANAGEMENT_URL=http://keycloak-<ENV>.apps.internal:9000 && /opt/keycloak/configure-idps.sh" \
       --name "configure-idps"
   ```
4. Run a bulk user sync to reconcile Django and Keycloak state:
   ```bash
   cf ssh tdp-backend-<name>
   /tmp/lifecycle/shell
   cd /home/vcap/app
   ./manage.py sync_users_to_keycloak
   ```

### Full Recovery (New Keycloak Instance)

If the Keycloak instance is completely lost:

1. Ensure the RDS instance exists (create a new one via Terraform if needed)
2. Run the full deploy:
   ```bash
   ./deploy.sh -e <environment> -d <rds_service> -p <hostname> -i <image> -u <username>
   ```
3. The realm import (`--import-realm`) creates the realm, clients, groups, and IdP configuration
4. The `configure-idps.sh` task configures the Login.gov signing key and other post-startup items
5. Users will need to log in again (Keycloak sessions are gone)
6. Run bulk sync to push current Django state to Keycloak

---

## Monitoring and Health Checks

### Health Endpoints

| Endpoint | Route | Description |
|----------|-------|-------------|
| `/health/ready` | Internal or public | Keycloak readiness (database connected, realm loaded) |
| `/health/live` | Internal or public | Keycloak liveness (process running) |

```bash
# Via public route
curl -sf https://<hostname>.app.cloud.gov/health/ready

# Via internal route (from within a CF app)
curl -sf http://keycloak-<ENV>.apps.internal:8080/health/ready
```

### Checking Keycloak Status

```bash
# App status
cf app keycloak

# Recent logs
cf logs keycloak --recent

# Streaming logs
cf logs keycloak

# Running tasks (e.g., configure-idps)
cf tasks keycloak
```

### Key Metrics to Watch

- **Memory usage**: `cf app keycloak` — default allocation is 768M
- **Response times**: Check Keycloak logs for slow token exchanges
- **Failed authentications**: Keycloak admin console → Events → Login events (filter by error)
- **Sync failures**: Check backend/celery logs for `KeycloakSyncClient` errors
- **Brute force lockouts**: Admin console → Events → filter for `LOGIN_ERROR` events. Keycloak locks accounts after 10 failures for 15 minutes.

### OIDC Discovery Endpoint

Verify the realm is properly configured:

```bash
curl -sf https://<hostname>.app.cloud.gov/realms/tdp/.well-known/openid-configuration | jq .
```

This should return all OIDC endpoints (authorization, token, userinfo, JWKS, end_session, etc.).

---

## Troubleshooting

### Keycloak Won't Start

**Symptoms:** App crashes on startup, health check never passes.

1. Check logs:
   ```bash
   cf logs keycloak --recent
   ```

2. Common causes:
   - **Database connection failure**: Verify the RDS service is bound (`cf services`) and credentials are correct. The manifest extracts `VCAP_SERVICES` JSON at startup.
   - **Out of memory**: Increase memory with `cf scale keycloak -m 1G`
   - **Invalid LOGIN_GOV_JWT_KEY**: Keycloak starts regardless, but `configure-idps.sh` will fail. Check if the key is properly base64-encoded or in PEM format.
   - **Port conflict**: The entrypoint uses port 8081 for Keycloak and `$PORT` (assigned by Cloud Foundry) for nginx. These should not conflict.

### Login Redirects Fail

**Symptoms:** User clicks login button but gets an error, redirect loop, or blank page.

1. **Verify `KEYCLOAK_BROWSER_URL`** on the backend matches the public Keycloak route:
   ```bash
   cf env tdp-backend-<name> | grep KEYCLOAK_BROWSER_URL
   ```
   This must be the URL the user's browser can reach (not the internal route).

2. **Verify redirect URIs** in the `tdp-django` client match the frontend URLs:
   - Admin console → Clients → `tdp-django` → Valid redirect URIs
   - Must include the frontend domain with `/*` suffix

3. **Verify the IdP is enabled**: Admin console → Identity providers → check `login-gov` or `ams` is enabled

4. **Check CORS**: If you see CORS errors in the browser console, verify `Web Origins` on the `tdp-django` client includes the frontend domain.

### User Sync Fails

**Symptoms:** Django group changes don't appear in Keycloak, bulk sync reports failures.

1. **Verify sync is enabled:**
   ```bash
   cf env tdp-backend-<name> | grep KEYCLOAK_SYNC_ENABLED
   ```

2. **Verify the user exists in Keycloak:** Sync only works for users who have logged in via Keycloak at least once. Check admin console → Users → search by email.

3. **Verify `tdp-django` service account roles:** Admin console → Clients → `tdp-django` → Service account roles. Must have `realm-management` roles: `view-users`, `manage-users`, `query-users`, `view-realm`, `query-groups`.

4. **Check backend logs for errors:**
   ```bash
   cf logs tdp-backend-<name> --recent | grep -i keycloak
   ```

### Grafana SSO Issues

**Symptoms:** Grafana login fails, shows "Login provider denied" or wrong role.

1. **Verify Grafana OAuth client secret matches:**
   ```bash
   cf env grafana | grep GF_AUTH_GENERIC_OAUTH_CLIENT_SECRET
   ```

2. **Verify network policy:**
   ```bash
   cf network-policies --source grafana
   ```
   Must show a policy allowing TCP port 8080 to keycloak.

3. **Check Grafana's token URL**: In `custom.ini`, `token_url` should use the **internal** route (`http://keycloak-<ENV>.apps.internal:8080/...`), while `auth_url` should use the **public** route.

4. **Verify role mapping**: If a user gets the wrong Grafana role, check their Keycloak group membership (admin console → Users → select user → Groups). The JMESPath expression maps:
   - `ofa-system-admin` or `developer` → Admin
   - `digit-team` → Editor
   - All others → Viewer

### `NoReverseMatch` Errors on `/v2/` Endpoints

Verify that `OIDC_EXEMPT_URLS` entries in Django settings start with `/`:
```python
OIDC_EXEMPT_URLS = ["/v1/", "/admin/", "/prometheus/", "/plg_auth_check/"]
```

The `/v2/` routes are **not** exempt — they are handled by `mozilla-django-oidc`.

### Admin Console Won't Load (X-Frame-Options)

The nginx proxy in the Keycloak container strips `X-Frame-Options: DENY` and replaces it with `SAMEORIGIN`. If the admin console still fails to load:

1. Verify the response header:
   ```bash
   curl -sI https://<hostname>.app.cloud.gov/ | grep -i x-frame
   ```
   Should show `X-Frame-Options: SAMEORIGIN`.

2. If it shows `DENY`, the nginx proxy may not be running. Check container logs for nginx startup errors.

3. The `configure-idps.sh` script also sets `SAMEORIGIN` on the master realm's `browserSecurityHeaders` as a belt-and-suspenders fix.

### Sessions Lost After Restart

Keycloak stores sessions in its database by default. Sessions should survive restarts. If sessions are lost:

1. Verify the same RDS instance is bound after restart:
   ```bash
   cf services
   cf env keycloak | grep VCAP_SERVICES
   ```

2. Check if the RDS instance was replaced or restored from a backup (this would lose sessions created after the backup point).
