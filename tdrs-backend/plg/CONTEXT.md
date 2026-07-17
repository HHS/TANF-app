# PLG Context

This context covers PLG configuration under `tdrs-backend/plg/`.

## Boundaries

- Grafana, Loki, Mimir, Prometheus, Tempo, Alloy, Alertmanager, and related deployment configuration live here.
- Grafana authentication is brokered through Keycloak OIDC using the `tdp-grafana` client.
- Monitoring changes should preserve least-privilege access and avoid exposing sensitive data.
- Operational dashboards and alerts should reflect production support needs, not only local development convenience.
- PLG auth changes are security-sensitive and usually require reading the Keycloak context too.

## Important Paths

- `grafana/custom.ini`: deployed Grafana configuration, including Keycloak generic OAuth.
- `grafana/custom.local.ini`: local Grafana configuration, including local Keycloak generic OAuth.
- `grafana/dashboards/keycloak_metrics.json`: Keycloak authentication and JVM metrics dashboard.
- `grafana/dashboards/keycloak_capacity.json`: Keycloak capacity dashboard.
- `prometheus/prometheus.yml`: deployed Prometheus scrape configuration.
- `prometheus/prometheus.local.yml`: local Prometheus scrape configuration.
- `deploy.sh`: PLG deployment orchestration.

## Grafana SSO

- Grafana uses `[auth.generic_oauth]` with `name = Keycloak` and `client_id = tdp-grafana`.
- Keycloak is the OIDC broker for Grafana SSO; Login.gov and AMS are available through Keycloak, and local developer accounts can exist directly in Keycloak.
- Django remains the source of truth for TDP user information. Grafana access depends on Keycloak token claims that are populated from Django-to-Keycloak sync.
- Users must have `account_approval_status == 'Approved'` and a required Keycloak group claim, otherwise Grafana login is denied.
- `role_attribute_strict = true`, so users without a matching role expression do not receive fallback access.
- Deployed Grafana disables basic auth; local Grafana keeps basic auth enabled as a debugging fallback.

Grafana role and org mapping is configured in `grafana/custom.ini` and `grafana/custom.local.ini`:

| Keycloak Group | Grafana Org | Grafana Role |
| --- | --- | --- |
| `ofa-system-admin` | Admin | Admin |
| `developer` | Admin | Admin |
| `digit-team` | DIGIT | Editor |

Deployed configuration maps `digit-team` to org ID 3. Local configuration maps `digit-team` to org ID 2.

## Keycloak URL Split

- Grafana browser redirects use Keycloak's public/browser-facing URL for `auth_url` and logout.
- Grafana token and userinfo calls use Keycloak's internal/server-to-server URL for `token_url` and `api_url`.
- In cloud.gov, Grafana needs a network policy allowing it to reach Keycloak on the internal route.

## Read With

- Root `CONTEXT.md`
- `CONTEXT-MAP.md`
- `tdrs-backend/keycloak/CONTEXT.md`
- PLG README and component-specific files in this directory
- Relevant observability and deployment docs under `docs/Technical-Documentation/`
- `docs/Technical-Documentation/auth-architecture.md`
- `docs/Technical-Documentation/Architecture-Decision-Record/005-application-authentication.md`
