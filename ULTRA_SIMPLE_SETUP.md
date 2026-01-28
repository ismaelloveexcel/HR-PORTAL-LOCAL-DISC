# ⚡ 3-STEP SETUP - NO READING REQUIRED

## What You Need (30 seconds)

1. **Azure CLI** installed on your computer
   - Not installed? Download: https://aka.ms/install-azure-cli
   - Takes 2 minutes to install

2. **Login to Azure** (one command)
   ```bash
   az login
   ```
   A browser window opens → Login → Close browser

**That's it for prerequisites!**

---

## 🚀 THE SETUP (Copy & Paste These 3 Commands)

### Windows Users:

1. **Open PowerShell** (right-click Start button → PowerShell)

2. **Copy and paste this:**
   ```powershell
   cd path\to\AZURE-DEPLOYMENT-HR-PORTAL
   .\setup-oidc.ps1
   ```

3. **Wait 2 minutes** - script does EVERYTHING automatically

### Mac/Linux Users:

1. **Open Terminal**

2. **Copy and paste this:**
   ```bash
   cd path/to/AZURE-DEPLOYMENT-HR-PORTAL
   ./setup-oidc.sh
   ```

3. **Wait 2 minutes** - script does EVERYTHING automatically

---

## 📋 AFTER THE SCRIPT FINISHES

The script will show you something like this:

```
AZURE_CLIENT_ID = 12345678-1234-1234-1234-123456789012
AZURE_TENANT_ID = 87654321-4321-4321-4321-210987654321
AZURE_SUBSCRIPTION_ID = abcdef12-3456-7890-abcd-ef1234567890
```

**Copy those 3 lines**

Then:

1. Go to: https://github.com/ismaelloveexcel/AZURE-DEPLOYMENT-HR-PORTAL/settings/secrets/actions

2. Click "New repository secret" for each one:
   - Name: `AZURE_CLIENT_ID` → Paste the value
   - Name: `AZURE_TENANT_ID` → Paste the value
   - Name: `AZURE_SUBSCRIPTION_ID` → Paste the value

3. Click "Add secret" for each

**DONE!** 🎉

---

## ✅ TEST IT WORKS

1. Go to: https://github.com/ismaelloveexcel/AZURE-DEPLOYMENT-HR-PORTAL/actions/workflows/deploy.yml

2. Click green "Run workflow" button → Click "Run workflow" again

3. Wait 5 minutes - watch it deploy successfully

---

## ❓ THAT'S IT?

**YES!** The script did:
- ✅ Created Azure application
- ✅ Set up permissions
- ✅ Configured OIDC authentication
- ✅ Everything you need

**Total time:** 5 minutes (mostly waiting for Azure)

**Your time:** 1 minute (copy/paste 3 commands + 3 secrets)

---

## 🆘 NEED HELP?

**Problem:** "Azure CLI not found"
→ Install it: https://aka.ms/install-azure-cli

**Problem:** "Not logged in"
→ Run: `az login`

**Problem:** Script error
→ Copy the error and create an issue: https://github.com/ismaelloveexcel/AZURE-DEPLOYMENT-HR-PORTAL/issues
