# Azure OIDC Authentication Setup for GitHub Actions

> 🔐 **Secure deployment without long-lived secrets using OpenID Connect (OIDC)**

## Overview

This guide shows you how to configure Azure Active Directory and GitHub to use OIDC federated authentication for automated deployments. OIDC eliminates the need for managing client secrets by using short-lived tokens that are automatically generated and validated.

### Benefits of OIDC

✅ **No secret rotation** - No long-lived credentials to manage or rotate  
✅ **Enhanced security** - Short-lived tokens that automatically expire  
✅ **Better audit trail** - Azure AD logs show detailed authentication information  
✅ **Zero-trust security** - Follows modern security best practices  
✅ **Compliance ready** - Meets enterprise security requirements

---

## Prerequisites

- Azure subscription with Owner or User Access Administrator role
- GitHub repository with Actions enabled
- Azure CLI installed locally (`az --version`)
- Existing Azure App Service or ability to create one

---

## Step 1: Create Azure AD Application

First, create an Azure AD application that will represent your GitHub Actions workflow:

```bash
# Login to Azure
az login

# Create the Azure AD application
az ad app create --display-name "GitHub Actions - HR Portal"
```

**Save the output** - you'll need the `appId` (also called `clientId`).

Example output:
```json
{
  "appId": "12345678-1234-1234-1234-123456789012",
  "displayName": "GitHub Actions - HR Portal",
  ...
}
```

---

## Step 2: Create Service Principal

Create a service principal for the application:

```bash
# Replace <APP_ID> with the appId from Step 1
az ad sp create --id <APP_ID>
```

---

## Step 3: Assign Azure Permissions

Grant the service principal contributor access to your resource group:

```bash
# Get your subscription ID
SUBSCRIPTION_ID=$(az account show --query id -o tsv)

# Assign contributor role to the resource group
az role assignment create \
  --role Contributor \
  --assignee <APP_ID> \
  --scope /subscriptions/$SUBSCRIPTION_ID/resourceGroups/baynunah-hr-rg
```

**Note:** Adjust the resource group name (`baynunah-hr-rg`) if your setup uses a different name.

---

## Step 4: Configure Federated Credentials

Create a federated credential that trusts your GitHub repository:

```bash
# Replace <APP_ID> with your appId
az ad app federated-credential create \
  --id <APP_ID> \
  --parameters '{
    "name": "github-actions-main",
    "issuer": "https://token.actions.githubusercontent.com",
    "subject": "repo:ismaelloveexcel/AZURE-DEPLOYMENT-HR-PORTAL:ref:refs/heads/main",
    "description": "GitHub Actions deployment from main branch",
    "audiences": ["api://AzureADTokenExchange"]
  }'
```

**Important:** The `subject` field must match your repository path exactly:
- Format: `repo:OWNER/REPO_NAME:ref:refs/heads/BRANCH_NAME`
- Example: `repo:ismaelloveexcel/AZURE-DEPLOYMENT-HR-PORTAL:ref:refs/heads/main`

### For Multiple Branches (Optional)

If you want to deploy from multiple branches, create additional federated credentials:

```bash
# For develop branch
az ad app federated-credential create \
  --id <APP_ID> \
  --parameters '{
    "name": "github-actions-develop",
    "issuer": "https://token.actions.githubusercontent.com",
    "subject": "repo:ismaelloveexcel/AZURE-DEPLOYMENT-HR-PORTAL:ref:refs/heads/develop",
    "description": "GitHub Actions deployment from develop branch",
    "audiences": ["api://AzureADTokenExchange"]
  }'
```

---

## Step 5: Add GitHub Secrets

Go to your GitHub repository:

1. Click **Settings** → **Secrets and variables** → **Actions**
2. Click **New repository secret**
3. Add the following secrets:

### Required Secrets for OIDC Authentication

| Secret Name              | Value                           | How to Get It                                       |
| ------------------------ | ------------------------------- | --------------------------------------------------- |
| `AZURE_CLIENT_ID`        | Application (client) ID         | `appId` from Step 1                                 |
| `AZURE_TENANT_ID`        | Directory (tenant) ID           | Run: `az account show --query tenantId -o tsv`     |
| `AZURE_SUBSCRIPTION_ID`  | Subscription ID                 | Run: `az account show --query id -o tsv`           |

### Application Secrets (Still Required)

| Secret Name              | Value                           | How to Get It                                       |
| ------------------------ | ------------------------------- | --------------------------------------------------- |
| `DATABASE_URL`           | PostgreSQL connection string    | Your Azure PostgreSQL connection string             |
| `AUTH_SECRET_KEY`        | Random secret key               | Generate: `python -c "import secrets; print(secrets.token_urlsafe(32))"` |
| `ALLOWED_ORIGINS`        | Comma-separated frontend URLs   | Include your App Service URL + any custom domains   |

**⚠️ IMPORTANT:** With OIDC, you do **NOT** need `AZURE_CLIENT_SECRET` anymore!

---

## Step 6: Verify Workflow Configuration

The workflow file `.github/workflows/deploy.yml` should have:

1. **OIDC permissions** at the workflow level:
```yaml
permissions:
  id-token: write   # Required for OIDC authentication
  contents: read    # Required to checkout code
```

2. **Azure login step without client-secret**:
```yaml
- name: Login to Azure
  uses: azure/login@v2
  with:
    client-id: ${{ secrets.AZURE_CLIENT_ID }}
    tenant-id: ${{ secrets.AZURE_TENANT_ID }}
    subscription-id: ${{ secrets.AZURE_SUBSCRIPTION_ID }}
    # No client-secret parameter - uses OIDC token instead
```

---

## Step 7: Test Deployment

### Verify Secrets

Run this command locally to verify you have the correct IDs:

```bash
# Check your tenant ID
az account show --query tenantId -o tsv

# Check your subscription ID
az account show --query id -o tsv

# List your Azure AD applications
az ad app list --display-name "GitHub Actions - HR Portal"
```

### Trigger Test Deployment

Option A: Push to main branch
```bash
git add .
git commit -m "Test OIDC deployment"
git push origin main
```

Option B: Manual trigger
1. Go to GitHub → **Actions** tab
2. Select **Deploy to Azure** workflow
3. Click **Run workflow** → **Run workflow**

### Monitor the Deployment

1. Go to GitHub → **Actions** tab
2. Click on the running workflow
3. Watch for successful Azure login step:
   ```
   ✅ Login to Azure
   ```

If successful, you'll see output like:
```
Login successful.
```

---

## Troubleshooting

### Error: "AADSTS70021: No matching federated identity record found"

**Issue:** The federated credential subject doesn't match your repository/branch.

**Fix:**
1. Verify the credential subject matches exactly:
   ```bash
   az ad app federated-credential list --id <APP_ID>
   ```
2. Ensure the format is: `repo:OWNER/REPO:ref:refs/heads/BRANCH`
3. Check for typos in owner name, repo name, or branch name

### Error: "Client assertion audience claim does not match"

**Issue:** The audience field is incorrect.

**Fix:** Ensure the federated credential has `"audiences": ["api://AzureADTokenExchange"]`

### Error: "AADSTS700016: Application not found"

**Issue:** The AZURE_CLIENT_ID secret is incorrect.

**Fix:**
1. Get the correct client ID:
   ```bash
   az ad app list --display-name "GitHub Actions - HR Portal" --query "[].appId" -o tsv
   ```
2. Update the AZURE_CLIENT_ID secret in GitHub

### Error: "AuthorizationFailed: The client does not have authorization"

**Issue:** The service principal doesn't have sufficient permissions.

**Fix:**
1. Verify role assignment:
   ```bash
   az role assignment list --assignee <APP_ID>
   ```
2. Grant Contributor role if missing (see Step 3)

### Secrets Validation Fails

**Issue:** Workflow fails at "Validate required secrets" step.

**Fix:** Ensure all three Azure secrets are set in GitHub:
- AZURE_CLIENT_ID
- AZURE_TENANT_ID
- AZURE_SUBSCRIPTION_ID

### Login Works but Deployment Fails

**Issue:** Authentication succeeds but Azure operations fail.

**Fix:** Check Azure permissions:
1. Verify the service principal has Contributor role on the resource group
2. Check if the resource group name in the workflow matches your actual resource group
3. Verify subscription ID is correct

---

## Security Best Practices

✅ **Restrict federated credentials** - Only add credentials for branches that need to deploy  
✅ **Use specific scopes** - Grant minimal permissions (Contributor to specific resource group, not entire subscription)  
✅ **Monitor Azure AD sign-ins** - Regularly review the Sign-in logs in Azure Portal  
✅ **Rotate manually if compromised** - While OIDC tokens are short-lived, recreate federated credentials if you suspect compromise  
✅ **Use branch protection** - Require pull request reviews before merging to main  
✅ **Enable secret scanning** - Turn on GitHub secret scanning to catch accidental leaks

---

## Migrating from Service Principal with Secret

If you're migrating from the old authentication method:

### Before (Service Principal with Secret):
```yaml
- name: Login to Azure
  uses: azure/login@v2
  with:
    client-id: ${{ secrets.AZURE_CLIENT_ID }}
    tenant-id: ${{ secrets.AZURE_TENANT_ID }}
    subscription-id: ${{ secrets.AZURE_SUBSCRIPTION_ID }}
    client-secret: ${{ secrets.AZURE_CLIENT_SECRET }}  # ❌ Long-lived secret
```

### After (OIDC):
```yaml
permissions:
  id-token: write
  contents: read

jobs:
  deploy:
    steps:
      - name: Login to Azure
        uses: azure/login@v2
        with:
          client-id: ${{ secrets.AZURE_CLIENT_ID }}
          tenant-id: ${{ secrets.AZURE_TENANT_ID }}
          subscription-id: ${{ secrets.AZURE_SUBSCRIPTION_ID }}
          # ✅ No client-secret - uses OIDC token
```

### Migration Steps:
1. Follow Steps 1-5 above to set up OIDC
2. Update workflow file (already done if using current deploy.yml)
3. Test deployment
4. Once verified, delete the old client secret:
   ```bash
   # List secrets
   az ad app credential list --id <APP_ID>
   
   # Remove client secret (optional - can keep as backup initially)
   az ad app credential delete --id <APP_ID> --key-id <KEY_ID>
   ```
5. Remove AZURE_CLIENT_SECRET from GitHub secrets

---

## Verification Checklist

Before going to production, verify:

- [ ] Azure AD application created
- [ ] Service principal created
- [ ] Federated credential configured with correct subject
- [ ] Contributor role assigned to service principal
- [ ] GitHub secrets added (AZURE_CLIENT_ID, AZURE_TENANT_ID, AZURE_SUBSCRIPTION_ID)
- [ ] Workflow has `permissions: id-token: write` and `contents: read`
- [ ] Azure login step does NOT have `client-secret` parameter
- [ ] Test deployment completed successfully
- [ ] Azure portal shows successful authentication in Sign-in logs

---

## Additional Resources

- [GitHub OIDC Documentation](https://docs.github.com/en/actions/deployment/security-hardening-your-deployments/configuring-openid-connect-in-azure)
- [Azure Federated Credentials Documentation](https://learn.microsoft.com/en-us/azure/active-directory/develop/workload-identity-federation)
- [Azure Login Action Documentation](https://github.com/Azure/login)

---

## Next Steps

After successful OIDC setup:

1. ✅ Test deployment from main branch
2. ✅ Monitor Azure AD sign-in logs
3. ✅ Update team documentation
4. ✅ Remove old client secret (if migrating)
5. 📊 Set up deployment monitoring and alerts

**Questions?** Check the [GitHub Deployment Setup Guide](GITHUB_DEPLOYMENT_SETUP.md) for general deployment information.
