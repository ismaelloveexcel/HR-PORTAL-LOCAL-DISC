#!/bin/bash
# Quick deployment script for HR Portal to Azure App Service

# Configuration
APP_SERVICE_NAME="BaynunahHRPortal"
RESOURCE_GROUP="BaynunahHR"
POSTGRES_SERVER="baynunahhrportal-server"

echo "=== HR Portal Deployment ==="
echo ""

# Check if password is provided
if [ -z "$1" ]; then
  echo "Usage: ./deploy_quick.sh <postgres_password>"
  echo ""
  echo "Get password from Azure Portal:"
  echo "  1. Go to baynunahhrportal-server"
  echo "  2. Settings → Reset password if needed"
  echo "  3. Run: ./deploy_quick.sh 'your_password_here'"
  exit 1
fi

POSTGRES_PASSWORD="$1"
AUTH_SECRET=$(openssl rand -hex 32)

echo "Step 1: Building frontend..."
cd frontend
npm install
npm run build
cd ..

echo ""
echo "Step 2: Preparing backend..."
rm -rf backend/static
cp -r frontend/dist backend/static

echo ""
echo "Step 3: Configuring App Service..."
az webapp config appsettings set \
  --name $APP_SERVICE_NAME \
  --resource-group $RESOURCE_GROUP \
  --settings \
    DATABASE_URL="postgresql+asyncpg://uutfqkhm:$POSTGRES_PASSWORD@$POSTGRES_SERVER.postgres.database.azure.com:5432/hrportal?ssl=require" \
    AUTH_SECRET_KEY="$AUTH_SECRET" \
    ALLOWED_ORIGINS="https://$APP_SERVICE_NAME.azurewebsites.net" \
    APP_ENV="production" \
    PASSWORD_MIN_LENGTH="8" \
    SESSION_TIMEOUT_HOURS="8"

echo ""
echo "Step 4: Creating deployment package..."
cd backend
zip -r ../deploy.zip . -x "*.pyc" -x "__pycache__/*" -x ".git/*" -x "*.env" -x "alembic.ini.example"
cd ..

echo ""
echo "Step 5: Deploying to Azure..."
az webapp deployment source config-zip \
  --resource-group $RESOURCE_GROUP \
  --name $APP_SERVICE_NAME \
  --src deploy.zip

echo ""
echo "Step 6: Waiting for deployment..."
sleep 10

echo ""
echo "=== Deployment Complete ==="
echo ""
echo "Next steps:"
echo "  1. Run migrations via SSH:"
echo "     az webapp ssh --name $APP_SERVICE_NAME --resource-group $RESOURCE_GROUP"
echo "     cd /home/site/wwwroot && python -m alembic upgrade head"
echo ""
echo "  2. Visit your app:"
echo "     https://$APP_SERVICE_NAME.azurewebsites.net"
echo ""
echo "  3. Check API docs:"
echo "     https://$APP_SERVICE_NAME.azurewebsites.net/docs"
echo ""
echo "  4. View logs:"
echo "     az webapp log tail --name $APP_SERVICE_NAME --resource-group $RESOURCE_GROUP"
