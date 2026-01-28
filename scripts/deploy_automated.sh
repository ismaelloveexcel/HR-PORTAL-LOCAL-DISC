#!/bin/bash
# Master Automated Deployment Script for HR Portal
# Requires: Azure CLI logged in, POSTGRES_PASSWORD env var or first argument

set -e  # Exit on error

# Configuration
APP_SERVICE_NAME="BaynunahHRPortal"
RESOURCE_GROUP="BaynunahHR"
POSTGRES_SERVER="baynunahhrportal-server"
POSTGRES_ADMIN_USER="${POSTGRES_ADMIN_USER:-uutfqkhm}"
VNET_NAME="BaynunahHRPortalVnet"
SUBNET_NAME="AppServiceSubnet"
DB_NAME="hrportal"
AUTO_APPROVE="${AUTO_APPROVE:-false}"
RESET_POSTGRES_PASSWORD="${RESET_POSTGRES_PASSWORD:-false}"
MIGRATION_COMMAND="cd /home/site/wwwroot && python -m alembic upgrade head"
MIGRATION_MAX_ATTEMPTS="${MIGRATION_MAX_ATTEMPTS:-2}"
MIGRATION_RETRY_DELAY="${MIGRATION_RETRY_DELAY:-15}"

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║         HR Portal - Automated Azure Deployment                ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

# Check if password provided
POSTGRES_PASSWORD="${POSTGRES_PASSWORD:-$1}"
if [ -z "$POSTGRES_PASSWORD" ]; then
  echo "❌ Error: PostgreSQL password required (set POSTGRES_PASSWORD or pass as argument)"
  exit 1
fi
AUTH_SECRET=$(openssl rand -hex 32)

echo "📋 Deployment Configuration:"
echo "   Resource Group: $RESOURCE_GROUP"
echo "   App Service: $APP_SERVICE_NAME"
echo "   PostgreSQL: $POSTGRES_SERVER"
echo "   Admin User: $POSTGRES_ADMIN_USER"
echo "   Database: $DB_NAME"
echo ""
if [[ "$AUTO_APPROVE" != "true" && "$CI" != "true" ]]; then
  read -p "Continue? (y/n) " -n 1 -r
  echo ""
  if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    exit 0
  fi
fi

# Step 1: Configure VNet Integration
echo ""
echo "🔧 Step 1/7: Configuring VNet Integration..."
echo "   Creating App Service subnet in VNet..."

# Check if subnet exists
SUBNET_EXISTS=$(az network vnet subnet show \
  --resource-group $RESOURCE_GROUP \
  --vnet-name $VNET_NAME \
  --name $SUBNET_NAME 2>/dev/null || echo "")

if [ -z "$SUBNET_EXISTS" ]; then
  # Find available address space
  az network vnet subnet create \
    --resource-group $RESOURCE_GROUP \
    --vnet-name $VNET_NAME \
    --name $SUBNET_NAME \
    --address-prefixes 10.0.2.0/24 \
    --delegations Microsoft.Web/serverFarms \
    --output none 2>/dev/null || \
  az network vnet subnet create \
    --resource-group $RESOURCE_GROUP \
    --vnet-name $VNET_NAME \
    --name $SUBNET_NAME \
    --address-prefixes 10.0.3.0/24 \
    --delegations Microsoft.Web/serverFarms \
    --output none
  echo "   ✅ Subnet created"
else
  echo "   ✅ Subnet already exists"
fi

echo "   Enabling VNet Integration on App Service..."
az webapp vnet-integration add \
  --name $APP_SERVICE_NAME \
  --resource-group $RESOURCE_GROUP \
  --vnet $VNET_NAME \
  --subnet $SUBNET_NAME \
  --output none 2>/dev/null || echo "   ✅ VNet Integration already enabled"

echo "   ✅ VNet Integration configured"

# Step 2: Create Database
echo ""
echo "🗄️  Step 2/7: Ensuring PostgreSQL access..."
if [[ "$RESET_POSTGRES_PASSWORD" == "true" ]]; then
  az postgres flexible-server update \
    --server-name $POSTGRES_SERVER \
    --resource-group $RESOURCE_GROUP \
    --admin-password "$POSTGRES_PASSWORD" \
    --output none
  echo "   ✅ Admin password updated"
else
  echo "   ⏭️  Skipping admin password update (RESET_POSTGRES_PASSWORD=false)"
fi

echo "   Creating PostgreSQL database..."
DB_EXISTS=$(az postgres flexible-server db show \
  --server-name $POSTGRES_SERVER \
  --resource-group $RESOURCE_GROUP \
  --database-name $DB_NAME 2>/dev/null || echo "")

if [ -z "$DB_EXISTS" ]; then
  az postgres flexible-server db create \
    --server-name $POSTGRES_SERVER \
    --resource-group $RESOURCE_GROUP \
    --database-name $DB_NAME \
    --output none
  echo "   ✅ Database '$DB_NAME' created"
else
  echo "   ✅ Database already exists"
fi

# Step 3: Build Frontend
echo ""
echo "⚛️  Step 3/7: Building frontend..."
cd frontend
npm install --silent
npm run build
cd ..
echo "   ✅ Frontend built"

# Step 4: Prepare Backend
echo ""
echo "🐍 Step 4/7: Preparing backend..."
# Frontend already built to backend/static by vite config
if [ -d "backend/static" ] && [ -f "backend/static/index.html" ]; then
  echo "   ✅ Frontend already in backend/static"
else
  echo "   ⚠️  Frontend not found, attempting manual copy..."
  rm -rf backend/static
  if [ -d "frontend/dist" ]; then
    cp -r frontend/dist backend/static
  fi
fi

# Step 5: Configure App Service
echo ""
echo "⚙️  Step 5/7: Configuring App Service environment..."
az webapp config appsettings set \
  --name $APP_SERVICE_NAME \
  --resource-group $RESOURCE_GROUP \
  --settings \
    DATABASE_URL="postgresql+asyncpg://$POSTGRES_ADMIN_USER:$POSTGRES_PASSWORD@$POSTGRES_SERVER.postgres.database.azure.com:5432/$DB_NAME?ssl=require" \
    AUTH_SECRET_KEY="$AUTH_SECRET" \
    ALLOWED_ORIGINS="https://$APP_SERVICE_NAME.azurewebsites.net" \
    APP_ENV="production" \
    PASSWORD_MIN_LENGTH="8" \
    SESSION_TIMEOUT_HOURS="8" \
  --output none
echo "   ✅ Environment variables configured"

# Step 6: Deploy Application
echo ""
echo "🚀 Step 6/7: Deploying application..."
cd backend
echo "   Creating deployment package..."
zip -r -q ../deploy.zip . \
  -x "*.pyc" \
  -x "*__pycache__*" \
  -x "*.git*" \
  -x "*.env*" \
  -x "*.example" \
  -x "*.md" \
  -x "*.lock" \
  -x "*test*.py" \
  -x "*.bak" \
  -x "*.tmp"
cd ..
echo "   Package size: $(du -h deploy.zip | cut -f1)"
echo "   Uploading to Azure..."
az webapp deployment source config-zip \
  --resource-group $RESOURCE_GROUP \
  --name $APP_SERVICE_NAME \
  --src deploy.zip \
  --output none
rm deploy.zip
echo "   ✅ Application deployed"

# Step 7: Run Database Migrations
echo ""
echo "🔄 Step 7/7: Running database migrations..."
echo "   Waiting for app to start..."
sleep 15

# Run migrations via SSH
echo "   Connecting via SSH to run migrations..."
attempt=1
while true; do
  if az webapp ssh --name $APP_SERVICE_NAME --resource-group $RESOURCE_GROUP --command "$MIGRATION_COMMAND" 2>/dev/null; then
    break
  fi
  if [ "$attempt" -ge "$MIGRATION_MAX_ATTEMPTS" ]; then
    echo "   ❌ Automatic migration failed. Check logs and retry."
    echo "   Logs: az webapp log tail --name $APP_SERVICE_NAME --resource-group $RESOURCE_GROUP"
    exit 1
  fi
  attempt=$((attempt + 1))
  echo "   ⚠️  Migration attempt failed. Retrying in ${MIGRATION_RETRY_DELAY}s..."
  sleep "$MIGRATION_RETRY_DELAY"
done

echo ""
echo "╔════════════════════════════════════════════════════════════════╗"
echo "║                  🎉 Deployment Complete! 🎉                    ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""
echo "📱 Your HR Portal is now live:"
echo "   🌐 App URL:  https://$APP_SERVICE_NAME.azurewebsites.net"
echo "   📚 API Docs: https://$APP_SERVICE_NAME.azurewebsites.net/docs"
echo ""
echo "🔍 Useful commands:"
echo "   View logs:     az webapp log tail --name $APP_SERVICE_NAME --resource-group $RESOURCE_GROUP"
echo "   SSH access:    az webapp ssh --name $APP_SERVICE_NAME --resource-group $RESOURCE_GROUP"
echo "   Restart app:   az webapp restart --name $APP_SERVICE_NAME --resource-group $RESOURCE_GROUP"
echo ""
echo "📝 Next steps:"
echo "   1. Visit the app URL and verify it loads"
echo "   2. Create your first admin user via the API"
echo "   3. Test the login flow"
echo ""
