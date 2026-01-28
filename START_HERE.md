# START HERE — Canonical Entry Point

> **📖 Solo HR Guide:** See [docs/SOLO_HR_GUIDE.md](docs/SOLO_HR_GUIDE.md) for daily HR workflows.  
> **🔧 Simplification:** See [SIMPLIFICATION_INDEX.md](SIMPLIFICATION_INDEX.md) to reduce complexity.

---

## What this system is
Secure Renewals HR Portal: a full-stack HR self-service and compliance platform for UAE private-sector employers. It runs on FastAPI (Python) + React (Vite) with PostgreSQL and targets Azure App Service.

## Who this is for
- HR/Admin owners responsible for compliance, onboarding, and renewals
- Managers approving requests and viewing team status
- Engineers operating and extending the platform

## The only supported setup/deployment path
**Azure App Service with PostgreSQL (OIDC-authenticated GitHub Actions).**

1. Prerequisites: Azure subscription, PostgreSQL instance, GitHub OIDC app registration, required secrets (`AZURE_CLIENT_ID`, `AZURE_TENANT_ID`, `AZURE_SUBSCRIPTION_ID`, `DATABASE_URL`, `AUTH_SECRET_KEY`).
2. Follow the canonical guide: [`docs/AZURE_DEPLOYMENT_REFERENCE_GUIDE.md`](docs/AZURE_DEPLOYMENT_REFERENCE_GUIDE.md).
3. Build and deploy via GitHub Actions workflow `deploy.yml` (main branch).

No other setup paths are supported by this repo steward plan.

## Essential documents (authoritative)
- Deployment: [`docs/AZURE_DEPLOYMENT_REFERENCE_GUIDE.md`](docs/AZURE_DEPLOYMENT_REFERENCE_GUIDE.md)
- Architecture: [`ARCHITECTURE_OVERVIEW.md`](ARCHITECTURE_OVERVIEW.md) *(foundation for responsibilities and boundaries)*
- Agents & guardrails: [`AGENT_GOVERNANCE.md`](AGENT_GOVERNANCE.md)
- Security baseline: [`SECURITY.md`](SECURITY.md)
- Contribution essentials: [`CONTRIBUTING.md`](CONTRIBUTING.md)

## Operating principles
- Single source of truth lives here; other legacy docs are informational only once deprecated.
- Keep auth, data, and infra secrets in environment/config—never in code.
- Follow UAE HR compliance rules when modifying HR, attendance, or payroll-adjacent logic (see `apps/hr-portal/**` rules).

## Next step
If you need to deploy: go to [`docs/AZURE_DEPLOYMENT_REFERENCE_GUIDE.md`](docs/AZURE_DEPLOYMENT_REFERENCE_GUIDE.md) and follow it end-to-end. If you need to understand structure: open [`ARCHITECTURE_OVERVIEW.md`](ARCHITECTURE_OVERVIEW.md).
