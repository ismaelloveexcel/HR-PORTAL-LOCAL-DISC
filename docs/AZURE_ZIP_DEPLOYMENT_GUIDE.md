# Azure Zip Deployment Guide

> 🚀 Deploy the HR Portal to Azure App Service by uploading a ZIP package (no GitHub Actions required).

This guide shows how to bundle the repository into a ZIP file and push it directly to Azure App Service using either the Azure CLI or the Azure Portal.

---

## New: one-command package generator

Run the helper script to produce a ready-to-deploy bundle that already contains the built frontend and infrastructure (Bicep) templates:

```bash
./scripts/build_azure_package.sh
```

It outputs `artifacts/azure-deployment-package/` and `artifacts/azure-deployment-package.zip`, which you can deploy with `az webapp deploy --type zip` after setting your app settings.

---

## When to Use ZIP Deployment

- You want a **one-time** or **manual** deployment without setting up GitHub Actions.
- You have a publish profile for the target App Service or can sign in with Azure CLI.
- You need a quick fallback method when CI/CD is unavailable.

---

## Prepare the ZIP Package

1. From the repository root, create a clean archive (exclude build and cache files):
   ```bash
   cd /path/to/AZURE-DEPLOYMENT-HR-PORTAL
   zip -r hr-portal.zip . \
     -x "*.git*" "*/node_modules/*" "frontend/dist/*" "__pycache__/*" "*.pyc" ".pytest_cache/*" ".env*" "*/.venv/*"
   ```
2. Ensure the archive contains these root items (required by Azure Oryx):
   - `requirements.txt` (root-level copy for Azure detection)
   - `app/main.py` (re-export entrypoint)
   - `backend/` and `frontend/` folders

---

## Deploy with Azure CLI (Fastest)

```bash
# 1) Sign in (or use Cloud Shell where you’re already authenticated)
az login

# 2) Variables
RESOURCE_GROUP="<your-rg>"
WEBAPP_NAME="<your-appservice-name>"
ZIP_PATH="hr-portal.zip"

# 3) Required app settings (enable Oryx build + clean logging)
az webapp config appsettings set \
  --resource-group $RESOURCE_GROUP \
  --name $WEBAPP_NAME \
  --settings SCM_DO_BUILD_DURING_DEPLOYMENT=true PYTHONUNBUFFERED=1

# 4) Deploy ZIP (Kudu Zip Deploy)
az webapp deploy \
  --resource-group $RESOURCE_GROUP \
  --name $WEBAPP_NAME \
  --src-path $ZIP_PATH \
  --type zip

# 5) Restart to apply settings
az webapp restart --resource-group $RESOURCE_GROUP --name $WEBAPP_NAME
```

### Post-Deploy Checks

- Browse: `https://$WEBAPP_NAME.azurewebsites.net`
- Health: `https://$WEBAPP_NAME.azurewebsites.net/api/health`
- Logs: `az webapp log tail --resource-group $RESOURCE_GROUP --name $WEBAPP_NAME`

---

## Deploy with Azure Portal (Upload ZIP)

1. Open **Azure Portal** → **App Services** → select your app.
2. Go to **Deployment Center** → **ZIP or WAR** → **Upload**.
3. Upload `hr-portal.zip` and click **Save/Deploy**.
4. Set **Configuration → Application settings**:
   - `SCM_DO_BUILD_DURING_DEPLOYMENT = true`
   - `PYTHONUNBUFFERED = 1`
   - `DATABASE_URL`, `AUTH_SECRET_KEY`, `ALLOWED_ORIGINS`, etc.
5. Restart the app from **Overview → Restart**.

---

## Startup Command (Linux App Service)

Set the startup command to avoid 502/timeout errors:

```
gunicorn app.main:app -k uvicorn.workers.UvicornWorker --bind=0.0.0.0:8000 --workers=2
```

Add this under **Configuration → General settings → Startup Command** or via:

```bash
az webapp config set \
  --resource-group $RESOURCE_GROUP \
  --name $WEBAPP_NAME \
  --startup-file "gunicorn app.main:app -k uvicorn.workers.UvicornWorker --bind=0.0.0.0:8000 --workers=2"
```

---

## Tips & Troubleshooting

- Make sure the ZIP was created from the repository root so `requirements.txt` is at the top level.
- If dependencies fail to install, re-run with `SCM_DO_BUILD_DURING_DEPLOYMENT=true` confirmed in app settings.
- For database migrations, SSH into the App Service and run:
  ```bash
  az webapp ssh --resource-group $RESOURCE_GROUP --name $WEBAPP_NAME
  cd /home/site/wwwroot/backend
  python -m alembic upgrade head
  exit
  ```
- Tail logs during first boot to catch startup issues quickly.
