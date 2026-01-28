
# Deployment Guide

## 1) Authenticate GitHub → Azure with OIDC

1. Create (or use) a Microsoft Entra App (Service Principal) and grant it **Contributor** on the target Resource Group.
2. Add a **Federated identity credential** for your GitHub repo to enable OIDC tokens.
3. In GitHub repo **Secrets and variables → Actions**, add:
   - `AZURE_CLIENT_ID` – App (client) ID
   - `AZURE_TENANT_ID` – Directory (tenant) ID
   - `AZURE_SUBSCRIPTION_ID` – Subscription ID

## 2) Provision infrastructure

EITHER provision manually in the portal, OR deploy `infra/bicep/appservice.bicep` from Cloud Shell:

```bash
az group create -n rg-employee-leave -l eastus
az deployment group create       -g rg-employee-leave       -f infra/bicep/appservice.bicep       -p webAppName=employee-leave-web planName=plan-employee-leave sku=B1
```

## 3) Pick your deployment target

- **App Service** (server-side apps): keep `.github/workflows/deploy-appservice.yml` and set repository **Variables**:
  - `AZURE_RESOURCE_GROUP`, `AZURE_WEBAPP_NAME` (or edit env in the YAML)
- **Static Web Apps** (frontend only): keep `.github/workflows/deploy-swa.yml` and add `AZURE_STATIC_WEB_APPS_API_TOKEN` secret (find it in SWA → Deployment token).

## 4) Operate with IssueOps

Comment `/deploy` on any issue or PR to trigger a deployment to staging; CI will auto-promote to production on a passing smoke test. Use `/promote` to force slot swap, `/rollback` to swap back, `/restart` to restart the app.

## Troubleshooting

- Ensure your app listens on the port expected by the runtime (for Node, default is 8080/Port binding via `PORT`).
- If using `webapps-deploy`, package size limit applies; enable `WEBSITE_RUN_FROM_PACKAGE=1` as provided in Bicep.
- For containerized apps, switch to Container Apps workflow.
