#!/bin/bash
# PostgreSQL Server Verification Script

SERVER_NAME="baynunahHRPortal-server"
RESOURCE_GROUP="BaynunahHR"

echo "=== PostgreSQL Server Verification ==="
echo ""

# Check server status
echo "1. Server Status:"
az postgres flexible-server show --name $SERVER_NAME --resource-group $RESOURCE_GROUP --query "{Name:name, State:state, Version:version, Tier:sku.tier}" -o table

echo ""
echo "2. Firewall Rules:"
az postgres flexible-server firewall-rule list --name $SERVER_NAME --resource-group $RESOURCE_GROUP -o table

echo ""
echo "3. Connection String:"
echo "Server: $SERVER_NAME.postgres.database.azure.com"
echo "Format: postgresql+asyncpg://username:password@$SERVER_NAME.postgres.database.azure.com:5432/dbname?ssl=require"

echo ""
echo "4. Databases:"
az postgres flexible-server db list --server-name $SERVER_NAME --resource-group $RESOURCE_GROUP -o table

echo ""
echo "=== Action Items ==="
echo "- Ensure firewall allows App Service IP or enable 'Allow Azure services'"
echo "- Create database if not exists: az postgres flexible-server db create --server-name $SERVER_NAME --resource-group $RESOURCE_GROUP --database-name hrportal"
echo "- Update backend .env with connection string"
