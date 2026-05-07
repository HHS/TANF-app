# 23. React Admin Console: CRA vs. Next.js

Date: 2026-04-13 (yyyy-mm-dd)

## Status

Proposed

## Context

Django admin is currently used for key administrative workflows in TDP but creates issues at scale:

- Data-heavy pages degrade as records and filters increase.
- Customization is expensive and tightly coupled to Django admin internals.
- Admin UX patterns are inconsistent with the React user-facing experience.
- Section 508 and USWDS consistency require ongoing workaround effort in the Django template layer.
- Engineering ownership is split across mismatched UI stacks (React for users, Django templates for admins).

These constraints motivate replacing Django admin with a React-based admin console. The decision is how to host and structure that console: inside the existing Create React App (CRA) frontend, or as a standalone Next.js application.

## Decision

Adopt a **standalone Next.js admin application** (`tdp-admin`) instead of adding admin routes into the existing CRA app (`tdp-frontend`).

## Options Considered

### Option A: Standalone Next.js admin app

- Separate Next.js application deployed as its own Cloud.gov app.
- Uses server-side rendering (SSR) and React Server Components (RSC) for data-heavy admin screens.
- Communicates with the existing Django backend via REST API.
- Independent deployment cadence from the user-facing frontend.

### Option B: CRA-integrated admin routes in existing frontend

- Add admin routes and components into the existing `tdp-frontend` CRA application.
- Share the existing build pipeline, deployment, and routing infrastructure.
- Admin screens are client-rendered like the rest of the CRA app.

## Why Option A

1. **Better fit for admin workloads.** Admin screens are data-heavy (large tables, complex filters, paginated lists). SSR and server components render these on the server, avoiding client-side data waterfalls and improving perceived performance.

2. **Separation of concerns.** User-facing and admin-facing UIs have different audiences, interaction patterns, and change cadences. A separate app prevents admin complexity from leaking into the user experience.

3. **Independent deployment.** Admin changes can ship without risking regressions on user-facing routes. Rollback is isolated.

4. **Cleaner migration path.** A standalone app can incrementally absorb Django admin workflows without refactoring the existing CRA app. Once complete, Django admin can be deprecated without touching `tdp-frontend`.

5. **No CRA lock-in for admin.** CRA is in maintenance mode. A Next.js admin app avoids deepening investment in CRA while the team evaluates long-term frontend strategy.

## Why not Option B

- CRA is client-rendered only — no SSR/RSC support for the data-heavy screens that define admin work.
- Adding admin routes and state management to `tdp-frontend` increases bundle size and complexity for all users, not just admins.
- Deployment coupling means admin changes require full user-frontend release coordination.
- CRA is in maintenance mode with no active development; deepening investment is a long-term liability.

## Important Tradeoff

CRA integration is faster for narrow short-term delivery because it reuses the existing build pipeline and deployment. The standalone approach requires standing up a new deployable unit (Cloud.gov app, CI/CD pipeline, deployment manifests). This upfront cost is accepted in exchange for cleaner long-term architecture.

## Consequences

### Benefits

- Admin screens get SSR/RSC rendering suited to their data-heavy workloads.
- User-facing app remains unaffected by admin development.
- Independent scaling and deployment for admin runtime.
- Clear boundary for incremental Django admin retirement.

### Risks

- **Additional operational overhead:** A third Cloud.gov app to deploy, monitor, and maintain. Mitigated by reusing existing deployment and monitoring practices.
- **MVP scope creep toward full parity:** Standalone app may invite pressure to replicate all Django admin features immediately. Mitigated by strict scope gating — see architecture doc for phasing principles.
- **BFF overgrowth:** The Next.js server layer could accumulate business logic that belongs in Django. Mitigated by architectural principle: use pass-through by default, BFF shaping only when composing multiple endpoints.

### Decisions deferred

- Which exact MVP workflows are in scope for the first production release, and which are explicitly deferred.
- What is the acceptance threshold for Django admin parity before deprecation milestones are approved.

## Notes

- Architecture specification: [React Admin Console Architecture](../React-Admin-Console-Architecture.md)
- Tracking issue: #5746
