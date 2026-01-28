# Azure OIDC Configuration - Quick Setup Guide

This document provides the exact commands needed to configure Azure federated credentials for OIDC authentication with GitHub Actions.

## ⚡ Quick Setup (5 Minutes)

### Step 1: Login to Azure
```bash
az login
```

### Step 2: Get or Create Azure AD Application

**Option A: Use existing application**
```bash
# List existing applications
az ad app list --display-name "GitHub Actions" --query "[].{Name:displayName, AppId:appId}" -o table

# Get the appId of your application
APP_ID=$(az ad app list --display-name "GitHub Actions - HR Portal" --query "[0].appId" -o tsv)
echo "App ID: $APP_ID"
```

**Option B: Create new application** (if you don't have one)
```bash
# Create Azure AD application
az ad app create --display-name "GitHub Actions - HR Portal"

# Get the appId from the output and save it
APP_ID="<paste-app-id-here>"
```

### Step 3: Create Service Principal (if not exists)
```bash
# Create service principal for the app
az ad sp create --id $APP_ID

# Assign Contributor role to resource group
SUBSCRIPTION_ID=$(az account show --query id -o tsv)
az role assignment create \
  --role Contributor \
  --assignee $APP_ID \
  --scope /subscriptions/$SUBSCRIPTION_ID/resourceGroups/baynunah-hr-rg
```

### Step 4: Create Federated Credential for Main Branch
```bash
# Create federated credential for main branch
az ad app federated-credential create \
  --id $APP_ID \
  --parameters '{
    "name": "github-actions-main",
    "issuer": "https://token.actions.githubusercontent.com",
    "subject": "repo:ismaelloveexcel/AZURE-DEPLOYMENT-HR-PORTAL:ref:refs/heads/main",
    "description": "GitHub Actions deployment from main branch",
    "audiences": ["api://AzureADTokenExchange"]
  }'
```

**Success!** You should see output like:
```json
{
  "audiences": ["api://AzureADTokenExchange"],
  "description": "GitHub Actions deployment from main branch",
  "issuer": "https://token.actions.githubusercontent.com",
  "name": "github-actions-main",
  "subject": "repo:ismaelloveexcel/AZURE-DEPLOYMENT-HR-PORTAL:ref:refs/heads/main"
}
```

### Step 5: Get Values for GitHub Secrets
```bash
# Get all required IDs
echo "=== Copy these values to GitHub Secrets ==="
echo ""
echo "AZURE_CLIENT_ID:        $APP_ID"
echo "AZURE_TENANT_ID:        $(az account show --query tenantId -o tsv)"
echo "AZURE_SUBSCRIPTION_ID:  $(az account show --query id -o tsv)"
echo ""
echo "Add these in GitHub: Settings → Secrets and variables → Actions"
```

### Step 6: Configure GitHub Secrets

Go to: `https://github.com/ismaelloveexcel/AZURE-DEPLOYMENT-HR-PORTAL/settings/secrets/actions`

Add or update these secrets:
- `AZURE_CLIENT_ID` → Use value from Step 5
- `AZURE_TENANT_ID` → Use value from Step 5
- `AZURE_SUBSCRIPTION_ID` → Use value from Step 5

**Note:** `AZURE_CLIENT_SECRET` is no longer needed with OIDC!

### Step 7: Test Deployment

**Option A: Manual trigger**
1. Go to: `https://github.com/ismaelloveexcel/AZURE-DEPLOYMENT-HR-PORTAL/actions/workflows/deploy.yml`
2. Click "Run workflow" → "Run workflow"
3. Watch the logs for successful Azure login

**Option B: Push to main**
```bash
git push origin main
```

Watch for this output in the "Login to Azure" step:
```
✅ Login successful
```

---

## 🔍 Verification Commands

### Check if federated credential exists
```bash
az ad app federated-credential list --id $APP_ID
```

### Check role assignments
```bash
az role assignment list --assignee $APP_ID --query "[].{Role:roleDefinitionName, Scope:scope}" -o table
```

### Check Azure resources
```bash
# Verify resource group exists
az group show --name baynunah-hr-rg

# Verify App Service exists
az webapp show --name baynunah-hr-portal --resource-group baynunah-hr-rg
```

---

## 🚨 Troubleshooting

### Error: "No matching federated identity record found"
```bash
# Verify the subject matches exactly
az ad app federated-credential list --id $APP_ID --query "[].subject"

# It should be: repo:ismaelloveexcel/AZURE-DEPLOYMENT-HR-PORTAL:ref:refs/heads/main
```

### Error: "Application not found"
```bash
# Verify APP_ID is correct
az ad app show --id $APP_ID
```

### Error: "AuthorizationFailed"
```bash
# Check role assignments
az role assignment list --assignee $APP_ID

# If empty, assign Contributor role (see Step 3)
```

### Workflow fails at secrets validation
```bash
# Verify all secrets are set in GitHub
# Go to: https://github.com/ismaelloveexcel/AZURE-DEPLOYMENT-HR-PORTAL/settings/secrets/actions

# Check for:
# - AZURE_CLIENT_ID
# - AZURE_TENANT_ID
# - AZURE_SUBSCRIPTION_ID
# - DATABASE_URL
# - AUTH_SECRET_KEY
```

---

## 🎯 Success Criteria

Before considering setup complete:

- [ ] Azure AD application created
- [ ] Service principal created with Contributor role
- [ ] Federated credential created for main branch
- [ ] GitHub secrets updated (CLIENT_ID, TENANT_ID, SUBSCRIPTION_ID)
- [ ] Test deployment completed successfully
- [ ] App accessible at: https://baynunah-hr-portal.azurewebsites.net

---

## 🔐 Optional: Add Federated Credentials for Other Branches

For develop branch:
```bash
az ad app federated-credential create \
  --id $APP_ID \
  --parameters '{
    "name": "github-actions-develop",
    "issuer": "https://token.actions.githubusercontent.com",
    "subject": "repo:ismaelloveexcel/AZURE-DEPLOYMENT-HR-PORTAL:ref:refs/heads/develop",
    "description": "GitHub Actions deployment from develop branch",
    "audiences": ["api://AzureADTokenExchange"]
  }'
```

For pull requests (if needed):
```bash
az ad app federated-credential create \
  --id $APP_ID \
  --parameters '{
    "name": "github-actions-pr",
    "issuer": "https://token.actions.githubusercontent.com",
    "subject": "repo:ismaelloveexcel/AZURE-DEPLOYMENT-HR-PORTAL:pull_request",
    "description": "GitHub Actions for pull requests",
    "audiences": ["api://AzureADTokenExchange"]
  }'
```

---

## 📚 Additional Documentation

- **Full OIDC Guide:** [docs/AZURE_OIDC_SETUP.md](AZURE_OIDC_SETUP.md)
- **Deployment Guide:** [docs/GITHUB_DEPLOYMENT_SETUP.md](GITHUB_DEPLOYMENT_SETUP.md)
- **Troubleshooting:** [docs/WORKFLOW_DEPLOYMENT_FIXES.md](WORKFLOW_DEPLOYMENT_FIXES.md)

---

## 🗑️ Cleanup (After Successful OIDC Setup)

Once OIDC is working, you can optionally remove the old client secret:

```bash
# List current credentials
az ad app credential list --id $APP_ID

# Delete client secret (optional - keep as backup initially)
az ad app credential delete --id $APP_ID --key-id <KEY_ID>

# Remove AZURE_CLIENT_SECRET from GitHub secrets
# (Manual step in GitHub UI)
```

**Recommendation:** Keep the old client secret for 1-2 weeks as a backup before removing it completely.

---

## ✅ Post-Setup Checklist

After successful deployment:
- [ ] Monitor first 2-3 deployments for issues
- [ ] Check Azure AD sign-in logs for OIDC authentications
- [ ] Update team documentation
- [ ] Schedule removal of old client secret (if applicable)
- [ ] Set up monitoring and alerts for deployment failures

---

**Need Help?** Contact the repository maintainer or create an issue with:
- Output from verification commands
- Deployment workflow logs
- Any error messages received
