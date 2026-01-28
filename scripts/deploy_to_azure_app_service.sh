#!/bin/bash
# Deploy HR Portal to Azure App Service

# Configuration
APP_SERVICE_NAME="BaynunahHRPortal"
RESOURCE_GROUP="BaynunahHR"
POSTGRES_SERVER="baynunahHRPortal-server"

echo "=== HR Portal Deployment to Azure ==="
echo ""

# Step 1: Build Frontend
echo "Step 1: Building Frontend..."
cd frontend
npm install
npm run build
cd ..

echo ""
echo "Step 2: Preparing Backend..."
# Copy frontend build to backend static folder
rm -rf backend/static
cp -r frontend/dist backend/static

echo ""
echo "Step 3: Configure App Service Settings..."
# Set environment variables (update these with your actual values)
az webapp config appsettings set --name $APP_SERVICE_NAME --resource-group $RESOURCE_GROUP --settings \
  DATABASE_URL="postgresql+asyncpg://username:password@$POSTGRES_SERVER.postgres.database.azure.com:5432/hrportal?ssl=require" \
  AUTH_SECRET_KEY="$(openssl rand -hex 32)" \
  ALLOWED_ORIGINS="https://$APP_SERVICE_NAME.azurewebsites.net" \
  APP_ENV="production"

echo ""
echo "Step 4: Deploy Application..."
cd backend
zip -r ../deploy.zip . -x "*.pyc" -x "__pycache__/*" -x ".git/*"
cd ..

az webapp deployment source config-zip --resource-group $RESOURCE_GROUP --name $APP_SERVICE_NAME --src deploy.zip

echo ""
echo "Step 5: Run Database Migrations..."
# SSH into app service and run migrations (manual step required)
echo "SSH to app service and run: cd /home/site/wwwroot && python -m alembic upgrade head"

echo ""
echo "=== Deployment Complete ==="
echo "App URL: https://$APP_SERVICE_NAME.azurewebsites.net"
echo "API Docs: https://$APP_SERVICE_NAME.azurewebsites.net/docs"
