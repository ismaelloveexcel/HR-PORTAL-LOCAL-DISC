# Simple Steps
1) Delete old: **baynunah-hr-rg** (RG) and **insurance-renewal-portal** (SWA).
2) App Service (hrportal-backend-new):
   - Runtime: Linux, Python 3.11
   - Application Insights: ON
   - Paste App Settings from AZURE_APPSETTINGS.md
   - Startup command from AZURE_APPSETTINGS.md
3) PostgreSQL firewall:
   - EITHER “Allow public access from any Azure service”
   - OR add the App Service outbound IPs to the DB firewall rules.
4) SWA (hrportal-frontend-new): set `VITE_API_BASE_URL` in Static Web Apps **Configuration** to `https://hrportal-backend-new.azurewebsites.net/api`.
5) OIDC: Entra App → add Federated credentials for your repo/branch.
   - GitHub secrets: AZURE_CLIENT_ID, AZURE_TENANT_ID, AZURE_SUBSCRIPTION_ID
6) Push to main → Pipelines auto-deploy.
