# Azure Deployment Workflow Fixes - January 2026

> 🔧 **Summary of fixes applied to `.github/workflows/deploy.yml` and `.github/workflows/ci.yml`**

## Overview

This document summarizes the fixes applied to address backend deployment failures and ensure proper delivery of static assets and app settings to Azure App Service.

---

## Issues Fixed

### 1. CI Workflow Indentation Error (`.github/workflows/ci.yml`)

**Problem:** Line 40 had incorrect indentation causing the Python syntax check to fail parsing.

**Fix:** Corrected indentation from 12 spaces to 6 spaces for the "Check Python syntax" step.

```diff
      - name: Install dependencies
        run: uv sync
      
-            - name: Check Python syntax
+      - name: Check Python syntax
        run: find app -name '*.py' -exec uv run python -m py_compile {} +
```

---

### 2. Missing Secrets Validation (`.github/workflows/deploy.yml`)

**Problem:** Workflow would proceed even if critical secrets were missing, causing deployment to fail late in the process.

**Fix:** Added early validation step that checks for required secrets and fails fast with clear error messages.

**New Step:**
```yaml
- name: Validate required secrets
  run: |
    echo "🔍 Validating required secrets..."

    # Azure OIDC secrets (no client-secret needed)
    if [ -z "${{ secrets.AZURE_CLIENT_ID }}" ] || \
       [ -z "${{ secrets.AZURE_TENANT_ID }}" ] || \
       [ -z "${{ secrets.AZURE_SUBSCRIPTION_ID }}" ]; then
      echo "❌ ERROR: One or more Azure OIDC authentication secrets are missing"
      echo "Required secrets: AZURE_CLIENT_ID, AZURE_TENANT_ID, AZURE_SUBSCRIPTION_ID"
      exit 1
    fi

    if [ -z "${{ secrets.DATABASE_URL }}" ]; then
      echo "❌ ERROR: DATABASE_URL secret is not set"
      exit 1
    fi

    if [ -z "${{ secrets.AUTH_SECRET_KEY }}" ]; then
      echo "❌ ERROR: AUTH_SECRET_KEY secret is not set"
      exit 1
    fi

    echo "✅ All required secrets are present"
```

---

### 3. Frontend Static Assets Not Verified (`.github/workflows/deploy.yml`)

**Problem:** Frontend was expected to build to `backend/static` via Vite config, but no verification step ensured this happened correctly.

**Fix:** Enhanced verification step that:
- Checks `backend/static` directory exists
- Verifies `index.html` is present
- Lists all static assets and their sizes
- Fails deployment if assets are missing

**Enhanced Step:**
```yaml
- name: Verify frontend build in backend/static
  run: |
    echo "🔍 Verifying frontend build output..."
    if [ ! -d "backend/static" ]; then
      echo "❌ ERROR: backend/static directory does not exist"
      exit 1
    fi
    
    if [ ! -f "backend/static/index.html" ]; then
      echo "❌ ERROR: backend/static/index.html not found"
      exit 1
    fi
    
    echo "✅ Frontend built successfully to backend/static"
    ls -lh backend/static/
```

---

### 4. Missing App Settings (`.github/workflows/deploy.yml`)

**Problem:** Workflow only set `ALLOWED_ORIGINS`, `APP_ENV`, and `SCM_DO_BUILD_DURING_DEPLOYMENT`. Critical settings `DATABASE_URL` and `AUTH_SECRET_KEY` were missing, causing the backend to fail on startup.

**Fix:** Updated `Configure App Settings` step to include all required environment variables from secrets.

**Before:**
```yaml
- name: Configure App Settings
  run: |
    az webapp config appsettings set --name BaynunahHRPortal --resource-group BaynunahHR --settings \
      ALLOWED_ORIGINS="https://baynunahhrportal.azurewebsites.net" \
      APP_ENV="production" \
      SCM_DO_BUILD_DURING_DEPLOYMENT="true" \
      --output none
```

**After:**
```yaml
- name: Configure App Settings
  run: |
    echo "⚙️  Configuring Azure App Service settings..."
    az webapp config appsettings set \
      --name BaynunahHRPortal \
      --resource-group BaynunahHR \
      --settings \
        DATABASE_URL="${{ secrets.DATABASE_URL }}" \
        AUTH_SECRET_KEY="${{ secrets.AUTH_SECRET_KEY }}" \
        ALLOWED_ORIGINS="https://baynunahhrportal.azurewebsites.net" \
        APP_ENV="production" \
        SCM_DO_BUILD_DURING_DEPLOYMENT="true" \
      --output none
    echo "✅ App settings configured successfully"
```

---

### 5. No Post-Deployment Migrations (`.github/workflows/deploy.yml`)

**Problem:** Database schema changes required manual intervention after every deployment. Schema could be out of sync with code.

**Fix:** Added post-deployment migration step that attempts to run `alembic upgrade head` via two methods:
1. Azure SSH (primary method)
2. Kudu REST API (fallback method)

Uses `continue-on-error: true` to prevent blocking deployments if migration fails, with clear instructions for manual execution.

**New Step:**
```yaml
- name: Run Alembic migrations
  continue-on-error: true
  run: |
    echo "🔄 Attempting to run Alembic migrations..."
    echo ""
    echo "NOTE: This step runs migrations via Azure CLI. It may fail if:"
    echo "  - The app is still starting up"
    echo "  - Database connection requires different credentials"
    echo "  - Migrations require manual intervention"
    echo ""
    
    # Try SSH method first
    az webapp ssh --name BaynunahHRPortal --resource-group BaynunahHR --timeout 60 << 'EOF' || {
      echo "⚠️  Could not run migrations via SSH"
      echo "To run migrations manually:"
      echo "  az webapp ssh --name BaynunahHRPortal --resource-group BaynunahHR"
      echo "  cd /home/site/wwwroot"
      echo "  python -m alembic upgrade head"
      exit 0
    }
    
    cd /home/site/wwwroot
    python -m alembic upgrade head
    echo "✅ Migrations completed successfully"
    EOF
    
    # Fallback to Kudu API if SSH fails
    if [ $? -ne 0 ]; then
      # ... kudu API implementation ...
    fi
```

---

## Benefits

✅ **Fail Fast:** Invalid configuration detected before deployment starts  
✅ **Clear Errors:** Specific error messages for each missing secret or failed step  
✅ **Asset Verification:** Ensures frontend is properly packaged before deployment  
✅ **Complete Configuration:** All required environment variables now deployed automatically  
✅ **Automated Migrations:** Database schema stays in sync with code (best effort)  
✅ **Better Logging:** Enhanced output with emojis and clear status indicators  
✅ **Graceful Degradation:** Migration failures don't block deployment

---

## Required GitHub Secrets

Ensure these secrets are configured in your repository:

| Secret Name | Description | Example |
|-------------|-------------|---------|
| `AZURE_CLIENT_ID` | Azure service principal client ID (OIDC) | `xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx` |
| `AZURE_TENANT_ID` | Azure AD tenant ID (OIDC) | `xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx` |
| `AZURE_SUBSCRIPTION_ID` | Azure subscription ID (OIDC) | `xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx` |
| `DATABASE_URL` | PostgreSQL connection string | `postgresql+asyncpg://user:pass@host:5432/db` |
| `AUTH_SECRET_KEY` | Secret key for JWT signing | Generate: `openssl rand -hex 32` |

**Legacy Option:** `AZURE_CREDENTIALS` (service principal JSON) if you cannot use OIDC.

**How to add secrets:**
1. Go to GitHub repository → Settings → Secrets and variables → Actions
2. Click "New repository secret"
3. Add each secret with exact name and value

---

## Workflow Behavior

### On Success:
1. ✅ All secrets validated
2. ✅ Frontend built to `backend/static`
3. ✅ Assets verified and packaged
4. ✅ Deployed to Azure App Service
5. ✅ App settings configured
6. ✅ Migrations run (or manual instructions provided)
7. ✅ Deployment summary displayed with URLs

### On Failure:
- **Missing secrets:** Fails immediately with specific error message
- **Frontend not built:** Fails before packaging with clear error
- **Deployment error:** Azure deployment step fails with error
- **Migration error:** Warning shown, manual instructions provided (doesn't block deployment)

---

## Manual Migration Steps

If automated migrations fail, run manually:

```bash
# Connect to Azure App Service via SSH
az webapp ssh --name BaynunahHRPortal --resource-group BaynunahHR

# Navigate to app directory
cd /home/site/wwwroot

# Run migrations
python -m alembic upgrade head

# Verify
python -m alembic current

# Exit
exit
```

---

## Verification Checklist

After deployment completes:

- [ ] Check workflow logs for all green checkmarks
- [ ] Visit https://baynunahhrportal.azurewebsites.net (app loads)
- [ ] Visit https://baynunahhrportal.azurewebsites.net/docs (API docs accessible)
- [ ] Visit https://baynunahhrportal.azurewebsites.net/api/health (returns 200 OK)
- [ ] Test login functionality
- [ ] Verify database migrations: `az webapp ssh` → `alembic current`
- [ ] Check app logs: `az webapp log tail --name BaynunahHRPortal --resource-group BaynunahHR`

---

## Related Documentation

- **[GitHub Deployment Setup](GITHUB_DEPLOYMENT_SETUP.md)** - Complete setup guide for GitHub Actions deployment
- **[Azure Deployment Reference](AZURE_DEPLOYMENT_REFERENCE_GUIDE.md)** - Comprehensive Azure Actions reference
- **[Deployment Checklist](../DEPLOYMENT_CHECKLIST.md)** - Pre-deployment checklist

---

## Support

If you encounter issues:

1. Check workflow logs in GitHub Actions tab
2. Review Azure App Service logs: `az webapp log tail --name BaynunahHRPortal --resource-group BaynunahHR`
3. Verify all secrets are configured correctly
4. Check Azure Portal → App Service → Configuration for applied settings
5. Test database connectivity from App Service console

---

**Last Updated:** January 11, 2026  
**Workflow Files:** `.github/workflows/deploy.yml`, `.github/workflows/ci.yml`  
**Target App:** BaynunahHRPortal  
**Resource Group:** BaynunahHR
