# Azure First-Time Deployment Guide

This guide provides step-by-step instructions to deploy the HR Portal to Azure for the first time.

## Quick Links
- [Prerequisites](#prerequisites)
- [Step 1: Create Azure Resources](#step-1-create-azure-resources)
- [Step 2: Configure GitHub Secrets](#step-2-configure-github-secrets)
- [Step 3: Deploy](#step-3-deploy)
- [Step 4: Verify](#step-4-verify)
- [Troubleshooting](#troubleshooting)

---

## Prerequisites

Before you begin, ensure you have:
- An Azure account with an active subscription
- A GitHub account with access to this repository
- Basic familiarity with Azure Portal

---

## Step 1: Create Azure Resources

### 1.1 Create Resource Group

1. Go to [Azure Portal](https://portal.azure.com)
2. Search for "Resource groups" → Click **+ Create**
3. Configure:
   - **Subscription**: Select your subscription
   - **Resource group**: `baynunah-hr-rg`
   - **Region**: `West Europe` (or your preferred region)
4. Click **Review + create** → **Create**

### 1.2 Create Azure PostgreSQL Flexible Server

1. Search for "Azure Database for PostgreSQL" → Click **+ Create**
2. Select **Flexible server**
3. Configure **Basics**:
   - **Subscription**: Your subscription
   - **Resource group**: `baynunah-hr-rg`
   - **Server name**: `baynunah-hr-db`
   - **Region**: Same as resource group
   - **PostgreSQL version**: `15`
   - **Workload type**: `Development` (for cost savings)
   - **Compute + storage**: Click **Configure server**
     - **Compute tier**: `Burstable`
     - **Compute size**: `Standard_B1ms` (1 vCore, $12/month approx)
     - Click **Save**
4. **Authentication**:
   - **Authentication method**: `PostgreSQL authentication only`
   - **Admin username**: `hradmin`
   - **Password**: Create a strong password (save this!)
5. Click **Next: Networking**
6. **Networking**:
   - **Connectivity method**: `Public access`
   - **Allow public access from any Azure service**: ✅ Check this
   - **Add current client IP address**: ✅ Check this (for testing)
7. Click **Review + create** → **Create**

**Wait for deployment to complete (~5-10 minutes)**

### 1.3 Create Database

1. Go to your PostgreSQL server (`baynunah-hr-db`)
2. In the left menu, click **Databases**
3. Click **+ Add**
4. **Name**: `hrportal`
5. Click **Save**

### 1.4 Get Database Connection String

Your DATABASE_URL will be:
```
postgresql+asyncpg://hradmin:<YOUR_PASSWORD>@baynunah-hr-db.postgres.database.azure.com:5432/hrportal?sslmode=require
```

Replace `<YOUR_PASSWORD>` with your admin password.

### 1.5 Create App Service (Backend)

1. Search for "App Services" → Click **+ Create** → **+ Web App**
2. Configure **Basics**:
   - **Subscription**: Your subscription
   - **Resource group**: `baynunah-hr-rg`
   - **Name**: `baynunah-hr-portal` (must be globally unique)
   - **Publish**: `Code`
   - **Runtime stack**: `Python 3.11`
   - **Operating System**: `Linux`
   - **Region**: Same as resource group
3. **Pricing plan**: Click **Create new**
   - **Name**: `baynunah-hr-plan`
   - **Sku and size**: `Basic B1` ($13/month approx)
4. Click **Review + create** → **Create**

### 1.6 Create Azure Static Web App (Frontend) - Optional

> **Note**: The default deployment uses the backend to serve the frontend. Use Static Web Apps only if you need separate frontend hosting.

1. Search for "Static Web Apps" → Click **+ Create**
2. Configure:
   - **Subscription**: Your subscription
   - **Resource group**: `baynunah-hr-rg`
   - **Name**: `baynunah-hr-frontend`
   - **Plan type**: `Free`
   - **Region**: `West Europe`
   - **Source**: `GitHub`
   - **Organization**: Your GitHub org
   - **Repository**: This repository
   - **Branch**: `main`
3. **Build Details**:
   - **Build Presets**: `Custom`
   - **App location**: `frontend`
   - **Output location**: `dist`
4. Click **Review + create** → **Create**

---

## Step 2: Configure GitHub Secrets

### 2.1 Create Azure Service Principal (for OIDC)

Open Azure Cloud Shell or terminal with Azure CLI:

```bash
# Login to Azure
az login

# Create service principal with Contributor role
az ad sp create-for-rbac \
  --name "github-hr-portal-deploy" \
  --role Contributor \
  --scopes /subscriptions/<SUBSCRIPTION_ID>/resourceGroups/baynunah-hr-rg \
  --sdk-auth
```

This outputs JSON - save the values for:
- `clientId` → `AZURE_CLIENT_ID`
- `tenantId` → `AZURE_TENANT_ID`
- `subscriptionId` → `AZURE_SUBSCRIPTION_ID`

### 2.2 Configure Federated Credentials (OIDC)

1. Go to Azure Portal → **Azure Active Directory** → **App registrations**
2. Find `github-hr-portal-deploy` → Click on it
3. Go to **Certificates & secrets** → **Federated credentials** → **+ Add credential**
4. Configure:
   - **Federated credential scenario**: `GitHub Actions deploying Azure resources`
   - **Organization**: Your GitHub username/org
   - **Repository**: `AZURE-DEPLOYMENT-HR-PORTAL`
   - **Entity type**: `Branch`
   - **GitHub branch name**: `main`
   - **Name**: `github-main-branch`
5. Click **Add**

### 2.3 Add GitHub Repository Secrets

Go to your GitHub repository → **Settings** → **Secrets and variables** → **Actions** → **New repository secret**

Add these secrets:

| Secret Name | Value | Description |
|------------|-------|-------------|
| `AZURE_CLIENT_ID` | From service principal | Azure AD App Client ID |
| `AZURE_TENANT_ID` | From service principal | Azure AD Tenant ID |
| `AZURE_SUBSCRIPTION_ID` | From service principal | Azure Subscription ID |
| `DATABASE_URL` | `postgresql+asyncpg://hradmin:<PASSWORD>@baynunah-hr-db.postgres.database.azure.com:5432/hrportal?sslmode=require` | PostgreSQL connection string |
| `AUTH_SECRET_KEY` | Generate with: `python -c "import secrets; print(secrets.token_urlsafe(32))"` | JWT signing secret |
| `ALLOWED_ORIGINS` | `https://baynunah-hr-portal.azurewebsites.net` | CORS allowed origins |
| `AZURE_STATIC_WEB_APPS_API_TOKEN` | *(Only if using Static Web Apps)* | Get from Static Web App → Overview → Manage deployment token |

### 2.4 Generate AUTH_SECRET_KEY

Run this in any Python environment:
```python
import secrets
print(secrets.token_urlsafe(32))
```

Or use a password generator to create a 32+ character random string.

---

## Step 3: Deploy

### 3.1 Trigger Deployment

1. Go to your GitHub repository
2. Click **Actions** tab
3. Select **Deploy to Azure** workflow
4. Click **Run workflow** → **Run workflow**

The deployment will:
1. ✅ Build the React frontend
2. ✅ Package the FastAPI backend
3. ✅ Deploy to Azure App Service
4. ✅ Run database migrations
5. ✅ Verify health endpoint

### 3.2 Monitor Deployment

1. Click on the running workflow to see progress
2. Each step shows logs in real-time
3. Green checkmark = success, Red X = failure

---

## Step 4: Verify

### 4.1 Check Application Health

Open in browser:
- **Health Check**: `https://baynunah-hr-portal.azurewebsites.net/api/health/ping`
- **Database Health**: `https://baynunah-hr-portal.azurewebsites.net/api/health/db`
- **API Docs**: `https://baynunah-hr-portal.azurewebsites.net/docs`

### 4.2 Test Login

1. Go to `https://baynunah-hr-portal.azurewebsites.net`
2. Default admin credentials (after first deployment):
   - **Employee ID**: `BAYN00008`
   - **Password**: `16051988` (date of birth format: DDMMYYYY)
3. You'll be prompted to change password on first login

### 4.3 Reset Admin Password (if needed)

```bash
curl -X POST https://baynunah-hr-portal.azurewebsites.net/api/health/reset-admin-password \
  -H "X-Admin-Secret: YOUR_AUTH_SECRET_KEY"
```

---

## Required Azure App Settings

These are automatically configured by the deployment workflow:

| Setting | Description |
|---------|-------------|
| `DATABASE_URL` | PostgreSQL connection string |
| `AUTH_SECRET_KEY` | JWT signing secret |
| `ALLOWED_ORIGINS` | CORS allowed origins |
| `APP_ENV` | `production` |
| `SCM_DO_BUILD_DURING_DEPLOYMENT` | `false` |
| `ENABLE_ORYX_BUILD` | `false` |
| `PYTHONUNBUFFERED` | `1` |

---

## Cost Estimate (Monthly)

| Resource | SKU | Estimated Cost |
|----------|-----|----------------|
| App Service | B1 Basic | ~$13/month |
| PostgreSQL Flexible | B1ms | ~$12/month |
| Static Web Apps | Free | $0/month |
| **Total** | | **~$25/month** |

> **Note**: Costs may vary by region. Use Azure Pricing Calculator for exact estimates.

---

## Troubleshooting

### Issue: Deployment fails with "secret not set"

**Solution**: Ensure all required GitHub secrets are configured:
- `AZURE_CLIENT_ID`
- `AZURE_TENANT_ID`
- `AZURE_SUBSCRIPTION_ID`
- `DATABASE_URL`
- `AUTH_SECRET_KEY`

### Issue: "Connection refused" on health check

**Solution**: 
1. Wait 2-3 minutes for app to fully start
2. Check App Service logs: `az webapp log tail --name baynunah-hr-portal --resource-group baynunah-hr-rg`
3. Verify DATABASE_URL is correct

### Issue: Database connection error

**Solution**:
1. Verify PostgreSQL firewall allows Azure services
2. Check connection string format includes `sslmode=require`
3. Verify database `hrportal` exists

### Issue: Login fails

**Solution**:
1. Reset admin password using the curl command above
2. Ensure AUTH_SECRET_KEY matches between App Service and your reset request

### Issue: Frontend shows blank page

**Solution**:
1. Check browser console for errors
2. Verify frontend build completed in deployment logs
3. Check `/api/health/ping` works to confirm backend is running

---

## Maintenance

### View Logs
```bash
az webapp log tail --name baynunah-hr-portal --resource-group baynunah-hr-rg
```

### Restart App
```bash
az webapp restart --name baynunah-hr-portal --resource-group baynunah-hr-rg
```

### Scale Up/Down
1. Go to Azure Portal → App Service → **Scale up (App Service plan)**
2. Select desired tier

---

## Support

If you encounter issues:
1. Check GitHub Actions logs for deployment errors
2. Check Azure App Service logs for runtime errors
3. Create an issue in this repository with:
   - Error message
   - Steps to reproduce
   - Screenshots if applicable
