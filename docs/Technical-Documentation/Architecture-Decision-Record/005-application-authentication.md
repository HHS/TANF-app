# 5. Application Authentication

Date: 2020-08-04 (_Updated 2022-09-01, 2026-04-09_)

## Status

Accepted.

## Context

TDP application requires strong multi-factor authentication (MFA) for all users, and Personal Identity Verification (PIV) authentication must be used as the 2nd factor for all internal ACF staff. To date, TDP has been leveraging Login.gov authentication for all users because (1) it requires MFA for all user accounts by default and accepts PIV for authentication, (2) it has a FedRAMP ATO on file, and (3) HHS already has an IAA for this service.

Since then, ACF OCIO (TDP's Authorizing Official) has recommended use of HHS-vetted authentication services for both internal ACF and external (i.e.non-ACF) users.

We initiated the integratation with NextGen XMS for external users in Spring 2022 because of the estimated cost savings, and because the refactoring was expected to be minimal (since NextGen leverages login.gov as one of its credential service providers). However, the time/effort to integrate with this newer service led to significant roadmap delays.

### Update — April 2026: Keycloak OIDC Broker

The direct integration pattern — where the Django backend implemented custom OIDC flows for each identity provider individually — created several challenges:

- **Tight coupling to IdP protocols.** ~500 lines of hand-rolled OIDC code (redirect generation, state/nonce management, token exchange, JWT validation) had to be maintained for each provider. Adding or changing an IdP required significant Django code changes.
- **Limited client support.** The browser-based auth flow (interactive redirects, CSRF-protected callbacks, session cookies) made it difficult for external tools (Postman, CLI tools, CI/CD) to authenticate against the Django API.
- **Secret distribution.** The Login.gov RSA private key was stored in every Django backend instance.
- **No centralized auth observability.** Authentication metrics and events were scattered across Django application logs with no unified view.

These issues — particularly the tight coupling concern raised in the original Risks section regarding the NextGen XMS integration — motivated the decision to introduce an OIDC broker layer.

## Decision

We will use [ACF AMS](https://hhsgov.sharepoint.com/:w:/s/TANFDataPortalOFA/EYsh4YvAE0hLrr_rVhYKsGABgeA_yuHzt-v7TGbxaBF2jA?e=zriBjY) authentication service for ACF users and [Login.gov](login.gov) authentication service for all non-ACF users.

### Update — April 2026

We will introduce [Keycloak](https://www.keycloak.org/) as a centralized OIDC broker between the TDP Django backend and the upstream identity providers (Login.gov and AMS). The identity providers themselves are unchanged — Keycloak brokers the same OIDC flows with the same assurance levels.

Under this architecture:

- The Django backend becomes a standard OIDC relying party using the `mozilla-django-oidc` library, pointed at Keycloak as its single identity provider.
- Keycloak handles all upstream IdP protocol complexity (Login.gov `private_key_jwt`, AMS `client_secret_post`).
- Django remains the authoritative source for user data. A one-way sync (Django → Keycloak) pushes user attributes and group memberships to Keycloak for inclusion in JWT tokens.
- A canary-based migration strategy allows gradual cutover from the legacy direct-integration flow to the Keycloak-brokered flow, with instant rollback via an environment variable.

The full architecture plan is documented in [Keycloak Architecture Plan](../tech-memos/keycloak/keycloak-architecture-plan.md).

## Consequences

**Benefits**
- ACF users will not need to sign up for additional user account credentials, since their default ACF (PIV) credentials will be accepted by ACF AMS for authentication.
- Over the longer term, the costs for leveraging these authentication services may be shared with other ACF program offices who leverage these services.

### Additional Benefits — Keycloak (April 2026)

- **Decoupled IdP integration.** Adding, replacing, or reconfiguring an identity provider is a Keycloak configuration change, not a Django code change. This directly addresses the adaptability concern raised by the NextGen XMS integration attempt.
- **Simplified Django auth code.** Replaces ~500 lines of hand-rolled OIDC code with library configuration plus a small authentication backend subclass.
- **Credential isolation.** The Login.gov RSA private key is stored only in the Keycloak container. Django never sees it.
- **External tool authentication.** Keycloak's support for standard OAuth2 grant types (Authorization Code + PKCE, Device Authorization) enables CLI tools, API testing tools (Postman), and CI/CD pipelines to authenticate without browser interaction — while still routing through Login.gov/AMS for user authentication.
- **Centralized auth observability.** Keycloak exposes Prometheus metrics for login attempts, token exchanges, and failures, providing a unified view of authentication health across all identity providers.
- **Grafana SSO.** The production Keycloak instance also manages SSO for the PLG observability stack (Grafana), eliminating the need for a separate auth mechanism for monitoring tools.

**Risks**
- The NextGen integration attempt uncovered questions about the extent to which our codebase can be easily adapted if ever it becomes necessary to consider alternative CSPs (e.g. ID.me).

### Additional Risks — Keycloak (April 2026)

- **New infrastructure dependency.** Keycloak becomes a single point of failure for new logins. Existing Django sessions are unaffected by a Keycloak outage, and Cloud Foundry auto-restarts crashed containers, but an extended outage blocks all new authentication. Scaling to 2+ instances is possible if needed.
- **Operational overhead.** Each environment requires a dedicated Keycloak instance with its own RDS database, deployment pipeline, monitoring, and upgrade lifecycle. Keycloak upgrades include automatic database migrations that are difficult to roll back.
- **Production Keycloak dual role.** The production Keycloak instance serves both TDP user authentication and Grafana/PLG SSO. An outage affects both, potentially losing monitoring access during an incident. Grafana basic auth can be re-enabled as an emergency fallback.
- **Realm configuration drift.** The declarative realm export (`realm-export.json`) does not overwrite existing configuration on re-import. Runtime changes made via the admin console must be back-ported to the export file to avoid drift.

## Notes

- The full Keycloak architecture plan, including infrastructure topology, deployment procedures, security considerations, and production readiness checklist, is maintained in [keycloak-architecture-plan.md](../tech-memos/keycloak/keycloak-architecture-plan.md).
