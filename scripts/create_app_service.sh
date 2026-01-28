#!/bin/bash
# Create Azure App Service for HR Portal Backend

set -e

APP_SERVICE_NAME="BaynunahHRPortal"
RESOURCE_GROUP="BaynunahHR"
LOCATION="uaenorth"
PLAN_NAME="BaynunahHRPortal-plan"
SKU="B1"  # Basic tier

echo "=== Creating Azure App Service ==="
echo ""

# Step 1: Create App Service Plan
echo "Step 1: Creating App Service Plan..."
az appservice plan create \
  --name $PLAN_NAME \
  --resource-group $RESOURCE_GROUP \
  --location $LOCATION \
  --sku $SKU \
  --is-linux \
  --output none

echo "   ✅ App Service Plan created"

# Step 2: Create Web App
echo ""
echo "Step 2: Creating Web App..."
az webapp create \
  --name $APP_SERVICE_NAME \
  --resource-group $RESOURCE_GROUP \
  --plan $PLAN_NAME \
  --runtime "PYTHON:3.11" \
  --output none

echo "   ✅ Web App created"

# Step 3: Configure startup command
echo ""
echo "Step 3: Configuring startup command..."
az webapp config set \
  --name $APP_SERVICE_NAME \
  --resource-group $RESOURCE_GROUP \
  --startup-file "python -m uvicorn app.main:app --host 0.0.0.0 --port 8000" \
  --output none

echo "   ✅ Startup command configured"

echo ""
echo "=== App Service Created Successfully ==="
echo "   Name: $APP_SERVICE_NAME"
echo "   URL: https://$APP_SERVICE_NAME.azurewebsites.net"
echo ""
echo "Next: Run deployment script"
echo "   ./scripts/deploy_automated.sh 'your_password'"
