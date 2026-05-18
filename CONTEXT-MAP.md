# Context Map

This repo is a multi-context monorepo. Read the root `CONTEXT.md` first, then read the context file for the subsystem you are touching.

| Context | Path | Notes |
| --- | --- | --- |
| Repo-wide | `CONTEXT.md` | Shared product, compliance, deployment, and cross-system language |
| Django API and Celery workers | `tdrs-backend/CONTEXT.md` | Python/Django backend, API behavior, async jobs, parsing orchestration |
| Keycloak initiative | `tdrs-backend/keycloak/CONTEXT.md` | Authentication and identity work related to Keycloak |
| PLG configuration | `tdrs-backend/plg/CONTEXT.md` | PLG configuration and related backend integration |
| Go parser service | `tdrs-services/parser/CONTEXT.md` | Go parser service under `tdrs-services/parser` |
| React frontend | `tdrs-frontend/CONTEXT.md` | CRA React frontend and user-facing workflows |

If a change crosses contexts, read each relevant context file before editing.
