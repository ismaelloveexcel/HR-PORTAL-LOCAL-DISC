# Deployment Workflow Guide

## Overview

This document explains how deployments work in this repository and answers common questions about workflow impacts on the deployed application.

## Quick Answer: Does Running Workflows Impact My Deployed App?

**Short Answer:** Not anymore! We've configured the workflows to prevent deployment conflicts.

**What Changed:**
- ✅ Added concurrency controls to prevent multiple simultaneous deployments
- ✅ Disabled redundant deployment workflows
- ✅ Only ONE workflow (`deploy.yml`) now deploys to production
- ✅ All deployments are queued and run one at a time

## Current Deployment Strategy

### Active Workflows

#### 1. **deploy.yml** - PRIMARY DEPLOYMENT WORKFLOW ⭐
- **Triggers:** 
  - Every push to `main` branch
  - Manual trigger via workflow_dispatch
- **What it does:**
  - Builds frontend
  - Packages backend
  - Deploys both to Azure App Service
  - Runs database migrations
  - Performs health checks
- **Concurrency:** Configured to run one deployment at a time
- **Status:** ✅ ACTIVE

#### 2. **ci.yml** - CI/CD CHECKS (NON-DEPLOYMENT)
- **Triggers:**
  - Every push to `main`
  - Every pull request to `main`
- **What it does:**
  - Lints Python code
  - Checks TypeScript syntax
  - Runs security scans (CodeQL)
- **Impact:** ❌ Does NOT deploy - safe to run on every commit
- **Status:** ✅ ACTIVE

### Disabled (But Available for Manual Trigger)

The following workflows are **disabled for automatic triggering** but can still be run manually:

- `backend-appservice.yml` - Backend-only deployment
- `frontend-deploy.yml` - Frontend to Static Web Apps
- `deploy-frontend.yml` - Alternative frontend deployment (PR deploys disabled to avoid SWA staging exhaustion)
- `azure-static-web-apps-proud-forest-051662503.yml` - Auto-generated SWA deployment
- `backend-appservice-oidc.yml` - OIDC backend deployment

**Why disabled?** These workflows were redundant and could cause conflicts when running simultaneously with `deploy.yml`.

## How Concurrency Control Works

### Before Our Changes ❌
```
Commit pushed to main
    ↓
5 workflows trigger simultaneously:
    ├── deploy.yml (deploys everything)
    ├── backend-appservice.yml (deploys backend)
    ├── frontend-deploy.yml (deploys frontend)
    ├── deploy-frontend.yml (deploys frontend again)
    └── azure-static-web-apps-*.yml (deploys frontend again)
    
Result: Race conditions, deployment conflicts, wasted resources
```

### After Our Changes ✅
```
Commit pushed to main
    ↓
2 workflows trigger:
    ├── ci.yml (lint & test - doesn't deploy)
    └── deploy.yml (single coordinated deployment)
        └── Concurrency control ensures only one runs at a time
    
Result: Clean, predictable deployments
```

## Deployment Frequency

### Current Behavior
- **Automatic:** Every push to `main` triggers ONE deployment
- **Manual:** You can also trigger deployments manually via GitHub UI

### If You Want Less Frequent Deployments

If you'd prefer deployments NOT to happen on every commit, you have several options:

#### Option 1: Change to Manual-Only Deployments
Edit `.github/workflows/deploy.yml` line 3-6:
```yaml
# Before:
on:
  push:
    branches: [main]
  workflow_dispatch:

# After (manual only):
on:
  workflow_dispatch:
```

#### Option 2: Deploy Only on Tags
```yaml
on:
  push:
    tags:
      - 'v*'  # Only deploy when you create version tags like v1.0.0
  workflow_dispatch:
```

#### Option 3: Add Approval Gates
Use GitHub Environments with required reviewers:
1. Go to repository Settings → Environments
2. Create "production" environment
3. Add required reviewers
4. Update `deploy.yml` to use environment:
```yaml
jobs:
  build-and-deploy:
    environment: production  # Requires approval before running
```

## Understanding Workflow Impact

### Workflows That Deploy (Affect Production)
- ✅ `deploy.yml` - ONLY active deployment workflow
- ⏸️ All others disabled for auto-trigger

### Workflows That Don't Deploy (Safe)
- `ci.yml` - Linting and tests
- `pr-quality-check.yml` - PR validation
- `post-deployment-health.yml` - Post-deployment checks
- `backup-db.yml` - Database backups (scheduled)
- `security-monitoring.yml` - Security scans (scheduled)
- `app-health-check.yml` - Health monitoring (disabled by default)

## Best Practices

### For Solo HR Admin
1. **Make changes in feature branches** - Not directly on `main`
2. **Test thoroughly before merging** - Each merge to main triggers deployment
3. **Use manual deployments for critical changes** - Disable auto-deploy temporarily
4. **Monitor post-deployment** - Check health after each deployment

### For Development Teams
1. **Use pull requests** - Review before merging to main
2. **Enable branch protection** - Require reviews before merge
3. **Add approval gates** - Use GitHub Environments for production
4. **Schedule deployments** - Deploy during maintenance windows

## Troubleshooting

### Deployment Failed
1. Check the workflow run in the Actions tab
2. Review error messages
3. Check Azure portal for service status
4. Use manual trigger to retry

### Multiple Deployments Running
This should not happen anymore due to concurrency controls. If you see it:
1. Check if someone manually triggered workflows
2. Verify concurrency settings in `deploy.yml`

### Want to Rollback
1. Go to Actions tab
2. Find the previous successful deployment
3. Click "Re-run jobs"
4. Wait for deployment to complete

## Monitoring Deployment Health

After each deployment, the `post-deployment-health.yml` workflow runs automatically to:
- ✅ Check backend health
- ✅ Check frontend accessibility
- ✅ Verify basic functionality
- ✅ Create issues if problems detected

You'll receive notifications if deployment health checks fail.

## Summary

| Question | Answer |
|----------|--------|
| Do workflows impact my app? | Only `deploy.yml` deploys; others just test |
| Can multiple deployments conflict? | No - concurrency controls prevent this |
| How often does it deploy? | Once per commit to main (can be changed) |
| Can I deploy manually? | Yes - all workflows have manual triggers |
| What if deployment fails? | Health checks alert you; easy to rollback |

## Need Help?

- 📖 See `README.md` for general setup
- 🔐 See `AZURE_DEPLOYMENT_REVIEW.md` for Azure configuration
- 🚀 See individual workflow files for specific configurations
- 🐛 Create an issue if you encounter problems

---

**Last Updated:** 2026-01-20  
**Related Files:** `.github/workflows/deploy.yml`, `.github/workflows/ci.yml`
