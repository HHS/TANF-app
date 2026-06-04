# Backend Context

This context covers the Django API, Python backend code, Celery workers, parsing orchestration, backend tests, and backend deployment assets under `tdrs-backend/`.

## Boundaries

- API behavior and backend application logic live here.
- Celery worker behavior and asynchronous jobs live here.
- Backend parsing orchestration lives here, even when parser implementation details are delegated to another service.
- Authentication integration touches this context, but Keycloak-specific configuration and deployment details are documented in `tdrs-backend/keycloak/CONTEXT.md`.
- PLG observability configuration is documented in `tdrs-backend/plg/CONTEXT.md`.

## Read With

- Root `CONTEXT.md`
- `CONTEXT-MAP.md`
- Relevant technical docs under `docs/Technical-Documentation/`
- Relevant backend README or module-level docs near the code being changed
