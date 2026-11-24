# Preliminary admin dashboard and user account reads

Local release notes draft. Do not publish to GitBook or Mural per user instruction.

The admin console now has a preliminary dashboard based on the #5966 PDF
reference, with live user totals and links to filtered account lists. Other
widgets clearly indicate that their data is not available yet. The Mural
information architecture board was reviewed in Chrome. It prioritizes
outstanding requests, new feedback, and failed nightly database backups, and
separates user accounts from access/change-request mutation workflows.

User accounts are the first reusable server-rendered list/detail surface.
Search, approval status, active/inactive status, page, and page size are stored in
the URL. Django filters, searches, orders, and paginates results before returning
at most 100 users. Detail pages retain list context in their return links.
The user directory groups filters and results in a single panel, with visible
account links, approval status badges, and previous/next pagination controls.
Loading, empty, unavailable, missing-record, expired-session, and unauthorized
states have explicit handling. This work adds no new mutation workflows.

Testing steps: use the [admin README checklist](../../tdp-admin/README.md#testing-checklist).

Validation recorded during implementation:

- Admin tests: 78 passed.
- TypeScript and production Next.js build: passed; dashboard/list/detail are dynamic.
- ESLint: no errors; three pre-existing login-page image warnings.
- Backend: 31 focused tests passed (user reads, existing admin forms, and admin API authorization); flake8 passed.
- Browser verification with synthetic data: dashboard layout/count links, filtered
  pagination, refresh persistence, detail return context, and no-match search passed.
  User list layout was also checked at a 390px viewport: filters stack and table
  overflow stays inside its scrollable region. Full accessibility/usability
  testing remains pending.

Media to attach after manual validation: dashboard at desktop and mobile widths,
filtered user list with pagination, and user detail with contextual return link.
Use synthetic accounts only.

GitBook and Mural remain unchanged. External publication is excluded at the user's
request; keep these notes in the repository.
