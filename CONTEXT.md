# TANF App Context

This repository contains the TANF Data Reporting System application and supporting services.

## Product Boundary

The system supports TANF data collection, validation, submission, reporting, operational monitoring, and related user workflows.

## Repository Shape

This is a multi-context monorepo. Read `CONTEXT-MAP.md` to choose the subsystem context before making changes.

The main contexts are:

- `tdrs-backend/`: Django API, Python backend logic, Celery workers, parsing orchestration, and backend deployment assets.
- `tdrs-backend/keycloak/`: Keycloak initiative for authentication and identity work.
- `tdrs-backend/plg/`: PLG configuration and observability deployment assets.
- `tdrs-services/parser/`: Go parser service.
- `tdrs-frontend/`: CRA React frontend.

## Cross-Cutting Concerns

- Security and compliance requirements matter across the repository.
- Data validation and parsing behavior should be treated as product behavior, not only implementation detail.
- Changes that affect user access, reporting workflows, or submitted data should be reviewed against relevant docs under `docs/`.
