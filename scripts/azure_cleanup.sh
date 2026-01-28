#!/bin/bash
# Azure resource cleanup script for HR Portal
# Deletes all resources except those needed for deployment

az login

# Resource groups
RG_BAYNUNAH="BaynunahHR"
RG_HR_PORTAL="rg-HR-PORTAL"
RG_HR_TOOLS="rg-hr-tools"

# Delete App Service plans
az appservice plan delete --name ASP-BaynunahHR-8021 --resource-group $RG_BAYNUNAH --yes
az appservice plan delete --name ASP-BaynunahHRH-9cb9 --resource-group $RG_BAYNUNAH --yes

# Delete App Services
az webapp delete --name BaynunahHRDigitalPass-1 --resource-group $RG_BAYNUNAH
az webapp delete --name BaynunahHRPortal --resource-group $RG_BAYNUNAH

# Delete Virtual Network
az network vnet delete --name BaynunahHRPortalVnet --resource-group $RG_BAYNUNAH

# Delete Storage Account
az storage account delete --name csb100320306532a78 --resource-group Cloud-shell-storage-westeurope --yes

# Delete Foundry projects
az resource delete --name hr-portal-resource --resource-group $RG_HR_PORTAL --resource-type "Microsoft.CognitiveServices/accounts"
az resource delete --name hr-portal-resource/hr-portal --resource-group $RG_HR_PORTAL --resource-type "Microsoft.CognitiveServices/accounts"

# Delete Network Watcher
az network watcher delete --name NetworkWatcher_uaenorth --resource-group NetworkWatcherRG

# Delete Private DNS zones
az network private-dns zone delete --name privateink.postgres.database.azure.com --resource-group $RG_BAYNUNAH --yes
az network private-dns zone delete --name privateink.redis.cache.windows.net --resource-group $RG_BAYNUNAH --yes

# Delete unused Azure DevOps orgs (manual step, not CLI)
# Visit https://dev.azure.com/ and remove orgs if not needed

# Note: insurance-renewal-portal (Static Web App) and BaynunahHRPortal-server (PostgreSQL) are NOT deleted

echo "Cleanup complete. Only deployment resources remain."
