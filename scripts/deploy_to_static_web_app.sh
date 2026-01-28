#!/bin/bash
# Deploy HR Portal to Azure Static Web Apps

set -e

# Configuration
STATIC_WEB_APP_NAME="insurance-renewal-portal"
RESOURCE_GROUP="rg-hr-tools"
POSTGRES_SERVER="baynunahhrportal-server"
POSTGRES_RESOURCE_GROUP="BaynunahHR"
DB_NAME="hrportal"

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║     HR Portal - Static Web Apps Deployment                    ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

# Check if password provided
if [ -z "$1" ]; then
  echo "❌ Error: PostgreSQL password required"
  echo ""
  echo "Usage: ./deploy_to_static_web_app.sh 'postgres_password'"
  exit 1
fi

POSTGRES_PASSWORD="$1"

echo "📋 Deployment Configuration:"
echo "   Static Web App: $STATIC_WEB_APP_NAME"
echo "   Resource Group: $RESOURCE_GROUP"
echo "   PostgreSQL: $POSTGRES_SERVER (in $POSTGRES_RESOURCE_GROUP)"
echo "   Database: $DB_NAME"
echo ""

# Step 1: Build Frontend
echo "⚛️  Step 1/4: Building frontend..."
cd frontend
npm install --silent
npm run build
cd ..
echo "   ✅ Frontend built to backend/static"

# Step 2: Get Static Web App deployment token
echo ""
echo "🔑 Step 2/4: Getting deployment token..."
DEPLOYMENT_TOKEN=$(az staticwebapp secrets list \
  --name $STATIC_WEB_APP_NAME \
  --resource-group $RESOURCE_GROUP \
  --query "properties.apiKey" -o tsv)

if [ -z "$DEPLOYMENT_TOKEN" ]; then
  echo "   ❌ Failed to get deployment token"
  exit 1
fi
echo "   ✅ Got deployment token"

# Step 3: Deploy Frontend to Static Web App
echo ""
echo "🚀 Step 3/4: Deploying frontend to Static Web App..."
npx @azure/static-web-apps-cli deploy \
  --app-location backend/static \
  --deployment-token "$DEPLOYMENT_TOKEN" \
  --no-use-keychain

echo "   ✅ Frontend deployed"

# Step 4: Display next steps
echo ""
echo "╔════════════════════════════════════════════════════════════════╗"
echo "║              ⚠️  Next Steps Required ⚠️                        ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""
echo "Your frontend is deployed to Static Web Apps!"
echo ""
echo "🌐 Frontend URL: https://purple-ground-099ab1410.2.azurestaticapps.net"
echo ""
echo "⚠️  Backend API Deployment Options:"
echo ""
echo "Option 1: Create Azure Container App (Recommended)"
echo "  - Best for FastAPI backend"
echo "  - Easy VNet integration"
echo "  - Run: ./scripts/deploy_backend_to_container_app.sh '$POSTGRES_PASSWORD'"
echo ""
echo "Option 2: Create Azure App Service"
echo "  - Run: ./scripts/create_app_service.sh"
echo "  - Then: ./scripts/deploy_backend_to_app_service.sh '$POSTGRES_PASSWORD'"
echo ""
echo "Option 3: Deploy API as Static Web Apps Functions"
echo "  - Requires converting FastAPI to Azure Functions"
echo "  - More complex, not recommended for existing FastAPI app"
echo ""
echo "📝 Recommendation: Use Option 1 (Container App) for easiest deployment"
