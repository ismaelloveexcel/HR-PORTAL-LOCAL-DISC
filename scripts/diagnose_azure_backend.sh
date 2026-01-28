#!/bin/bash
# Azure Backend Diagnostic Script
# Purpose: Diagnose why hrportal-backend-new is not responding
# Usage: bash scripts/diagnose_azure_backend.sh

set -e

WEBAPP_NAME="hrportal-backend-new"
RESOURCE_GROUP="baynunah-hr-portal-rg"
WEBAPP_URL="https://hrportal-backend-new.azurewebsites.net"

echo "=========================================="
echo "Azure Backend Diagnostic Tool"
echo "=========================================="
echo ""

# Check if Azure CLI is installed
if ! command -v az &> /dev/null; then
    echo "❌ Azure CLI not found. Please install it:"
    echo "   https://docs.microsoft.com/en-us/cli/azure/install-azure-cli"
    exit 1
fi

echo "✅ Azure CLI found"

# Check if jq is installed (optional but recommended)
if ! command -v jq &> /dev/null; then
    echo "ℹ️  'jq' not found. Install jq for pretty JSON output: https://stedolan.github.io/jq/"
    echo "   Script will continue without jq..."
    JQ_AVAILABLE=false
else
    echo "✅ jq found"
    JQ_AVAILABLE=true
fi
echo ""

# Check if logged in
echo "Checking Azure authentication..."
if ! az account show &> /dev/null; then
    echo "❌ Not logged into Azure. Please run: az login"
    exit 1
fi

echo "✅ Authenticated to Azure"
echo "Subscription: $(az account show --query name -o tsv)"
echo ""

# 1. Check App Service Status
echo "=========================================="
echo "1. App Service Status"
echo "=========================================="
APP_STATUS=$(az webapp show \
    --name "$WEBAPP_NAME" \
    --resource-group "$RESOURCE_GROUP" \
    --query "{state:state, enabled:enabled, defaultHostName:defaultHostName}" \
    -o json 2>&1)

if [ $? -eq 0 ]; then
    if [ "$JQ_AVAILABLE" = true ]; then
        echo "$APP_STATUS" | jq .
    else
        echo "$APP_STATUS"
    fi
    
    STATE=$(echo "$APP_STATUS" | jq -r '.state' 2>/dev/null || echo "$APP_STATUS" | grep -oP '(?<="state":")[^"]*' || echo "unknown")
    ENABLED=$(echo "$APP_STATUS" | jq -r '.enabled' 2>/dev/null || echo "$APP_STATUS" | grep -oP '(?<="enabled":")[^"]*' || echo "unknown")
    
    if [ "$STATE" != "Running" ]; then
        echo "⚠️  App is not running! Current state: $STATE"
        echo ""
        set +e  # Disable exit on error for interactive prompt
        read -p "Would you like to start the app? (y/n) " -n 1 -r
        echo
        set -e  # Re-enable exit on error
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            echo "Starting app..."
            az webapp start --name "$WEBAPP_NAME" --resource-group "$RESOURCE_GROUP"
            echo "✅ App started. Waiting 30 seconds..."
            sleep 30
        fi
    elif [ "$ENABLED" != "true" ]; then
        echo "⚠️  App is disabled!"
    else
        echo "✅ App is running and enabled"
    fi
else
    echo "❌ Failed to get app status:"
    echo "$APP_STATUS"
fi
echo ""

# 2. Check App Settings
echo "=========================================="
echo "2. Critical App Settings"
echo "=========================================="
echo "Checking for required environment variables..."

SETTINGS=$(az webapp config appsettings list \
    --name "$WEBAPP_NAME" \
    --resource-group "$RESOURCE_GROUP" \
    -o json 2>&1)

if [ $? -eq 0 ]; then
    # Check critical settings (without revealing values)
    for key in "DATABASE_URL" "AUTH_SECRET_KEY" "APP_ENV"; do
        VALUE=$(echo "$SETTINGS" | jq -r ".[] | select(.name==\"$key\") | .value")
        if [ -z "$VALUE" ] || [ "$VALUE" = "null" ]; then
            echo "❌ $key: NOT SET"
        else
            echo "✅ $key: SET (length: ${#VALUE} chars)"
        fi
    done
else
    echo "❌ Failed to get app settings"
fi
echo ""

# 3. Check Recent Deployments
echo "=========================================="
echo "3. Recent Deployments"
echo "=========================================="
DEPLOYMENTS=$(az webapp deployment list \
    --name "$WEBAPP_NAME" \
    --resource-group "$RESOURCE_GROUP" \
    --query "[0:3].{id:id, status:status, received:received_time, deployer:deployer}" \
    -o table 2>&1)

if [ $? -eq 0 ]; then
    echo "$DEPLOYMENTS"
else
    echo "❌ Failed to get deployment history"
fi
echo ""

# 4. Check Application Logs (last 50 lines)
echo "=========================================="
echo "4. Recent Application Logs"
echo "=========================================="
echo "Fetching last 50 log entries..."

LOG_OUTPUT=$(az webapp log download \
    --name "$WEBAPP_NAME" \
    --resource-group "$RESOURCE_GROUP" \
    --log-file /tmp/webapp_logs.zip 2>&1)

if [ $? -eq 0 ]; then
    echo "✅ Logs downloaded to /tmp/webapp_logs.zip"
    echo "Extracting relevant errors..."
    unzip -q -o /tmp/webapp_logs.zip -d /tmp/webapp_logs/
    
    # Check if any log files exist
    if [ -n "$(find /tmp/webapp_logs/LogFiles/Application/ -name '*.log' 2>/dev/null)" ]; then
        echo "Recent Python errors:"
        grep -i "error\|exception\|traceback" /tmp/webapp_logs/LogFiles/Application/*.log | tail -20 || echo "No errors found"
    else
        echo "No application log files found in expected location"
    fi
else
    echo "⚠️  Log download failed, trying log stream..."
    timeout 5 az webapp log tail \
        --name "$WEBAPP_NAME" \
        --resource-group "$RESOURCE_GROUP" 2>&1 | head -50 || echo "Log stream unavailable"
fi
echo ""

# 5. Test Connectivity
echo "=========================================="
echo "5. Connectivity Test"
echo "=========================================="
echo "Testing $WEBAPP_URL/api/health/ping ..."

RESPONSE=$(curl -s -w "\n%{http_code}" -m 10 "$WEBAPP_URL/api/health/ping" 2>&1)
HTTP_CODE=$(echo "$RESPONSE" | tail -1)
BODY=$(echo "$RESPONSE" | head -n -1)

if [ "$HTTP_CODE" = "200" ]; then
    echo "✅ Backend is responding!"
    echo "Response: $BODY"
else
    echo "❌ Backend not responding (HTTP $HTTP_CODE)"
    echo "Response: $BODY"
fi
echo ""

# 6. Database Connection Test
echo "=========================================="
echo "6. Database Connection"
echo "=========================================="
echo "Testing $WEBAPP_URL/api/health/db ..."

DB_RESPONSE=$(curl -s -w "\n%{http_code}" -m 10 "$WEBAPP_URL/api/health/db" 2>&1)
DB_HTTP_CODE=$(echo "$DB_RESPONSE" | tail -1)
DB_BODY=$(echo "$DB_RESPONSE" | head -n -1)

if [ "$DB_HTTP_CODE" = "200" ]; then
    echo "✅ Database connection working"
    if [ "$JQ_AVAILABLE" = true ]; then
        echo "Response: $DB_BODY" | jq .
    else
        echo "Response: $DB_BODY"
    fi
else
    echo "❌ Database connection issue (HTTP $DB_HTTP_CODE)"
    echo "Response: $DB_BODY"
fi
echo ""

# 7. Recommendations
echo "=========================================="
echo "7. Recommendations"
echo "=========================================="

if [ "$HTTP_CODE" != "200" ]; then
    echo "🔧 ACTIONS TO TRY:"
    echo ""
    echo "1. Restart the app service:"
    echo "   az webapp restart --name $WEBAPP_NAME --resource-group $RESOURCE_GROUP"
    echo ""
    echo "2. Check platform logs in Azure Portal:"
    echo "   https://portal.azure.com → $WEBAPP_NAME → Monitoring → Log stream"
    echo ""
    echo "3. Verify startup command:"
    echo "   az webapp config show --name $WEBAPP_NAME --resource-group $RESOURCE_GROUP --query 'linuxFxVersion'"
    echo ""
    echo "4. Check for memory/CPU issues:"
    echo "   https://portal.azure.com → $WEBAPP_NAME → Metrics"
    echo ""
    echo "5. Review Oryx build logs:"
    echo "   https://$WEBAPP_NAME.scm.azurewebsites.net → Debug console → Bash"
    echo ""
else
    echo "✅ Backend appears healthy!"
    echo ""
    echo "To see backend version info (after the version tracking feature is deployed):"
    echo "curl $WEBAPP_URL/api/health/revision"
fi

echo ""
echo "=========================================="
echo "Diagnostic Complete"
echo "=========================================="
