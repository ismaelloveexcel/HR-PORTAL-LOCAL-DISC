# GitHub Secrets Reference Guide

> Complete reference for all GitHub secrets used in the HR Portal workflows

---

## Overview

This document provides a comprehensive reference for all GitHub secrets used across different workflows in the HR Portal. Secrets are categorized by their purpose and whether they are required or optional.

---

## Required Secrets (Core Deployment)

These secrets **must** be configured for the deployment workflow (`deploy.yml`) to succeed:

### 1. AZURE_CLIENT_ID

**Purpose:** OIDC authentication client ID for Azure login  
**Format:** GUID  
**Workflow:** `deploy.yml`

**How to Get:**
```bash
az ad app list --display-name "GitHub Actions - HR Portal" --query "[0].appId" -o tsv
```

---

### 2. AZURE_TENANT_ID

**Purpose:** Azure AD tenant ID for OIDC login  
**Format:** GUID  
**Workflow:** `deploy.yml`

**How to Get:**
```bash
az account show --query tenantId -o tsv
```

---

### 3. AZURE_SUBSCRIPTION_ID

**Purpose:** Azure subscription for OIDC login  
**Format:** GUID  
**Workflow:** `deploy.yml`

**How to Get:**
```bash
az account show --query id -o tsv
```

---

### Legacy Alternative: AZURE_CREDENTIALS (Optional)

**Purpose:** Service principal JSON for Azure login (legacy, if not using OIDC)  
**Format:** JSON object  
**Workflow:** `deploy.yml`

**How to Create:**
```bash
az ad sp create-for-rbac \
  --name "github-actions-baynunah-hr" \
  --role contributor \
  --scopes /subscriptions/{subscription-id}/resourceGroups/baynunah-hr-rg \
  --sdk-auth
```

**Example Value:**
```json
{
  "clientId": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
  "clientSecret": "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
  "subscriptionId": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
  "tenantId": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
}
```

**⚠️ Security Note:** Prefer OIDC. Only use this if your workflow uses the `creds:` input for `azure/login@v2` or OIDC cannot be enabled. Never commit this JSON to the repository.

**Workflow Note:** `deploy.yml` uses `azure/login@v2` with OIDC; the `creds:` input on that action is only for legacy service principal flows.

---

### 4. DATABASE_URL

**Purpose:** PostgreSQL database connection string  
**Format:** Connection URI with `postgresql+asyncpg://` prefix  
**Workflow:** `deploy.yml`

**Format:**
```
postgresql+asyncpg://username:password@host:5432/database?sslmode=require
```

**Example:**
```
postgresql+asyncpg://hruser:mySecureP@ss@baynunah-hr-server.postgres.database.azure.com:5432/hrportal?sslmode=require
```

**Important:**
- Must use `postgresql+asyncpg://` prefix (not `postgres://` or `postgresql://`)
- Must include `?sslmode=require` for Azure PostgreSQL
- Password must be URL-encoded if it contains special characters

**How to Get:**
1. Go to Azure Portal → PostgreSQL server
2. Get connection details from "Connection strings" section
3. Replace the prefix with `postgresql+asyncpg://`
4. Add your password
5. Ensure `?sslmode=require` is at the end

---

### 5. AUTH_SECRET_KEY

**Purpose:** JWT token signing key for authentication  
**Format:** Random 32-byte hex string (64 characters)  
**Workflow:** `deploy.yml`

**How to Generate:**
```bash
openssl rand -hex 32
```

**Example Output:**
```
a1b2c3d4e5f6789012345678901234567890abcdef1234567890abcdef123456
```

**⚠️ Security Note:** 
- Generate a unique key for production
- Never reuse keys across environments
- Store securely - losing this key invalidates all user sessions

---

### 6. ALLOWED_ORIGINS

**Purpose:** CORS allow-list for the frontend  
**Format:** Comma-separated URLs  
**Workflow:** `deploy.yml` (app setting)

**Example:**
```
https://baynunah-hr-portal.azurewebsites.net,https://hr.example.com
```

**Note:** If unset, the deployment workflow defaults to the Azure web app URL.

---

## Optional Secrets (Health Checks)

These secrets are used by `post-deployment-health.yml` for automated health monitoring. They are optional but recommended for production deployments.

### 4. BACKEND_URL

**Purpose:** Backend API URL for health checks  
**Format:** Full URL without trailing slash  
**Workflow:** `post-deployment-health.yml`

**Example:**
```
https://baynunah-hr-portal.azurewebsites.net/api
```

**Default Behavior:** If not set, health check workflow will fail but deployment continues.

---

### 5. FRONTEND_URL

**Purpose:** Frontend URL for health checks  
**Format:** Full URL without trailing slash  
**Workflow:** `post-deployment-health.yml`

**Example:**
```
https://baynunah-hr-portal.azurewebsites.net
```

**Default Behavior:** If not set, health check workflow will fail but deployment continues.

---

## Optional Secrets (Database Backups)

These secrets are used by `backup-db.yml` for automated daily backups. Only configure if you want automated backups via GitHub Actions.

### 6. PGHOST

**Purpose:** PostgreSQL server hostname  
**Format:** Hostname only (no protocol or port)  
**Workflow:** `backup-db.yml`

**Example:**
```
baynunah-hr-server.postgres.database.azure.com
```

---

### 7. PGUSER

**Purpose:** PostgreSQL username  
**Format:** Plain text username  
**Workflow:** `backup-db.yml`

**Example:**
```
hruser
```

---

### 8. PGPASSWORD

**Purpose:** PostgreSQL password  
**Format:** Plain text password  
**Workflow:** `backup-db.yml`

**Example:**
```
mySecurePassword123!
```

---

### 9. PGDATABASE

**Purpose:** PostgreSQL database name  
**Format:** Database name  
**Workflow:** `backup-db.yml`

**Example:**
```
hrportal
```

---

## How to Add Secrets to GitHub

1. Go to your repository on GitHub
2. Click **Settings** → **Secrets and variables** → **Actions**
3. Click **New repository secret**
4. Enter the secret name (exactly as shown above, case-sensitive)
5. Paste the secret value
6. Click **Add secret**
7. Repeat for each required/optional secret

---

## Verifying Secrets

After adding secrets, you can verify they're configured:

1. Go to **Settings** → **Secrets and variables** → **Actions**
2. You should see all configured secrets listed (values are hidden)
3. Secrets shown as "Not set" or missing from the list need to be added

---

## Security Best Practices

✅ **DO:**
- Use strong, randomly generated values for `AUTH_SECRET_KEY`
- Rotate secrets regularly (every 90 days recommended)
- Use different secrets for staging and production
- Enable GitHub secret scanning for additional protection
- Use Azure Key Vault for additional secret management

❌ **DON'T:**
- Never commit secrets to the repository (even in examples)
- Never share secrets via email or chat
- Never reuse secrets across different applications
- Never log secrets in workflow outputs
- Never use weak or predictable values

---

## Troubleshooting

### "Secret not found" Error in Workflow

**Symptom:** Workflow fails with "secret is not set" message

**Solution:** 
1. Check secret name spelling (case-sensitive)
2. Verify secret is added to repository secrets (not environment secrets)
3. Re-add the secret if necessary

### Database Connection Fails

**Symptom:** Deployment succeeds but app can't connect to database

**Solution:**
1. Verify `DATABASE_URL` format is correct
2. Ensure password doesn't contain unescaped special characters
3. Check that `?sslmode=require` is included
4. Verify database firewall allows Azure services

### Authentication Fails After Deployment

**Symptom:** Users can't log in after deployment

**Solution:**
1. Verify `AUTH_SECRET_KEY` is correctly set
2. If you changed the key, users need to log in again
3. Check Azure App Service configuration has the key set

### Health Checks Fail

**Symptom:** Post-deployment health check workflow fails

**Solution:**
1. Add `BACKEND_URL` and `FRONTEND_URL` secrets
2. Verify URLs are correct and accessible
3. Allow 2-3 minutes for app to fully start before health checks run

---

## Secret Rotation Guide

### When to Rotate

- **AUTH_SECRET_KEY:** Every 90 days or after suspected compromise
- **AZURE_CLIENT_ID / AZURE_TENANT_ID / AZURE_SUBSCRIPTION_ID:** When Azure app/tenant changes
- **AZURE_CREDENTIALS (legacy):** Every 180 days or when team members leave
- **DATABASE_URL:** When database password is reset
- **ALLOWED_ORIGINS:** When frontend domains change
- **Backup credentials:** Every 90 days

### How to Rotate

1. Generate new secret value
2. Update in GitHub secrets
3. Trigger new deployment (for `AUTH_SECRET_KEY`, `DATABASE_URL`)
4. Verify app still works
5. Document rotation in your security log

**Note:** Rotating `AUTH_SECRET_KEY` will invalidate all active user sessions - users will need to log in again.

---

## Summary Table

| Secret                    | Required? | Used By                       | Frequency |
| ------------------------- | --------- | ----------------------------- | --------- |
| `AZURE_CLIENT_ID`         | ✅ Yes    | `deploy.yml`                  | Every deployment |
| `AZURE_TENANT_ID`         | ✅ Yes    | `deploy.yml`                  | Every deployment |
| `AZURE_SUBSCRIPTION_ID`   | ✅ Yes    | `deploy.yml`                  | Every deployment |
| `AZURE_CREDENTIALS`       | ⚠️ Legacy | `deploy.yml`                  | Only if using service principal JSON |
| `DATABASE_URL`            | ✅ Yes    | `deploy.yml`                  | Every deployment |
| `AUTH_SECRET_KEY`         | ✅ Yes    | `deploy.yml`                  | Every deployment |
| `ALLOWED_ORIGINS`         | ⚠️ Optional | `deploy.yml`                | When domains change |
| `BACKEND_URL`             | ⚠️ Optional | `post-deployment-health.yml` | After deployment |
| `FRONTEND_URL`            | ⚠️ Optional | `post-deployment-health.yml` | After deployment |
| `PGHOST`                  | ⚠️ Optional | `backup-db.yml`              | Daily at 2am UTC |
| `PGUSER`                  | ⚠️ Optional | `backup-db.yml`              | Daily at 2am UTC |
| `PGPASSWORD`              | ⚠️ Optional | `backup-db.yml`              | Daily at 2am UTC |
| `PGDATABASE`              | ⚠️ Optional | `backup-db.yml`              | Daily at 2am UTC |

---

## Related Documentation

- [GitHub Deployment Setup Guide](GITHUB_DEPLOYMENT_SETUP.md) - Step-by-step deployment instructions
- [Azure Deployment Reference Guide](AZURE_DEPLOYMENT_REFERENCE_GUIDE.md) - Azure-specific configuration
- [Deployment Status Summary](../DEPLOYMENT_STATUS_SUMMARY.md) - Current deployment status
- [Security Policy](../SECURITY.md) - Overall security guidelines

---

**Last Updated:** January 15, 2026  
**Maintained By:** DevOps Team
