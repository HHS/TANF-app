# VS Code Workspaces Walkthrough

There are five dedicated VS Code workspace configurations for the TANF Data Portal (TDP) monorepo, along with workspace settings, extension recommendations, and full task integrations from `Taskfile.yml`.

---

## Workspaces Overview

| Workspace File | Target Persona / Scope | Folders Mounted | Recommended Extensions | Notes |
| :--- | :--- | :--- | :--- | :--- |
| [`tanf-app.code-workspace`](./tanf-app.code-workspace) | Full Monorepo | Entire project root (`.`) | Full set from `.vscode/extensions.json` (Python, Django, PostgreSQL, Prettier, Jest, Go, Docker, Task, Markdown, YAML, Terraform, GitLens, etc.) | Complete monorepo visibility |
| [`frontend.code-workspace`](./frontend.code-workspace) | Frontend Engineers | `tdrs-frontend` (React/CRA), `tdp-admin` (Next.js) | Prettier, Prettier-Standard, Cucumber, Jest, Docker, Task, GitLens, YAML, Spell Checker, Antigravity | `node_modules` hidden from explorer |
| [`backend.code-workspace`](./backend.code-workspace) | Backend Engineers | `tdrs-backend` (Django/Celery), `tdrs-services/parser` (Go) | Python, Pylance, Flake8, Black, Django, PostgreSQL, Go, Docker, Task, GitLens, YAML, Spell Checker, Antigravity | `node_modules` hidden from explorer |
| [`docs.code-workspace`](./docs.code-workspace) | Documentation & Architecture | `docs/`, `tdrs-backend/docs/`, `product-updates/`, Project Docs | Markdownlint, Markdown All in One, Mermaid Preview, PDF Viewer, Code Spell Checker, YAML, Task, GitLens, Antigravity | `node_modules` hidden from explorer |
| [`terraform.code-workspace`](./terraform.code-workspace) | Infrastructure & DevOps | `terraform/` (dev, staging, prod) | HashiCorp Terraform, CircleCI, YAML, Task, Markdownlint, GitLens, Spell Checker, Antigravity | `node_modules` hidden from explorer |

In addition, [`.vscode/tasks.json`](./.vscode/tasks.json) and [`.vscode/extensions.json`](./.vscode/extensions.json) exist at the root to support developers who open the root folder directly (`code .`).

---

## How to Open Workspaces in VS Code

### Via Terminal
From the repository root:
```bash
# Open entire repository
code tanf-app.code-workspace

# Open frontend workspace
code frontend.code-workspace

# Open backend workspace
code backend.code-workspace

# Open documentation workspace
code docs.code-workspace

# Open terraform workspace
code terraform.code-workspace
```

### Via VS Code Menu
1. In VS Code, navigate to **File > Open Workspace from File...**
2. Select the desired `.code-workspace` file from the root directory.
3. VS Code will prompt you to install recommended extensions for that workspace.

---

## Running Development Environment & Tasks

All tasks from `Taskfile.yml` are integrated into VS Code's native task runner. If you installed the Task extension, they are also available in the left panel.

### How to Run Tasks in VS Code
1. Press `Cmd + Shift + P` (macOS) or `Ctrl + Shift + P` (Windows/Linux).
2. Type **Tasks: Run Task** and press `Enter`.
3. Select any task to execute it in an integrated VS Code terminal.

### Key Tasks Available by Category

#### 1. Spinning Up the Development Environment
- **`Dev: Start All (Backend + Frontend)`** (`task up`): Default build task (`Cmd+Shift+B`). Spins up frontend and backend services in Docker.
- **`Dev: Start All with Admin (Backend + Frontend + Admin)`** (`task up-with-admin`): Spins up backend, frontend, and Next.js admin app.
- **`Dev: Stop All (Backend + Frontend)`** (`task down`): Stops running containers.
- **`Dev: Stop All with Admin`** (`task down-with-admin`): Stops all containers including the admin app.
- **`Dev: Rebuild & Update Dependencies`** (`task update-deps`): Rebuilds frontend/backend images without data loss.

#### 2. Backend & Database Tasks
- **`Backend: Start Web Server`** (`task backend-up`)
- **`Backend: Stop Web Server`** (`task backend-down`)
- **`Backend: Restart Web Server`** (`task backend-restart`)
- **`Backend: Follow Web Server Logs`** (`task backend-logs`)
- **`Backend: Open Django Shell (shell_plus)`** (`task backend-shell`)
- **`Backend: Open Shell (Bash)`** (`task backend-bash`)
- **`Backend: Open PostgreSQL Shell`** (`task psql`)
- **`Backend: Make Migrations`** (`task backend-makemigrations`)
- **`Backend: Run Migrations`** (`task backend-migrate`)
- **`Backend: Clean & Recreate DB (Dev Only)`** (`task backend-clean-db`)
- **`Backend: Seed DB with Initial Data`** (`task backend-exec-seed-db`)
- **`Backend: Run Pytest Suite`** (`task backend-pytest`)
- **`Backend: Run Flake8 Linter`** (`task backend-lint`)
- **`Backend: Run Go Parser Integration Suite`** (`task backend-pytest-go-integration`)
- **`Backend: Run ETL Integration Suite`** (`task backend-pytest-etl-integration`)
- **`Backend: Start ClamAV Service`** (`task clamav-up`)

#### 3. Frontend & Admin Tasks
- **`Frontend: Start Web Server`** (`task frontend-up`)
- **`Frontend: Stop Web Server`** (`task frontend-down`)
- **`Frontend: Restart Web Server`** (`task frontend-restart`)
- **`Frontend: Follow Web Server Logs`** (`task frontend-logs`)
- **`Frontend: Open Shell in Container`** (`task frontend-bash`)
- **`Frontend: Initialize Project (Docker + Yarn)`** (`task frontend-init`)
- **`Frontend: Install Dependencies on Host`** (`task frontend-install`)
- **`Frontend: Run ESLint in Docker`** (`task frontend-lint`)
- **`Frontend: Run Unit Tests in Docker`** (`task frontend-test`)
- **`Frontend: Run Unit Tests on Host (Watch)`** (`task frontend-test-watch`)
- **`Frontend: Run Cypress E2E Tests Locally`** (`task frontend-e2e-local`)
- **`Frontend: Run Cypress E2E Tests Headless (CI Mode)`** (`task frontend-e2e-ci-local`)
- **`Admin: Start Web Server`** (`task admin-up`)
- **`Admin: Stop Web Server`** (`task admin-down`)
- **`Admin: Run Unit Tests (Vitest) in Docker`** (`task admin-test`)

#### 4. Go Parser Tasks
- **`Parser: Compile Check Packages & Tests`** (`task parser:compile-check`)
- **`Parser: Run Static Analysis (Lint)`** (`task parser:lint`)
- **`Parser: Run All Tests with Coverage`** (`task parser:test-all-coverage`)
- **`Parser: Validate Config & Coverage`** (`task parser:validate-config`)

#### 5. Documentation Tasks
- **`Docs: Serve MkDocs (Backend API Docs)`** (`mkdocs serve -a 0.0.0.0:8001`)
- **`Docs: Configure Git Hooks`** (`task gitcfg`)

#### 6. Terraform Tasks
- **`Terraform: Format Check (All)`** (`terraform fmt -check -recursive`)
- **`Terraform: Format Apply (All)`** (`terraform fmt -recursive`)
- **`Terraform: Dev / Staging / Prod - Init, Validate, Plan`**

<!-- ---

## Verification Summary

- **JSON Validation**: Validated all 7 JSON configuration files (`tanf-app.code-workspace`, `frontend.code-workspace`, `backend.code-workspace`, `docs.code-workspace`, `terraform.code-workspace`, `.vscode/tasks.json`, `.vscode/extensions.json`) using Python's `json` module.
- **Task Mapping**: All task commands align directly with tasks defined in [`Taskfile.yml`](./Taskfile.yml).
- **Codebase Integrity**: `git status` confirmed that zero existing application code was changed. -->
