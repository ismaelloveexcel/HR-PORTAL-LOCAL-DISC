# 🚀 Automated OIDC Setup Scripts

This directory contains automated scripts that configure Azure OIDC authentication for GitHub Actions in **one command**.

## What These Scripts Do

The scripts automatically:
1. ✅ Create Azure AD Application (if needed)
2. ✅ Create Service Principal
3. ✅ Assign Contributor role to resource group
4. ✅ Create federated credential for GitHub Actions
5. ✅ Display GitHub secrets to copy

**Time required:** 2-3 minutes

## Prerequisites

- Azure CLI installed ([Download](https://aka.ms/install-azure-cli))
- Logged into Azure (`az login`)
- Permissions to create Azure AD applications

## Quick Start

### For Linux/macOS:

```bash
# Make the script executable
chmod +x setup-oidc.sh

# Run the setup
./setup-oidc.sh
```

### For Windows (PowerShell):

```powershell
# Run the setup
.\setup-oidc.ps1
```

## What Happens Next

After running the script:

1. **Script Output:** You'll see the GitHub secrets you need to configure
2. **Copy Secrets:** Add them to: https://github.com/ismaelloveexcel/AZURE-DEPLOYMENT-HR-PORTAL/settings/secrets/actions
3. **Test Deployment:** Trigger a workflow run to verify OIDC authentication works

## Example Output

```
╔════════════════════════════════════════════════════════════════════════════╗
║                          SETUP COMPLETE!                                   ║
╚════════════════════════════════════════════════════════════════════════════╝

✓ Azure AD Application configured
✓ Service Principal created
✓ Contributor role assigned to resource group
✓ Federated credential created for GitHub Actions

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📋 GitHub Secrets Configuration
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

AZURE_CLIENT_ID = 12345678-1234-1234-1234-123456789012
AZURE_TENANT_ID = 87654321-4321-4321-4321-210987654321
AZURE_SUBSCRIPTION_ID = abcdef12-3456-7890-abcd-ef1234567890
```

## Troubleshooting

### "Azure CLI is not installed"
Install from: https://aka.ms/install-azure-cli

### "Not logged in to Azure"
Run: `az login`

### "Resource group does not exist"
The script will create it automatically

### "Federated credential already exists"
The script will recreate it to ensure correct configuration

## Understanding OIDC Token Expiration

**Question:** "It's over 1 hour - so token is expired?"

**Answer:** Yes, but this is **by design** and is a security feature:

- ✅ **OIDC tokens expire after 1 hour** - this is intentional
- ✅ **GitHub Actions automatically requests a new token** for each workflow run
- ✅ **You never manage tokens manually** - GitHub handles it all
- ✅ **No rotation needed** - tokens are temporary and auto-renewed

**How it works:**
1. Workflow starts → GitHub generates a fresh OIDC token (valid 1 hour)
2. Token is used to authenticate to Azure
3. Deployment completes (usually in 5-10 minutes)
4. Token expires after 1 hour (but workflow is already done)
5. Next workflow run → New token generated automatically

**This is better than client secrets because:**
- Client secrets last years and can be stolen
- OIDC tokens last 1 hour and are automatically managed
- No manual rotation or storage required

## Manual Setup (If You Prefer)

See `AZURE_OIDC_QUICK_SETUP.md` for step-by-step manual commands.

## Security Notes

✅ No secrets are stored in files  
✅ Federated credentials are repository-specific  
✅ Only the main branch can deploy  
✅ Follows Azure and GitHub security best practices

## Next Steps After Setup

1. Add the secrets to GitHub repository settings
2. Trigger a workflow: https://github.com/ismaelloveexcel/AZURE-DEPLOYMENT-HR-PORTAL/actions/workflows/deploy.yml
3. Watch the "Login to Azure" step succeed without client secret
4. Verify deployment completes successfully

## Need Help?

- 📖 Full documentation: `docs/AZURE_OIDC_SETUP.md`
- 🔧 Manual setup: `AZURE_OIDC_QUICK_SETUP.md`
- 🐛 Troubleshooting: See docs for common errors

---

**Ready to set up OIDC? Just run the script for your platform! 🚀**
