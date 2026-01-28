#!/usr/bin/env bash
# Build a full Azure deployment package (backend + frontend + DB infra definitions)
# Usage: ./scripts/build_azure_package.sh
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
OUTPUT_DIR="${ROOT_DIR}/artifacts"
PACKAGE_DIR="${OUTPUT_DIR}/azure-deployment-package"
BACKEND_ZIP="${PACKAGE_DIR}/deploy.zip"

echo "📦 Preparing Azure deployment package..."
rm -rf "${PACKAGE_DIR}"
mkdir -p "${PACKAGE_DIR}"

echo "⚛️  Building frontend..."
pushd "${ROOT_DIR}/frontend" >/dev/null
npm ci --silent
if ! npm run build; then
  echo "❌ Frontend build failed"
  exit 1
fi
popd >/dev/null

echo "🔄 Syncing frontend build into backend/static..."
if [ ! -d "${ROOT_DIR}/frontend/dist" ] || [ -z "$(ls -A "${ROOT_DIR}/frontend/dist")" ]; then
  echo "❌ Frontend build output not found in frontend/dist"
  exit 1
fi
rm -rf "${ROOT_DIR}/backend/static"
mkdir -p "${ROOT_DIR}/backend/static"
cp -r "${ROOT_DIR}/frontend/dist/." "${ROOT_DIR}/backend/static/"

echo "🐍 Packaging backend (includes frontend assets)..."
pushd "${ROOT_DIR}/backend" >/dev/null
if [ ! -f "azure_startup.sh" ]; then
  echo "❌ backend/azure_startup.sh missing"
  exit 1
fi
chmod +x azure_startup.sh
zip -r "${BACKEND_ZIP}" . \
  -x "*.pyc" \
  -x "*__pycache__*" \
  -x "*.git*" \
  -x "*.env*" \
  -x "*.example" \
  -x "*.md" \
  -x "*test*.py" \
  -x "*.bak" \
  -x "*.tmp" \
  -x "node_modules/*" \
  -x "dist/*" \
  -x ".vscode/*" \
  -x ".pytest_cache/*" \
  -x "*.log" \
  -x ".DS_Store"
popd >/dev/null

echo "🗂️  Adding infrastructure (Bicep) definitions..."
mkdir -p "${PACKAGE_DIR}/infra"
if [ ! -f "${ROOT_DIR}/infra/main.bicep" ] || [ ! -f "${ROOT_DIR}/infra/resources.bicep" ]; then
  echo "❌ Missing infra/main.bicep or infra/resources.bicep"
  exit 1
fi
cp "${ROOT_DIR}/infra/main.bicep" "${ROOT_DIR}/infra/resources.bicep" "${PACKAGE_DIR}/infra/"
cp "${ROOT_DIR}/azure.yaml" "${PACKAGE_DIR}/"
cat > "${PACKAGE_DIR}/infra/parameters.example.json" <<'EOF'
{
  "$schema": "https://schema.management.azure.com/schemas/2019-04-01/deploymentParameters.json#",
  "contentVersion": "1.0.0.0",
  "parameters": {
    "location": { "value": "eastus2" },
    "resourceGroupName": { "value": "rg-hr-portal" },
    "appServicePlanName": { "value": "hrportal-plan" },
    "backendAppName": { "value": "hrportal-backend" },
    "staticWebAppName": { "value": "hrportal-frontend" },
    "staticWebAppLocation": { "value": "eastus2" },
    "postgresServerName": { "value": "hrportal-db" },
    "postgresAdminUsername": { "value": "hradmin" },
    "postgresAdminPassword": { "value": "<replace-with-secure-password>" },
    "postgresDbName": { "value": "hrportal" },
    "appInsightsName": { "value": "hrportal-ai" },
    "authSecretKey": { "value": "<replace-with-auth-secret>" },
    "databaseUrl": { "value": "postgresql+asyncpg://hradmin:<replace-with-secure-password>@hrportal-db.postgres.database.azure.com:5432/hrportal?sslmode=require" },
    "minCredentialLength": { "value": 8 },
    "sessionTimeoutMinutes": { "value": 480 },
    "allowAzureServices": { "value": true },
    "allowedIpAddresses": { "value": [] }
  }
}
EOF

cat > "${PACKAGE_DIR}/README.md" <<'EOF'
# Azure Deployment Package

Contents:
- deploy.zip — Backend + built frontend ready for Azure App Service zip deploy
- infra/ — Bicep templates for App Service, Static Web App, and PostgreSQL
- azure.yaml — Azure Developer CLI manifest referencing the Bicep templates

How to use:
1) Provision infra (resource group, App Service plan, Web App, PostgreSQL) with the entrypoint template infra/main.bicep (which references infra/resources.bicep). Use a parameters file to avoid exposing secrets (see infra/parameters.example.json):
   az deployment sub create --location <location> --template-file infra/main.bicep --parameters @infra/parameters.json
2) Deploy the application:
   az webapp deploy --resource-group <rg> --name <app-service-name> --src-path deploy.zip --type zip --restart true
3) Ensure App Service settings include DATABASE_URL, AUTH_SECRET_KEY, ALLOWED_ORIGINS, and SCM_DO_BUILD_DURING_DEPLOYMENT=false.
EOF

echo "🗜️  Creating top-level archive..."
pushd "${OUTPUT_DIR}" >/dev/null
zip -r "azure-deployment-package.zip" "$(basename "${PACKAGE_DIR}")" >/dev/null
popd >/dev/null

echo ""
echo "✅ Package ready:"
echo " - Directory: ${PACKAGE_DIR}"
echo " - Archive:   ${OUTPUT_DIR}/azure-deployment-package.zip"
echo ""
echo "Next steps:"
echo " 1) Deploy infra with infra/main.bicep"
echo " 2) Deploy deploy.zip to your App Service (az webapp deploy --type zip)"
echo " 3) Set DATABASE_URL and AUTH_SECRET_KEY in App Service settings"
