# Backend Downtime Troubleshooting Guide

## Overview

This guide provides step-by-step instructions for diagnosing and resolving issues when the HR Portal backend (https://hrportal-backend-new.azurewebsites.net) becomes unresponsive.

---

## Quick Diagnostic Steps (Azure Portal)

### Step 1: Check if App Service is Running

1. Go to **Azure Portal** (https://portal.azure.com)
2. Navigate to **App Services** → **hrportal-backend-new**
3. Check the **Overview** tab:
   - **Status:** Should say "Running"
   - If it says "Stopped", click **Start** button
   - Wait 2-3 minutes for startup

### Step 2: Check Application Logs

1. In **hrportal-backend-new**, go to **Monitoring** → **Log stream**
2. Look for errors:
   - Python startup errors
   - Database connection errors
   - Missing environment variables
   - Module import errors

Common error patterns:
```
ERROR: Could not connect to database
ERROR: Missing environment variable: DATABASE_URL
ModuleNotFoundError: No module named 'app'
Connection refused (database)
```

### Step 3: Verify Configuration

1. Go to **Configuration** → **Application settings**
2. Verify these settings exist:
   - `DATABASE_URL` - PostgreSQL connection string
   - `AUTH_SECRET_KEY` - Secret for JWT tokens
   - `ALLOWED_ORIGINS` - CORS origins
   - `APP_ENV` - Should be "production"

3. Check **General settings** → **Startup Command**:
   - Should be: `gunicorn --bind 0.0.0.0:$PORT --worker-class uvicorn.workers.UvicornWorker app.main:app`

### Step 4: Try Manual Restart

1. In **Overview** tab, click **Restart** button
2. Wait 3-5 minutes
3. Test from command line:
   ```bash
   curl https://hrportal-backend-new.azurewebsites.net/api/health/ping
   ```

---

## Using the Diagnostic Script (Requires Azure CLI)

If you have Azure CLI installed and configured:

```bash
# Make sure you're logged in
az login

# Run the diagnostic script
cd /path/to/AZURE-DEPLOYMENT-HR-PORTAL
./scripts/diagnose_azure_backend.sh
```

The script will:
- Check app service status
- Verify configuration settings
- Review recent deployments
- Download and analyze logs
- Test connectivity and database
- Provide specific recommendations

---

## Common Causes & Solutions

### 1. App Service Stopped

**Symptom:** Status shows "Stopped"  
**Solution:** Click "Start" button in Azure Portal

### 2. Database Connection Failed

**Symptoms:**
- Logs show: "Could not connect to database"
- App starts but crashes immediately

**Solutions:**
- Verify `DATABASE_URL` in Configuration → Application settings
- Check Azure PostgreSQL server is running
- Verify firewall rules allow Azure services
- Format should be: `postgresql+asyncpg://user:pass@host:5432/dbname?sslmode=require`

### 3. Python Dependencies Missing

**Symptoms:**
- Logs show: "ModuleNotFoundError"
- Oryx build failed

**Solutions:**
- Check Deployment Center → Logs for Oryx build errors
- Verify `requirements.txt` is correct
- Redeploy from GitHub Actions

### 4. Memory/CPU Exhaustion

**Symptoms:**
- App crashes randomly
- Very slow response times
- Logs show "Out of memory"

**Solutions:**
- Go to **Monitoring** → **Metrics**
- Check CPU and Memory usage
- Consider scaling up App Service plan

### 5. Environment Variable Missing

**Symptoms:**
- Logs show: "Missing environment variable: X"
- 500 errors

**Solutions:**
- Go to **Configuration** → **Application settings**
- Add missing variables
- Restart app after adding

### 6. Cold Start (Long Inactivity)

**Symptoms:**
- First request takes 30+ seconds
- Subsequent requests work fine

**Solutions:**
- This is normal for Azure App Service Free/Basic tier
- Consider "Always On" setting (requires Standard tier or higher)
- Or accept 30-60 second cold start after inactivity

---

## Step-by-Step Recovery Process

### Option A: Quick Restart (Try This First)

```bash
# Using Azure CLI
az webapp restart --name hrportal-backend-new --resource-group baynunah-hr-portal-rg

# Wait 3 minutes, then test
sleep 180
curl https://hrportal-backend-new.azurewebsites.net/api/health/ping
```

### Option B: Redeploy from Last Known Good State

1. Go to **Deployment Center** → **Logs**
2. Find last successful deployment (Run #105)
3. Click **Redeploy** button
4. Wait for deployment to complete
5. Test endpoint

### Option C: Manual Deployment from GitHub

1. Merge PR #92 to `main` (includes the fixes AND version tracking)
2. GitHub Actions will automatically deploy
3. This will create a fresh deployment with all latest code

---

## After Backend is Running

### Verify Health

```bash
# Basic health check
curl https://hrportal-backend-new.azurewebsites.net/api/health/ping

# Expected response (before PR merge):
{
  "status": "ok",
  "message": "pong",
  "version": "2026-01-20-v3"
}

# Database health
curl https://hrportal-backend-new.azurewebsites.net/api/health/db
```

### After PR #92 is Merged and Deployed

```bash
# New revision endpoint
curl https://hrportal-backend-new.azurewebsites.net/api/health/revision

# Expected response:
{
  "status": "ok",
  "revision": {
    "version": "106",
    "git_commit": "0864982...",
    "build_timestamp": "2026-01-23 06:00:00 UTC",
    "environment": "production",
    "build_info": {
      "github_run_id": "...",
      "deployed_by": "ismaelloveexcel"
    }
  }
}
```

---

## Prevention for Future

### Enable Application Insights (Recommended)

1. Go to **Application Insights** in Azure Portal
2. Create new Application Insights resource
3. Link to **hrportal-backend-new**
4. Set up alerts for:
   - HTTP 5xx errors
   - Failed requests > 5%
   - Response time > 5 seconds
   - App crashes

### Enable Always On (If Budget Allows)

1. Requires **Standard** tier or higher
2. Go to **Configuration** → **General settings**
3. Enable **Always On**
4. Prevents cold starts

### Set Up Health Check Monitoring

1. Go to **Health check** settings
2. Set path: `/api/health/ping`
3. Enable health check
4. Set probe interval: 5 minutes

---

## Get Help

If you've tried the above and backend is still down:

1. **Check Azure Service Health**
   - Go to Azure Portal → Service Health
   - Look for active issues in your region

2. **Review Full Logs**
   - Download complete logs: `az webapp log download`
   - Look for stack traces and error patterns

3. **Azure Support**
   - If critical, open Azure support ticket
   - Reference: App Service name and time of failure

---

## Summary

| Status | Description |
|--------|-------------|
| ❌ **Backend Down** | Separate issue from PR #92 |
| ✅ **PR #92 Ready** | Version tracking implemented, pending merge |
| ⏳ **Not Yet Deployed** | PR must be merged to `main` first |
| 🔧 **Action Needed** | Investigate and fix backend downtime |

**Next Steps:**
1. Fix backend downtime using steps above
2. Merge PR #92 to add version tracking
3. Verify deployment with new revision endpoint

**Questions?** Reply to this comment with error messages from Azure logs.
