# Azure App Service Deployment Script (for non-technical users)
# This script uses Azure CLI. You can run it in Azure Cloud Shell (no install needed):
# https://shell.azure.com

# Set variables (edit these as needed)
RESOURCE_GROUP="secure-renewals-rg"
APP_SERVICE_PLAN="secure-renewals-plan"
WEBAPP_NAME="secure-renewals-app"
LOCATION="eastus"
GITHUB_REPO="ismaelloveexcel/AZURE-DEPLOYMENT-HR-PORTAL"
BRANCH="main"

# 1. Create resource group
az group create \
  --name $RESOURCE_GROUP \
  --location $LOCATION

# 2. Create Linux App Service Plan
az appservice plan create \
  --name $APP_SERVICE_PLAN \
  --resource-group $RESOURCE_GROUP \
  --sku B1 \
  --is-linux

# 3. Create Web App (Python 3.11)
az webapp create \
  --resource-group $RESOURCE_GROUP \
  --plan $APP_SERVICE_PLAN \
  --name $WEBAPP_NAME \
  --runtime "PYTHON|3.11"

# 4. Configure GitHub Deployment (triggers Oryx build, installs requirements.txt)
az webapp deployment source config \
  --name $WEBAPP_NAME \
  --resource-group $RESOURCE_GROUP \
  --repo-url https://github.com/$GITHUB_REPO \
  --branch $BRANCH \
  --manual-integration

# 5. REQUIRED App Settings (CRITICAL for FastAPI to start reliably)
az webapp config appsettings set \
  --resource-group $RESOURCE_GROUP \
  --name $WEBAPP_NAME \
  --settings \
  SCM_DO_BUILD_DURING_DEPLOYMENT=true \
  PYTHONUNBUFFERED=1

# 6. Environment Variables (edit with your actual values)
az webapp config appsettings set \
  --resource-group $RESOURCE_GROUP \
  --name $WEBAPP_NAME \
  --settings \
  DATABASE_URL="<your-db-url>" \
  AUTH_SECRET_KEY="<your-secret-key>" \
  ALLOWED_ORIGINS="https://$WEBAPP_NAME.azurewebsites.net" \
  APP_ENV="production"

# 7. Set startup command for FastAPI (CRITICAL: requires explicit bind)
# Note: we point Gunicorn directly to backend.app.main:app to avoid import ambiguity
# Oryx builds and installs requirements during deployment
az webapp config set \
  --resource-group $RESOURCE_GROUP \
  --name $WEBAPP_NAME \
  --startup-file "gunicorn backend.app.main:app -k uvicorn.workers.UvicornWorker --bind=0.0.0.0:8000 --workers=2"

# 8. Restart App (DO NOT SKIP - applies settings)
az webapp restart \
  --name $WEBAPP_NAME \
  --resource-group $RESOURCE_GROUP

# 9. (Optional) SSH into the app and run Alembic migrations
# az webapp ssh --resource-group $RESOURCE_GROUP --name $WEBAPP_NAME
# cd /home/site/wwwroot/backend
# python -m alembic upgrade head
# exit

# 10. View logs for troubleshooting
# az webapp log tail --name $WEBAPP_NAME --resource-group $RESOURCE_GROUP

# 11. Done! Your app will be live at: https://$WEBAPP_NAME.azurewebsites.net
