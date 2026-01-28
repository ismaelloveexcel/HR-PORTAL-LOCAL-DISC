#!/bin/bash

# Azure OIDC Setup Script for GitHub Actions
# This script automates the complete OIDC configuration process
#
# Prerequisites:
# - Azure CLI installed (https://aka.ms/install-azure-cli)
# - You must be logged into Azure (az login)
# - You must have permissions to create Azure AD applications

set -e  # Exit on any error

# Configuration
REPO_OWNER="ismaelloveexcel"
REPO_NAME="AZURE-DEPLOYMENT-HR-PORTAL"
APP_DISPLAY_NAME="GitHub Actions - HR Portal"
RESOURCE_GROUP="baynunah-hr-rg"
FEDERATED_CRED_NAME="github-actions-main"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo ""
echo "╔════════════════════════════════════════════════════════════════════════════╗"
echo "║          Azure OIDC Setup for GitHub Actions - HR Portal                  ║"
echo "╚════════════════════════════════════════════════════════════════════════════╝"
echo ""

# Check if Azure CLI is installed
if ! command -v az &> /dev/null; then
    echo -e "${RED}❌ ERROR: Azure CLI is not installed${NC}"
    echo "Please install it from: https://aka.ms/install-azure-cli"
    exit 1
fi

echo -e "${GREEN}✓${NC} Azure CLI is installed"

# Check if logged in to Azure
if ! az account show &> /dev/null; then
    echo -e "${RED}❌ ERROR: Not logged in to Azure${NC}"
    echo "Please run: az login"
    exit 1
fi

echo -e "${GREEN}✓${NC} Logged in to Azure"
echo ""

# Get subscription info
SUBSCRIPTION_ID=$(az account show --query id -o tsv)
TENANT_ID=$(az account show --query tenantId -o tsv)
SUBSCRIPTION_NAME=$(az account show --query name -o tsv)

echo -e "${BLUE}📋 Azure Account Information:${NC}"
echo "   Subscription: $SUBSCRIPTION_NAME"
echo "   Subscription ID: $SUBSCRIPTION_ID"
echo "   Tenant ID: $TENANT_ID"
echo ""

# Step 1: Check if app exists or create new one
echo -e "${YELLOW}Step 1: Azure AD Application${NC}"
echo "Checking if app '$APP_DISPLAY_NAME' exists..."

APP_ID=$(az ad app list --display-name "$APP_DISPLAY_NAME" --query "[0].appId" -o tsv 2>/dev/null || echo "")

if [ -z "$APP_ID" ]; then
    echo "   App does not exist. Creating new application..."
    APP_ID=$(az ad app create --display-name "$APP_DISPLAY_NAME" --query appId -o tsv)
    echo -e "   ${GREEN}✓${NC} Created app: $APP_DISPLAY_NAME"
else
    echo -e "   ${GREEN}✓${NC} App already exists: $APP_DISPLAY_NAME"
fi

echo "   App ID (Client ID): $APP_ID"
echo ""

# Step 2: Create service principal if it doesn't exist
echo -e "${YELLOW}Step 2: Service Principal${NC}"
echo "Checking if service principal exists..."

SP_EXISTS=$(az ad sp show --id "$APP_ID" --query appId -o tsv 2>/dev/null || echo "")

if [ -z "$SP_EXISTS" ]; then
    echo "   Creating service principal..."
    az ad sp create --id "$APP_ID" > /dev/null
    echo -e "   ${GREEN}✓${NC} Service principal created"
else
    echo -e "   ${GREEN}✓${NC} Service principal already exists"
fi
echo ""

# Step 3: Assign Contributor role to resource group
echo -e "${YELLOW}Step 3: Role Assignment${NC}"
echo "Checking role assignments on resource group '$RESOURCE_GROUP'..."

# Check if resource group exists
if ! az group show --name "$RESOURCE_GROUP" &> /dev/null; then
    echo -e "   ${YELLOW}⚠${NC}  Resource group '$RESOURCE_GROUP' does not exist"
    echo "   Creating resource group..."
    az group create --name "$RESOURCE_GROUP" --location westeurope > /dev/null
    echo -e "   ${GREEN}✓${NC} Resource group created"
fi

# Check if role assignment exists
ROLE_EXISTS=$(az role assignment list \
    --assignee "$APP_ID" \
    --role "Contributor" \
    --scope "/subscriptions/$SUBSCRIPTION_ID/resourceGroups/$RESOURCE_GROUP" \
    --query "[0].id" -o tsv 2>/dev/null || echo "")

if [ -z "$ROLE_EXISTS" ]; then
    echo "   Assigning Contributor role..."
    az role assignment create \
        --role Contributor \
        --assignee "$APP_ID" \
        --scope "/subscriptions/$SUBSCRIPTION_ID/resourceGroups/$RESOURCE_GROUP" \
        > /dev/null
    echo -e "   ${GREEN}✓${NC} Contributor role assigned to resource group"
else
    echo -e "   ${GREEN}✓${NC} Role already assigned"
fi
echo ""

# Step 4: Create federated credential
echo -e "${YELLOW}Step 4: Federated Credential${NC}"
echo "Checking if federated credential '$FEDERATED_CRED_NAME' exists..."

# Check if federated credential exists
CRED_EXISTS=$(az ad app federated-credential list --id "$APP_ID" \
    --query "[?name=='$FEDERATED_CRED_NAME'].name" -o tsv 2>/dev/null || echo "")

if [ -n "$CRED_EXISTS" ]; then
    echo -e "   ${YELLOW}⚠${NC}  Federated credential '$FEDERATED_CRED_NAME' already exists"
    echo "   Deleting existing credential to recreate..."
    az ad app federated-credential delete --id "$APP_ID" --federated-credential-id "$FEDERATED_CRED_NAME" 2>/dev/null || true
fi

echo "   Creating federated credential for GitHub Actions..."
az ad app federated-credential create \
    --id "$APP_ID" \
    --parameters "{
        \"name\": \"$FEDERATED_CRED_NAME\",
        \"issuer\": \"https://token.actions.githubusercontent.com\",
        \"subject\": \"repo:$REPO_OWNER/$REPO_NAME:ref:refs/heads/main\",
        \"description\": \"GitHub Actions deployment from main branch\",
        \"audiences\": [\"api://AzureADTokenExchange\"]
    }" > /dev/null

echo -e "   ${GREEN}✓${NC} Federated credential created"
echo "   Subject: repo:$REPO_OWNER/$REPO_NAME:ref:refs/heads/main"
echo ""

# Step 5: Verify configuration
echo -e "${YELLOW}Step 5: Verification${NC}"
echo "Verifying federated credential..."

CRED_SUBJECT=$(az ad app federated-credential show \
    --id "$APP_ID" \
    --federated-credential-id "$FEDERATED_CRED_NAME" \
    --query subject -o tsv)

if [ "$CRED_SUBJECT" == "repo:$REPO_OWNER/$REPO_NAME:ref:refs/heads/main" ]; then
    echo -e "   ${GREEN}✓${NC} Federated credential verified"
else
    echo -e "   ${RED}❌ ERROR: Credential subject mismatch${NC}"
    exit 1
fi
echo ""

# Summary
echo "╔════════════════════════════════════════════════════════════════════════════╗"
echo "║                          SETUP COMPLETE!                                   ║"
echo "╚════════════════════════════════════════════════════════════════════════════╝"
echo ""
echo -e "${GREEN}✓${NC} Azure AD Application configured"
echo -e "${GREEN}✓${NC} Service Principal created"
echo -e "${GREEN}✓${NC} Contributor role assigned to resource group"
echo -e "${GREEN}✓${NC} Federated credential created for GitHub Actions"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo -e "${BLUE}📋 GitHub Secrets Configuration${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Add these secrets to GitHub repository:"
echo "URL: https://github.com/$REPO_OWNER/$REPO_NAME/settings/secrets/actions"
echo ""
echo "AZURE_CLIENT_ID = $APP_ID"
echo "AZURE_TENANT_ID = $TENANT_ID"
echo "AZURE_SUBSCRIPTION_ID = $SUBSCRIPTION_ID"
echo ""
echo "Note: AZURE_CLIENT_SECRET is no longer needed with OIDC!"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo -e "${BLUE}🚀 Next Steps${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "1. Copy the secrets above to GitHub repository settings"
echo "2. Trigger a workflow: https://github.com/$REPO_OWNER/$REPO_NAME/actions/workflows/deploy.yml"
echo "3. Click 'Run workflow' and watch the deployment succeed"
echo ""
echo -e "${GREEN}Setup complete! Your GitHub Actions can now use OIDC authentication.${NC}"
echo ""
