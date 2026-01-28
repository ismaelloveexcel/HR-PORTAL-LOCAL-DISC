# ARCHITECTURE OVERVIEW

## High-level system diagram (textual)
```
Users (HR / Manager / Employee)
        |
        v
[Frontend SPA - React/Vite/TS]
        |
   HTTPS /api
        |
[Backend - FastAPI (Python 3.11)]
        |
[Services & Repositories]
        |
[PostgreSQL (Azure)]
```

## Boundaries
- **Frontend (React/Vite/TS):** Client SPA, role-based UX, calls `/api` only.
- **Backend (FastAPI):** API surface, auth, validation, business logic orchestration; no direct SQL outside repositories.
- **Repositories (SQLAlchemy async):** Data access only; parameterized queries.
- **Database (PostgreSQL on Azure):** System of record; migrations via Alembic.
- **Static delivery:** Frontend build served by backend in production (`backend/static` or `frontend/dist` fallback).

## Data responsibility boundaries
- **Authentication & Authorization:** JWT via backend `require_role`; roles: admin, hr, manager, viewer/employee.
- **Compliance data:** HR-only; stored and accessed via repositories; no exposure without role checks.
- **Personal data:** Sanitized (`sanitize_text`), separated from compliance/bank data models.
- **Documents:** Metadata before files; stored linked to immutable employee number.

## Non-goals (explicit)
- No payroll calculation engine (visibility only).
- No infrastructure provisioning inside app (Azure resources managed externally).
- No synchronous DB operations; async only.
- No bypass of role checks for protected routes.

## Deployment boundary
- Single supported path: Azure App Service + PostgreSQL via GitHub Actions OIDC (`deploy.yml`).
- Secrets managed via GitHub/Azure config, not in code.

## Observability & health
- FastAPI health endpoints and startup migrations.
- CI: `ci.yml`, `pr-quality-check.yml`; deploy: `deploy.yml`; post-deploy health: `post-deployment-health.yml`.
