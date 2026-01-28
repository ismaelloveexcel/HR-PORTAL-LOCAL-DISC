# DEPRECATED — see START_HERE.md

# HR Portal Deployment - Simple Step-by-Step Guide

Follow these steps in order. Copy and paste each command.

## Step 1: Set Deployment Secrets (Automated)

Choose a secure password and export it (the script updates the server password automatically):

```bash
export POSTGRES_PASSWORD="YOUR_SECURE_PASSWORD"
export AUTO_APPROVE=true
export RESET_POSTGRES_PASSWORD=true
```

If your admin username differs, also set:

```bash
export POSTGRES_ADMIN_USER="YOUR_ADMIN_USER"
```

To keep the existing admin password, set:

```bash
export RESET_POSTGRES_PASSWORD=false
```

## Step 2: Run Automated Deployment (5 minutes)

Open your terminal in this project directory and run:

```bash
# Make script executable
chmod +x scripts/deploy_automated.sh

# Run deployment (non-interactive)
./scripts/deploy_automated.sh
```

**That's it!** The script will:

- Configure VNet integration
- Create database
- Build frontend
- Deploy everything
- Run migrations

## Step 3: Verify Deployment

After deployment completes, visit:

- **App:** https://BaynunahHRPortal.azurewebsites.net
- **API Docs:** https://BaynunahHRPortal.azurewebsites.net/docs

## Troubleshooting

### If deployment fails:

**Check logs:**

```bash
az webapp log tail --name BaynunahHRPortal --resource-group BaynunahHR
```

**Restart app:**

```bash
az webapp restart --name BaynunahHRPortal --resource-group BaynunahHR
```

If migrations fail, check logs and rerun the script after the app restarts.

### If login shows "An error occurred during login"

1. **Check database health:**

```bash
curl "https://BaynunahHRPortal.azurewebsites.net/api/health/db"
```

2. **If the admin account is missing or inactive, reset it:**

```bash
curl -X POST "https://BaynunahHRPortal.azurewebsites.net/api/health/reset-admin-password" \
  -H "X-Admin-Secret: <AUTH_SECRET_KEY>"
```

Replace `<AUTH_SECRET_KEY>` with the value from your App Service Configuration.

3. **Verify app settings** (`DATABASE_URL`, `AUTH_SECRET_KEY`) and restart the app:

```bash
az webapp restart --name BaynunahHRPortal --resource-group BaynunahHR
```

## Need Help?

If something fails, check the error message and:

1. Verify you're logged into Azure CLI: `az login`
2. Verify `POSTGRES_PASSWORD` is set
3. Check the logs command above

---

**Total Time: ~6 minutes**

- Step 1 (Automated): 1 minute
- Step 2 (Automated): 5 minutes
- Step 3 (Verify): 1 minute
