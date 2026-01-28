# Azure OIDC Setup Script for GitHub Actions (PowerShell)
# This script automates the complete OIDC configuration process
#
# Prerequisites:
# - Azure CLI installed (https://aka.ms/install-azure-cli)
# - You must be logged into Azure (az login)
# - You must have permissions to create Azure AD applications

$ErrorActionPreference = "Stop"

# Configuration
$REPO_OWNER = "ismaelloveexcel"
$REPO_NAME = "AZURE-DEPLOYMENT-HR-PORTAL"
$APP_DISPLAY_NAME = "GitHub Actions - HR Portal"
$RESOURCE_GROUP = "baynunah-hr-rg"
$FEDERATED_CRED_NAME = "github-actions-main"

Write-Host ""
Write-Host "╔════════════════════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║          Azure OIDC Setup for GitHub Actions - HR Portal                  ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

# Check if Azure CLI is installed
try {
    $null = az version 2>$null
    Write-Host "✓ Azure CLI is installed" -ForegroundColor Green
} catch {
    Write-Host "❌ ERROR: Azure CLI is not installed" -ForegroundColor Red
    Write-Host "Please install it from: https://aka.ms/install-azure-cli"
    exit 1
}

# Check if logged in to Azure
try {
    $null = az account show 2>$null
    Write-Host "✓ Logged in to Azure" -ForegroundColor Green
} catch {
    Write-Host "❌ ERROR: Not logged in to Azure" -ForegroundColor Red
    Write-Host "Please run: az login"
    exit 1
}

Write-Host ""

# Get subscription info
$SUBSCRIPTION_ID = az account show --query id -o tsv
$TENANT_ID = az account show --query tenantId -o tsv
$SUBSCRIPTION_NAME = az account show --query name -o tsv

Write-Host "📋 Azure Account Information:" -ForegroundColor Blue
Write-Host "   Subscription: $SUBSCRIPTION_NAME"
Write-Host "   Subscription ID: $SUBSCRIPTION_ID"
Write-Host "   Tenant ID: $TENANT_ID"
Write-Host ""

# Step 1: Check if app exists or create new one
Write-Host "Step 1: Azure AD Application" -ForegroundColor Yellow
Write-Host "Checking if app '$APP_DISPLAY_NAME' exists..."

$APP_ID = az ad app list --display-name "$APP_DISPLAY_NAME" --query "[0].appId" -o tsv 2>$null

if ([string]::IsNullOrEmpty($APP_ID)) {
    Write-Host "   App does not exist. Creating new application..."
    $APP_ID = az ad app create --display-name "$APP_DISPLAY_NAME" --query appId -o tsv
    Write-Host "   ✓ Created app: $APP_DISPLAY_NAME" -ForegroundColor Green
} else {
    Write-Host "   ✓ App already exists: $APP_DISPLAY_NAME" -ForegroundColor Green
}

Write-Host "   App ID (Client ID): $APP_ID"
Write-Host ""

# Step 2: Create service principal if it doesn't exist
Write-Host "Step 2: Service Principal" -ForegroundColor Yellow
Write-Host "Checking if service principal exists..."

$SP_EXISTS = az ad sp show --id "$APP_ID" --query appId -o tsv 2>$null

if ([string]::IsNullOrEmpty($SP_EXISTS)) {
    Write-Host "   Creating service principal..."
    az ad sp create --id "$APP_ID" | Out-Null
    Write-Host "   ✓ Service principal created" -ForegroundColor Green
} else {
    Write-Host "   ✓ Service principal already exists" -ForegroundColor Green
}
Write-Host ""

# Step 3: Assign Contributor role to resource group
Write-Host "Step 3: Role Assignment" -ForegroundColor Yellow
Write-Host "Checking role assignments on resource group '$RESOURCE_GROUP'..."

# Check if resource group exists
try {
    $null = az group show --name "$RESOURCE_GROUP" 2>$null
} catch {
    Write-Host "   ⚠ Resource group '$RESOURCE_GROUP' does not exist" -ForegroundColor Yellow
    Write-Host "   Creating resource group..."
    az group create --name "$RESOURCE_GROUP" --location westeurope | Out-Null
    Write-Host "   ✓ Resource group created" -ForegroundColor Green
}

# Check if role assignment exists
$ROLE_EXISTS = az role assignment list `
    --assignee "$APP_ID" `
    --role "Contributor" `
    --scope "/subscriptions/$SUBSCRIPTION_ID/resourceGroups/$RESOURCE_GROUP" `
    --query "[0].id" -o tsv 2>$null

if ([string]::IsNullOrEmpty($ROLE_EXISTS)) {
    Write-Host "   Assigning Contributor role..."
    az role assignment create `
        --role Contributor `
        --assignee "$APP_ID" `
        --scope "/subscriptions/$SUBSCRIPTION_ID/resourceGroups/$RESOURCE_GROUP" | Out-Null
    Write-Host "   ✓ Contributor role assigned to resource group" -ForegroundColor Green
} else {
    Write-Host "   ✓ Role already assigned" -ForegroundColor Green
}
Write-Host ""

# Step 4: Create federated credential
Write-Host "Step 4: Federated Credential" -ForegroundColor Yellow
Write-Host "Checking if federated credential '$FEDERATED_CRED_NAME' exists..."

# Check if federated credential exists
$CRED_EXISTS = az ad app federated-credential list --id "$APP_ID" `
    --query "[?name=='$FEDERATED_CRED_NAME'].name" -o tsv 2>$null

if (-not [string]::IsNullOrEmpty($CRED_EXISTS)) {
    Write-Host "   ⚠ Federated credential '$FEDERATED_CRED_NAME' already exists" -ForegroundColor Yellow
    Write-Host "   Deleting existing credential to recreate..."
    az ad app federated-credential delete --id "$APP_ID" --federated-credential-id "$FEDERATED_CRED_NAME" 2>$null | Out-Null
}

Write-Host "   Creating federated credential for GitHub Actions..."

$parameters = @{
    name = $FEDERATED_CRED_NAME
    issuer = "https://token.actions.githubusercontent.com"
    subject = "repo:${REPO_OWNER}/${REPO_NAME}:ref:refs/heads/main"
    description = "GitHub Actions deployment from main branch"
    audiences = @("api://AzureADTokenExchange")
} | ConvertTo-Json -Compress

az ad app federated-credential create --id "$APP_ID" --parameters $parameters | Out-Null

Write-Host "   ✓ Federated credential created" -ForegroundColor Green
Write-Host "   Subject: repo:${REPO_OWNER}/${REPO_NAME}:ref:refs/heads/main"
Write-Host ""

# Step 5: Verify configuration
Write-Host "Step 5: Verification" -ForegroundColor Yellow
Write-Host "Verifying federated credential..."

$CRED_SUBJECT = az ad app federated-credential show `
    --id "$APP_ID" `
    --federated-credential-id "$FEDERATED_CRED_NAME" `
    --query subject -o tsv

if ($CRED_SUBJECT -eq "repo:${REPO_OWNER}/${REPO_NAME}:ref:refs/heads/main") {
    Write-Host "   ✓ Federated credential verified" -ForegroundColor Green
} else {
    Write-Host "   ❌ ERROR: Credential subject mismatch" -ForegroundColor Red
    exit 1
}
Write-Host ""

# Summary
Write-Host "╔════════════════════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║                          SETUP COMPLETE!                                   ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""
Write-Host "✓ Azure AD Application configured" -ForegroundColor Green
Write-Host "✓ Service Principal created" -ForegroundColor Green
Write-Host "✓ Contributor role assigned to resource group" -ForegroundColor Green
Write-Host "✓ Federated credential created for GitHub Actions" -ForegroundColor Green
Write-Host ""
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
Write-Host "📋 GitHub Secrets Configuration" -ForegroundColor Blue
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
Write-Host ""
Write-Host "Add these secrets to GitHub repository:"
Write-Host "URL: https://github.com/${REPO_OWNER}/${REPO_NAME}/settings/secrets/actions"
Write-Host ""
Write-Host "AZURE_CLIENT_ID = $APP_ID"
Write-Host "AZURE_TENANT_ID = $TENANT_ID"
Write-Host "AZURE_SUBSCRIPTION_ID = $SUBSCRIPTION_ID"
Write-Host ""
Write-Host "Note: AZURE_CLIENT_SECRET is no longer needed with OIDC!" -ForegroundColor Yellow
Write-Host ""
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
Write-Host "🚀 Next Steps" -ForegroundColor Blue
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
Write-Host ""
Write-Host "1. Copy the secrets above to GitHub repository settings"
Write-Host "2. Trigger a workflow: https://github.com/${REPO_OWNER}/${REPO_NAME}/actions/workflows/deploy.yml"
Write-Host "3. Click 'Run workflow' and watch the deployment succeed"
Write-Host ""
Write-Host "Setup complete! Your GitHub Actions can now use OIDC authentication." -ForegroundColor Green
Write-Host ""
