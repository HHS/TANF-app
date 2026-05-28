# React Admin Console: High-Level Architecture Specification

**Issue:** #5746  
**Status:** Draft for Architecture Review  
**Date:** April 2026  
**Audience:** Engineering, Technical Leadership, DevOps

---

## Table of Contents

- [React Admin Console: High-Level Architecture Specification](#react-admin-console-high-level-architecture-specification)
  - [Table of Contents](#table-of-contents)
  - [Executive Summary](#executive-summary)
  - [Scope](#scope)
  - [Principles](#principles)
  - [High-Level Component Architecture](#high-level-component-architecture)
  - [System Boundaries and Data Access](#system-boundaries-and-data-access)
    - [Backend for Frontend (BFF) shaping vs. pass-through pattern](#backend-for-frontend-bff-shaping-vs-pass-through-pattern)
  - [Form Metadata and Validation](#form-metadata-and-validation)
    - [Guiding design principles](#guiding-design-principles)
    - [Third-party library expectations](#third-party-library-expectations)
    - [Backend metadata pattern](#backend-metadata-pattern)
    - [Form submission validation flow](#form-submission-validation-flow)
  - [Authentication and Authorization](#authentication-and-authorization)
    - [Authentication model](#authentication-model)
    - [Trust boundary and origin model](#trust-boundary-and-origin-model)
    - [Authorization model](#authorization-model)
    - [CSRF and cookie posture](#csrf-and-cookie-posture)
    - [Cache behavior and audit forwarding](#cache-behavior-and-audit-forwarding)
    - [Session validation flow](#session-validation-flow)
  - [Rendering and Interaction Model](#rendering-and-interaction-model)
  - [Technology Stack](#technology-stack)
  - [Deployment Topology (Cloud.gov)](#deployment-topology-cloudgov)
  - [Migration Strategy](#migration-strategy)
  - [Phasing Principles](#phasing-principles)
  - [Risks and Mitigations](#risks-and-mitigations)

---

## Executive Summary

This document defines the target architecture for replacing Django admin workflows with a React-based admin console while keeping Django as the system-of-record backend. For the decision rationale (CRA vs. Next.js, motivations for moving away from Django admin), see [ADR-023: React Admin Console — CRA vs. Next.js](Architecture-Decision-Record/023-react-admin-console.md).

The architecture is a standalone Next.js admin application that:

- uses server-side rendering and server components for data-heavy admin workflows,
- uses Keycloak SSO with an admin-specific client and browser origin,
- keeps business rules, authorization enforcement, workflow transitions, and audit behavior in Django,
- is deployed as a separate Cloud.gov app alongside the existing user frontend and backend.

Core workflows this architecture must support:

- user access and account-change review workflows,
- data file submission review and reparse initiation,
- parsed record inspection and error report viewing,
- feature flag administration,
- audit log review and filtering.

---

## Scope

This is an architecture specification. It describes system structure, boundaries, key design choices, and critical integration patterns.

---

## Principles

1. Django remains authoritative for domain and security decisions.
2. Next.js is a presentation/orchestration layer, not a replacement backend.
3. Prefer API reuse over policy duplication.
4. Use Backend for Frontend (BFF) behavior only where it adds clear admin UX value.

---

## High-Level Component Architecture

In the diagram below:

- SSR means server-side rendering.
- RSC means React Server Components.
- BFF means Backend for Frontend.
- USWDS means U.S. Web Design System.
- REST API means Representational State Transfer application programming interface.
- CRA means Create React App.

<table>
  <tr>
    <th>Admin Console</th>
    <th>User Application</th>
  </tr>
  <tr>
    <td>
<pre>
┌──────────────────────────────────────────────────────────────────┐
│                          Admin Browser                           │
└──────────────────────────────────────────────────────────────────┘
                               │
                               ▼
┌──────────────────────────────────────────────────────────────────┐
│                     tdp-admin (Next.js)                          │
│  - server-side rendering / React Server Components               │
│  - admin route protection                                        │
│  - optional thin Backend for Frontend shaping                    │
│  - U.S. Web Design System-based admin UI                         │
└──────────────────────────────────────────────────────────────────┘
                               │
                               ▼
┌──────────────────────────────────────────────────────────────────┐
│                     tdp-backend (Django)                         │
│  - auth/session validation                                       │
│  - authorization + workflow rules                                │
│  - audit logging                                                 │
│  - REST API and business logic                                   │
└──────────────────────────────────────────────────────────────────┘
                               │
                               ▼
┌──────────────────────────────────────────────────────────────────┐
│                         PostgreSQL                               │
└──────────────────────────────────────────────────────────────────┘
</pre>
    </td>
    <td>
<pre>
┌──────────────────────────────────────────────────────────────────┐
│                          User Browser                            │
└──────────────────────────────────────────────────────────────────┘
                               │
                               ▼
┌──────────────────────────────────────────────────────────────────┐
│               tdp-frontend (Current Create React App)            │
│                     user-facing routes                           │
└──────────────────────────────────────────────────────────────────┘
                               │
                               ▼
┌──────────────────────────────────────────────────────────────────┐
│                     tdp-backend (Django)                         │
└──────────────────────────────────────────────────────────────────┘
</pre>
    </td>
  </tr>
</table>

This reflects the target coexistence model: existing CRA user app remains, while admin moves to a dedicated Next.js runtime and separate browser origin.

---

## System Boundaries and Data Access

Expected request path for admin workflows:

Browser → Next.js admin → Django API → PostgreSQL

Boundary rules:

- Next.js can shape or aggregate responses for admin views.
- Django owns permission checks, workflow transitions, and domain validation.
- Direct database access from Next.js is out of scope.
- Any exception to direct DB access requires separate architecture review.

Data access patterns by workflow:

- Read-heavy pages (lists/tables): server-rendered with server-side filtering and pagination.
- Workflow mutations (approve/reparse/update flags): explicit mutation endpoints with Django-side audit and policy enforcement.
- Large dataset navigation: paginated or cursor-based API interactions, not client-side bulk loading.

### Backend for Frontend (BFF) shaping vs. pass-through pattern

Most admin screens should use **pass-through** — the Next.js server component calls a single Django endpoint and renders the response directly.

```
// Pass-through example: fetch one Django endpoint and render the response.
fetch(`${BACKEND_URL}/api/admin/users/?page=1&status=approved`, reqOpts)
```

Use **BFF shaping** only when an admin view requires data from multiple Django endpoints that should be composed before rendering.

```
// BFF shaping example: compose multiple Django responses for one admin view.
Promise.all([
  fetch(`${BACKEND_URL}/api/admin/submissions/${id}/`, reqOpts),
  fetch(`${BACKEND_URL}/api/admin/submissions/${id}/errors/`, reqOpts),
])
```

The rule of thumb: if a single Django endpoint can serve the view, pass-through. If the view needs to join data that Django doesn't serve in a single response, use BFF shaping — but do not add business logic or authorization checks in the BFF layer.

---

## Form Metadata and Validation

Django remains the source of truth for editable admin forms. The React admin should not manually duplicate Django model or form validators in TypeScript. Instead, each migrated admin workflow should expose an explicit form-metadata endpoint from Django and a matching mutation endpoint for submission.

The target pattern is metadata-driven, not fully generic form generation. Shared React components should render common field types from backend metadata, while workflow-specific screens can still provide layout, conditional behavior, and specialized controls where needed. This gives the frontend reusable building blocks without requiring every Django admin form to fit a single universal form-builder abstraction.

### Guiding design principles

- **Explicit workflow contracts:** each migrated admin form should have a clear backend metadata endpoint and mutation endpoint rather than relying on frontend inference from unrelated APIs.
- **Shared component mapping:** the frontend should map common metadata field types to reusable USWDS React form controls.
- **Server-authoritative validation:** Django remains the final authority for validation, permission checks, workflow rules, persistence, and audit behavior.
- **Generic where safe:** required fields, choices, labels, help text, simple type checks, lengths, and numeric/date bounds can drive reusable form behavior.
- **Workflow-specific escape hatches:** custom layouts, conditional fields, specialized controls, and server-only validation are expected for complex admin workflows.
- **No hidden business logic in the frontend:** frontend adapters may improve usability, but they should not duplicate Django authorization, workflow transitions, or domain rules.

### Third-party library expectations

Third-party libraries can help with frontend form state and generic client-side checks, but they should not be treated as a complete Django-to-React admin form solution.

- **React Hook Form** should manage form state, touched/dirty state, field registration, and submission handling.
- A TypeScript schema validation library may be used to express generic client-side rules derived from backend metadata.
- USWDS React components should provide the accessible visual controls for common inputs.
- Django should still own authoritative validation, authorization, persistence, workflow transitions, and audit behavior.

The implementation should assume we own the Django metadata contract and the component mapping layer. A third-party package may reduce boilerplate, but it should not define the cross-system contract or move business rules out of Django.

### Backend metadata pattern

For model-backed forms, the backend should derive generic metadata from the same Django form, serializer, and model field definitions used for server-side validation where practical:

- field type and widget intent,
- required/optional state,
- labels and help text,
- choice values,
- max length and numeric/date bounds where Django exposes them,
- simple field validators that can be represented as client rules,
- initial values for edit forms,
- read-only or disabled state derived from permissions or workflow state,
- field and form-level errors returned from Django validation.

The backend contract should be explicit per workflow rather than inferred by the frontend. For example, a migrated user-access review form could expose one metadata endpoint for the editable fields on that screen and one mutation endpoint for approve/reject/update actions.

Conceptual shape:

```
GET /api/admin/users/{id}/access-review/form/
  -> fields, initial values, generic constraints, permissions

POST /api/admin/users/{id}/access-review/
  -> runs Django validation and workflow logic, persists changes, returns success or validation errors
```

High-level metadata example:

```json
{
  "workflow": "user_access_review",
  "fields": [
    {
      "name": "role",
      "label": "Role",
      "type": "choice",
      "widget": "select",
      "required": true,
      "choices": [
        { "value": "data_analyst", "label": "Data Analyst" },
        { "value": "ofa_admin", "label": "OFA Admin" }
      ]
    },
    {
      "name": "decision_reason",
      "label": "Decision reason",
      "type": "string",
      "widget": "textarea",
      "required": false,
      "maxLength": 500
    }
  ],
  "initialValues": {
    "role": "data_analyst",
    "decision_reason": ""
  }
}
```

High-level validation error example:

```json
{
  "fieldErrors": {
    "role": ["Select a valid role."]
  },
  "nonFieldErrors": [
    "This user cannot be approved until all required profile fields are complete."
  ]
}
```

The metadata response should be stable enough for frontend reuse, but it does not need to expose every Django validator. Rules that are permission-sensitive, cross-field, workflow-state-dependent, or hard to serialize should stay server-only and return as validation errors after submission.

The frontend uses metadata to construct React Hook Form inputs and pre-submit schema validation for immediate feedback. Mutating requests still submit to Django, where `ModelForm`, serializer, model, and domain validation run authoritatively before persistence and audit logging.

### Form submission validation flow

Form submission should follow this sequence:

1. The Next.js admin page requests metadata and initial values from Django.
2. The React form maps backend field metadata to shared USWDS input components.
3. React Hook Form applies generic client-side checks for immediate feedback.
4. On submit, the form sends the payload to the Django mutation endpoint.
5. Django runs authoritative `ModelForm`, serializer, model, permission, workflow, and domain validation.
6. Django returns either a successful result or a normalized error response containing field errors and non-field errors.
7. The React form maps server-returned errors back onto the corresponding fields or form-level alert region.

Validation support should be tiered:

- **Generic client validation:** required fields, type checks, choice constraints, length, numeric bounds, date bounds, and simple regex patterns when safely serializable.
- **Server-returned validation:** cross-field validation, permission-sensitive rules, custom Python validators, workflow-state rules, and any validator that cannot be losslessly represented in frontend schema form.
- **Workflow-specific overrides:** allowed only when a migrated admin surface has behavior that cannot be described by generic metadata; these should remain thin UI adapters, not copies of business rules.

This preserves Django's validation ownership while still giving admins pre-submission feedback for common mistakes. It also gives the migration a practical rule: no Django admin form is retired until its React replacement handles server-returned field and non-field errors and has parity for the generic metadata-supported validations.

---

## Authentication and Authorization

### Authentication model

The admin console should use Keycloak SSO through a dedicated admin client rather than treating admin as another path on the main CRA host.

Target model:

- `tdp-admin` is served from a separate hostname, such as `tdp-admin-raft.app.cloud.gov` in development and `admin.tanfdata.acf.hhs.gov` in production.
- Keycloak registers `tdp-admin` as a separate client with admin-specific redirect URIs and web origins.
- Keycloak preserves seamless SSO for users who already have an active SSO session, but the admin browser session is scoped to the admin hostname.
- Django remains the application session authority for backend API enforcement after the Keycloak login callback completes.
- Admin and non-admin Django sessions should be separate browser cookies. Prefer host-only `SESSION_COOKIE_DOMAIN` and `CSRF_COOKIE_DOMAIN` behavior by leaving broad domain settings unset for the admin deployment path.

This model intentionally avoids sharing broad `.app.cloud.gov` or `.acf.hhs.gov` cookies between the user-facing CRA origin and the admin origin. It reduces the blast radius of a user-frontend XSS bug and gives admin routes their own redirect, cookie, CSRF, and session lifecycle boundaries.

### Trust boundary and origin model

Moving from `/admin/` reverse-proxied through nginx to a standalone Next.js app changes the trust boundary. Next.js becomes a privileged server-side component that can receive admin requests, validate admin session state, and call Django APIs on behalf of an admin user.

Required guardrails:

- Serve `tdp-admin` on a separate origin from `tdp-frontend`; do not host the admin console as a same-origin CRA path.
- Treat Next.js server actions, route handlers, and BFF endpoints as privileged code paths.
- Prefer pass-through calls to Django for mutations; any BFF mutation must forward Django-required CSRF context and must not become the final authorization authority.
- Keep final authentication, authorization, workflow validation, and audit persistence in Django.
- Do not share admin cookies with the user-facing frontend host.
- Add CSP, dependency scanning, and XSS regression coverage to the admin app release gate because an admin-origin XSS has privileged impact.
- Disable shared CDN/browser caching for authenticated admin responses.

### Authorization model

- Route-level UX gating in Next.js is allowed for user experience.
- Final authorization enforcement is always in Django.
- Object-level and workflow-level checks remain backend-owned.

### CSRF and cookie posture

- Admin session cookies must be `Secure`, `HttpOnly`, and host-only where possible.
- Admin CSRF cookies should also be scoped to the admin host and not shared with the user frontend.
- Cookie-authenticated mutating calls must carry Django's expected CSRF context through the Next.js layer.
- Trusted origins should be explicit to the admin hostname and backend hostname; avoid wildcard subdomain trust.
- SameSite behavior should be chosen for the deployed cross-host flow and documented before implementation. If the admin app and Django API require cross-site cookie submission, use the narrowest `SameSite=None; Secure` scope possible and compensate with strict origin/referrer checks.
- Next.js BFF endpoints that accept browser mutations must perform CSRF validation or forward the request to Django without weakening Django's CSRF checks.
- Logout must clear the admin-scoped Django session and trigger Keycloak logout or session revocation behavior consistent with the broader Keycloak architecture.

### Cache behavior and audit forwarding

Authenticated admin responses must not be stored in shared caches. Next.js server responses, route handlers, and BFF responses should set `Cache-Control: no-store` unless an endpoint is explicitly proven safe to cache. Server-rendered admin pages that contain user, submission, audit, or report data should always be dynamic and user-specific.

When Next.js calls Django on behalf of an admin user, requests must preserve provenance for audit and incident response:

- authenticated Django user/session identifier,
- originating admin route or action name,
- request ID/correlation ID,
- source IP chain from platform headers,
- Keycloak client/auth flow identifier when available.

Django remains responsible for durable audit records. Next.js may add request context, but it must not be the only place where privileged admin activity is recorded.

### Session validation flow

Every admin route validates the session before rendering. The integration works as follows:

```
Admin request
  -> browser reaches the separate admin hostname
  -> unauthenticated admin user is redirected through Keycloak tdp-admin client
  -> Django establishes or validates an admin-scoped session
  -> Next.js validates the admin session via lightweight Django auth endpoint
  -> invalid session redirects to login
  -> valid session continues to server-rendered admin route
```

For mutations, the CSRF token must be forwarded from the Django-issued cookie:

```
POST admin mutation
  -> browser submits to Next.js admin origin
  -> Next.js forwards admin-scoped Django session cookie
  -> include CSRF token in header
  -> include provenance headers/request context
  -> Django performs final authz, mutation, and audit logging
```

These examples illustrate the critical auth integration. The flow is pseudocode — exact implementation will depend on Keycloak client configuration, cookie domain configuration, and session endpoint design.

---

## Rendering and Interaction Model

Rendering strategy mapped to specific admin surfaces:

| Surface | Strategy | Rationale |
|---------|----------|----------|
| User list / Data file list | SSR (server component) | Large paginated datasets; no client state needed |
| User detail / Submission detail | SSR (server component) | Single-entity fetch; render on server |
| Audit log viewer | SSR with streaming | Potentially high-latency queries; progressive render |
| Feature flag toggles | Client component | Immediate local feedback on toggle; mutation via server action |
| Filter/search controls | Client component | Interactive UI; triggers server re-fetch on submit |
| Approval/reparse confirmation modals | Client component | Dialog interaction; form submission via server action |

General rules:

- Default to server components. Only promote to client component when the surface requires browser interactivity (event handlers, local state).
- Server-driven pagination and filtering: pass `page` and filter params as URL search params so server components can fetch the correct slice.
- Avoid client-side bulk loading of large datasets.

---

## Technology Stack

| Area | Choice | Notes |
|------|--------|-------|
| Framework | Next.js 14+ | App Router, SSR/RSC support |
| Auth | Keycloak SSO + Django sessions | Separate admin client/origin with Django-authoritative API enforcement |
| UI System | USWDS React | Required design/accessibility alignment |
| Forms | React Hook Form + metadata-driven schema validation | Client ergonomics from Django-derived metadata with server-authoritative validation |
| Tables / Data Grid | Server-rendered USWDS tables with backend pagination | Prefer simple tables first; only introduce a heavier grid library if admin workflows prove it necessary |
| Data Fetching | Server-first fetch patterns | Avoid client waterfalls |
| State Management | URL/search-param driven server state plus local component state | Avoid Redux by default for MVP; introduce shared client state only for a concrete cross-page need |
| API Layer | Django REST API with optional thin BFF | Preserve existing backend ownership |
| Testing | Component + integration + E2E | Validate authz, workflow transitions, and admin UX paths |

Tailwind CSS is intentionally excluded from this recommendation. USWDS is the styling system for this architecture.

---

## Deployment Topology (Cloud.gov)

Target runtime model:

- tdp-frontend: existing CRA user app
- tdp-admin: new Next.js admin app
- tdp-backend: shared Django backend and API

Operational implications:

- adds one deployable frontend unit,
- allows admin deployment cadence independent of user-facing frontend,
- preserves backend as shared domain and security boundary.

Cloud.gov considerations:

- prefer internal app-to-app calls from admin to backend,
- serve admin from a dedicated route/hostname instead of a same-origin CRA path,
- register the admin hostname as a separate Keycloak client redirect URI and web origin,
- prefer host-only session and CSRF cookies for admin and non-admin browser sessions,
- treat local filesystem as ephemeral,
- keep observability aligned with existing platform monitoring patterns,
- support rollback strategies without coupling user and admin releases.

---

## Migration Strategy

- Run the existing Django admin and `tdp-admin` in parallel during migration.
- Replace Django admin workflows incrementally, starting with the highest-value read and mutation paths called out in this document.
- Keep Django as the system of record until each replacement workflow is production-validated for authorization, audit behavior, and operational readiness.
- Retire individual Django admin surfaces only after the corresponding React admin workflow is available, stable, and accepted by engineering/product stakeholders.

---

## Phasing Principles

- Auth integration and deployment skeleton come first — all subsequent work depends on a working session flow.
- Read-heavy views (lists, detail pages) before mutation flows — they validate the data-access patterns with lower risk.
- Mutation workflows (approve, reparse) follow once read paths are stable.
- Accessibility verification is continuous, not a final phase — every merged view must pass automated USWDS conformance checks.

---

## Risks and Mitigations

| Risk | Severity | Mitigation |
|------|----------|-----------|
| Performance regressions on large datasets | High | Server-driven pagination and filtering from day one |
| Admin trust-boundary expansion | High | Separate admin hostname, separate Keycloak client, host-only admin cookies, Django-authoritative authz |
| Auth/session edge-case defects | Medium | Explicit session-expiry, logout, cookie-domain, and CSRF test matrix |
| Accidental caching of privileged admin data | High | `Cache-Control: no-store` for authenticated admin pages and BFF responses |
| Frontend/backend validation drift | Medium | Generate generic form metadata from Django form/model definitions; keep Django validation authoritative |
| BFF overgrowth into second backend | Medium | Boundary guardrails in design and review; pass-through as default pattern |
| Operational overhead from third app | Medium | Reuse existing deployment and monitoring practices |
| Accessibility drift | Medium | USWDS conformance plus automated checks in CI |

---

**Document Version:** 3.0  
**Last Updated:** April 2026  
**Related ADR:** [023 — React Admin Console: CRA vs. Next.js](Architecture-Decision-Record/023-react-admin-console.md)  
**Next Review Gate:** Architecture sign-off
