#!/bin/bash
# Configure App Service VNet Integration for Private PostgreSQL Access

APP_SERVICE_NAME="BaynunahHRPortal"
RESOURCE_GROUP="BaynunahHR"
VNET_NAME="BaynunahHRPortalVnet"
SUBNET_NAME="AppServiceSubnet"  # We'll create this subnet for App Service

echo "=== Configuring VNet Integration for App Service ==="
echo ""

# Step 1: Create a new subnet for App Service in the same VNet
echo "Step 1: Creating App Service subnet in VNet..."
az network vnet subnet create \
  --resource-group $RESOURCE_GROUP \
  --vnet-name $VNET_NAME \
  --name $SUBNET_NAME \
  --address-prefixes 10.0.1.0/24 \
  --delegations Microsoft.Web/serverFarms

echo ""
echo "Step 2: Enable VNet Integration on App Service..."
az webapp vnet-integration add \
  --name $APP_SERVICE_NAME \
  --resource-group $RESOURCE_GROUP \
  --vnet $VNET_NAME \
  --subnet $SUBNET_NAME

echo ""
echo "Step 3: Verify VNet Integration..."
az webapp vnet-integration list \
  --name $APP_SERVICE_NAME \
  --resource-group $RESOURCE_GROUP

echo ""
echo "=== VNet Integration Complete ==="
echo "App Service can now access PostgreSQL through private networking"
echo ""
echo "Next: Create database and run deployment"
echo "  1. Create database: az postgres flexible-server db create --server-name baynunahhrportal-server --resource-group BaynunahHR --database-name hrportal"
echo "  2. Run: ./scripts/deploy_quick.sh 'your_postgres_password'"
