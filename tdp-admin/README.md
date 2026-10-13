# TDP Admin

Administrative frontend for the TANF Data Portal.

## Getting Started

Install dependencies and start the app with the workspace task or a local dev server.

```bash
corepack prepare yarn@4.6.0 --activate
yarn install
yarn dev
```

Open [http://localhost:3001](http://localhost:3001) to reach the admin login page.

Local development uses Webpack (`next dev --webpack`). We observed repeated
Turbopack `ChunkLoadError` failures in Safari after a successful login, causing
the development client to reload `/dashboard` many times before it settled.
Webpack avoids that development chunk loader; production build and start
commands are unchanged. If a running Docker service still uses Turbopack after
pulling this change, restart it from this directory:

```bash
docker compose -f docker-compose.local.yml restart tdp-admin
```

## Environment

Copy `.env.example` to `.env` for Docker Compose, or `.env.local` for
`yarn dev`, then adjust values for your backend.

The login and health flows use these environment variables:

- `NEXT_PUBLIC_AUTH_URL`
- `NEXT_PUBLIC_AUTH_BROWSER_URL`
- `NEXT_PUBLIC_BACKEND_URL`
- `ADMIN_BACKEND_URL`
- `ADMIN_FRONTEND_ORIGIN`
- `ADMIN_API_PROXY_TOKEN`
- `ADMIN_SESSION_COOKIE_NAME` (defaults to `admin_sessionid`)

`NEXT_PUBLIC_AUTH_URL` should point to the Django auth origin. When it is not
set, the app derives the auth origin from `NEXT_PUBLIC_BACKEND_URL`.
When the admin app runs in Docker, set `NEXT_PUBLIC_AUTH_URL` to the
container-reachable Django origin and `NEXT_PUBLIC_AUTH_BROWSER_URL` to the
browser-reachable Django origin, for example:

```bash
NEXT_PUBLIC_AUTH_URL=http://host.docker.internal:8989
NEXT_PUBLIC_AUTH_BROWSER_URL=http://localhost:8989
```

The backend auth service should expose admin-scoped routes under
`/admin-auth`:

- `/admin-auth/login/dotgov`
- `/admin-auth/login/ams`
- `/admin-auth/auth_check`
- `/admin-auth/logout/oidc`

Admin API proxy requests use the Django backend's admin-only API prefix:

- `/admin-api/v1/*`

When `ADMIN_BACKEND_URL` is not set, the app derives it from
`NEXT_PUBLIC_BACKEND_URL` by replacing `/v1` with `/admin-api/v1`.
`ADMIN_API_PROXY_TOKEN` must match the Django backend's
`ADMIN_API_PROXY_TOKEN`; the Next.js server sends it to Django for
`/admin-api/v1/*` requests.
`ADMIN_FRONTEND_ORIGIN` must match the browser origin of the admin app, such as
`http://localhost:3001` locally or `https://admin.tanfdata.acf.hhs.gov` in
production. The `/api/admin/*` proxy rejects mutating requests when the request
`Origin` does not match this value, and it forwards CSRF only from the
`X-CSRFToken` request header.

The Django backend remains authoritative for session validation and admin
authorization. Next.js route gating is only a user-experience guard.
Django also validates `/admin-api/v1/*` requests before API handlers run; the
Next.js proxy only forwards request context and the server-side proxy token.

## Routes

- `/` checks the Django admin session before rendering the admin console.
- `/login` renders the same login page.
- `/logout` redirects through the admin-scoped Django logout flow.
- `/api/backend-health` is a backing JSON probe for the Django auth endpoint.
  The login page shows recovery guidance when the service is unavailable,
  without exposing internal URLs or probe errors.
- `/api/admin/*` forwards backend API requests with the Django session cookie,
  CSRF token required by mutating requests, and server-side proxy token to
  `/admin-api/v1/*`.
- `/api-validation` calls a Django endpoint through the shared server-side API
  helper and displays the returned status, cache headers, content type, and
  response body. Use `?endpoint=test-viewset` to validate a mocked or local
  Django viewset response.
- `/users` lists Django user accounts through `/admin-api/v1/users/`.
- `/users/[id]/edit` renders the first migrated admin form from Django-derived
  metadata at `/admin-api/v1/admin-forms/users.user.change/[id]/metadata/` and
  submits mutations to the generic `submit_url` returned by that metadata.

## API Boundary

`src/app/api/admin/[...path]/route.ts` is the Next.js catch-all BFF route. The
`[...path]` segment preserves the Django viewset path while keeping the
server-only proxy token out of browser code. Next.js requires each supported
HTTP verb to be exported from that route.

Use `src/lib/admin-api.ts` for server-side calls from admin pages and route
handlers. It centralizes backend URL construction, admin session and CSRF
forwarding, proxy identity, request ID/correlation headers, provenance headers,
and no-store behavior. Resource methods such as `adminApi.dataFiles.list()`,
`adminApi.dataFiles.get()`, and `adminApi.adminForms.metadata()` are the
component-facing API and should be expanded as admin viewsets and allowlisted
admin form workflows are migrated.

Django remains the source of truth for migrated admin form validation. React
Hook Form should consume Django metadata for generic client-side feedback, then
display normalized Django field and non-field errors returned by mutation
endpoints.

The proxy intentionally does not make a second auth-check request before each
API call. Django's `/admin-api/v1/*` middleware validates the admin session and
authorization before the requested viewset runs, avoiding a redundant
time-of-check/time-of-use gate in Next.js.

Authenticated admin responses should default to `Cache-Control: no-store`.
The `/api/admin/*` route is the default pass-through path for views backed by a
single Django endpoint. BFF shaping should be limited to composing multiple
Django responses for one admin view. Do not implement business logic,
authorization enforcement, workflow transitions, validation authority,
persistence, or durable audit records in Next.js.

## Testing

Run the focused admin checks with:

```bash
yarn test
```

Manual validation:

```bash
yarn dev
open http://localhost:3001/api-validation?endpoint=test-viewset
open http://localhost:3001/users
```

## Reference read-only list/detail pattern

The first migrated surface is **User accounts**. `/dashboard` places live, database-aggregated user counts first, followed by
the #5966 operational cards. The other
cards explicitly say **Not available yet** until their APIs are migrated; they do
not report sample scan results, service health, or activity as live data.

- `/users` is a server component. A GET form stores `search`, `status`, `active`,
  and `page_size` in the URL. Applying filters resets the page to 1.
- `page` selects a backend page; page sizes are 25 (default), 50, or 100.
  Django caps even direct API requests at 100 records, orders by last name,
  first name, and ID, and applies search and filters before pagination.
- Search is a case-insensitive match on first name, last name, email, or username.
  Approval and active/inactive filters can be combined with search.
- `/users/[id]` displays account details. Its return link preserves the original
  list's filters, search, page, and page size. The existing edit workflow remains
  available as a separate link.
- `/admin-api/v1/users/`, `/admin-api/v1/users/[id]/`, and
  `/admin-api/v1/users/summary/` are read-only admin endpoints. The standard
  `/v1/users/` API is unchanged. Django requires an approved, active staff
  superuser, an admin-scoped session, and the existing proxy token boundary.
- Dashboard summaries use a database aggregate rather than fetching all users.
  The list makes one bounded server-side request. Detail links disable prefetch
  to avoid fetching every account detail while scanning a page.
- Shared `readAdminResource` maps network/HTTP failures into explicit states,
  redirects expired sessions to login, and invokes the forbidden page for 403s.
  Empty results are never inferred from failed requests. Loading and error
  boundaries cover both routes. An out-of-range page offers a filtered page-1 link.
- Reuse `adminApi`, `readAdminResource`, `AdminDataLoadError`, and `AdminPagination`
  for later surfaces. Keep query parsing and URL construction next to each
  resource, with backend validation and authorization remaining authoritative.

### Testing checklist

Automated checks:

```bash
yarn test
yarn lint
yarn tsc --noEmit
yarn build
# From the repository root, with the backend Compose services running:
docker exec tdrs-backend-web-1 python -m pytest -k test_admin_user_reads --no-cov -q
docker exec tdrs-backend-web-1 python -m flake8 tdpservice/users/admin_views.py tdpservice/users/test/test_admin_user_reads.py
```

Manual usability/release checks (use test accounts):

1. Sign in as an authorized admin and open `/dashboard`. Verify the named cards,
   unavailable labels, and user totals; follow each count to its filtered list.
2. Open `/users`, search a name or email, combine both filters, and change page
   size. Confirm Apply resets pagination and Clear removes all filters.
3. Go to page 2, refresh, and open the URL in another authorized session. Confirm
   the same query and page. Open a user and use Back to user accounts.
4. Verify no-match search, an out-of-range page, and a missing user ID. Confirm
   clear recovery links. Simulate backend failure and a slow connection to check
   error and loading states. Check anonymous and non-admin access are denied.
5. Use a large fixture dataset and confirm each API response contains no more
   than the selected page size; there should be no browser-side bulk user fetch.
6. Check keyboard navigation, labels, table scrolling, and narrow/mobile layout.
   Capture dashboard, filtered list, and detail screenshots with synthetic data
   for the release digest.

No database migration is required. Deploy the Django API and admin app together.

Design context: the Mural “IA Django Admin” board prioritizes outstanding requests,
new feedback, and failed nightly database backups. User accounts, access requests,
change requests, feedback, and audit logs are separate surfaces. This preliminary
release implements account reads and status totals; feedback/task integration and
request approval workflows remain future work.
