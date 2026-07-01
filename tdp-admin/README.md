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

## Environment

The login and health flows use these environment variables:

- `NEXT_PUBLIC_AUTH_URL`
- `NEXT_PUBLIC_BACKEND_URL`

The backend auth service should expose `/login` and `/auth_check` under the configured base URL.

## Routes

- `/` renders the admin login page.
- `/login` renders the same login page.
- `/api/backend-health` probes the backend auth endpoint and reports non-2xx responses as failures.
