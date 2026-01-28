
# Azure Deployment Agent (GitHub Actions)

This folder contains reusable CI/CD workflows and infrastructure-as-code you can drop into **any** repo to deploy a web app to Azure. It supports two targets:

1. **Azure App Service (Code)** – for server-rendered apps/APIs (.NET, Node.js/Express, Python/Flask, Java, PHP). Uses blue/green via **staging** slot + swap.
2. **Azure Static Web Apps** – for static front-ends (React, Vue, Angular, Vite, Next.js static export). Optional Azure Functions API.

---
## Quick start

1. **Create Azure resources** (choose one):
   - *App Service*: create Resource Group, App Service Plan (Linux), and a Web App. Also create a **staging** slot.
   - *Static Web App*: create a Static Web App in the Azure portal.

2. **Configure GitHub secrets**
   - For OIDC login to Azure (recommended):
     - `AZURE_CLIENT_ID` – Microsoft Entra App (Service Principal) **Client ID**
     - `AZURE_TENANT_ID` – Tenant ID
     - `AZURE_SUBSCRIPTION_ID` – Subscription ID
   - For Static Web Apps only:
     - `AZURE_STATIC_WEB_APPS_API_TOKEN` – SWA deployment token

3. **Pick one workflow**
   - Keep **deploy-appservice.yml** for App Service
   - or keep **deploy-swa.yml** for Static Web Apps
   - (You can keep both and disable one by setting `if: false` in the job.)

4. **Push to `main`** – CI builds, runs tests, deploys to staging, runs smoke-tests, then swaps to production on success.

---
## Files

- `.github/workflows/ci.yml` – Lint + Test + Build
- `.github/workflows/deploy-appservice.yml` – App Service blue/green deploy using OIDC + `azure/webapps-deploy`
- `.github/workflows/deploy-swa.yml` – Static Web Apps deploy using `Azure/static-web-apps-deploy`
- `.github/workflows/issueops.yml` – ChatOps commands: `/deploy`, `/promote`, `/rollback`, `/restart`
- `infra/bicep/appservice.bicep` – App Service Plan, Web App, **staging** slot
- `scripts/smoke-test.sh` – Simple HTTP smoke-test
- `docs/README-DEPLOYMENT.md` – Detailed setup guide

---
## Notes

- Uses **OpenID Connect (OIDC)** for GitHub → Azure authentication. No long-lived secrets.
- If your app is containerized, replace App Service workflow with **Azure Container Apps** via `azure/container-apps-deploy-action`.
- Workflows are safe-by-default with deployment protections and concurrency.
