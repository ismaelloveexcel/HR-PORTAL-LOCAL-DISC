# Deploy the HR Portal with Azure Developer CLI

One-command provisioning for the new stack (App Service + Static Web App + PostgreSQL + Application Insights).

## Prerequisites (local machine)
1. Install Azure Developer CLI: `winget install microsoft.azd` (or follow https://aka.ms/azd-install)
2. Install Azure CLI: `winget install Microsoft.AzureCLI` (if not already available)
3. Authenticate: `azd auth login`

## Provision + Deploy
```bash
# From the repo root
azd init # uses the committed azure.yaml

# Create/select an environment (choose a short env name; location defaults to uaenorth)
azd env new prod --location uaenorth

# Set required secrets before provisioning (example values)
azd env set postgresAdminPassword "<strong-db-password>"
azd env set AUTH_SECRET_KEY "<strong-random-secret>"
azd env set PASSWORD_MIN_LENGTH "8"
azd env set SESSION_TIMEOUT_MINUTES "480"
azd env set DATABASE_URL "postgresql://<user>:<password>@hrportal-db-new.postgres.database.azure.com:5432/postgres?sslmode=require"

# Provision all resources and deploy both services
azd up
```

Use the `postgresConnectionStringTemplate` output from `azd env get-values` as a starting point when setting `DATABASE_URL` (replace `<password>` with your admin password).

What azd creates (names are fixed unless you override parameters):
- Resource Group: `rg-hr-portal-new`
- App Service Plan: `hrportal-plan-new`
- Backend App Service (Python 3.11): `hrportal-backend-new`
- PostgreSQL Flexible Server: `hrportal-db-new`
- Static Web App: `hrportal-frontend-new` (deployed in `eastus2`, the nearest SWA-supported region)
- Application Insights linked to the backend
- Postgres admin user defaults to `hradmin` (password = `postgresAdminPassword` set above)

## Expected endpoints
- Backend API & docs: `https://hrportal-backend-new.azurewebsites.net/docs`
- Frontend: `https://hrportal-frontend-new.azurestaticapps.net` (calls the backend via `VITE_API_BASE_URL`)

## Logs & validation
- App Service logs: `az webapp log tail -g rg-hr-portal-new -n hrportal-backend-new`
- Static Web App logs: Azure Portal ➜ Static Web App ➜ Environment ➜ Logs
- Post-deploy health: hit `https://hrportal-backend-new.azurewebsites.net/api/health/ping`

## GitHub CI/CD (push-to-deploy)
If you want automated deploys from `main`, add the required secrets to the repository:
- `AZURE_WEBAPP_PUBLISH_PROFILE_BACKEND` (publish profile for `hrportal-backend-new`)
- `AZURE_STATIC_WEB_APPS_TOKEN` (deployment token for `hrportal-frontend-new`)

The workflows in `.github/workflows/backend-appservice.yml` and `.github/workflows/frontend-staticwebapp.yml` will deploy on each push to `main`.

## Troubleshooting
- **azd up fails on secrets**: ensure the four required env values above are set (`azd env get-values` to confirm).
- **Static Web App build can’t reach backend**: verify `VITE_API_BASE_URL` is set to `https://hrportal-backend-new.azurewebsites.net/api` in the workflow or SWA Configuration.
- **Alembic migrations**: startup command runs `alembic upgrade head` before Uvicorn. Check App Service logs for migration errors.
- **Database access**: the default firewall rule allows only Azure services (`0.0.0.0/0.0.0.0`). Add your client IP as an additional rule in the portal, or set `allowAzureServices=false` and pass `allowedIpAddresses` as a JSON array via `azd env set allowedIpAddresses "[\"1.2.3.4\",\"5.6.7.8\"]"` if you want to lock it down to specific IPs (e.g., App Service outbound IPs).

## Rollback (lightweight)
- Revert the last commit and push to `main`; GitHub Actions will redeploy the previous version.
- Or in Azure Portal: App Service ➜ Deployment Center ➜ select a previous deployment and redeploy.
